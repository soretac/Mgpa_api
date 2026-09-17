from rest_framework import serializers
from django.conf import settings
from.models import Compteurs, AlerteEp, CptAlert, CountCritique
from MatRoulant.models import VehiculesEses
from MatRoulant.SerializerMatRoulant import VehSerializer
from django.db.models import Q
from Mgpa_api.middleware import get_tenant
from django_tenants.utils import tenant_context
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


class CompteurSerializer(serializers.ModelSerializer):
    # vehicule = VehSerializer
     
    class Meta:
        model = Compteurs
        fields = ["id", "start_compt", "last_compt", "compt_act", "date_compt", "ecart", "releveur", "statut_compt", "vehicule"]
        # read_only_fields = ["vehicule", "date_compt", "statut_compt", "start_compt", "last_compt", "ecart", "releveur"]
        # required_fields = ["vehicule", "date_compt", "statut_compt", "start_compt", "last_compt", "ecart", "releveur"]
        
        

    def create(self, validated_data):
        engin_id = self.context['engin_id'] 
        return Compteurs.objects.create(vehicule_id=engin_id, **validated_data)


class AlerteEpSerializer(serializers.ModelSerializer):
    # alert = serializers.SerializerMethodField()
    
    class Meta:
        model = AlerteEp
        fields = ["id", "destinataires", "alerte", "message", "compt", "vehicule", "statut", "session_alert", 'ecart', 'type_alert', 'date_alert', 'nbalert', 'chef_smrlt']
        read_only_fields =["utilisateur"]

 




class CptAlertSerializer(serializers.ModelSerializer):
    alertep = AlerteEpSerializer()
    class Meta:
        model = CptAlert
        fields = ["id", "nbalert", "ecart", "date_alert", "alertep"]







class CountCritiqSerializer(serializers.ModelSerializer):

    class Meta:
        model = CountCritique
        fields = ["id", "date_count", "vehicule", "n_depassement", "n_danger", "n_critique", "ecart", "statut", "type_ep", "session"]
