from django.db import models
from django.utils import timezone


ETABLISSEMENTS = [
    ('Saint Jean Ingénieur', 'Saint Jean Ingénieur'),
    ('Saint Jean Ingenieur', 'Saint Jean Ingenieur'),
    ('Saint Jean School of Management', 'Saint Jean School of Management'),
    ('Prépa Vogt', 'Prépa Vogt'),
    ('Prepa Vogt', 'Prepa Vogt'),
    ('CPGE', 'CPGE'),
    ('Prépa Saint Jean Douala', 'Prépa Saint Jean Douala'),
    ('Prepa Saint Jean Douala', 'Prepa Saint Jean Douala'),
]

USER_ROLES = [
    ('Administrateur', 'Administrateur'),
    ('Responsable sportif', 'Responsable sportif'),
    ('Capitaine equipe', 'Capitaine equipe'),
    ('Étudiant', 'Étudiant'),
    ('Etudiant', 'Etudiant'),
]

SPORT_TYPES = [
    ('Football', 'Football'),
    ('Basketball', 'Basketball'),
    ('Handball', 'Handball'),
    ('Volleyball', 'Volleyball'),
]

COMPETITION_TYPES = [
    ('championnat', 'championnat'),
    ('coupe', 'coupe'),
    ('élimination directe', 'élimination directe'),
    ('elimination directe', 'elimination directe'),
]

COMPETITION_STATUSES = [
    ('Planifié', 'Planifié'),
    ('Planifie', 'Planifie'),
    ('En cours', 'En cours'),
    ('Terminé', 'Terminé'),
    ('Termine', 'Termine'),
]

MATCH_STATUSES = [
    ('Planifié', 'Planifié'),
    ('Planifie', 'Planifie'),
    ('En cours', 'En cours'),
    ('Terminé', 'Terminé'),
    ('Termine', 'Termine'),
    ('Reporté', 'Reporté'),
    ('Reporte', 'Reporte'),
]

CARD_TYPES = [
    ('yellow', 'yellow'),
    ('red', 'red'),
]

NOTIFICATION_TYPES = [
    ('match_update', 'match_update'),
    ('schedule', 'schedule'),
    ('result', 'result'),
    ('announcement', 'announcement'),
]


def next_id(prefix: str) -> str:
    return f'{prefix}-{int(timezone.now().timestamp() * 1000)}'


class User(models.Model):
    id = models.CharField(max_length=64, primary_key=True, editable=False)
    email = models.EmailField(unique=True)
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    motDePasse = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=50, choices=USER_ROLES)
    etablissement = models.CharField(max_length=100, choices=ETABLISSEMENTS, blank=True)
    avatarUrl = models.URLField(blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['lastName', 'firstName']

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = next_id('u')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.firstName} {self.lastName}'


class Competition(models.Model):
    id = models.CharField(max_length=64, primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=COMPETITION_TYPES)
    sport = models.CharField(max_length=50, choices=SPORT_TYPES)
    startDate = models.DateField()
    endDate = models.DateField()
    rules = models.TextField()
    status = models.CharField(max_length=50, choices=COMPETITION_STATUSES)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-startDate', 'name']

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = next_id('c')
        super().save(*args, **kwargs)

    @property
    def teamsCount(self):
        team_ids = set()
        for match in self.matches.all():
            team_ids.add(match.teamA_id)
            team_ids.add(match.teamB_id)
        return len(team_ids)

    def __str__(self):
        return self.name


class Team(models.Model):
    id = models.CharField(max_length=64, primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    etablissement = models.CharField(max_length=100, choices=ETABLISSEMENTS)
    filiere = models.CharField(max_length=255)
    logoColor = models.CharField(max_length=40, default='#38bdf8')
    captain = models.ForeignKey(
        'Player',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='captained_teams',
    )
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = next_id('t')
        super().save(*args, **kwargs)

    @property
    def captainId(self):
        return self.captain_id

    @property
    def captainName(self):
        if not self.captain:
            return None
        return f'{self.captain.firstName} {self.captain.lastName}'

    @property
    def playersCount(self):
        return self.players.count()

    def __str__(self):
        return self.name


class Player(models.Model):
    id = models.CharField(max_length=64, primary_key=True, editable=False)
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    number = models.PositiveSmallIntegerField()
    position = models.CharField(max_length=100)
    className = models.CharField(max_length=255)
    photoUrl = models.URLField(blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['team__name', 'number', 'lastName']
        constraints = [
            models.UniqueConstraint(fields=['team', 'number'], name='unique_player_number_by_team'),
        ]

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = next_id('p')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.firstName} {self.lastName}'


class Match(models.Model):
    id = models.CharField(max_length=64, primary_key=True, editable=False)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='matches')
    teamA = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='home_matches')
    teamB = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='away_matches')
    scoreA = models.PositiveSmallIntegerField(blank=True, null=True)
    scoreB = models.PositiveSmallIntegerField(blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()
    pitch = models.CharField(max_length=255)
    referee = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=MATCH_STATUSES, default='Planifié')
    reportReason = models.TextField(blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'time']
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(teamA=models.F('teamB')),
                name='match_requires_two_distinct_teams',
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = next_id('m')
        super().save(*args, **kwargs)

    @property
    def competitionName(self):
        return self.competition.name

    @property
    def teamAName(self):
        return self.teamA.name

    @property
    def teamALogoColor(self):
        return self.teamA.logoColor

    @property
    def teamBName(self):
        return self.teamB.name

    @property
    def teamBLogoColor(self):
        return self.teamB.logoColor

    def __str__(self):
        return f'{self.teamAName} vs {self.teamBName}'


class GoalRecord(models.Model):
    id = models.CharField(max_length=64, primary_key=True, editable=False)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='goals')
    scorer = models.ForeignKey(Player, on_delete=models.PROTECT, related_name='goals')
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='goals')
    minute = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['minute', 'id']

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = next_id('goal')
        super().save(*args, **kwargs)

    @property
    def scorerName(self):
        return f'{self.scorer.firstName} {self.scorer.lastName}'

    def __str__(self):
        return f'{self.scorerName} {self.minute}'


class CardRecord(models.Model):
    id = models.CharField(max_length=64, primary_key=True, editable=False)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='cards')
    player = models.ForeignKey(Player, on_delete=models.PROTECT, related_name='cards')
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='cards')
    type = models.CharField(max_length=20, choices=CARD_TYPES)
    minute = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['minute', 'id']

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = next_id('card')
        super().save(*args, **kwargs)

    @property
    def playerName(self):
        return f'{self.player.firstName} {self.player.lastName}'

    def __str__(self):
        return f'{self.playerName} {self.type}'


class SportNotification(models.Model):
    id = models.CharField(max_length=64, primary_key=True, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    date = models.DateTimeField(default=timezone.now)
    isRead = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = next_id('n')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ActionLog(models.Model):
    id = models.CharField(max_length=64, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='logs')
    userName = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    details = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = next_id('log')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.action
