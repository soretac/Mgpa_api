from django.shortcuts import render
from rest_framework.generics import CreateAPIView, UpdateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView
from .SerializerComptApps import CompteurSerializer, AlerteEpSerializer, CountCritiqSerializer
from .models import Compteurs, AlerteEp, CountCritique
from rest_framework.viewsets import ModelViewSet
from Mgpa_api.middleware import get_tenant
from django_tenants.utils import tenant_context
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from MatRoulant.models import VehiculesEses
from .models import Compteurs
from MgpaUsers.models import UserAccount
from rest_framework import status
from django.db.models import Q
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend


User = get_user_model()

class CompteurCreate(ModelViewSet):
    serializer_class = CompteurSerializer

    def get_queryset(self): 
        users = self.request.user
        return Compteurs.objects.filter(Q(vehicule_id=self.kwargs['engin_pk'])).select_related('vehicule')
        # return VehiculesEses.objects.filter(Q(id=self.kwargs['engin_pk']) & Q(conducteurs__id=self.request.user.id))
        # if users in veh.conducteurs.all():        
        #     return Compteurs.objects.filter(Q(vehicule_id=veh)).select_related('vehicule')
        # else:
        #     return Response("Engin n'appartenant pas")
        
        
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return {"engin_id": self.kwargs['engin_pk']}
    
    def create(self, request, *args, **kwargs):
        type_zone = ["DIR_EXPLOIT", "CHEF_SMRLT"]
        type_total = ["MASTER_DATA", "DIR_GEN"]
        cpt = ''
        usercurrent = self.request.user
        veh = VehiculesEses.objects.get(id=self.kwargs['engin_pk'])
        
        
        if usercurrent.type in type_zone:    
            cpt = 'oui'
            
        elif usercurrent.type in type_total:
            cpt = 'oui'
        else:
            idd = veh.conducteurs.all().values_list("email", flat=True)
            print("-------------------------------------\n")
            print(idd)
            if usercurrent.email in idd:
                cpt = 'oui'
            else:
                cpt = 'non'


        if cpt == 'non':
            return Response({'message': "Engin ne faisant pas parti du parc de l'utilisateur !"},  status=status.HTTP_406_NOT_ACCEPTABLE)
        
        if cpt == 'oui':


            if request.data['compt_act'] == "":
                return Response({'message': "Compteur incorrect, Veuillez renseigner le compteur"},  status=status.HTTP_406_NOT_ACCEPTABLE)
            
            else:

                client = get_tenant(request)
                with tenant_context(client):
                    datacopy =  request.data.copy()
                                
                    last_enrg = Compteurs.objects.filter(vehicule_id=self.kwargs['engin_pk']).last()
                    print("******------------*************--------------***********---------\n")
                    print(last_enrg)
                    if last_enrg != None:
                        if Decimal(datacopy['compt_act']) >= Decimal(last_enrg.compt_act):
                            datacopy['last_compt'] = last_enrg.compt_act
                            datacopy['start_compt'] = last_enrg.start_compt
                            datacopy['ecart'] = Decimal(datacopy['compt_act']) - Decimal(last_enrg.start_compt)
                            print(datacopy['ecart'])
                            print("********************------------------------------\n")
                            datacopy['releveur'] = self.request.user.id

                            serializer = self.get_serializer(data=datacopy)
                            serializer.is_valid(raise_exception=True)                        
                            serializer.save()
                            return Response(serializer.data, status=status.HTTP_200_OK)
                        else:
                            return Response({'message': "Compteur incorrect, donnant un écart négatif avec le précédent"},  status=status.HTTP_406_NOT_ACCEPTABLE)
                
                    else:
                        datacopy['last_compt'] = datacopy['compt_act']
                        datacopy['start_compt'] = datacopy['compt_act']
                        datacopy['ecart'] = 0.0
                        datacopy['releveur'] = self.request.user.id

                        serializer = self.get_serializer(data=datacopy)
                        serializer.is_valid(raise_exception=True)                        
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_200_OK)

        




# class AlertEpViews(ModelViewSet):
#     serializer_class = AlerteEpSerializer
#     queryset = AlerteEp.objects.all()
#     pagination_class = PageNumberPagination
#     parser_classes =  [FormParser, MultiPartParser]
#     filter_backends = [DjangoFilterBackend, SearchFilter]
#     # search_fields = ["immat", "num_parc", "identite", "categorie", "type", "marque", "model", "branding", "statut"]
#     # ordering_fields = ["date_mse"]











# class CompteurViewSet(ModelViewSet):
#     serializer_class = CompteurSerializer

#     def get_queryset(self): 
#         veh = VehiculesEses.objects.filter(id=self.kwargs['engin_pk']).first()
#         users = self.request.user
#         return Compteurs.objects.filter(vehicule_id=veh).select_related('vehicule')

#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context['request'] = self.request
#         return {"engin_id": self.kwargs['engin_pk']}
    


#     def create(self, request, *args, **kwargs):

#         client = get_tenant(request)
#         with tenant_context(client):
#             data =  request.data.copy()
#             enrg_compt = Compteurs.objects.filter(vehicule_id=self.kwargs['engin_pk'])

#             if enrg_compt.exists():
                
#                 query_ep = enrg_compt.filter(~Q(rel_ep = 0.0))
#                 if query_ep.exists():
#                     enrg_ep = query_ep.latest('date_ep').rel_ep
#                     ecart = Decimal(Decimal(data['rel_compt']) - enrg_ep.rel_ep)
#                     last_rel = enrg_compt.last().rel_compt
#                     if ecart < 0.00 or Decimal(data['rel_compt']) < last_rel:
#                         return Response({'message': "Compteur incorrect, donnant un écart négatif avec le précédent"},  status=status.HTTP_406_NOT_ACCEPTABLE)
#                     else:
#                         serializer = self.get_serializer(data=data)
#                         serializer.is_valid(raise_exception=True)                        
#                         serializer.save(releveur=self.request.user, rel_ecart=ecart)
#                         return Response(serializer.data, status=status.HTTP_200_OK)

#                 else:
#                     enrg_first = enrg_compt.order_by('id')[0]
#                     last_rel = enrg_compt.last().rel_compt
#                     ecart = Decimal(Decimal(data['rel_compt'])-enrg_first.rel_compt)
#                     if ecart < 0.00 or Decimal(data['rel_compt']) < last_rel:
#                         return Response({'message': "Compteur incorrect, donnant un écart négatif avec le précédent"}, status=status.HTTP_406_NOT_ACCEPTABLE)

#                     else:
#                         # data['vehicule_id'] = self.kwargs['engin_pk']
#                         # data['rel_ecart'] = ecart
#                         serializer = self.get_serializer(data=data)                         
#                         serializer.is_valid(raise_exception=True)                        
#                         serializer.save(releveur=self.request.user, rel_ecart=ecart)
#                         return Response(serializer.data, status=status.HTTP_200_OK)

#             else:
#                 data['vehicule'] = self.kwargs['engin_pk']    
#                 serializer = self.get_serializer(data=data)
#                 serializer.is_valid(raise_exception=True)  
#                 serializer.save(releveur=self.request.user)
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)


class AlertEpViewSet(ListAPIView):
    serializer_class = AlerteEpSerializer

    def get_queryset(self): 
        list_operateur = ["UTIL", "OPER", "MAG"]
        list_chef = ["CFONCT", "CGAR", "CMR", "DMR", "MDATA", "DGEN"]
        if self.request.user.type in list_operateur:
            return AlerteEp.objects.filter(utilisateur=self.request.user)
        elif self.request.user.type in list_chef:
            return AlerteEp.objects.all()


class ListAlertEp(ListAPIView):
    serializer_class = AlerteEpSerializer

    def get_queryset(self): 
        my_user = self.request.user
        altep = AlerteEp.objects.all()
        return altep
        # list_operateur = ["UTILISATEUR", "OPERATEUR", "MAGASINIER"]
        # list_chef = ["DIRECTEUR MATERIEL ROULANT", "MASTER DATA", "DIRECTEUR GENERAL"]
        # dest_alert =[user for user in User.objects.filter(Q(type__in=list_chef))]
        
        # if users.type in list_operateur:
        #     alert = AlerteEp.objects.filter(vehicule__conducteurs=users.id)
            

class ListCountEpCritiq(ListAPIView):
    serializer_class = CountCritiqSerializer
    queryset = CountCritique.objects.all()


# class ListCptAlertEp(ListAPIView):
#     serializer_class = CptAlertSerializer

#     def get_queryset(self): 
#         list_operateur = ["UTILISATEUR", "OPERATEUR", "MAGASINIER"]
#         list_chef = ["CHEF FONCTIONNEL", "CHEF GARAGE", "CHEF MATERIEL ROULANT", "DIRECTEUR MATERIEL ROULANT", "MASTER DATA", "DIRECTEUR GENERAL"]
#         users = self.request.user
#         if users.type in list_operateur:
#             alert = CptAlert.objects.select_related('vehicule').filter(vehicule__conducteurs=users.id).distinct()
#             print(alert)
#             return alert
#             # return AlerteEp.objects.filter(utilisateur=self.request.user)
#         elif self.request.user.type in list_chef:
#             return AlerteEp.objects.all()