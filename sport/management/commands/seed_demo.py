from datetime import date, time

from django.core.management.base import BaseCommand

from sport.models import Competition, Match, Player, SportNotification, Team, User


class Command(BaseCommand):
    help = 'Charge les donnees de demonstration deduites du frontend Angular.'

    def handle(self, *args, **options):
        users = [
            {
                'id': 'u1',
                'email': 'admin@iusj.org',
                'firstName': 'Jean-Marc',
                'lastName': 'Nkou',
                'role': 'Administrateur',
                'etablissement': 'Saint Jean Ingénieur',
                'motDePasse': 'admin123',
            },
            {
                'id': 'u2',
                'email': 'responsable@iusj.org',
                'firstName': 'Aline',
                'lastName': 'Zanga',
                'role': 'Responsable sportif',
                'etablissement': 'Saint Jean School of Management',
                'motDePasse': 'resp123',
            },
            {
                'id': 'u3',
                'email': 'capitaine@iusj.org',
                'firstName': 'Marc',
                'lastName': 'Atangana',
                'role': 'Capitaine equipe',
                'etablissement': 'Saint Jean Ingénieur',
                'motDePasse': 'cap123',
            },
            {
                'id': 'u4',
                'email': 'student@iusj.org',
                'firstName': 'Paul',
                'lastName': 'Mbarga',
                'role': 'Étudiant',
                'etablissement': 'Prépa Vogt',
                'motDePasse': 'stud123',
            },
        ]
        for item in users:
            User.objects.update_or_create(id=item['id'], defaults=item)

        competitions = [
            {
                'id': 'c1',
                'name': 'Championnat Inter-Établissements IUSJ 2026',
                'type': 'championnat',
                'sport': 'Football',
                'startDate': date(2026, 5, 1),
                'endDate': date(2026, 6, 25),
                'rules': 'Matchs de 90 minutes. Victoire = 3 points, nul = 1 point, defaite = 0 point.',
                'status': 'En cours',
            },
            {
                'id': 'c2',
                'name': "Coupe de l'Ingénieur Basket-ball",
                'type': 'coupe',
                'sport': 'Basketball',
                'startDate': date(2026, 6, 1),
                'endDate': date(2026, 6, 20),
                'rules': 'Elimination directe. Matchs de 4 x 10 minutes.',
                'status': 'Planifié',
            },
        ]
        for item in competitions:
            Competition.objects.update_or_create(id=item['id'], defaults=item)

        teams = [
            {'id': 't1', 'name': 'SJI Génie Logiciel FC', 'etablissement': 'Saint Jean Ingénieur', 'filiere': 'Génie Logiciel', 'logoColor': '#38bdf8'},
            {'id': 't2', 'name': 'SJSM Finance Kings', 'etablissement': 'Saint Jean School of Management', 'filiere': 'Finance & Comptabilité', 'logoColor': '#22c55e'},
            {'id': 't3', 'name': 'Vogt Lions', 'etablissement': 'Prépa Vogt', 'filiere': 'MPSI - PCSI', 'logoColor': '#6366f1'},
            {'id': 't4', 'name': 'CPGE Titans', 'etablissement': 'CPGE', 'filiere': 'Classes Préparatoires', 'logoColor': '#ec4899'},
            {'id': 't5', 'name': 'Douala Sharks', 'etablissement': 'Prépa Saint Jean Douala', 'filiere': 'Tronc Commun', 'logoColor': '#14b8a6'},
        ]
        for item in teams:
            Team.objects.update_or_create(id=item['id'], defaults=item)

        players = [
            {'id': 'p1', 'firstName': 'Marc', 'lastName': 'Atangana', 'number': 10, 'position': 'Milieu', 'className': 'SJI 4', 'team_id': 't1'},
            {'id': 'p2', 'firstName': 'Cédric', 'lastName': 'Fouda', 'number': 9, 'position': 'Attaquant', 'className': 'SJI 3', 'team_id': 't1'},
            {'id': 'p3', 'firstName': 'Stève', 'lastName': 'Ondoua', 'number': 1, 'position': 'Gardien', 'className': 'SJI 5', 'team_id': 't1'},
            {'id': 'p4', 'firstName': 'Yannick', 'lastName': 'Noah', 'number': 8, 'position': 'Milieu', 'className': 'SJSM 3', 'team_id': 't2'},
            {'id': 'p5', 'firstName': 'Emmanuel', 'lastName': 'Simo', 'number': 10, 'position': 'Attaquant', 'className': 'SJSM 2', 'team_id': 't2'},
            {'id': 'p7', 'firstName': 'Arthur', 'lastName': 'Nguene', 'number': 11, 'position': 'Attaquant', 'className': 'Sup Vogt', 'team_id': 't3'},
            {'id': 'p9', 'firstName': 'Stéphane', 'lastName': 'Belinga', 'number': 7, 'position': 'Meneur', 'className': 'CPGE 2', 'team_id': 't4'},
            {'id': 'p11', 'firstName': 'Olivier', 'lastName': 'Kamdem', 'number': 9, 'position': 'Attaquant', 'className': 'Douala 1', 'team_id': 't5'},
        ]
        for item in players:
            Player.objects.update_or_create(id=item['id'], defaults=item)

        captains = {'t1': 'p1', 't2': 'p4', 't3': 'p7', 't4': 'p9', 't5': 'p11'}
        for team_id, player_id in captains.items():
            Team.objects.filter(id=team_id).update(captain_id=player_id)

        matches = [
            {'id': 'm1', 'competition_id': 'c1', 'teamA_id': 't1', 'teamB_id': 't2', 'scoreA': 3, 'scoreB': 1, 'date': date(2026, 5, 10), 'time': time(15, 30), 'pitch': "Stade de l'Ingénieur (Campus SJI)", 'referee': 'M. Jean-Paul Mvogo', 'status': 'Terminé'},
            {'id': 'm2', 'competition_id': 'c1', 'teamA_id': 't3', 'teamB_id': 't5', 'scoreA': 2, 'scoreB': 2, 'date': date(2026, 5, 12), 'time': time(14, 0), 'pitch': 'Terrain A (Campus Vogt)', 'referee': 'Arbitre Fédéral M. Noah', 'status': 'Terminé'},
            {'id': 'm3', 'competition_id': 'c1', 'teamA_id': 't4', 'teamB_id': 't1', 'scoreA': 0, 'scoreB': 4, 'date': date(2026, 5, 15), 'time': time(16, 0), 'pitch': "Stade de l'Ingénieur (Campus SJI)", 'referee': 'M. Jean-Paul Mvogo', 'status': 'Terminé'},
            {'id': 'm4', 'competition_id': 'c1', 'teamA_id': 't5', 'teamB_id': 't4', 'date': date(2026, 6, 12), 'time': time(15, 30), 'pitch': 'Synthetique de Douala (Campus PSJD)', 'referee': 'Arbitre Littoral M. Soni', 'status': 'Planifié'},
        ]
        for item in matches:
            Match.objects.update_or_create(id=item['id'], defaults=item)

        notifications = [
            {'id': 'n1', 'title': 'Report de match', 'content': 'Un match peut etre reporte depuis le module rencontres.', 'type': 'schedule', 'isRead': False},
            {'id': 'n2', 'title': 'Resultat disponible', 'content': 'Les classements sont recalcules automatiquement.', 'type': 'result', 'isRead': False},
        ]
        for item in notifications:
            SportNotification.objects.update_or_create(id=item['id'], defaults=item)

        self.stdout.write(self.style.SUCCESS('Donnees de demonstration chargees.'))
