from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from .views import MeasureViewSet, ChannelViewSet, TimeSerieViewSet


router = routers.DefaultRouter()
router.register(r'measure', MeasureViewSet)
router.register(r'channel', ChannelViewSet)
router.register(r'timeserie', TimeSerieViewSet)


urlpatterns = [

    # path("", HomeView.as_view()),
    path('/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),

]

