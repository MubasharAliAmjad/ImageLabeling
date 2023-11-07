from rest_framework import serializers
from .models import Slice, Image, Category_Type, Labels, Session, Project, Case, Reference_Folder, Options, ZipFile
import uuid
from django.conf import settings
import os, zipfile
from django.core.files import File
from django.core.files.storage import FileSystemStorage
import copy
from django.core.files.storage import default_storage


class Unzip_Serializer(serializers.Serializer):
    uploaded_file = serializers.FileField()

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

    def process_uploaded_file(self):
        try:
            uploaded_file = self.validated_data['uploaded_file']
        except KeyError:
            raise serializers.ValidationError("Uploaded file is required.")

        if uploaded_file.name.endswith('.zip'):
            if ZipFile.objects.exists():
                exist_file = ZipFile.objects.first()
                file = exist_file.uploaded_file
                default_storage.delete(file.name)
                
                exist_file.uploaded_file = uploaded_file
                exist_file.save()
                
            else:
                zip_obj = ZipFile(uploaded_file = uploaded_file)
                zip_obj.save()

            unique_id = str(uuid.uuid4())
            uploaded_file.name = f"{unique_id}_{uploaded_file.name}"

            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                extract_dir = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
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

                return {
                    'categories_types': unique_categories_types_dict,
                    'list_folders': dict_folders,
                    'zip_folder': uploaded_file.name
                }
        else:
            raise serializers.ValidationError("Uploaded file is not zip file.")







class Category_Type_Serializer(serializers.ModelSerializer):
    image_list = serializers.SerializerMethodField()
    class Meta:
        model = Category_Type
        fields = ["category","type", "image_list"]

    def get_image_list(self, obj):
        image_list = obj.image.all().values()
        for image in image_list:
            image['image'] = f"media/{image['image']}"
        return image_list

class Reference_Folder_Serializer(serializers.ModelSerializer):
    image_list =  serializers.SerializerMethodField()
    class Meta:
        model = Reference_Folder
        fields = ["reference_name", "image_list"]

    def get_image_list(self, obj):
        image_list = obj.image.all().values()
        for image in image_list:
            image['image'] = f"media/{image['image']}"
        return image_list
    
class Labels_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Labels
        fields = ["value"]

class Options_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Options
        fields = ["value"]

class Slice_Serializer(serializers.ModelSerializer):
    labels = Labels_Serializer(many = True)
    options = Options_Serializer(many = True)
    class Meta:
        model = Slice
        fields = "__all__"


class Image_Serializer(serializers.ModelSerializer):
    slice = Slice_Serializer()
    class Meta:
        model = Image
        fields = ["image", "slice"]

    def update(self, instance, validated_data):
        import pdb; pdb.set_trace()
        return super().update(instance, validated_data)
        
    def to_representation(self, instance):
        data = super(Image_Serializer, self).to_representation(instance)
        if instance.image:
            data['image'] = f'media/{instance.image.url}'
        return data


class Case_Serializer(serializers.ModelSerializer):
    labels = Labels_Serializer(many = True)
    options = Options_Serializer(many = True)
    category_type = Category_Type_Serializer(many = True, read_only=True)
    reference_folder = Reference_Folder_Serializer()
    class Meta:
        model = Case
        fields = "__all__"
        

class Session_Serializer(serializers.ModelSerializer):
    case = Case_Serializer(many = True)
    # category = Category_Serializer(many = True)
    # type = Type_Serializer(many = True)
    class Meta:
        model = Session
        fields = "__all__"
    

# class Zip_Folder_Serializer(serializers.Serializer):
#     zip_folder = serializers.CharField()

# class Folder_Input_Serializer(serializers.Serializer):
#     # refernece_name = serializers.CharField(max_length = 50)
#     rows_list = serializers.ListField(max_length = 50)
#     columns_list = serializers.ListField(max_length = 50)

class Project_Serializer(serializers.ModelSerializer):
    # folder_names = Folder_Input_Serializer(write_only = True)
    zip_folder = serializers.CharField(max_length = 150, write_only = True)
    # cols_number = serializers.IntegerField()
    # rows_number = serializers.IntegerField()
    rows_list = serializers.ListField(max_length = 50, write_only = True)
    columns_list = serializers.ListField(max_length = 50, write_only = True)
    session = Session_Serializer(many = True, read_only = True)
    case = Case_Serializer(many = True, write_only = True)
    # zip_folder = Zip_Folder_Serializer(write_only = True)
    
    class Meta:
        model = Project
        fields = "__all__"

# overriding methods of serializer is useful when you want to apply logic on particular models

    def find_list_folders(self, subfolders_path):
        list_folders = []
        for case_name in os.listdir(subfolders_path):
                    if os.path.isdir(os.path.join(subfolders_path, case_name)):
                        for file_dir in os.listdir(os.path.join(subfolders_path, case_name)):
                            if file_dir not in list_folders:
                                if os.path.isdir(os.path.join(subfolders_path, case_name, file_dir)):
                                    list_folders.append(file_dir)
        return list_folders

    def find_images(self, list_cases_in_zip, subfolders_path, file_folder):
        for case in list_cases_in_zip:
            if os.path.isdir(os.path.join(subfolders_path, case)):
                if file_folder in os.listdir(os.path.join(subfolders_path, case)):
                    image_folder_path = os.path.join(subfolders_path, case, file_folder)
                    list_images = os.listdir(image_folder_path)
                    return {"list_images": list_images, 
                            "image_folder_path": image_folder_path}


    def create(self, validated_data):
        
        zip_folder = validated_data.pop('zip_folder')
        
        # zip_folder = zip_folder.get("zip_folder")

        # user_list_folders = validated_data.pop('list_folders')
        # user_list_folders = user_list_folders.get('list_folders') 
        # rows_number = validated_data.pop('rows_number')
        # cols_number = validated_data.pop('cols_number')
        rows_list = validated_data.pop('rows_list')
        # rows_list = user_folder_names.get('rows_list') 
        columns_list = validated_data.pop('columns_list') 
        
        
        zip_folder_path = os.path.join(settings.MEDIA_ROOT, zip_folder)
        subfolders_names = os.listdir(zip_folder_path)
        if '__MACOSX' in subfolders_names:
                    subfolders_names.remove('__MACOSX') 
                    
        subfolders_path = os.path.join(zip_folder_path, subfolders_names[0])
        list_cases_in_zip = os.listdir(subfolders_path)
        
        # sessions_data = validated_data.pop('session')
        # session_list = []
        case_data_item = validated_data.pop("case")
        cols_number = case_data_item[0].get('cols_number')
        rows_number = case_data_item[0].get('rows_number')

        labels_data = case_data_item[0].get('labels')
        options_data = case_data_item[0].pop('options')

        user_reference_folder = case_data_item[0].pop('reference_folder')
        user_reference_folder = user_reference_folder.get("reference_name")

        notes = case_data_item[0].pop('notes')
        randomize_cases = case_data_item[0].pop('randomize_cases')
        randomize_categories = case_data_item[0].pop('randomize_categories')


        # import pdb; pdb.set_trace()
        session_list = []
        case_list = []
        label_list = []
        option_list = []
        for case in list_cases_in_zip:
            if not os.path.isdir(os.path.join(subfolders_path, case)):
                continue
            list_folders_in_zip = self.find_list_folders(subfolders_path)
            
            for label_data in labels_data:
                label, _ = Labels.objects.get_or_create(value=label_data['value'])
                label_list.append(label)

            for option_data in options_data:
                option, _ = Options.objects.get_or_create(value=option_data['value'])
                option_list.append(option)

            images_and_path = self.find_images(list_cases_in_zip, subfolders_path, user_reference_folder)
            
            reference_obj = Reference_Folder.objects.create(reference_name = user_reference_folder)
            for image in images_and_path.get("list_images"):
                        file_path = os.path.join(images_and_path.get("image_folder_path"), image)
                        dicom_file = open(file_path, "rb")
                        image = Image(image=File(dicom_file, name=image))
                        image.save()
                        reference_obj.image.add(image)
                        dicom_file.close()
                            
            case_obj = Case.objects.create(case_name = case, notes = notes, cols_number = cols_number, rows_number = rows_number, randomize_cases = randomize_cases, randomize_categories = randomize_categories, reference_folder = reference_obj)

            case_obj.labels.set(label_list)
            case_obj.options.set(option_list)

            category_type_list = []
            for row_data in rows_list:
                for column_data in  columns_list:
                
                    if f"{row_data}_{column_data}" in list_folders_in_zip:
                        file_folder = f"{row_data}_{column_data}"

                        images_and_path = self.find_images(list_cases_in_zip, subfolders_path, file_folder)
                        category_type = Category_Type.objects.create(category = row_data, type = column_data)
                        for image in images_and_path.get("list_images"):
                            file_path = os.path.join(images_and_path.get("image_folder_path"), image)
                            dicom_file = open(file_path, "rb")
                            image = Image(image=File(dicom_file, name=image))
                            image.save()
                            category_type.image.add(image)
                            dicom_file.close()
                            
                        category_type_list.append(category_type)
                    elif f"{column_data}_{row_data}" in list_folders_in_zip:
                        file_folder = f"{column_data}_{row_data}"

                        images_and_path = self.find_images(list_cases_in_zip, subfolders_path, file_folder)
                        category_type = Category_Type.objects.create(category = column_data, type = row_data)

                        for image in images_and_path.get("list_images"):
                            file_path = os.path.join(images_and_path.get("image_folder_path"), image)
                            dicom_file = open(file_path, "rb")
                            image = Image(image=File(dicom_file, name=image))
                            image.save()
                            category_type.image.add(image)
                            dicom_file.close()
                        category_type_list.append(category_type)
                    else:
                        category_type = Category_Type.objects.create(category = column_data, type = row_data)
                        category_type_list.append(category_type)
                    case_obj.category_type.set(category_type_list)
                    case_list.append(case_obj)
            
        session = Session.objects.create()
        
        session.case.add(*case_list)  # Using the 'case' field name
        #session.labels.add(*label_list)  # Using the 'labels' field name
        # session.labels.add(*label_list)

            # for case in case_list:
            #     session.case.add(case)
            
            # for label in label_list:
            #     session.labels.add(label)

        session_list.append(session)
            #session.category.set(category_list)
            #session.type.set(type_list)

        project = Project.objects.create(**validated_data)
        project.session.set(session_list)
        
        def delete_directory(path):
            for root, dirs, files in os.walk(path, topdown=False):
                for file in files:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    os.rmdir(dir_path)

        media_storage = FileSystemStorage(location='media/')


        if media_storage.exists(zip_folder):
            try:
                delete_directory(zip_folder_path)
                media_storage.delete(zip_folder)
                print(f"Folder '{zip_folder}' has been successfully deleted from media.")
            except OSError as e:
                print(f"Error deleting folder: {e}")
        else:
            print(f"Folder '{zip_folder}' does not exist in media.")
            
        return project

    # def update(self, instance, validated_data):
    #     instance.project_name = validated_data.get('project_name', instance.project_name)
    #     instance.question = validated_data.get('question', instance.question)
    #     instance.save()
    #     # You can also update the related session objects in a similar fashion
    #     sessions_data = validated_data.pop('session')
    #     existing_sessions = instance.session.all()        

    #     for session_data_item in sessions_data:
    #         session_id = session_data_item.get('id')
            
    #         if session_id:
    #             session = existing_sessions.get(id=session_id)
    #         else:
    #             continue
            
    #         labels_data = session_data_item.pop('labels')
    #         category_data = session_data_item.pop('category')
    #         type_data = session_data_item.pop('type')
    #         category_type_data = session_data_item.pop('category_type')
    #             # Update session attributes here
    #         # Update related fields for the session
    #         labels = [Labels.objects.get_or_create(value=label_data['value'])[0] for label_data in labels_data]
    #         session.labels.set(labels)

    #         categories = [Category.objects.get_or_create(category_name=category_item['category_name'])[0] for category_item in category_data]
    #         session.category.set(categories)

    #         types = [Type.objects.get_or_create(type_name=type_item['type_name'])[0] for type_item in type_data]
    #         session.type.set(types)

    #         category_types = []
    #         for category_type_item in category_type_data:
    #             slice_data = category_type_item.pop('slice')
    #             slice, _ = Slice.objects.get_or_create(zoom=slice_data['zoom'])
    #             category_type, _ = Category_Type.objects.update_or_create(session=session, slice=slice, defaults=category_type_item)
    #             category_types.append(category_type)


    #     return instance