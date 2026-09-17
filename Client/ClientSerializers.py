from rest_framework import serializers
from .models import Clients, Domain, AbonneClient, Prix_soretac



class CreateClientEseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Clients
        fields = ['id_enreg', 'schema_name', 'created_on', 'nom_ese', 'schema_sigle', 'nom_domaine', 'description_ese', 'email', 
                  'siteweb', 'slogan',  'user_admin', 'mdp_admin', 'adresse', 'niu_ese', 'ville_siege', 'pays', 
                  'phone1', 'phone2', 'logo_ese', 'ese_activate', 'code'] 
        read_only_fields = ['code', 'mdp_admin', 'ese_activate']




class ClientEseSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Clients
        fields = ['id_enreg', 'schema_name', 'created_on', 'nom_ese', 'schema_sigle', 'nom_domaine', 'code_ab', 'description_ese', 'email', 
                  'siteweb', 'slogan',  'user_admin', 'mdp_admin', 'adresse', 'niu_ese', 'ville_siege', 'pays', 
                  'phone1', 'phone2', 'logo_ese', 'ese_activate'] 
        read_only_fields = ['code_ab','mdp_admin', 'ese_activate']


        
    class DomainSerializer(serializers.ModelSerializer):
        class Meta:
            model : Domain
            fields = '__all__'    


class PrixSoretacSerializer(serializers.ModelSerializer):

    class Meta:
        model = Prix_soretac
        fields = '__all__'



class AbonneClientSerializer(serializers.ModelSerializer):

    
    montant_engins = serializers.SerializerMethodField()
    montant_users = serializers.SerializerMethodField()
    montant_ht = serializers.SerializerMethodField()
    montant_taxe = serializers.SerializerMethodField()
    montant_ttc = serializers.SerializerMethodField()
    montant_restant = serializers.SerializerMethodField()

    class Meta:
        model = AbonneClient
        fields = ['id', 'ese', 'code', 'num_abon', 'schema_name', 'date_saisie', 'date_debut', 'date_fin', 'mensualite', 'nbre_man', 'nbre_vl', 'nbre_pl1', 'nbre_pl2',
                   'nbre_autobus', 'nbre_gc', 'prcent_remise', 'nusers_dg', 'nusers_dop', 'nusers_dex', 'nusers_srm', 'nusers_reg', 
                   'nusers_age', 'nusers_ctq', 'nusers_util', 'nusers_gar', 'nusers_mag', 'montant_verse', 'date_next_versement', 
                   'is_active', 'is_valid', 'nbre_users', 'nbre_engins', 'montant_engins', 'montant_users', 'montant_ht', 'montant_taxe', 
                   'montant_ttc', 'montant_restant']
        read_only_fields = ['id', 'num_abon',  'code', 'date_saisie', 'schema_name']
        required_fields = ['id', 'num_abon',  'code', 'date_saisie', 'schema_name']


    


    def get_montant_engins(self, abonneclient:AbonneClient):
        prix = Prix_soretac.objects.all().first()
        mnt_engins = (int(abonneclient.nbre_man) * prix.prix_man + int(abonneclient.nbre_vl) * prix.prix_vl + int(abonneclient.nbre_pl1) * prix.prix_pl1 + int(abonneclient.nbre_pl2) * prix.prix_pl2  + int(abonneclient.nbre_man) * prix.prix_man + int(abonneclient.nbre_autobus) * prix.prix_autobus + int(abonneclient.nbre_gc) * prix.prix_gc) * abonneclient.mensualite
        mnt_engins = round(mnt_engins - mnt_engins*abonneclient.prcent_remise/100, 0)
        return int(mnt_engins)


    def get_montant_users(self, abonneclient:AbonneClient):
        prix = Prix_soretac.objects.all().first()
        mnt_users = (int(abonneclient.nusers_dg) * prix.prix_udg + int(abonneclient.nusers_dop) * prix.prix_udop + int(abonneclient.nusers_dex) * prix.prix_udex + int(abonneclient.nusers_srm) * prix.prix_usrm  + int(abonneclient.nusers_reg) * prix.prix_ureg + int(abonneclient.nusers_age) * prix.prix_uage + int(abonneclient.nusers_ctq) * prix.prix_uctq + int(abonneclient.nusers_util) * prix.prix_uutil + int(abonneclient.nusers_gar) * prix.prix_ugar + int(abonneclient.nusers_mag) * prix.prix_umag) * abonneclient.mensualite       
        return mnt_users


    def get_montant_ht(self, abonneclient:AbonneClient):
        return self.get_montant_engins(abonneclient) + self.get_montant_users(abonneclient)


    def get_montant_taxe(self, abonneclient:AbonneClient):
        prix = Prix_soretac.objects.all().first()
        return round(self.get_montant_ht(abonneclient)*prix.prix_taxe/100, 0)

    def get_montant_ttc(self, abonneclient:AbonneClient):
        return self.get_montant_ht(abonneclient) + self.get_montant_taxe(abonneclient)

    def get_montant_restant(self, abonneclient:AbonneClient):
        return self.get_montant_ttc(abonneclient) - abonneclient.montant_verse


    # def create(self, validated_data):
    #     num_abon = validated_data.pop('num_abon', None)

    #     return AbonneClient.objects.create(**validated_data)