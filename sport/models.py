from django.db import models



# =========================
# ENUMS / CHOICES
# =========================

ETABLISSEMENT_CHOICES = [
    ('Saint Jean Ingénieur', 'Saint Jean Ingénieur'),
    ('Saint Jean School of Management', 'Saint Jean School of Management'),
    ('Prépa Vogt', 'Prépa Vogt'),
    ('CPGE', 'CPGE'),
    ('Prépa Saint Jean Douala', 'Prépa Saint Jean Douala'),
]

USER_ROLE_CHOICES = [
    ('Administrateur', 'Administrateur'),
    ('Responsable sportif', 'Responsable sportif'),
    ('Capitaine equipe', 'Capitaine equipe'),
    ('Étudiant', 'Étudiant'),
]

SPORT_TYPE_CHOICES = [
    ('Football', 'Football'),
    ('Basketball', 'Basketball'),
    ('Handball', 'Handball'),
    ('Volleyball', 'Volleyball'),
]

COMPETITION_TYPE_CHOICES = [
    ('championnat', 'championnat'),
    ('coupe', 'coupe'),
    ('élimination directe', 'élimination directe'),
]

COMPETITION_STATUS_CHOICES = [
    ('Planifié', 'Planifié'),
    ('En cours', 'En cours'),
    ('Terminé', 'Terminé'),
]

MATCH_STATUS_CHOICES = [
    ('Planifié', 'Planifié'),
    ('En cours', 'En cours'),
    ('Terminé', 'Terminé'),
    ('Reporté', 'Reporté'),
]

CARD_TYPE_CHOICES = [
    ('yellow', 'yellow'),
    ('red', 'red'),
]

NOTIFICATION_TYPE_CHOICES = [
    ('match_update', 'match_update'),
    ('schedule', 'schedule'),
    ('result', 'result'),
    ('announcement', 'announcement'),
]


# =========================
# USER
# =========================

class User(models.Model):
    id = models.CharField(max_length=100, primary_key=True)

    email = models.EmailField(unique=True)

    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)

    motDePasse = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    role = models.CharField(
        max_length=50,
        choices=USER_ROLE_CHOICES
    )

    etablissement = models.CharField(
        max_length=100,
        choices=ETABLISSEMENT_CHOICES,
        blank=True,
        null=True
    )

    avatarUrl = models.URLField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.firstName} {self.lastName}"


# =========================
# COMPETITION
# =========================

class Competition(models.Model):
    id = models.CharField(max_length=100, primary_key=True)

    name = models.CharField(max_length=255)

    type = models.CharField(
        max_length=50,
        choices=COMPETITION_TYPE_CHOICES
    )

    sport = models.CharField(
        max_length=50,
        choices=SPORT_TYPE_CHOICES
    )

    startDate = models.DateField()

    endDate = models.DateField()

    rules = models.TextField()

    status = models.CharField(
        max_length=50,
        choices=COMPETITION_STATUS_CHOICES
    )

    teamsCount = models.IntegerField()

    def __str__(self):
        return self.name


# =========================
# TEAM
# =========================

class Team(models.Model):
    id = models.CharField(max_length=100, primary_key=True)

    name = models.CharField(max_length=255)

    etablissement = models.CharField(
        max_length=100,
        choices=ETABLISSEMENT_CHOICES
    )

    filiere = models.CharField(max_length=255)

    logoColor = models.CharField(max_length=100)

    captain = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='captain_teams'
    )

    captainName = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    playersCount = models.IntegerField()

    def __str__(self):
        return self.name


# =========================
# PLAYER
# =========================

class Player(models.Model):
    id = models.CharField(max_length=100, primary_key=True)

    firstName = models.CharField(max_length=100)

    lastName = models.CharField(max_length=100)

    number = models.IntegerField()

    position = models.CharField(max_length=100)

    className = models.CharField(max_length=255)

    photoUrl = models.URLField(
        blank=True,
        null=True
    )

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='players'
    )

    def __str__(self):
        return f"{self.firstName} {self.lastName}"


# =========================
# MATCH
# =========================

class Match(models.Model):
    id = models.CharField(max_length=100, primary_key=True)

    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name='matches'
    )

    competitionName = models.CharField(max_length=255)

    teamA = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='matches_team_a'
    )

    teamAName = models.CharField(max_length=255)

    teamALogoColor = models.CharField(max_length=100)

    teamB = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='matches_team_b'
    )

    teamBName = models.CharField(max_length=255)

    teamBLogoColor = models.CharField(max_length=100)

    scoreA = models.IntegerField(
        blank=True,
        null=True
    )

    scoreB = models.IntegerField(
        blank=True,
        null=True
    )

    date = models.DateField()

    time = models.TimeField()

    pitch = models.CharField(max_length=255)

    referee = models.CharField(max_length=255)

    status = models.CharField(
        max_length=50,
        choices=MATCH_STATUS_CHOICES
    )

    reportReason = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.teamAName} vs {self.teamBName}"


# =========================
# CARD RECORD
# =========================

class CardRecord(models.Model):
    id = models.CharField(max_length=100, primary_key=True)

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='cards'
    )

    playerName = models.CharField(max_length=255)

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE
    )

    type = models.CharField(
        max_length=20,
        choices=CARD_TYPE_CHOICES
    )

    minute = models.IntegerField()

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='cards'
    )

    def __str__(self):
        return f"{self.playerName} - {self.type}"


# =========================
# GOAL RECORD
# =========================

class GoalRecord(models.Model):
    id = models.CharField(max_length=100, primary_key=True)

    scorer = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='goals'
    )

    scorerName = models.CharField(max_length=255)

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE
    )

    minute = models.IntegerField()

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='goals'
    )

    def __str__(self):
        return self.scorerName


# =========================
# STANDING
# =========================

class Standing(models.Model):
    team = models.OneToOneField(
        Team,
        on_delete=models.CASCADE,
        related_name='standing'
    )

    teamName = models.CharField(max_length=255)

    etablissement = models.CharField(
        max_length=100,
        choices=ETABLISSEMENT_CHOICES
    )

    played = models.IntegerField()

    won = models.IntegerField()

    drawn = models.IntegerField()

    lost = models.IntegerField()

    points = models.IntegerField()

    goalsFor = models.IntegerField()

    goalsAgainst = models.IntegerField()

    goalDifference = models.IntegerField()

    def __str__(self):
        return self.teamName


# =========================
# ETABLISSEMENT STANDING
# =========================

class EtablissementStanding(models.Model):
    etablissement = models.CharField(
        max_length=100,
        choices=ETABLISSEMENT_CHOICES
    )

    teamsCount = models.IntegerField()

    matchesPlayed = models.IntegerField()

    matchesWon = models.IntegerField()

    points = models.IntegerField()

    def __str__(self):
        return self.etablissement


# =========================
# SPORT NOTIFICATION
# =========================

class SportNotification(models.Model):
    id = models.CharField(max_length=100, primary_key=True)

    title = models.CharField(max_length=255)

    content = models.TextField()

    type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES
    )

    date = models.DateTimeField()

    isRead = models.BooleanField(default=False)

    def __str__(self):
        return self.title


# =========================
# ACTION LOG
# =========================

class ActionLog(models.Model):
    id = models.CharField(max_length=100, primary_key=True)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='logs'
    )

    userName = models.CharField(max_length=255)

    action = models.CharField(max_length=255)

    details = models.TextField()

    timestamp = models.DateTimeField()

    def __str__(self):
        return self.action

