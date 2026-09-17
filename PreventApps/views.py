from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView, DestroyAPIView, RetrieveUpdateAPIView
from rest_framework import status
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
from Mgpa_api.middleware import get_tenant
from rest_framework.parsers import MultiPartParser, FormParser
from .SerializerPrevent import SuiviEpSerializer
from .models import SuiviEp


class ListSuiviEp(ListAPIView):
    serializer_class = SuiviEpSerializer
    parser_classes = [FormParser, MultiPartParser]
    # queryset = SuiviEp.objects.all()

    def get_queryset(self):
        my_user = self.request.user
        liste_type = ["DIRECTEUR MATERIEL ROULANT", "MASTER DATA" "DIRECTEUR GENERAL"]
        if my_user.type == "CHEF MATERIEL ROULANT":
            print(my_user)        
            return SuiviEp.objects.filter(site_matrlt=my_user.site)

        elif my_user.type == "CHEF FONCTIONNEL":
            return SuiviEp.objects.filter(site_fonct=my_user.site)

        elif my_user.type in liste_type:
            return SuiviEp.objects.all()
