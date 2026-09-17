from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Clients, Domain, AbonneClient, Prix_soretac
from rest_framework.views import APIView
from .ClientSerializers import ClientEseSerializer, AbonneClientSerializer, PrixSoretacSerializer
from .pwd_generator import CodeGenerator, PwdGenerator, abonnement
from rest_framework.response import Response
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from rest_framework import status
import datetime
from rest_framework.parsers import MultiPartParser, FormParser
from .tasks import notif_client


class ClientViewSet(ModelViewSet):
    parser_classes = [FormParser, MultiPartParser]
    queryset = Clients.objects.all()
    serializer_class = ClientEseSerializer

    def get_serializer_context(self):
        data = self.request.data
        return {'request': self.request,}
    
    def perform_create(self, serializer):
        
        # code = CodeGenerator()
        mdpbrut = PwdGenerator()
        abnt = abonnement()
        serializer.save(mdp_admin=mdpbrut, code_ab=abnt)

        return Response(serializer.data, status=status.HTTP_200_OK)


class PrixViews(ModelViewSet):
    parser_classes = [FormParser, MultiPartParser]
    queryset = Prix_soretac.objects.all()
    serializer_class = PrixSoretacSerializer



class ClientAbonneViewset(ModelViewSet):
    parser_classes = [FormParser, MultiPartParser]
    queryset = AbonneClient.objects.all()
    serializer_class = AbonneClientSerializer

    def perform_create(self, serializer):
        data = self.request.data
        
        client = Clients.objects.filter(id_enreg= data['ese']).first() 
        
        if client == None :
            return Response({
                'status': False,
                'message': "Nom d'entreprise inexistante"
            }, status=status.HTTP_400_BAD_REQUEST) 
        else:
            
            racine = abonnement()
            dat = str(datetime.date.today())
            print(dat)
            d = dat[9:]
            m = dat[6:8]               
            ab = str(client.code_ab)+d+m+str(racine)
            # data["num_abon"] = ab
        
            code = CodeGenerator()
            serializer.save(code=code, num_abon=ab, schema_name=client.schema_name)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        
            



      
class ClientDeactivate(APIView):

    def post(self, request):   
        instance = self.get_object()
        instance.ese_activate = False
        instance.save()
        return Response(status=status.HTTP_423_LOCKED)