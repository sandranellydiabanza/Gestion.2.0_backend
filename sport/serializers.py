from django.contrib.auth.models import User as DjangoUser
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    ActionLog,
    CardRecord,
    Competition,
    GoalRecord,
    Match,
    Player,
    SportNotification,
    Team,
    User,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'firstName',
            'lastName',
            'motDePasse',
            'role',
            'etablissement',
            'avatarUrl',
        ]
        extra_kwargs = {'motDePasse': {'write_only': True, 'required': False}}


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    motDePasse = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs['email'].lower()
        password = attrs['motDePasse']
        try:
            sport_user = User.objects.get(email__iexact=email, motDePasse=password)
        except User.DoesNotExist as exc:
            raise serializers.ValidationError('Identifiants invalides') from exc

        django_user, _ = DjangoUser.objects.get_or_create(
            username=sport_user.email,
            defaults={
                'email': sport_user.email,
                'first_name': sport_user.firstName,
                'last_name': sport_user.lastName,
            },
        )
        django_user.email = sport_user.email
        django_user.first_name = sport_user.firstName
        django_user.last_name = sport_user.lastName
        django_user.set_unusable_password()
        django_user.save()

        refresh = RefreshToken.for_user(django_user)
        return {
            'refresh': str(refresh),
            'token': str(refresh.access_token),
            'user': UserSerializer(sport_user).data,
        }


class CompetitionSerializer(serializers.ModelSerializer):
    teamsCount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Competition
        fields = ['id', 'name', 'type', 'sport', 'startDate', 'endDate', 'rules', 'status', 'teamsCount']


class TeamSerializer(serializers.ModelSerializer):
    captainId = serializers.PrimaryKeyRelatedField(
        source='captain',
        queryset=Player.objects.all(),
        allow_null=True,
        required=False,
    )
    captainName = serializers.CharField(read_only=True)
    playersCount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'etablissement', 'filiere', 'logoColor', 'captainId', 'captainName', 'playersCount']


class PlayerSerializer(serializers.ModelSerializer):
    teamId = serializers.PrimaryKeyRelatedField(source='team', queryset=Team.objects.all())

    class Meta:
        model = Player
        fields = ['id', 'firstName', 'lastName', 'number', 'position', 'className', 'photoUrl', 'teamId']


class GoalRecordSerializer(serializers.ModelSerializer):
    scorerId = serializers.PrimaryKeyRelatedField(source='scorer', queryset=Player.objects.all())
    scorerName = serializers.CharField(read_only=True)
    teamId = serializers.PrimaryKeyRelatedField(source='team', queryset=Team.objects.all())

    class Meta:
        model = GoalRecord
        fields = ['id', 'scorerId', 'scorerName', 'teamId', 'minute']


class CardRecordSerializer(serializers.ModelSerializer):
    playerId = serializers.PrimaryKeyRelatedField(source='player', queryset=Player.objects.all())
    playerName = serializers.CharField(read_only=True)
    teamId = serializers.PrimaryKeyRelatedField(source='team', queryset=Team.objects.all())

    class Meta:
        model = CardRecord
        fields = ['id', 'playerId', 'playerName', 'teamId', 'type', 'minute']


class MatchSerializer(serializers.ModelSerializer):
    competitionId = serializers.PrimaryKeyRelatedField(source='competition', queryset=Competition.objects.all())
    competitionName = serializers.CharField(read_only=True)
    teamAId = serializers.PrimaryKeyRelatedField(source='teamA', queryset=Team.objects.all())
    teamAName = serializers.CharField(read_only=True)
    teamALogoColor = serializers.CharField(read_only=True)
    teamBId = serializers.PrimaryKeyRelatedField(source='teamB', queryset=Team.objects.all())
    teamBName = serializers.CharField(read_only=True)
    teamBLogoColor = serializers.CharField(read_only=True)
    goals = GoalRecordSerializer(many=True, read_only=True)
    cards = CardRecordSerializer(many=True, read_only=True)

    class Meta:
        model = Match
        fields = [
            'id',
            'competitionId',
            'competitionName',
            'teamAId',
            'teamAName',
            'teamALogoColor',
            'teamBId',
            'teamBName',
            'teamBLogoColor',
            'scoreA',
            'scoreB',
            'date',
            'time',
            'pitch',
            'referee',
            'status',
            'cards',
            'goals',
            'reportReason',
        ]

    def validate(self, attrs):
        team_a = attrs.get('teamA') or getattr(self.instance, 'teamA', None)
        team_b = attrs.get('teamB') or getattr(self.instance, 'teamB', None)
        if team_a and team_b and team_a == team_b:
            raise serializers.ValidationError('Une rencontre doit opposer deux equipes distinctes.')
        return attrs


class SportNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportNotification
        fields = ['id', 'title', 'content', 'type', 'date', 'isRead']
        read_only_fields = ['date', 'isRead']


class ActionLogSerializer(serializers.ModelSerializer):
    userId = serializers.PrimaryKeyRelatedField(
        source='user',
        queryset=User.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = ActionLog
        fields = ['id', 'userId', 'userName', 'action', 'details', 'timestamp']
        read_only_fields = ['timestamp']
