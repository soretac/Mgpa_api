from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .SerializerTravaux import SerializerDTEp, SerializerDTEpCreate, VehRecuEpSerializer, VehDepoEpSerializer
from .models import DTPrev, VehDepoEp, VehRecuEp
from django.contrib.auth import get_user_model
from rest_framework.parsers import MultiPartParser, FormParser
from Mgpa_api.middleware import get_tenant
from django.db.models import Q
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from MatRoulant.models import VehiculesEses
from rest_framework.response import Response
from rest_framework import status
from CompteurApps.models import AlerteEp
from PreventApps.models import SuiviEp, Eps
from PreventApps.SerializerPrevent import SerializerEps, SuiviEpSerializer
from Travaux.models import DTPrev
from Travaux.models import NumPrefix
from Travaux.SerializerTravaux import NumPrefixSerializer
from Travaux.models import DTPrev
from Travaux.SerializerTravaux import SerializerDTEpCreate
import os
from django.conf import settings
from twilio.rest import Client
from django.utils import timezone
from fillpdf import fillpdfs
import datetime



User = get_user_model()

class DTEpCreate(CreateAPIView):
    serializer_class = SerializerDTEpCreate
    queryset = DTPrev.objects.all()


    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        
        data_eps = {}
        sep = SuiviEp.objects.filter(id=data["ep"]).first()
        data_eps['vehicule'] = sep.vehicule_id
        data_eps['statut_dt'] = "EN DEMANDE"
        data_eps['type_ep'] = sep.prochain_ep
        data_eps['compt_alert'] = sep.compt_act
        data_eps['compt_ep'] = None
        data_eps['date_ep'] = None   
        data_eps['observation'] = "Entretien Préventif"
        data_eps['garagiste'] = data["garagiste"]

        serializer = SerializerEps(data=data_eps)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        suivi = SuiviEp.objects.filter(id=data['ep']).first()
        suivi.statut_ep = "EN ATTENTE"
        suivi.save()

        

        num = NumPrefix.objects.filter(Q(entete="DTEP") & Q(statut="valide")).order_by("id").first()
        suff = num.suffix
        
        pref = str(num.prefix)
        
        clients = get_tenant(request)
        ndtep = ""
        ndtep += "".join(clients.schema_name)
        ndtep += "".join("-")
        ndtep += "".join("DTEP")
        ndtep += "".join("/")
        ndtep += "".join(pref)
        suffix = int(suff) + 1
        r = 3 - len(str(suffix))
        
        if r > 0:
            m = 1
            suf = ""
            while m <= r:
                suf = str(suf)+"0"
                m += 1
            
            suffix = suf + str(suffix)
            print(suf)

        ndtep += "".join(str(suffix))
        # print("************************************************************\n")
        # print(ndtep)
        # print(request.user)
        # print(sep.vehicule_id)
        # print(data["description"])
        # print(str(data["description"]))
        # print(data["description"][0])
        
        print("************************************************************\n")
        data_dt = {}
        
        data_dt["description"] = data["description"]
        data_dt["ep"] = data["ep"]
        data_dt["garagiste"] = data["garagiste"]
        data_dt["demandeur"] = request.user.id
        data_dt["vehicule"] = sep.vehicule_id
        data_dt["num_dtep"] = ndtep

        num.suffix = str(suffix)
        if suff == "998":
            num.statut = "invalide"
        num.save()

        serializer_dtep = SerializerDTEpCreate(data=data_dt)
        serializer_dtep.is_valid(raise_exception=True)
        serializer_dtep.save()

        return Response(serializer_dtep.data, status=status.HTTP_200_OK)


class ListDTEp(ListAPIView):
    serializer_class = SerializerDTEpCreate
    queryset = DTPrev.objects.all()

    def get_queryset(self):
        list_dest = ["DIRECTEUR MATERIEL ROULANT", "MASTER DATA", "DIRECTEUR GENERAL"]
        my_user = self.request.user
        if my_user.type == "CHEF MATERIEL ROULANT":
                   
            return DTPrev.objects.filter(vehicule__site_matrlt=my_user.site)

        elif my_user.type == "CHEF FONCTIONNEL":
            return SuiviEp.objects.filter(vehicule__site_fonct=my_user.site)

        if my_user.type == "CHEF GARAGE":
                    
            return DTPrev.objects.filter(vehicule__site_matrlt=my_user.site)

        elif my_user.type in list_dest:
            return DTPrev.objects.all()



class CreateVehDepo(CreateAPIView):
    serializer_class = VehDepoEpSerializer
    queryset = VehDepoEp.objects.all()
    parser_classes =  [FormParser, MultiPartParser]


    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        my_user = request.user 
        data["utilisateur"] = my_user
        serializer = VehDepoEpSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)



class CreateVehRecu(CreateAPIView):
    serializer_class = VehRecuEpSerializer
    queryset = VehRecuEp.objects.all()
    parser_classes =  [FormParser, MultiPartParser]


    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        depo = VehDepoEp.objects.filter(dtep_id=data["dtep"]).first()
        if depo == None: 
            return Response({'message': "Vous ne pouvez receptionner l'engin, puisqu'il n'a pas encore été déposé!"},  status=status.HTTP_406_NOT_ACCEPTABLE)

        elif depo.depot_utilisateur == "PAS DEPOSE": 
            return Response({'message': "Vous ne pouvez receptionner l'engin, puisqu'il n'a pas encore été déposé!"},  status=status.HTTP_406_NOT_ACCEPTABLE)
            
        else: 
            my_user = request.user 
            data["garagiste"] = my_user
            serializer = VehRecuEpSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dt = DTPrev.objects.filter(id=data["dtep"]).first()
            dt.statut_dt = "En cours"
            dt.save()
            return Response(serializer.data, status=status.HTTP_200_OK)



    # def partial_update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     my_user = request.data 
    #     data = request.data
    #     data["utilisateur"] = my_user

    #     serializer = self.get_serializer(instance, data=data, partial=True)
    #     serializer.is_valid(raise_exception=True)

    #     self.perform_update(serializer)

    #     dt = DTPrev.objects.filter(id=instance.dtep_id)
    #     dt.statut_dt = "En Cours"
    #     dt.save()

    #     return super().partial_update(request, *args, **kwargs)

    # def get_queryset(self):
    #     my_user = self.request.user
    #     if my_user in VehDispoEp.utilisateur.all():
    #         return VehDispoEp.objects.all()

    #     if my_user.type == "CHEF GARAGE":
    #         return VehDispoEp.objects.filter(garagiste=my_user)


# class DispoVehUtil(CreateAPIView):
#     serializer_class = MiseDispoEPSerializer
#     queryset = MiseDispoEp.objects.all()

#     def create(self, request, *args, **kwargs):

#         return super().create(request, *args, **kwargs)





# product = Product.objects.get(id=1)

# # Loop through field definitions and extract their values
# for field in product._meta.fields:
#     field_name = field.name
#     field_value = getattr(product, field_name)
#     print(f"{field_name}: {field_value}")