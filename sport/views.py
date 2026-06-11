from datetime import datetime, timedelta

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ActionLog, CardRecord, Competition, GoalRecord, Match, Player, SportNotification, Team, User
from .serializers import (
    ActionLogSerializer,
    CardRecordSerializer,
    CompetitionSerializer,
    GoalRecordSerializer,
    LoginSerializer,
    MatchSerializer,
    PlayerSerializer,
    SportNotificationSerializer,
    TeamSerializer,
    UserSerializer,
)
from .services import calculate_etablissement_standings, calculate_standings, log_action


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        log_action(request.user, 'Login', 'Authentification utilisateur reussie')
        return Response(serializer.validated_data)


class CurrentUserAPIView(APIView):
    def get(self, request):
        user = User.objects.filter(email__iexact=request.user.email).first()
        if not user:
            return Response({'detail': 'Profil applicatif introuvable.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserSerializer(user).data)

    def patch(self, request):
        user = User.objects.filter(email__iexact=request.user.email).first()
        if not user:
            return Response({'detail': 'Profil applicatif introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        log_action(request.user, 'Profil mis a jour', 'Mise a jour des informations personnelles.')
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.prefetch_related('matches').all()
    serializer_class = CompetitionSerializer

    def perform_create(self, serializer):
        competition = serializer.save()
        log_action(self.request.user, 'Creation Competition', f'Creation de {competition.name} ({competition.sport})')

    def perform_update(self, serializer):
        competition = serializer.save()
        log_action(self.request.user, 'Modification Competition', f'Mise a jour de la competition {competition.name}')

    def perform_destroy(self, instance):
        log_action(self.request.user, 'Suppression Competition', f'Suppression de la competition ID: {instance.id}')
        instance.delete()


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.select_related('captain').prefetch_related('players').all()
    serializer_class = TeamSerializer

    def perform_create(self, serializer):
        team = serializer.save()
        log_action(self.request.user, 'Creation Equipe', f"Creation de l'equipe {team.name} ({team.etablissement})")

    def perform_update(self, serializer):
        team = serializer.save()
        log_action(self.request.user, 'Modification Equipe', f"Mise a jour de l'equipe {team.name}")

    def perform_destroy(self, instance):
        log_action(self.request.user, 'Suppression Equipe', f"Suppression de l'equipe ID: {instance.id}")
        instance.delete()

    @action(detail=True, methods=['get'])
    def players(self, request, pk=None):
        team = self.get_object()
        serializer = PlayerSerializer(team.players.all(), many=True)
        return Response(serializer.data)


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.select_related('team').all()
    serializer_class = PlayerSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        team_id = self.request.query_params.get('teamId')
        if team_id:
            queryset = queryset.filter(team_id=team_id)
        return queryset

    def perform_create(self, serializer):
        player = serializer.save()
        log_action(self.request.user, 'Ajout Joueur', f'Ajout de {player.firstName} {player.lastName}')

    def perform_update(self, serializer):
        player = serializer.save()
        log_action(self.request.user, 'Modification Joueur', f'Mise a jour du joueur {player.firstName} {player.lastName}')

    def perform_destroy(self, instance):
        log_action(self.request.user, 'Suppression Joueur', f'Suppression du joueur {instance.firstName} {instance.lastName}')
        instance.delete()


class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.select_related('competition', 'teamA', 'teamB').prefetch_related(
        'goals__scorer',
        'goals__team',
        'cards__player',
        'cards__team',
    )
    serializer_class = MatchSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        competition_id = self.request.query_params.get('competitionId')
        if competition_id:
            queryset = queryset.filter(competition_id=competition_id)
        return queryset

    def perform_create(self, serializer):
        match = serializer.save()
        log_action(self.request.user, 'Creation Match', f'Planification du match: {match.teamAName} vs {match.teamBName}')

    def perform_update(self, serializer):
        match = serializer.save()
        log_action(self.request.user, 'Mise a jour Match', f'Mise a jour du match ID {match.id} - Statut: {match.status}')

    def perform_destroy(self, instance):
        log_action(self.request.user, 'Suppression Match', f'Suppression du match ID: {instance.id}')
        instance.delete()

    @action(detail=True, methods=['post'], url_path='goals')
    def add_goal(self, request, pk=None):
        match = self.get_object()
        serializer = GoalRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        goal = serializer.save(match=match)

        if goal.team_id == match.teamA_id:
            match.scoreA = (match.scoreA or 0) + 1
        elif goal.team_id == match.teamB_id:
            match.scoreB = (match.scoreB or 0) + 1
        match.save(update_fields=['scoreA', 'scoreB', 'updatedAt'])

        log_action(self.request.user, 'Ajout But', f'But de {goal.scorerName} a la minute {goal.minute}')
        match = self.get_queryset().get(pk=match.pk)
        return Response(MatchSerializer(match).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='cards')
    def add_card(self, request, pk=None):
        match = self.get_object()
        serializer = CardRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        card = serializer.save(match=match)
        log_action(self.request.user, 'Ajout Carton', f'Carton {card.type} pour {card.playerName}')
        match = self.get_queryset().get(pk=match.pk)
        return Response(MatchSerializer(match).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='generate-auto-schedule')
    def generate_auto_schedule(self, request):
        competition = Competition.objects.get(pk=request.data['competitionId'])
        teams = list(Team.objects.filter(id__in=request.data.get('teamIds', [])))
        if len(teams) < 2:
            return Response({'detail': 'Il faut au moins 2 equipes.'}, status=status.HTTP_400_BAD_REQUEST)

        start_date = datetime.strptime(request.data['startDate'], '%Y-%m-%d').date()
        pitches = ['Terrain A (Campus Vogt)', "Stade de l'Ingenieur (Campus SJI)", 'Synthetique de Douala (Campus PSJD)']
        referees = ['M. Jean-Paul Mvogo', 'Arbitre Federal M. Noah', 'Arbitre Littoral M. Soni', 'M. Stephane Nkou']
        created = []
        current_date = start_date

        for i, team_a in enumerate(teams):
            for j, team_b in enumerate(teams):
                if j <= i:
                    continue
                match = Match.objects.create(
                    competition=competition,
                    teamA=team_a,
                    teamB=team_b,
                    date=current_date,
                    time=f'{14 + ((i + j) % 3)}:30',
                    pitch=pitches[(i + j) % len(pitches)],
                    referee=referees[(i + j) % len(referees)],
                    status='Planifié',
                )
                created.append(match)
                current_date += timedelta(days=3)

        log_action(self.request.user, 'Calendrier Auto', f'Generation automatique de {len(created)} matchs pour {competition.name}')
        return Response(MatchSerializer(created, many=True).data, status=status.HTTP_201_CREATED)


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = SportNotification.objects.all()
    serializer_class = SportNotificationSerializer

    @action(detail=True, methods=['post'], url_path='mark-as-read')
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.isRead = True
        notification.save(update_fields=['isRead'])
        return Response(self.get_serializer(notification).data)

    @action(detail=False, methods=['post'], url_path='mark-all-as-read')
    def mark_all_as_read(self, request):
        SportNotification.objects.update(isRead=True)
        return Response(self.get_serializer(self.get_queryset(), many=True).data)


class ActionLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActionLog.objects.select_related('user').all()
    serializer_class = ActionLogSerializer


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def standings(request, competition_id):
    return Response(calculate_standings(competition_id))


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def etablissement_standings(request):
    return Response(calculate_etablissement_standings())
