from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView, DestroyAPIView, RetrieveUpdateAPIView
from rest_framework import status
import pandas as pd
from django.contrib.auth import get_user_model 
from django.core.exceptions import ObjectDoesNotExist
from Mgpa_api.middleware import get_tenant
from rest_framework.parsers import MultiPartParser, FormParser
from .SerializerEses import ValidationSerializer, AbonnementSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from Client.models import Clients, AbonneClient
from Client.ClientSerializers import AbonneClientSerializer
from .models import Eses
import datetime
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from .SerializerEses import EseSerializer, OrganigramSerializer, ImportOrgFonctSerializer, PrestationSerializer, PieceRechangeSerializer, ListAbonneSerializer, SubscribeSerializer
from .models import Eses, Organigramme, Prestations, PieceRechange, AbonnementEse, Newsubscribe
from django_tenants.utils import tenant_context,schema_context
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.contenttypes.models import ContentType
from Client.tasks import notif_client
from Travaux.models import  NumPrefix
from Travaux.SerializerTravaux import NumPrefixSerializer
import string
import secrets
from guardian.shortcuts import assign_perm
from MatRoulant.models import VehiculesEses






class EseValidation(CreateAPIView):
    serializer_class = ValidationSerializer
    parser_classes =  [FormParser, MultiPartParser]

    

    def create(self, request, *args, **kwargs):        
        data = request.data
        code_ese = data["code_ese"]
        nom_ese = data["nom_ese"].lower()

        abonne = AbonneClient.objects.filter(code=code_ese, is_active=True).first()
        # schem = AbonneClient.objects.values_list("schema_name", flat=True).first()
        
        print("********************************************************\n")
        print(abonne)
        
        if abonne != None:

            client = Clients.objects.filter(schema_name=abonne.schema_name).first()
            if client == None:
                return Response("Identifiants erronés, veuillez vous rassurez se l'exactitude de ces identifiants")
            else:
                if Eses.objects.all().exists() == False:
 
                    data_ese = {}
                    

                    # CREATION DU MODEL ENTREPRISE
                    client = abonne.ese
                    # with tenant_context(client):
                    data_ese['nom_ese'] = nom_ese
                    data_ese['adresse_ese'] = abonne.ese.adresse
                    data_ese['abrev_ese']   = abonne.ese.schema_sigle
                    data_ese["schema_name"] = abonne.ese.schema_name
                    data_ese["domaine_ese"] = abonne.ese.nom_domaine
                    data_ese["datecreat_ese"] = abonne.ese.created_on
                    data_ese['slogan_ese']  = abonne.ese.slogan
                    data_ese['siege_ese']   = abonne.ese.ville_siege
                    data_ese['pays_ese']    = abonne.ese.pays
                    data_ese['email_ese']   = abonne.ese.email
                    data_ese['siteweb_ese'] = abonne.ese.siteweb
                    data_ese['user_admin_ese'] = abonne.ese.user_admin
                    data_ese['mdp_admin_ese'] = abonne.ese.mdp_admin
                    data_ese['description_ese']  = abonne.ese.description_ese
                    data_ese['logo_ese']    = abonne.ese.logo_ese
                    data_ese['phone1_ese']  = abonne.ese.phone1
                    data_ese['phone2_ese']  = abonne.ese.phone2
                    data_ese['num_contrib_ese'] = abonne.ese.niu_ese     

                    serializer_valid = EseSerializer(data=data_ese)
                    serializer_valid.is_valid(raise_exception=True)
                    serializer_valid.save()

                    # CREATION DES NUMEROS DE DEMANDE DE TRAVAIL POUR EP

                    digits = string.digits
                    code_length = 3
                    nbre = 0
                    set_prefix = {'000'}
                    data = {}
                    while nbre < 10:
                        cod = ""   
                        for i in range(code_length):
                            cod += "".join(secrets.choice(digits))
                        set_prefix.add(cod)
                        nbre += 1
                    for prefix in set_prefix:
                        data['entete'] = "DTEP"
                        data['prefix'] = prefix
                    
                        serializer_prefix = NumPrefixSerializer(data=data)
                        serializer_prefix.is_valid(raise_exception=True)
                        serializer_prefix.save()
                    set_prefix.clear()
                    
                    # # CREATION DES NUMEROS DE DEMANDE DE TRAVAIL POUR CURATIFS
                    
                    digit = string.digits
                    nbre = 0
                    set_prefix = {'000'}
                    data = {}
                    while nbre < 10:
                        cod = ""
                        for i in range(code_length):
                            cod += "".join(secrets.choice(digit))
                        set_prefix.add(cod)
                        nbre += 1
                    for prefix in set_prefix:
                        data['entete'] = "DTCUR"
                        data['prefix'] = prefix
                    
                        serializer_prefix = NumPrefixSerializer(data=data)
                        serializer_prefix.is_valid(raise_exception=True)
                        serializer_prefix.save()
                    set_prefix.clear()




                    # CREATION DES GROUPES DE PERMISSIONS

                    UTILISATEUR, created = Group.objects.create(name='UTILISATEUR')
                    MAGASINIER, created = Group.objects.create(name='MAGASINIER')
                    GARAGISTE, created = Group.objects.create(name='GARAGISTE')
                    CHEF_SITE, created = Group.objects.create(name='CHEF_SITE')
                    CHEF_CTECH, created = Group.objects.create(name='CHEF_CTECH')
                    CHEF_AGENCE, created = Group.objects.create(name='CHEF_AGENCE')
                    CHEF_REGION, created = Group.objects.create(name='CHEF_REGION')
                    DIR_EXPLOIT, created = Group.objects.create(name='DIR_EXPLOIT')
                    CHEF_SMRLT, created = Group.objects.create(name='CHEF_SMRLT')
                    DIR_OPER, created = Group.objects.create(name='DIR_OPER')
                    MASTER_DATA, created = Group.objects.create(name='MASTER_DATA')
                    DIR_GEN, created = Group.objects.create(name='DIR_GEN')
                    VIDE, created = Group.objects.create(name="VIDE")

                    User = get_user_model()
                    users = User.objects.filter(groups__name='UTILISATEUR')
                    # task = VehiculesEses.objects.
                    # assign_perm('change_task', users, task)





                    ctype_organigramme = ContentType.objects.get(app_label='Entreprise', model='organigramme')
                    ctype_piecerechange = ContentType.objects.get(app_label='Entreprise', model='piecerechange')
                    ctype_prestations = ContentType.objects.get(app_label='Entreprise', model='prestations')
                    ctype_useraccount = ContentType.objects.get(app_label='MgpaUsers', model='useraccount')
                    ctype_assurveh = ContentType.objects.get(app_label='MatRoulant', model='assurveh')
                    ctype_cgveh = ContentType.objects.get(app_label='MatRoulant', model='cgveh')
                    ctype_vehiculeseses = ContentType.objects.get(app_label='MatRoulant', model='vehiculeseses')
                    ctype_visiteveh = ContentType.objects.get(app_label='MatRoulant', model='visiteveh')
                    ctype_alerteep = ContentType.objects.get(app_label='CompteurApps', model='alerteep')
                    ctype_compteurs = ContentType.objects.get(app_label='CompteurApps', model='compteurs')
                    ctype_eps = ContentType.objects.get(app_label='PreventApps', model='eps')
                    ctype_suiviep = ContentType.objects.get(app_label='PreventApps', model='suiviep')
                    ctype_dtprev = ContentType.objects.get(app_label='PreventApps', model='dtprev')
                    ctype_permission = ContentType.objects.get(app_label='auth', model='permission')
                    ctype_organigramme = ContentType.objects.get(app_label='Entreprise', model='organigramme')

                    permissions_organigramme = Permission.objects.filter(content_type=ctype_organigramme)
                    permissions_piecerechange = Permission.objects.filter(content_type=ctype_piecerechange)
                    permissions_prestations = Permission.objects.filter(content_type=ctype_prestations)
                    permissions_useraccount = Permission.objects.filter(content_type=ctype_useraccount)
                    permissions_assurveh = Permission.objects.filter(content_type=ctype_assurveh)
                    permissions_cgveh = Permission.objects.filter(content_type=ctype_cgveh)
                    permissions_vehiculeseses = Permission.objects.filter(content_type=ctype_vehiculeseses)
                    permissions_visiteveh = Permission.objects.filter(content_type=ctype_visiteveh)
                    permissions_alerteep = Permission.objects.filter(content_type=ctype_alerteep)
                    permissions_compteurs = Permission.objects.filter(content_type=ctype_compteurs)
                    permissions_eps = Permission.objects.filter(content_type=ctype_eps)
                    permissions_suiviep = Permission.objects.filter(content_type=ctype_suiviep)
                    permissions_dtprev = Permission.objects.filter(content_type=ctype_dtprev)
                    permissions_permission = Permission.objects.filter(content_type=ctype_permission)

                    # LISTE DES PERMISSIONS DU CHEF SMRLT
                    list_permission_smrlt = []
                    list_permission_smrlt.extend(permissions_vehiculeseses)
                    list_permission_smrlt.extend(permissions_visiteveh)
                    list_permission_smrlt.extend(permissions_cgveh)
                    list_permission_smrlt.extend(permissions_assurveh)
                    list_permission_smrlt.extend(permissions_compteurs)
                    list_permission_smrlt.extend(permissions_alerteep)
                    list_permission_smrlt.extend(permissions_suiviep)
                    list_permission_smrlt.extend(permissions_dtprev)
                    list_permission_smrlt.extend(permissions_prestations)
                    list_permission_smrlt.extend(permissions_piecerechange)
                    list_permission_smrlt.extend(permissions_eps)
                    list_permission_smrlt.extend(permissions_organigramme)
                    

                    CHEF_SMRLT.permissions.add(*list_permission_smrlt)  # LES PERMISSIONS DU CHEF MATRLT

                    # LES PERMISSIONS DES GARAGISTES

                    gar = Group.objects.get(name='GARAGISTE')

                    # 2. Fetch the existing permission using its unique codename
                    permission_gar1 = Permission.objects.get(codename='view_dtprev')
                    permission_gar2 = Permission.objects.get(codename='add_vehrecuep')
                    permission_gar3 = Permission.objects.get(codename='view_vehrecuep')
                    permission_gar4 = Permission.objects.get(codename='view_vehdepoep')

                    # 3. Add the permission to the group
                    gar.permissions.add(permission_gar1)
                    gar.permissions.add(permission_gar2)
                    gar.permissions.add(permission_gar3)
                    gar.permissions.add(permission_gar4)


                    # LES PERMISSIONS DES UTILISATEURS
                    
                    util = Group.objects.get(name='UTILISATEUR')  # LES PERMISSIONS DES UTILISATEURS

                    permission_util1 = Permission.objects.get(codename='add_compteurs')
                    permission_util2 = Permission.objects.get(codename='view_compteurs')
                    permission_util3 = Permission.objects.get(codename='view_dtprev')
                    permission_util4 = Permission.objects.get(codename='view_cptalert')


                    util.permissions.add(permission_util1)
                    util.permissions.add(permission_util2)
                    util.permissions.add(permission_util3)
                    util.permissions.add(permission_util4)


                    # "add_permission"
                    # "change_permission"
                    # "delete_permission"
                    # "view_permission"
                    # "add_eses"
                    # "change_eses"
                    # "delete_eses"
                    # "view_eses"
                    # "add_newsubscribe"
                    # "change_newsubscribe"
                    # "delete_newsubscribe"
                    # "view_newsubscribe"
                    # "add_organigramme"
                    # "change_organigramme"
                    # "delete_organigramme"
                    # "view_organigramme"
                    # "add_piecerechange"
                    # "change_piecerechange"
                    # "delete_piecerechange"
                    # "view_piecerechange"
                    # "add_prestations"
                    # "change_prestations"
                    # "delete_prestations"
                    # "view_prestations"
                    # "add_validationelement"
                    # "change_validationelement"
                    # "delete_validationelement"
                    # "view_validationelement"
                    # "add_abonnementese"
                    # "change_abonnementese"
                    # "delete_abonnementese"
                    # "view_abonnementese"
                    # "add_paramcomptalert"
                    # "change_paramcomptalert"
                    # "delete_paramcomptalert"
                    # "view_paramcomptalert"
                    # "add_piecerechange"
                    # "change_piecerechange"
                    # "delete_piecerechange"
                    # "view_piecerechange"
                    # "add_prestatons"
                    # "change_prestatons"
                    # "delete_prestatons"
                    # "view_prestatons"
                    # "add_useraccount"
                    # "change_useraccount"
                    # "delete_useraccount"
                    # "view_useraccount"
                    # "add_groupusers"
                    # "change_groupusers"
                    # "delete_groupusers"
                    # "view_groupusers"
                    # "add_assurveh"
                    # "change_assurveh"
                    # "delete_assurveh"
                    # "view_assurveh"
                    # "add_cgveh"
                    # "change_cgveh"
                    # "delete_cgveh"
                    # "view_cgveh"
                    # "add_visiteveh"
                    # "change_visiteveh"
                    # "delete_visiteveh"
                    # "view_visiteveh"
                    # "add_vehiculeseses"
                    # "change_vehiculeseses"
                    # "delete_vehiculeseses"
                    # "view_vehiculeseses"
                    # "add_alerteep"
                    # "change_alerteep"
                    # "delete_alerteep"
                    # "view_alerteep"
                    # "add_compteurs"
                    # "change_compteurs"
                    # "delete_compteurs"
                    # "view_compteurs"
                    # "add_countcritique"
                    # "change_countcritique"
                    # "delete_countcritique"
                    # "view_countcritique"
                    # "add_cptalert"
                    # "change_cptalert"
                    # "delete_cptalert"
                    # "view_cptalert"
                    # "add_eps"
                    # "change_eps"
                    # "delete_eps"
                    # "view_eps"
                    # "add_suiviep"
                    # "change_suiviep"
                    # "delete_suiviep"
                    # "view_suiviep"
                    # "add_numprefix"
                    # "change_numprefix"
                    # "delete_numprefix"
                    # "view_numprefix"
                    # "add_dtprev"
                    # "change_dtprev"
                    # "delete_dtprev"
                    # "view_dtprev"
                    # "add_vehdepoep"
                    # "change_vehdepoep"
                    # "delete_vehdepoep"
                    # "view_vehdepoep"
                    # "add_vehrecuep"
                    # "change_vehrecuep"
                    # "delete_vehrecuep"
                    # "view_vehrecuep"







                    # ctype_eses = ContentType.objects.get(app_label='Entreprise', model='Entreprise')
                    # ctype_abonne = ContentType.objects.get(app_label='Entreprise', model='AbonnementEse')

                    # Create the custom permission
                    # permission_change_eses = Permission.objects.create(
                    #     codename='can_change_eses',
                    #     name='Can Change Eses',
                    #     content_type=ctype_eses,
                    # )
                    


                    # permission_add_abonne = Permission.objects.create(
                    #     codename='can_add_abonnementese',
                    #     name='Can Change AbonnementEse',
                    #     content_type=ctype_abonne,
                    # )

                    # DIR_GEN.permissions.add(permission_change_eses)
                    # MASTER_DATA.permissions.add(permission_change_eses)
                    # DIR_GEN.permissions.add(permission_add_abonne)
                    # MASTER_DATA.permissions.add(permission_add_abonne)


                # CREATION DE L'ABONNEMENT

                serializers = AbonneClientSerializer(abonne)
                serialized_data = serializers.data

                reab = AbonneClient.objects.filter(code=code_ese).filter(is_active=True).first()

                    
                data_ab = {}
                data_ab['ese'] = reab.ese.id_enreg
                
                data_ab['date_saisie'] = reab.date_saisie
                
                data_ab['num_abon'] = reab.num_abon

                data_ab['schema_name'] = reab.schema_name
                
                data_ab['date_debut'] = reab.date_debut
                
                data_ab['mensualite'] = reab.mensualite
                
                data_ab['date_fin'] = reab.date_fin
                
                data_ab['code'] = reab.code
                data_ab['nbre_man'] = reab.nbre_man
                data_ab['nbre_vl'] = reab.nbre_vl
                
                data_ab['nbre_pl1'] = reab.nbre_pl1
                
                data_ab['nbre_pl2'] = reab.nbre_pl2
                
                data_ab['nbre_autobus'] = reab.nbre_autobus
                data_ab['nbre_gc'] = reab.nbre_gc
                data_ab['prcent_remise'] = reab.prcent_remise
                data_ab['nusers_dg'] = reab.nusers_dg
                
                data_ab['nusers_dop'] = reab.nusers_dop
                data_ab['nusers_dex'] = reab.nusers_dex
                data_ab['nusers_srm'] = reab.nusers_srm
                data_ab['nusers_reg'] = reab.nusers_reg
                data_ab['nusers_age'] = reab.nusers_age
                data_ab['nusers_ctq'] = reab.nusers_ctq
                data_ab['nusers_util'] = reab.nusers_util
                data_ab['nusers_gar'] = reab.nusers_gar
                data_ab['nusers_mag'] = reab.nusers_mag
                data_ab['nbre_users'] = reab.nbre_users()
                data_ab['nbre_engins'] = reab.nbre_engins()
                data_ab['montant_engins'] = round(serialized_data["montant_engins"], 0)
                data_ab['montant_users'] = round(serialized_data["montant_users"], 0)
                data_ab['montant_ht'] = round(serialized_data["montant_ht"], 0)
                data_ab['montant_taxe'] = round(serialized_data["montant_taxe"], 0)
                data_ab['montant_ttc'] = round(serialized_data["montant_ttc"], 0)
                data_ab['montant_verse'] = reab.montant_verse
                data_ab['montant_restant'] = round(serialized_data["montant_restant"], 0)
                data_ab['date_next_versement'] = reab.date_next_versement
                data_ab['is_active'] = reab.is_active

                
                serializ = AbonnementSerializer(data=data_ab)
                serializ.is_valid(raise_exception=True)
                serializ.save()
                print(serializ)
                    
                return Response({'status': True, 'message': "abonnement validé"}, status=status.HTTP_200_OK)    
        else:
            return Response({'status': False, 'message':"Code ou nom de l'entreprise erroné! Veuillez renseigner convenablement le code et le nom de votre entreprise."}, status=status.HTTP_400_BAD_REQUEST)            

                
                    
                        
                    



                        # try:
                        #     data_mail = {}
                        #     data_mail['mdp_admin_ese']
                        #     data_mail['user_admin_ese']

                        #     text_html = render_to_string("user_mail_notif.html", data_mail)
                        #     msg = EmailMessage(
                        #     "CREATION DE COMPTE ENTREPRISE",
                        #     text_html,
                        #     "SORETAC <duparce.netzone@gmail.com>",
                        #     [erese.user_admin]
                        #     )
                        #     msg.content_subtype = "html"
                        #     msg.send()

                        # except Exception as e:
                        #     print("Erreur de connexion internet")

              


class AccueilEntreprises(ListAPIView):
    queryset = Eses.objects.all()
    # notif_client.delay('Transfert')
    serializer_class = EseSerializer


class ListAbonneViews(ListAPIView):
    queryset = AbonnementEse.objects.all()
    serializer_class = AbonnementSerializer



# class CreateAbonne(CreateAPIView):
#     queryset = Newsubscribe.objects.all()
#     serializer_class = SubscribeSerializer

#     def create(self, request, *args, **kwargs):
#         data = request.data
#         client = get_tenant(request)
#         # print(client.nom_ese)

        
#         qcode = CodeAbonne.objects.filter(Q(ese=client.id_enreg) & Q(code_ab=data['code_ab']) & Q(statut=True)).first()
#         if qcode != None:
#             data_code = {}
#             data_code['code_ese'] = qcode.code_ab
#             data_code['nbre_engin'] = qcode.nbre_engin
#             data_code['nbre_users'] = qcode.nbre_users
#             data_code['start_date'] = qcode.start_date

#             endate = datetime.date.strftime(qcode.start_date, "%Y-%m-%d")
#             endate = datetime.date.strptime(endate, "%Y-%m-%d")
#             data_code['end_date'] = endate + (datetime.timedelta(days=qcode.periode_ab))

#             data_code['mont_engin'] = round((qcode.nbre_engin * qcode.periode_ab/30)*8000)
#             data_code['mont_licence'] = round((qcode.nbre_users * qcode.periode_ab/30)*3000)
#             data_code['mont_total'] = round((qcode.nbre_engin * qcode.periode_ab/30)*8000 + (qcode.nbre_users * qcode.periode_ab/30)*3000)
            
#             last_ab = AbonnementClient.objects.last()
#             num = last_ab.num_abonne[-4:]
#             num_ab = int(num)+1
           
#             data_code['num_abonne'] = "Mgpa/ab-" + str(qcode.ese.schema_name) + str(num_ab)
#             qcode.statut = False
#             qcode.save()
#             serializer_ab = AbonnementSerializer(data=data_code)
#             serializer_ab.is_valid(raise_exception=True)
#             serializer_ab.save()

#             serializer = SubscribeSerializer(data=data)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
            

#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         else:
        
#             return Response({'status': False, 'message': 'Code erroné'}, status=status.HTTP_400_BAD_REQUEST) 






class CreateOrganFonct(CreateAPIView):
    parser_classes = [FormParser, MultiPartParser]
    queryset = Organigramme.objects.all()
    serializer_class = OrganigramSerializer

    def post(self, request, *args, **kwargs):

        client = get_tenant(request)
        with tenant_context(client):

            data = request.data.copy()
            pos = ""
            pos += "".join(str(client.schema_name).strip().upper())
            pos += "".join("_")
            pos += "".join(str(data['direction_gen']).upper())

            if data['direction_fonct'] !="":
                pos += "".join("_")
                pos += "".join(str(data['direction_fonct']).upper())

            if data['service'] !="":
                pos += "".join("_")
                pos += "".join(str(data['service']).upper())

            if data['agence'] !="":
                pos += "".join("_")
                pos += "".join(str(data['agence']).upper())

            if data['site'] !="":
                pos += "".join("_")
                pos += "".join(str(data['site']).upper())

            data['organigramme'] = pos.upper()

            serializer = OrganigramSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)



class ListOrganFonct(ListAPIView):
    parser_classes = [FormParser, MultiPartParser]
    queryset = Organigramme.objects.all()
    serializer_class = OrganigramSerializer

class UpdateOrganFonct(RetrieveUpdateAPIView):
    parser_classes = [FormParser, MultiPartParser]
    queryset = Organigramme.objects.all()
    serializer_class = OrganigramSerializer



    def update(self, request, *args, **kwargs):
        client = get_tenant(request)
        with tenant_context(client):

            instance = Organigramme.objects.get(id=kwargs['pk'])

            data = request.data.copy()

            pos = ""
            pos += "".join(str(client.schema_name).strip().upper())
            pos += "".join("_")
            pos += "".join(str(data['direction_gen']).strip().upper())

            if data['direction_fonct'] !="":
                pos += "".join("_")
                pos += "".join(str(data['direction_fonct']).strip().upper())

            if data['service'] !="":
                pos += "".join("_")
                pos += "".join(str(data['service']).strip().upper())

            if data['agence'] !="":
                pos += "".join("_")
                pos += "".join(str(data['agence']).strip().upper())

            if data['site'] !="":
                pos += "".join("_")
                pos += "".join(str(data['site']).strip().upper())
            
            if data['sous_site'] !="":
                pos += "".join("_")
                pos += "".join(str(data['sous_site']).strip().upper())

            data['organigramme'] = pos.strip().upper()

            serializer = OrganigramSerializer(instance, data, partial=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

class DelOrganFonct(DestroyAPIView):
    parser_classes = [FormParser, MultiPartParser]
    queryset = Organigramme.objects.all()
    serializer_class = OrganigramSerializer


class ImportOrgFonctView(APIView):
    serializer_class = ImportOrgFonctSerializer
    parser_classes =  [FormParser, MultiPartParser]

    def post(self, request):
        cliente = get_tenant(request)

        data = request.FILES
        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            return Response({
                'status': False,
                'message': 'Veuillez pourvoir un fichier valide'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        excel_file = data.get('file')
        df = pd.read_excel(excel_file, sheet_name=0)
        
        with tenant_context(cliente):
            
            for k in range(len(df)):

                pos = ""
                
                data_org = {}
                if str(df.iloc[k, 0]).strip() != "":
                    data_org['direction_gen'] = str(df.iloc[k, 0]).strip().upper()
                    pos += "".join(str(cliente.schema_name).strip().upper())
                    pos += "".join("_")
                    pos += "".join(str(df.iloc[k, 0]).strip().upper())
                    

                if str(df.iloc[k, 1]).strip() != "" :
                    if str(df.iloc[k, 1]).strip() != "nan":
                        data_org['direction_fonct'] = str(df.iloc[k, 1]).strip().upper()
                        if pos == "":
                            pos += "".join(str(df.iloc[k, 1]).strip()).upper()
                        else:
                            pos += "".join("_")
                            pos += "".join(str(df.iloc[k, 1]).strip()).upper()
                    
                
                if str(df.iloc[k, 2]).strip() != "":
                    if str(df.iloc[k, 2]).strip() != "nan":
                        data_org['service'] = str(df.iloc[k, 2]).strip().upper()
                        if pos == "":
                            pos += "".join(str(df.iloc[k, 2]).strip()).upper()
                        else:
                            pos += "".join("_")
                            pos += "".join(str(df.iloc[k, 2]).strip()).upper()
                        
                
                if str(df.iloc[k, 3]).strip() != "":
                    if str(df.iloc[k, 3]).strip() != "nan":
                        data_org['agence'] = str(df.iloc[k, 3]).strip().upper()
                        if pos == "":
                            pos += "".join(str(df.iloc[k, 3]).strip()).upper()
                        else:
                            pos += "".join("_")
                            pos += "".join(str(df.iloc[k, 3]).strip()).upper()
                    
                
                if str(df.iloc[k, 4]).strip() != "":
                    if str(df.iloc[k, 4]).strip() != "nan":
                        data_org['site'] = str(df.iloc[k, 4]).strip().upper()
                        if pos == "":
                            pos += "".join(str(df.iloc[k, 4]).strip()).upper()
                        else:
                            pos += "".join("_")
                            pos += "".join(str(df.iloc[k, 4]).strip()).upper()
                    
                
                if str(df.iloc[k, 5]).strip() != "":
                    if str(df.iloc[k, 5]).strip() != "nan":
                        data_org['sous_site'] = str(df.iloc[k, 5]).strip().upper()
                        if pos == "":
                            pos += "".join(str(df.iloc[k, 5]).strip()).upper()
                        else:
                            pos += "".join("_")
                            pos += "".join(str(df.iloc[k, 5]).strip()).upper()
                    
                
                
                data_org['organigramme'] = pos.upper()
                serializer_org = OrganigramSerializer(data=data_org)
                if serializer_org.is_valid(raise_exception=True):
                    serializer_org.save()
        
        return Response({
                'status': True,
                'message': "Fichier des organigammes importé avec succès.",
                
            }, status=status.HTTP_201_CREATED)



# CRUD POUR LES PRESTATIONS

class ListPrestations(ListAPIView):
    parser_classes = [FormParser, MultiPartParser]
    queryset = Prestations.objects.all()
    serializer_class = PrestationSerializer


class CreatePrestations(CreateAPIView):
    parser_classes = [FormParser, MultiPartParser]
    queryset = Prestations.objects.all()
    serializer_class = PrestationSerializer


class UpdatePrestations(RetrieveUpdateAPIView):
    parser_classes = [FormParser, MultiPartParser]
    queryset = Prestations.objects.all()
    serializer_class = PrestationSerializer


class DeletePrestations(DestroyAPIView):
    parser_classes = [FormParser, MultiPartParser]
    queryset = Prestations.objects.all()
    serializer_class = PrestationSerializer



# CRUD POUR LES PIECES DE RECHANGE

class ListPieceRechange(ListAPIView):
    parser_classes = [FormParser, MultiPartParser]
    queryset = PieceRechange.objects.all()
    serializer_class = PieceRechangeSerializer


class CreatePieceRechange(CreateAPIView):
    parser_classes = [FormParser, MultiPartParser]
    queryset = PieceRechange.objects.all()
    serializer_class = PieceRechangeSerializer


class UpdatePieceRechange(RetrieveUpdateAPIView):
    parser_classes = [FormParser, MultiPartParser]
    queryset = PieceRechange.objects.all()
    serializer_class = PieceRechangeSerializer


class DeletePieceRechange(DestroyAPIView):
    parser_classes = [FormParser, MultiPartParser]
    queryset = PieceRechange.objects.all()
    serializer_class = PieceRechangeSerializer