from django.shortcuts import render
from rest_framework.response import Response
from .models import Project, ZipFile, Session
from .serializers import ProjectSerializer, UnzipSerializer, SessionCreateSerializer,SessionUpdateSerializer
from rest_framework import viewsets
from django.http import HttpResponse
from .request_permissions import CustomPermission
from rest_framework.views import APIView
import os, zipfile
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, DestroyAPIView
import csv
from .utilis import delete_cases

# Create your views here.

class UnZipView(viewsets.ViewSet):
    serializer_class = UnzipSerializer
    permission_classes = [CustomPermission]
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            result_lists = serializer.process_uploaded_file()
            return Response({'result_lists': result_lists}, status=200)
        return Response(serializer.errors, status=400)
    
class ReadFromLocalView(APIView):
    def get(self, request):
        try:        
            last_zip_file = ZipFile.objects.first()
            last_created_instance = Project.objects.latest('created_at')
            serializer = ProjectSerializer(last_created_instance)
        except:
            return HttpResponse("No object is created before")
        
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

            for subfolder in subfolders_names:
                if os.path.isdir(os.path.join(extract_dir, subfolder)):
                    subfolders_path = os.path.join(extract_dir, subfolder)

            # code reused from Serializer Class
            project_serializer = ProjectSerializer()
            category_type_folder_list  = project_serializer.find_list_folders(subfolders_path)

            unzip_serializer = UnzipSerializer()
            unique_categories_types_dict = unzip_serializer.find_categories_types_dict(category_type_folder_list)
                    
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


class ProjectView(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [CustomPermission]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_sessions = instance.session.all()
        for session in instance_sessions:
            delete_cases(session)
        instance.session.all().delete()
        instance.delete()
        return super(ProjectView, self).destroy(request, *args, **kwargs)
    
class SessionDestroyView(DestroyAPIView):
    serializer_class = SessionCreateSerializer
    queryset = Session.objects.all()

    def destroy(self, request, *args, **kwargs):
        session = self.get_object()
        ProjectView.delete_cases(session)
        projects_related_to_session = session.project_set.all()
        try:
            session_list = projects_related_to_session[0].session.all()
            if len(session_list)  == 1:
                projects_related_to_session[0].delete()
        except:
            pass
        return super().destroy(request, *args, **kwargs)




class SessionCreateView(CreateAPIView):
    serializer_class = SessionCreateSerializer
    queryset = Session.objects.all()
    permission_classes = [CustomPermission]

class SessionUpdateView(RetrieveUpdateAPIView):
    serializer_class = SessionUpdateSerializer
    queryset = Session.objects.all()
    
class ExportDataview(APIView):
    def get(self, request, id):
        session = Session.objects.get(id = id)
        projects_related_to_session = session.project_set.all()
        slice_all = session.slice.all()
        
        project_name = projects_related_to_session[0].project_name
        
        date_time = session.created_at.strftime("%d:%m:%Y %I:%M %p")
        
        title = f"{project_name}-{date_time}.csv"
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{title}"'
        csv_data = []
        csv_data.append(['Project Name', 'Session Name', 'Case Name', 'TimeStamp', 'Category_Type', 'Image Id', 'Score', 'Labels', 'Options'])
        row = []

        for slice in slice_all:
            row = [slice.project_name, slice.session_name, slice.case_name, date_time, slice.category_type_name, slice.image_id, slice.score, slice.labels, slice.options]
            csv_data.append(row)

        csv_text = "\n".join([",".join(['"{}"'.format(value) for value in row]) for row in csv_data])

        # Return the CSV data as text content
        response_data = {'csv_text': csv_text}
        return Response(response_data)


class CustomSliceView(APIView):
    def post(self, request):
        serializer = SessionCreateSerializer(data=request.data)

        if serializer.is_valid():
            session_obj = serializer.save()
            return Response({'session_obj_id': session_obj.id}, status=201)
        return Response(serializer.errors, status=400) 
