from rest_framework import serializers
from .models import ParamComptAlert

class ParamComptAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParamComptAlert
        fields = ['id', 'schema_name', 'code_ese', 'categorie', 'alert', 'vehicule', 'observations']


