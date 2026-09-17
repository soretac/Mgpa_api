import datetime

from django.shortcuts import render
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser, FormParser
from .SerializerMatRoulant import ImportEnginSerializer, VehSerializer, VisitSerializer, AssurSerializer, CGSerializer
from rest_framework.views import APIView
# from filters import VehiculeFilters
from django.db.models.aggregates import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from Mgpa_api.middleware import get_tenant
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.response import Response
from django_tenants.utils import tenant_context,schema_context
import pandas as pd
from Client.models import Clients
from .models import VehiculesEses, VisiteVeh, CGVeh, AssurVeh
from Entreprise.models import Organigramme, AbonnementEse
from django.contrib.auth import get_user_model
from MgpaUsers.models import UserAccount
from django.db.models import F, Q, Value, BooleanField
from guardian.shortcuts import get_objects_for_user




class ImportEnginView(APIView):
    serializer_class = ImportEnginSerializer
    parser_classes =  [FormParser, MultiPartParser]
    

    def post(self, request):
        client = get_tenant(request)

        data = request.FILES
        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            return Response({
                'status': False,
                'message': 'Pourvoir un fichier valide'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        excel_file = data.get('file')
        df = pd.read_excel(excel_file, sheet_name=0)
        
        with tenant_context(client):
            User = get_user_model()
            messages_errors = []
            messages_success = []
            abon = AbonnementEse.objects.last()
            # abon = [ab for ab in all_abon if ab.is_valid()==True]
            # abon = AbonnementEse.objects.filter(is_valid=True).last() 
            #abon = AbonnementEse.objects.annotate(is_valid=F('is_active') and F('date_fin') > datetime.date.today()).filter(is_valid=True).last()
            # abon = AbonnementEse.objects.annotate(is_valid=Value(True, output_field=BooleanField())).last()
            if abon.is_valid == True: 
                nbre_veh = abon.nbre_engins              
                nbre_vehActuel = VehiculesEses.objects.all().count()

                nbre_pl1 = VehiculesEses.objects.filter(categorie='PL1').count()
                nbre_pl2 = VehiculesEses.objects.filter(categorie='PL2').count()
                nbre_vl = VehiculesEses.objects.filter(categorie='VL').count()
                nbre_mn = VehiculesEses.objects.filter(categorie='MN').count()
                nbre_gc = VehiculesEses.objects.filter(categorie='GC').count()
                # abon = AbonnementEse.objects.filter(is_valid=True).last()
                max_pl1 = int(abon.nbre_pl1)
                max_pl2 = int(abon.nbre_pl2)
                max_vl = int(abon.nbre_vl)
                max_mn = int(abon.nbre_man)
                max_gc = int(abon.nbre_gc)
                
                for k in range(len(df)):
                    if nbre_vehActuel < nbre_veh:

                        cat = str(df.iloc[k, 4]).strip().upper()
                        if cat == "PL1":
                            booll = nbre_pl1 < max_pl1
        
                        if cat == "PL2":
                            booll = nbre_pl2 < max_pl2
        
                        if cat == "VL":
                            booll = nbre_vl < max_vl
                            
                        if cat == "MN":
                            booll = nbre_mn < max_mn
        
                        if cat == "GC":
                            booll = nbre_gc < max_gc
        
                        if booll:

                            if VehiculesEses.objects.filter(immat=str(df.iloc[k, 2]).upper()).first() == None:
                                pos = ""
                                if df.iloc[k, 15] != "":
                                    pos += "".join(str(df.iloc[k, 15]).strip().upper())                           

                                if df.iloc[k, 16] != "" :
                                    if str(df.iloc[k, 16]).strip() != "nan":
                                        if pos == "":
                                            pos += "".join(str(df.iloc[k, 16]).strip().upper())
                                        else:
                                            pos += "".join("_")
                                            pos += "".join(str(df.iloc[k, 16]).strip().upper())
                                                            
                                if df.iloc[k, 17] != "":
                                    if str(df.iloc[k, 17]).strip() != "nan":
                                        if pos == "":
                                            pos += "".join(str(df.iloc[k, 17]).strip().upper())
                                        else:
                                            pos += "".join("_")
                                            pos += "".join(str(df.iloc[k, 17]).strip().upper())
                                                            
                                if df.iloc[k, 18] != "":
                                    if str(df.iloc[k, 18]).strip() != "nan":
                                        if pos == "":
                                            pos += "".join(str(df.iloc[k, 18]).strip().upper())
                                        else:
                                            pos += "".join("_")
                                            pos += "".join(str(df.iloc[k, 18]).strip().upper())                           
                                
                                if df.iloc[k, 19] != "":
                                    if str(df.iloc[k, 19]).strip() != "nan":
                                        if pos == "":
                                            pos += "".join(str(df.iloc[k, 19]).strip().upper())
                                        else:
                                            pos += "".join("_")
                                            pos += "".join(str(df.iloc[k, 19]).strip().upper())
                                                        
                                if df.iloc[k, 20] != "":
                                    if str(df.iloc[k, 20]).strip() != "nan":
                                        if pos == "":
                                            pos += "".join(str(df.iloc[k, 20]).strip().upper())
                                        else:
                                            pos += "".join("_")
                                            pos += "".join(str(df.iloc[k, 20]).strip().upper())
                                                    
                                if df.iloc[k, 2] in VehiculesEses.objects.all().values_list('immat',flat=True):
                                    j = k+1
                                    messages_errors.append("L'engin immatriculé " +str(df.iloc[k, 2])+ " de la ligne " +str(j)+ " existe déjà dans le parc")
                                
                                
                                vehicule = {}
                                                    
                                vehicule['num_parc'] = str(df.iloc[k, 1]).strip().upper()
                                vehicule['immat'] = str(df.iloc[k, 2]).upper()
                                vehicule['typecompteur'] = str(df.iloc[k, 3]).strip().upper()
                                vehicule['categorie'] = str(df.iloc[k, 4]).strip().upper()
                                vehicule['type'] = str(df.iloc[k, 5]).strip().upper()
                                vehicule['marque'] = str(df.iloc[k, 6]).strip().upper()
                                vehicule['model'] = str(df.iloc[k, 7]).strip().upper()
                                vehicule['energie'] = str(df.iloc[k, 8]).strip().upper()
                                vehicule['puissance'] = str(df.iloc[k, 9]).strip().upper()
                                vehicule['serie'] = str(df.iloc[k, 10]).strip().upper()
                                vehicule['branding'] = str(df.iloc[k, 11] ).strip().upper()                  
                                vehicule['date_mse'] = str(df.iloc[k, 12])
                                vehicule['statut'] = str(df.iloc[k, 13]).strip().upper()

                                pole_matrlt = ""
                                pole_matrlt += "".join(str(client.schema_name).strip().upper())
                                pole_matrlt += "".join("_")
                                # pole_matrlt += "".join("DG")
                                # pole_matrlt += "".join("_")
                                pole_matrlt += "".join(str(df.iloc[k, 14]).strip().upper())

                                matrlt = Organigramme.objects.filter(organigramme=pole_matrlt).first()
                                if matrlt != None:
                                    vehicule['site_matrlt'] = matrlt.id
                                else:
                                    vehicule['site_matrlt'] = None

                                
                                position = ""
                                position += "".join(str(client.schema_name).strip().upper())
                                position += "".join("_")
                                position += "".join(pos.upper())

                                organig = Organigramme.objects.filter(organigramme=position).first()
                                
                                if organig != None:
                                    vehicule['affectation'] = organig.id                        
                                    iden = ""
                                    iden += "".join(client.schema_sigle.upper())                        
                                    iden += "".join("_")
                                    iden += "".join(str(df.iloc[k, 2]).strip().upper())
                                    iden += "".join("_")
                                    iden += "".join(pos)

                                    vehicule['identite'] = iden

                                    serializer_engin = VehSerializer(data=vehicule)
                                    serializer_engin.is_valid(raise_exception=True)
                                    serializer_engin.save()
                                    nbre_vehActuel += 1
                                else:
                                    
                                    vehicule['affectation'] = None                        
                                    iden = ""
                                    iden += "".join(client.schema_sigle.upper())                        
                                    iden += "".join("_")
                                    iden += "".join(str(df.iloc[k, 2]).strip().upper())
                                    iden += "".join("_")
                                    iden += "".join(pos)

                                    vehicule['identite'] = iden

                                    serializer_engin = VehSerializer(data = vehicule)
                                    serializer_engin.is_valid(raise_exception=True)
                                    serializer_engin.save()

                                    l = k+1
                                    messages_success.append("L'engin immatriculé " +str(df.iloc[k, 2])+ " de la ligne " +str(l)+ " a été enregistré avec succès")
                                    nbre_vehActuel += 1
                        else:
                            j = k+1
                            messages_errors.append("L'enregistrement de la ligne " +str(j)+ " ne peut se faire, la catégorie " + cat + " de cet engin a atteint son seuil d'après votre abonnement. Veuillez le mettre à jour ")
                            
                else:
                    return Response({
                        'status': False,
                        'message': "Importation non achevée, Seuil d'importation atteint",
                        'messages_success':messages_success,
                        'messages_errors': messages_errors,
                    }, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                messages_errors.append("Votre abonnement est expiré")
                           

            return Response({
                'status': True,
                'message': "Fichier des engin importé avec succès.",
                'messages_success':messages_success,
                'messages_errors': messages_errors,
            }, status=status.HTTP_201_CREATED)



class VehiculeViewSet(ModelViewSet):

    serializer_class = VehSerializer
    def get_queryset(self):
        list_perms = ['MatRoulant.add_vehiculeseses', 'MatRoulant.change_vehiculeseses', 'MatRoulant.delete_vehiculeseses', 'MatRoulant.view_vehiculeseses']
        return get_objects_for_user(self.request.user, list_perms)

    filter_backends = [DjangoFilterBackend, SearchFilter]
    # filterset_class = VehiculeFilters
    search_fields = ["immat", "num_parc", "identite", "categorie", "type", "marque", "model", "branding", "statut"]
    ordering_fields = ["date_mse"]
    pagination_class = PageNumberPagination
    parser_classes =  [FormParser, MultiPartParser]


    def create(self, request, *args, **kwargs):

        client = get_tenant(request)
        with tenant_context(client):
            datas = request.data.copy()
            conducts = datas.pop('conducteurs', None)
            abon = AbonnementEse.objects.last()
            if abon.is_valid == True:          
                nbre_vehActuel = VehiculesEses.objects.all().count()
                nbre_pl1 = VehiculesEses.objects.filter(categorie='PL1').count()
                nbre_pl2 = VehiculesEses.objects.filter(categorie='PL2').count()
                nbre_vl = VehiculesEses.objects.filter(categorie='VL').count()
                nbre_mn = VehiculesEses.objects.filter(categorie='MN').count()
                nbre_gc = VehiculesEses.objects.filter(categorie='GC').count()
                
                # abon = AbonnementEse.objects.filter(is_valid=True).last()
                max_pl1 = int(abon.nbre_pl1)
                max_pl2 = int(abon.nbre_pl2)
                max_vl = int(abon.nbre_vl)
                max_mn = int(abon.nbre_man)
                max_gc = int(abon.nbre_gc)
                max_eng = int(abon.nbre_engins)
                if nbre_vehActuel < max_eng:

                    cat = request.data['categorie']
                    if cat == "PL1":
                        booll = nbre_pl1 < max_pl1

                    if cat == "PL2":
                        booll = nbre_pl2 < max_pl2

                    if cat == "VL":
                        booll = nbre_vl < max_vl
                        
                    if cat == "MN":
                        booll = nbre_mn < max_mn

                    if cat == "GC":
                        booll = nbre_gc < max_gc

                    if booll:

                        org = Organigramme.objects.get(id=request.data["affectation"]).organigramme
                        schemas = str(org).split('_')[0]
                        organ = str(org).split(schemas)

                        datas["identite"] = schemas
                        # datas["identite"] += "".join(client.schema_sigle.upper())  
                        datas["identite"] += "".join("_")
                        datas["identite"] += "".join(str(request.data['num_parc']).upper().split())
                        # datas["identite"] += "".join("_")
                        datas["identite"] += "".join(str(organ[1]))  
                        serializer = VehSerializer(data=datas)
                        serializer.is_valid(raise_exception=True)
                        veh = serializer.save()

                        if conducts:
                            # Accepts a list of model instances, querysets, or primary keys
                            veh.conducteurs.add(*conducts)

                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                    else:
                        return Response({
                                'message': "Le seuil d'enregistrement d'engin de cette catégorie est atteint. Vous ne pouvez plus en ajouter. Veuillez mettre à jour votre abonnement au cas échéant Merci.",
                            }, status=status.HTTP_406_NOT_ACCEPTABLE)
                        
                else:
                    return Response({
                            'message': "Création impossible, Seuil d'importation atteint",
                        }, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                return Response({'message': "Votre abonnement est expiré",})  

                     

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        VisiteVeh.objects.get(vehicule=instance).delete()
        AssurVeh.objects.get(vehicule=instance).delete()
        CGVeh.objects.get(vehicule=instance).delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def update(self, request, *args, **kwargs):
        client = get_tenant(request)
        with tenant_context(client):

            instance = VehiculesEses.objects.get(id=kwargs['pk'])

            data = request.data.copy()

            org = Organigramme.objects.get(id=request.data["affectation"]).organigramme
            schemas = str(org).split('_')[0]
            organ = str(org).split(schemas)

            data["identite"] = schemas
            
            data["identite"] += "".join("_")
            data["identite"] += "".join(str(request.data['num_parc']).upper().split())
          
            data["identite"] += "".join(str(organ[1]))
            serializer = VehSerializer(instance, data, partial=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)


        return super().update(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)




class AssurViewSet(ModelViewSet):
    serializer_class = AssurSerializer

    def get_queryset(self):
        veh = VehiculesEses.objects.filter(id=self.kwargs['engin_pk']).first()
        return AssurVeh.objects.filter(vehicule_id=veh).select_related('vehicule')
    
    def get_serializer_context(self):
        return {"engin_id": self.kwargs['engin_pk']}
    


class VisitechViewSet(ModelViewSet):
    serializer_class = VisitSerializer

    def get_queryset(self):
        veh = VehiculesEses.objects.filter(id=self.kwargs['engin_pk']).first()
        return VisiteVeh.objects.filter(vehicule_id=veh).select_related('vehicule')
    
    def get_serializer_context(self):
        return {"engin_id": self.kwargs['engin_pk']}


class CartegriseViewSet(ModelViewSet):
    serializer_class = CGSerializer

    def get_queryset(self):
        veh = VehiculesEses.objects.filter(id=self.kwargs['engin_pk']).first()
        return CGVeh.objects.filter(vehicule_id=veh).select_related('vehicule')
    
    def get_serializer_context(self):
        return {"engin_id": self.kwargs['engin_pk']}
    
    