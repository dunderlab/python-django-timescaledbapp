from django.urls import path, include
from rest_framework import routers
from django.utils.safestring import mark_safe

from django.urls import path
from .views import SourceViewSet, MeasureViewSet, ChannelViewSet, TimeserieViewSet, ChunkViewSet

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


########################################################################
class EpochStreamDBRoot(routers.APIRootView):

    # ----------------------------------------------------------------------
    def get_view_name(self) -> str:
        return "TimeScaleDB App"

    # ----------------------------------------------------------------------
    def get_view_description(self, html=False) -> str:
        text = """"""
        if html:
            return mark_safe(f"<p>{text}</p>")
        else:
            return text


########################################################################
class DocumentedRouter(routers.DefaultRouter):
    APIRootView = EpochStreamDBRoot


router = DocumentedRouter()
router.register(r'source', SourceViewSet, basename='source')
router.register(r'measure', MeasureViewSet, basename='measure')
router.register(r'channel', ChannelViewSet, basename='channel')
router.register(r'chunk', ChunkViewSet, basename='chunk')
router.register(r'timeserie', TimeserieViewSet, basename='timeserie')
# router.register(r'token', CreateTokenView, basename='token')


app_name = 'timescaledbapp'
urlpatterns = [

    path('', include(router.urls)),



    path('api-auth/', include('rest_framework.urls')),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),


]

