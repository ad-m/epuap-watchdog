from rest_framework import routers
from epuap_watchdog.institutions.viewsets import RESPViewSet, REGONViewSet, REGONErrorViewSet, JSTConnectionViewSet, InstitutionViewSet, ESPViewSet


router = routers.DefaultRouter()
router.register(r'institutions/institution', InstitutionViewSet)
router.register(r'institutions/esp', ESPViewSet)
router.register(r'institutions/resp', RESPViewSet)
router.register(r'institutions/regon', REGONViewSet)
router.register(r'institutions/regonerror', REGONErrorViewSet)
router.register(r'institutions/jstconnection', JSTConnectionViewSet)
