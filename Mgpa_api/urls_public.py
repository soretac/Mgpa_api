from django.contrib import admin
from django.urls import path
from Client.views import  ClientViewSet, ClientAbonneViewset, PrixViews
from Entreprise.views import EseValidation
from django.conf.urls.static import static
from rest_framework.routers import SimpleRouter
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView




router = SimpleRouter()
router.register('client', ClientViewSet)
router.register('abonnement-ese', ClientAbonneViewset)
router.register('prix-soretac', PrixViews)

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('client/abonnement', EseValidation.as_view(), name="validation"),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
      
] + router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)