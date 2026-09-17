from django.contrib import admin
from django.urls import path, include, re_path
from Client.views import ClientAbonneViewset
from Entreprise.views import EseValidation, ListOrganFonct, DelOrganFonct, UpdateOrganFonct, CreateOrganFonct, ImportOrgFonctView
from MatRoulant.views import AssurViewSet, VehiculeViewSet, VisitechViewSet, CartegriseViewSet
from CompteurApps.views import CompteurCreate, AlertEpViewSet, ListAlertEp, ListCountEpCritiq
from MatRoulant.views import ImportEnginView
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers
from django.views.generic import TemplateView
from Travaux.views import DTEpCreate, ListDTEp, CreateVehDepo, CreateVehRecu
from PreventApps.views import ListSuiviEp
from Entreprise.views import AccueilEntreprises, CreatePrestations, CreatePieceRechange, ListPrestations, ListPieceRechange, UpdatePrestations, UpdatePieceRechange, DeletePrestations, DeletePieceRechange, ListAbonneViews
from django.conf import settings
from django.conf.urls.static import static



router = routers.DefaultRouter()

router.register("engins", VehiculeViewSet, basename="engins")

# router.register("profile", ProfileViewSet, basename="profile")

engin_router = routers.NestedSimpleRouter(router, "engins", lookup='engin')
compt_router = routers.NestedSimpleRouter(router, "engins", lookup='engin')





engin_router.register("assurance", AssurViewSet, basename='engin-assurance')
engin_router.register("visitech", VisitechViewSet, basename='engin-visite')
engin_router.register("cartegrise", CartegriseViewSet, basename='engin-cartegrise')
engin_router.register("compteur", CompteurCreate, basename='engin-compteur')

# engin_router.register("alerte-ep", AlertEpViewSet, basename='alerte-ep')




urlpatterns = [
    path('admin/', admin.site.urls),

    path('abonnement', EseValidation.as_view(), name="validation"),

    path('', AccueilEntreprises.as_view(), name="accueil"),
    path('list-abonnement', ListAbonneViews.as_view(), name="list-abonnement"),
    # path('nouvel-abonnement', CreateAbonne.as_view(), name="nouvel-abonnement"),

    path('import-organigramme', ImportOrgFonctView.as_view(), name="import-organigramme"), 
    path('creer-organes', CreateOrganFonct.as_view(), name='creer-organes'),
    path('list-organigramme', ListOrganFonct.as_view(), name='list-organigramme'),
    path('delete-org-fonct/<str:pk>', DelOrganFonct.as_view(), name='delete-org-fonct'),
    path('update-org-fonct/<str:pk>', UpdateOrganFonct.as_view(), name='update-org-fonct'),

     
    path('creer-prestations', CreatePrestations.as_view(), name='creer-prestations'),
    path('list-prestations', ListPrestations.as_view(), name='list-prestations'),
    path('delete-prestations/<str:pk>', DeletePrestations.as_view(), name='delete-prestations'),
    path('update-prestations/<str:pk>', UpdatePrestations.as_view(), name='update-prestations'),


    path('creer-piece', CreatePieceRechange.as_view(), name='creer-piece'),
    path('list-piece', ListPieceRechange.as_view(), name='list-piece'),
    path('delete-piece/<str:pk>', DeletePieceRechange.as_view(), name='delete-piece'),
    path('update-piece/<str:pk>', UpdatePieceRechange.as_view(), name='update-piece'),


    path("dt-ep/", DTEpCreate.as_view(), name="dt-ep"),

    path("list-dt-ep/", ListDTEp.as_view(), name="list-dt-ep"),

    path('alerts-ep/', ListAlertEp.as_view(), name='alerts-ep'),

    path('suivi-ep/', ListSuiviEp.as_view(), name='suivi-ep'),

    path("depassement-ep/", ListCountEpCritiq.as_view(), name="depassement-ep"),

    path('depo-vehicule/', CreateVehDepo.as_view(), name='depo-vehicule'),

    path('recept-vehicule/', CreateVehRecu.as_view(), name='recept-vehicule'),



    
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

    
    path('alerte-ep/', include('CompteurApps.urls')),
    # path('preventif/', include('PreventApps.urls')),

    path('import-engins', ImportEnginView.as_view(), name="import-engins"),
    
]+ router.urls + engin_router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
