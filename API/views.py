from django.shortcuts import render, redirect
from rest_framework.response import Response
from .models import Project, ZipFile, Session, CustomUser
from .serializers import ProjectSerializer, UnzipSerializer, SessionCreateSerializer,SessionUpdateSerializer
from rest_framework import viewsets
from django.http import HttpResponse, JsonResponse
from .request_permissions import CustomPermission
from rest_framework.views import APIView
import os, zipfile
from django.views import View
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, DestroyAPIView
import csv
from .utilis import delete_cases
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
User = get_user_model()
from djangosaml2.views import LoginView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.tokens import AccessToken

# Create your views here.
class JsonLoginView(LoginView):
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        html_content = response.content.decode('utf-8')

        action_url_start = html_content.find('action="') + len('action="')
        action_url_end = html_content.find('"', action_url_start)
        action_url = html_content[action_url_start:action_url_end]

        saml_request_start = html_content.find('name="SAMLRequest" value="') + len('name="SAMLRequest" value="')
        saml_request_end = html_content.find('"', saml_request_start)
        saml_request = html_content[saml_request_start:saml_request_end]

        # Construct JSON response
        json_data = {
            'action_url': action_url,
            'saml_request': saml_request,
            'relay_state': '/api/saml_response/',
        }

        return JsonResponse(json_data)

class LogoutView(APIView):
    def post(self, request, *args, **kwargs):

        token = self.request.headers.get("Authorization")
        token = RefreshToken(token)
        if not token:
            return Response({'error': 'Refresh token not provided'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token.blacklist()
            return Response({'success': 'Logout successful'})
        except Exception as e:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
class SAMLResponseView(APIView):
    def get(self, request):
        user = request.user
        try:
            
            refresh = RefreshToken.for_user(user)
            redirect_url = f'https://www.pixelpeek.xyz/sign-in?token={refresh}'
            # redirect_url = f'http://localhost:3000/sign-in?token={refresh}'
            return redirect(redirect_url)
        except Exception as e:
            # redirect_url = f'http://localhost:3000/sign-in?error={e}'
            redirect_url = f'https://www.pixelpeek.xyz/sign-in?error={e}'
            return redirect(redirect_url)

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


    def list(self, request, *args, **kwargs):
        token = self.request.headers.get("Authorization")
        try:
            token = RefreshToken(token)
            user_id = token['user_id']
        except Exception as e:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch user data
        user = User.objects.get(id=user_id)
        user_data = {'user_data': user.email, 'username': user.email.split('@')[0]}

        # Fetch project data
        projects = Project.objects.filter(user=user)
        serializer = ProjectSerializer(projects, many=True)
        project_data = serializer.data

        # Construct the response data
        data = {'user_data': user_data, 'project_data': project_data}

        return Response(data, status=status.HTTP_200_OK)


    def get_serializer_context(self):
        
        context = super().get_serializer_context()
        context['token'] = self.request.headers.get('Authorization')
        return context
        

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_sessions = instance.session.all()
        for session in instance_sessions:
            delete_cases(session)
        instance.session.all().delete()
        instance.delete()
        return Response({'message': 'Object deleted successfully'}, status=status.HTTP_200_OK)
    
class SessionDestroyView(DestroyAPIView):
    serializer_class = SessionCreateSerializer
    queryset = Session.objects.all()

    def destroy(self, request, *args, **kwargs):
        session = self.get_object()
        delete_cases(session)
        projects_related_to_session = session.project_set.all()
        try:
            session_list = projects_related_to_session[0].session.all()
            if len(session_list)  == 1:
                projects_related_to_session[0].delete()
        except:
            pass
        session.delete()
        return Response({'message': 'Object deleted successfully'}, status=status.HTTP_200_OK)


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
        
        date_time = session.created_at.strftime("%d:%m:%Y %I:%M:%S %p")

        
        title = f"{project_name}-{date_time}.csv"
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{title}"'
        csv_data = []
        csv_data.append(['User', 'Project Name', 'Session Name', 'Case Name', 'TimeStamp', 'Category_Type', 'Image Id', 'Score', 'Labels', 'Options'])
        row = []

        for slice in slice_all:
            date_time = slice.created_at.strftime("%d:%m:%Y %I:%M:%S %p")
            row = [slice.email, slice.project_name, slice.session_name, slice.case_name, date_time, slice.category_type_name, slice.image_id, slice.score, slice.labels, slice.options]
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
