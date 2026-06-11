from django.contrib import admin

from .models import ActionLog, CardRecord, Competition, GoalRecord, Match, Player, SportNotification, Team, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'firstName', 'lastName', 'role', 'etablissement')
    search_fields = ('email', 'firstName', 'lastName')
    list_filter = ('role', 'etablissement')


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'sport', 'status', 'startDate', 'endDate')
    search_fields = ('name', 'sport')
    list_filter = ('type', 'sport', 'status')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'etablissement', 'filiere', 'playersCount', 'captainName')
    search_fields = ('name', 'filiere')
    list_filter = ('etablissement',)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('firstName', 'lastName', 'number', 'position', 'team')
    search_fields = ('firstName', 'lastName', 'team__name')
    list_filter = ('team', 'position')


class GoalInline(admin.TabularInline):
    model = GoalRecord
    extra = 0


class CardInline(admin.TabularInline):
    model = CardRecord
    extra = 0


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('competition', 'teamA', 'teamB', 'date', 'time', 'status', 'scoreA', 'scoreB')
    search_fields = ('competition__name', 'teamA__name', 'teamB__name')
    list_filter = ('status', 'competition', 'date')
    inlines = [GoalInline, CardInline]


@admin.register(SportNotification)
class SportNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'date', 'isRead')
    search_fields = ('title', 'content')
    list_filter = ('type', 'isRead')


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('userName', 'action', 'timestamp')
    search_fields = ('userName', 'action', 'details')
    list_filter = ('action',)
