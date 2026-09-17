from rest_framework import serializers
from .models import VehiculesEses, VisiteVeh, AssurVeh, CGVeh
from Entreprise.SerializerEses import OrganigramSerializer
from Entreprise.models import Organigramme
from MgpaUsers.serializers import UserSerializer


class VehSerializer(serializers.ModelSerializer):
    affectation = OrganigramSerializer
    conducteurs = UserSerializer
    class Meta:
        model = VehiculesEses
        fields =["id", "num_parc", "immat", "typecompteur", "categorie", "type", "marque", "model", "energie", "puissance", 
        "serie", "branding", "date_mse", "statut", "affectation", "conducteurs", "identite", "site_matrlt"]
        
        # read_only_fields = ["identite"]





class ImportEnginSerializer(serializers.Serializer):
   file = serializers.FileField()


class AssurSerializer(serializers.ModelSerializer):
    vehicule = VehSerializer
    class Meta:
        model = AssurVeh
        fields =["id", "ref", "date", "type", "montant", "duree", "date_fin"]
    
    def create(self, validated_data):
        engin_id = self.context['engin_id']
        return AssurVeh.objects.create(vehicule_id=engin_id, **validated_data)
        


class VisitSerializer(serializers.ModelSerializer):
    vehicule = VehSerializer
    class Meta:
        model = VisiteVeh
        fields =["id", "ref", "centre", "date", "resultat", "montant", "date_fin"]
    
    def create(self, validated_data):
        engin_id = self.context['engin_id']
        return VisiteVeh.objects.create(vehicule_id=engin_id, **validated_data)
    

class CGSerializer(serializers.ModelSerializer):
    vehicule = VehSerializer
    class Meta:
        model = CGVeh
        fields =["id", "ref", "date", "montant", "date_fin"]
    
    def create(self, validated_data):
        engin_id = self.context['engin_id']
        return CGVeh.objects.create(vehicule_id=engin_id, **validated_data)