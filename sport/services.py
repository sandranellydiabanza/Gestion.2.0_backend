from collections import defaultdict

from .models import ActionLog, Match, Team, User


def log_action(user, action: str, details: str):
    if not user or not getattr(user, 'is_authenticated', False):
        return None

    sport_user = User.objects.filter(email__iexact=user.email).first()
    user_name = user.get_full_name() or user.username
    if sport_user:
        user_name = f'{sport_user.firstName} {sport_user.lastName}'

    return ActionLog.objects.create(
        user=sport_user,
        userName=user_name,
        action=action,
        details=details,
    )


def calculate_standings(competition_id: str):
    standings = {
        team.id: {
            'teamId': team.id,
            'teamName': team.name,
            'etablissement': team.etablissement,
            'played': 0,
            'won': 0,
            'drawn': 0,
            'lost': 0,
            'points': 0,
            'goalsFor': 0,
            'goalsAgainst': 0,
            'goalDifference': 0,
        }
        for team in Team.objects.all()
    }

    matches = Match.objects.filter(competition_id=competition_id, status__in=['Terminé', 'Termine'])
    for match in matches:
        if match.scoreA is None or match.scoreB is None:
            continue

        standing_a = standings.get(match.teamA_id)
        standing_b = standings.get(match.teamB_id)
        if not standing_a or not standing_b:
            continue

        standing_a['played'] += 1
        standing_b['played'] += 1
        standing_a['goalsFor'] += match.scoreA
        standing_a['goalsAgainst'] += match.scoreB
        standing_b['goalsFor'] += match.scoreB
        standing_b['goalsAgainst'] += match.scoreA

        if match.scoreA > match.scoreB:
            standing_a['won'] += 1
            standing_a['points'] += 3
            standing_b['lost'] += 1
        elif match.scoreA < match.scoreB:
            standing_b['won'] += 1
            standing_b['points'] += 3
            standing_a['lost'] += 1
        else:
            standing_a['drawn'] += 1
            standing_b['drawn'] += 1
            standing_a['points'] += 1
            standing_b['points'] += 1

    rows = list(standings.values())
    for row in rows:
        row['goalDifference'] = row['goalsFor'] - row['goalsAgainst']

    return sorted(rows, key=lambda x: (-x['points'], -x['goalDifference'], -x['goalsFor'], x['teamName']))


def calculate_etablissement_standings():
    rows = defaultdict(lambda: {
        'etablissement': '',
        'teamsCount': 0,
        'matchesPlayed': 0,
        'matchesWon': 0,
        'points': 0,
    })

    for team in Team.objects.all():
        rows[team.etablissement]['etablissement'] = team.etablissement
        rows[team.etablissement]['teamsCount'] += 1

    matches = Match.objects.filter(status__in=['Terminé', 'Termine'])
    for match in matches:
        if match.scoreA is None or match.scoreB is None:
            continue

        row_a = rows[match.teamA.etablissement]
        row_b = rows[match.teamB.etablissement]
        row_a['etablissement'] = match.teamA.etablissement
        row_b['etablissement'] = match.teamB.etablissement
        row_a['matchesPlayed'] += 1
        row_b['matchesPlayed'] += 1

        if match.scoreA > match.scoreB:
            row_a['matchesWon'] += 1
            row_a['points'] += 3
        elif match.scoreA < match.scoreB:
            row_b['matchesWon'] += 1
            row_b['points'] += 3
        else:
            row_a['points'] += 1
            row_b['points'] += 1

    return sorted(rows.values(), key=lambda x: (-x['points'], x['etablissement']))
