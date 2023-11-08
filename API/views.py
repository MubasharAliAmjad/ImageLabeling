from django.shortcuts import render
from rest_framework.response import Response
from .models import Slice, Category_Type, Labels, Session, Project, Image, ZipFile, SliceSession
from .serializers import Slice_Serializer, Category_Type_Serializer, Labels_Serializer, Session_Serializer, Project_Serializer, Unzip_Serializer, customSliceSerializer
from rest_framework import viewsets
from rest_framework import status
from django.http import HttpResponse
from django.core.files.base import ContentFile
from .request_permissions import CustomPermission
from rest_framework.views import APIView
import os, zipfile
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
import csv
from django.contrib.sites.shortcuts import get_current_site
from django.views.generic import TemplateView
from django.http import JsonResponse
from rest_framework import generics

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
    
class ReadFromLocal(APIView):

    def find_list_folders(self, subfolders_path):
        list_folders = []
        for case_name in os.listdir(subfolders_path):
                    if os.path.isdir(os.path.join(subfolders_path, case_name)):
                        for file_dir in os.listdir(os.path.join(subfolders_path, case_name)):
                            if file_dir not in list_folders:
                                if os.path.isdir(os.path.join(subfolders_path, case_name, file_dir)):
                                    list_folders.append(file_dir)
        return list_folders
    
    def find_categories_types_dict(self, category_type_folder_list):
        categories_types = []
        categoroes_types_dict = []
        for folder in category_type_folder_list:
            try:
                category, type = folder.split('_')
            except:
                continue
            if category not in categories_types:
                categories_types.append(category)
            if type not in categories_types:
                categories_types.append(type)

        for index, value in enumerate(categories_types, start=1):
            item_category = {"id": str(index), "value": value}
            categoroes_types_dict.append(item_category)
        return categoroes_types_dict

    def get(self, request):
        try:        
            last_zip_file = ZipFile.objects.first()
            last_created_instance = Project.objects.latest('created_at')
            serializer = Project_Serializer(last_created_instance)
        except:
            return HttpResponse("Nothing object is created before")
        file_name = last_zip_file.uploaded_file.name
        just_file_name = os.path.basename(file_name)

        unique_id = str(uuid.uuid4())
        just_file_name = f"{unique_id}_{just_file_name}"

        file_path = default_storage.path(last_zip_file.uploaded_file.name)
            
            
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            extract_dir = os.path.join(settings.MEDIA_ROOT, just_file_name)
            os.makedirs(extract_dir, exist_ok=True)
            zip_ref.extractall(extract_dir)
            subfolders_names = os.listdir(extract_dir)
            if '__MACOSX' in subfolders_names:
                subfolders_names.remove('__MACOSX') 

            # Client said there will be one parent folder, which will have Cases.
            for subfolder in subfolders_names:
                if os.path.isdir(os.path.join(extract_dir, subfolder)):
                    subfolders_path = os.path.join(extract_dir, subfolder)
                
            category_type_folder_list = self.find_list_folders(subfolders_path)
                
            unique_categories_types_dict = self.find_categories_types_dict(category_type_folder_list)
                    
            dict_folders = []
            for index, folder in enumerate(category_type_folder_list, start=1):
                item = {"id": str(index), "value": folder}
                dict_folders.append(item)
                
                output_data = {
                    "result_lists": {
                        "categories_types": unique_categories_types_dict,
                        "list_folders": dict_folders,
                        "zip_folder": just_file_name,
                        "last_created_instance": serializer.data
                    }
                }
            return Response(output_data)


class Project_View(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = Project_Serializer
    permission_classes = [CustomPermission]


# class Image_View(viewsets.ModelViewSet):
#     queryset = Image.objects.all()
#     serializer_class = Image_Serializer

class Export_Data_view(APIView):
    def get(self,request, id):
        
        session_data = SliceSession.objects.get(id = id)
        slice_data = session_data.slice.all()
        project_name = slice_data[0].project_name
        date_time = slice_data[0].created_at.strftime("%Y-%m-%d_%H-%M")
        # import pdb; pdb.set_trace()
        
        
        title = f"{project_name}-{date_time}.csv"
        # title = "testing"
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{title}"'
        csv_data = []
        csv_data.append(['Project Name', 'Session Name', 'Case Name', 'TimeStamp', 'Category_Type', 'Slice Id', 'Score', 'Labels', 'Options'])
        # writer.writerow()
        row = []

        for slice_item in slice_data:
            import pdb; pdb.set_trace()
            date_time = slice_item.created_at.strftime("%Y-%m-%d_%H-%M")
            # category_type = f"{category_type_item.category}_{category_type_item.type}"
            # import pdb;pdb.set_trace()
            row = [slice_item.project_name, id, slice_item.case_name, date_time, slice_item.category_type_name, slice_item.image_id, slice_item.labels, slice_item.options]

            csv_data.append(row)

        csv_text = "\n".join([",".join(map(str, row)) for row in csv_data])

        # Return the CSV data as text content
        response_data = {'csv_text': csv_text}
        return Response(response_data)

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

class customSliceView(APIView):
    def post(self, request):
        # Create an instance of the customSliceSerializer
        serializer = customSliceSerializer(data=request.data)

        # Validate and save the data
        if serializer.is_valid():
            session_obj = serializer.save()
            # You can also do additional processing here if needed
            return Response({'session_obj_id': session_obj.id}, status=201)  # Return the session_obj or its ID as a response
        return Response(serializer.errors, status=400)  # Return validation errors
