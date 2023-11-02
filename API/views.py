from django.shortcuts import render
from rest_framework.response import Response
from .models import Slice, Category_Type, Labels, Session, Project, Image
from .serializers import Slice_Serializer, Image_Serializer, Category_Type_Serializer, Labels_Serializer, Session_Serializer, Project_Serializer, Unzip_Serializer
from rest_framework import viewsets
from rest_framework import status
from django.http import HttpResponse
from django.core.files.base import ContentFile
from .request_permissions import CustomPermission
# Create your views here.

class UnZip_View(viewsets.ViewSet):
    serializer_class = Unzip_Serializer
    permission_classes = [CustomPermission]
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            result_lists = serializer.process_uploaded_file()
            return Response({'result_lists': result_lists}, status=200)
        return Response(serializer.errors, status=400)

class Project_View(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = Project_Serializer
    permission_classes = [CustomPermission]


# class Slice_View(viewsets.ModelViewSet):
#     queryset = Slice.objects.all()
#     serializer_class = Slice_Serializer

# class Type_View(viewsets.ModelViewSet):
#     queryset = Type.objects.all()
#     serializer_class = Type_Serializer

# class Category_View(viewsets.ModelViewSet):
#     queryset = Category.objects.all()
#     serializer_class = Category_Serializer

# class Category_Type_View(viewsets.ModelViewSet):
#     queryset = Category_Type.objects.all()
#     serializer_class = Category_Type_Serializer

# class Labels_View(viewsets.ModelViewSet):
#     queryset = Labels.objects.all()
#     serializer_class = Labels_Serializer

# class Session_View(viewsets.ModelViewSet):
#     queryset = Session.objects.all()
#     serializer_class = Session_Serializer

