from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from MgpaUsers.models import GroupUsers
from django.contrib.auth import get_user_model
from Entreprise.SerializerEses import OrganigramSerializer
from django.contrib.auth.models import Group


User = get_user_model()


class CreateUserSerializer(BaseUserCreateSerializer):
    site = OrganigramSerializer()
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'mobile', 'type', 'poste', 'site', 'date_nais', 'genre', 'matrimonial', 'address', 'avatar', 'permis', 'num_cni', 'signature', 'is_superuser', 'password')  
        # 



class UserSerializer(BaseUserSerializer):  
    class Meta(BaseUserSerializer.Meta):
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'mobile', 'type', 'poste', 'site', 'date_nais', 'genre', 'matrimonial', 'address', 'avatar', 'permis', 'num_cni', 'signature', 'is_superuser', 'password')  
        # ['id', 'username', 'email', 'first_name', 'last_name', 'mobile', 'type', 'poste', 'site', 'date_nais', 'genre', 'matrimonial', 'address', 'avatar', 'permis', 'num_cni', 'document', 'is_superuser', 'password']


# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = ['id', 'user', 'date_nais', 'genre', 'matrimonial', 'address', 'affectation', 'avatar', 'engin', 'permis', 'num_cni', 'document']
#         # read_only_fields = ['user']


class GroupUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = GroupUsers
        fields = ["user", "group"]


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'