from rest_framework import serializers
from .models import Eses, Organigramme, Prestations, PieceRechange, ValidationElement, Newsubscribe
from .models import AbonnementEse




class EseSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Eses
        fields = ['nom_ese', 'adresse_ese', 'abrev_ese', 'domaine_ese', 'description_ese', 'schema_name', 'slogan_ese', 
                  'datecreat_ese', 'siege_ese', 'pays_ese', 'email_ese', 'user_admin_ese', 'mdp_admin_ese', 
                  'siteweb_ese', 'phone1_ese', 'phone2_ese', 'logo_ese', 'num_contrib_ese', 'statut_ese'] 
        write_only_fields = ['nom_ese']
    
   

class OrganigramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organigramme
        fields = ['id', 'direction_gen', 'direction_fonct', 'service', 'agence', 'site', 'sous_site', 'organigramme']
        # read_only_fields = ['organigramme']

class ImportOrgFonctSerializer(serializers.Serializer):
   file = serializers.FileField()


class PrestationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prestations
        fields = ['code_prest', 'libelle_prest', 'organe', 'duree_prest', 'montant_prest']



class PieceRechangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PieceRechange
        fields = ['code_pr', 'libelle_pr', 'prix_pr', 'ref_usine', 'cat_pr']
    

class ValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationElement
        fields = "__all__"


class AbonnementSerializer(serializers.ModelSerializer):

    class Meta:
        model = AbonnementEse
        fields = ['ese', 'num_abon', 'code', 'schema_name', 'date_saisie', 'date_debut', 'date_fin', 'mensualite', 'nbre_man', 'nbre_vl', 'nbre_pl1', 'nbre_pl2',
                   'nbre_autobus', 'nbre_gc', 'prcent_remise', 'nusers_dg', 'nusers_dop', 'nusers_dex', 'nusers_srm', 'nusers_reg', 
                   'nusers_age', 'nusers_ctq', 'nusers_util', 'nusers_gar', 'nusers_mag', 'montant_verse', 'date_next_versement', 
                   'is_active', 'is_valid', 'nbre_users', 'nbre_engins', 'montant_engins', 'montant_users', 'montant_ht', 'montant_taxe', 
                   'montant_ttc', 'montant_restant']
        

class ListAbonneSerializer(serializers.ModelSerializer):

    class Meta:
        model = AbonnementEse
        fields = ('num_abonne', 'nbre_users', 'nbre_engin', 'mont_engin', 'mont_licence', 'mont_total', 'mont_check', 'start_date', 'end_date', 'is_active', 'mont_dossier', 'is_valid')  


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsubscribe
        fields = ['code_ab']