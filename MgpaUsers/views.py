from django.shortcuts import render
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework import generics
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from .models import GroupUsers
from rest_framework.response import Response
from .serializers import GroupUserSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import Group
from .models import UserAccount, GroupUsers
from .serializers import GroupUserSerializer
from rest_framework import status




class AddGroupUser(generics.CreateAPIView):
    queryset = GroupUsers.objects.all()
    serializer_class = GroupUserSerializer

    def create(self, request, *args, **kwargs):
        data = request.data 
        gr = data['group']
        us = data["user"]
        
        us.groups.add(gr)
        
        return Response({'status': True, 'message': "l'utilisateur " + str(us.last_name) + " " + str(us.first_name) + " a été ajouté au groupe"}, status=status.HTTP_200_OK) 





# @staff_member_required
# def addToPremiumGroup(request):
#     group = Group.objects.get(name='premium')
#     request.user.groups.add(group)
#     return HttpResponse('<h1> a ete ajouter avec success dans le group premium</h1>')






#pour les profiles des utilisateurs

# class ProfileViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
#     queryset = Profile.objects.all()
#     serializer_class = ProfileSerializer
#     pagination_class = PageNumberPagination
#     parser_classes =  [FormParser, MultiPartParser]
#     # permission_classes = [IsAdminUser]

    

#     def get_permissions(self):
#         if self.request.method == 'GET' or self.request.method == 'PUT':
#             return [AllowAny()]
#         return [IsAuthenticated()]
    
#     def update(self, request, *args, **kwargs):
#         return super().update(request, *args, **kwargs)
    
    

    

    # @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    # def me(self, request):
    #     (profile, created) = Profile.objects.get_or_create(user_id=request.user.id)
    #     if request.method == 'GET':
    #         serializer = ProfileSerializer(profile)
    #         return Response(serializer.data) 
    #     elif request.method == 'PUT':
    #         serializer = ProfileSerializer(profile, data=request.data)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         return Response(serializer.data)


