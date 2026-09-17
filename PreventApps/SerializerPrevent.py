from rest_framework import serializers
from Entreprise.SerializerEses import OrganigramSerializer
from .models import SuiviEp, Eps
from CompteurApps.models import AlerteEp
from CompteurApps.SerializerComptApps import AlerteEpSerializer
from django.contrib.auth import get_user_model


User = get_user_model()


class DemandEpSerializer(serializers.ModelSerializer):
    alert_ep = serializers.SlugRelatedField(slug_field='alerte', queryset= AlerteEp.objects.filter(statut=False))
    personnel_garage = serializers.SlugRelatedField(slug_field='email', queryset= User.objects.filter(type='CGAR'))
    demandeur_ep = serializers.SerializerMethodField()
    

    

class SuiviEpSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuiviEp
        fields = ['vehicule', 'statut_ep', 'dernier_ep', 'comptlast_ep', 'datelast_ep', 'compt_act', 'compt_cible', 'ecart', 'type_alert', 'prochain_ep', 'statut_dt', 'site_matrlt', 'session_alerte']
        read_only_fields = []


class SerializerEps(serializers.ModelSerializer):
    class Meta:
        model = Eps
        fields = ['vehicule', 'statut_dt', 'type_ep', 'compt_alert', 'date_recept', 'date_ep', 'compt_ep', 'etat_ep', 'observation', 'garagiste']