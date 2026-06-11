from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ActionLogViewSet,
    CompetitionViewSet,
    CurrentUserAPIView,
    LoginAPIView,
    MatchViewSet,
    NotificationViewSet,
    PlayerViewSet,
    TeamViewSet,
    UserViewSet,
    etablissement_standings,
    standings,
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('competitions', CompetitionViewSet, basename='competition')
router.register('teams', TeamViewSet, basename='team')
router.register('players', PlayerViewSet, basename='player')
router.register('matches', MatchViewSet, basename='match')
router.register('notifications', NotificationViewSet, basename='notification')
router.register('audit-logs', ActionLogViewSet, basename='audit-log')

urlpatterns = [
    path('auth/login/', LoginAPIView.as_view(), name='auth-login'),
    path('auth/me/', CurrentUserAPIView.as_view(), name='auth-me'),
    path('standings/<str:competition_id>/', standings, name='standings'),
    path('standings/etablissements/', etablissement_standings, name='etablissement-standings'),
]

urlpatterns += router.urls
