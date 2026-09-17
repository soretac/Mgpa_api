from rest_framework import serializers
from .models import DTPrev, NumPrefix, VehDepoEp, VehRecuEp
from CompteurApps.models import AlerteEp
from CompteurApps.SerializerComptApps import AlerteEpSerializer
from PreventApps.models import SuiviEp
from PreventApps.SerializerPrevent import SuiviEpSerializer
from django.db.models import Q
from django.contrib.auth import get_user_model
from MatRoulant.SerializerMatRoulant import VehSerializer
from MgpaUsers.serializers import UserSerializer

user = get_user_model()

class SerializerDTEp(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Access the request context to filter choices by the logged-in user
        request = self.context.get('request')
        my_user = request.user
        if request and request.user:
            self.fields['ep'].queryset = SuiviEp.objects.filter(Q(site_matrlt=my_user.site) & Q(statut_ep="EN ATTENTE"))

    class Meta:
        model = DTPrev
        fields = ["id", "num_dtep", "vehicule", "demandeur", "garagiste", "ep", "description", "statut_dt", "date_demande"]
        read_only_fields = ["demandeur"]

    
class SerializerDTEpCreate(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Access the request context to filter choices by the logged-in user
        request = self.context.get('request')
        
        # my_user = request.user
        if request and request.user:
            self.fields['ep'].queryset = SuiviEp.objects.filter(Q(site_matrlt=request.user.site) & Q(statut_ep="EN ATTENTE"))
            self.fields['garagiste'].queryset = user.objects.filter(Q(type="CHEF GARAGE") )

    # vehicule = VehSerializer()
    # demandeur = UserSerializer()
    # garagiste = UserSerializer()
    # ep = SuiviEpSerializer()

    class Meta:
        model = DTPrev
        fields = ["id", "date_demande", "ep", "num_dtep", "demandeur", "garagiste", "description", "vehicule", "date_depo", "statut_dt", "priorite", "document_dtep" ]
        read_only_fields = ["statut_dt","date_demande", ]


class NumPrefixSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumPrefix
        fields = ['entete', 'prefix', 'statut', 'suffix']


# class VehDispoEPSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = VehDispoEp
#         fields = ['dtep', 'utilisateur', 'depot_utilisateur', 'date_utilisateur', 'garagiste', 'valid_garage', 'observation_util', 'observation_gar', 'signature_util', 'signature_gar']


class VehDepoEpSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        # Access the request context to filter choices by the logged-in user
        request = self.context.get('request')
        if request and request.user:
            self.fields['dtep'].queryset = DTPrev.objects.filter(Q(vehicule__conducteurs=request.user) & Q(statut_dt="En Demande"))
            
    class Meta:
        model = VehDepoEp
        fields = ['dtep', 'utilisateur', 'depot_utilisateur', 'date_depot', 'observation_util', 'signature_util']
        read_only_fields = ['utilisateur']


class VehRecuEpSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        # Access the request context to filter choices by the logged-in user
        request = self.context.get('request')
        if request and request.user:
            self.fields['dtep'].queryset = DTPrev.objects.filter(Q(garagiste=request.user) & Q(statut_dt="En Demande"))
 
    class Meta:
        model = VehRecuEp
        fields = ['dtep', 'date_recept', 'garagiste', 'valid_garage','observation_gar','signature_gar']
        read_only_fields = ['garagiste']