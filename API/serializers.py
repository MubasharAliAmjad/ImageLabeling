from rest_framework import serializers
from .models import Slice, Image, Category_Type, Labels, Session, Project, Case, Reference_Folder, Options, ZipFile, SliceSession
import uuid
from django.conf import settings
import os, zipfile
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
import random


class UnzipSerializer(serializers.Serializer):
    uploaded_file = serializers.FileField()

    def find_category_type_folders(self, subfolders_path):
        list_file_dir = []
        for case_name in os.listdir(subfolders_path):
                    if os.path.isdir(os.path.join(subfolders_path, case_name)):
                        for file_dir in os.listdir(os.path.join(subfolders_path, case_name)):
                            if file_dir not in list_file_dir:
                                if os.path.isdir(os.path.join(subfolders_path, case_name, file_dir)):
                                    list_file_dir.append(file_dir)
        return list_file_dir
    
    def find_categories_types_dict(self, category_type_folder_list):
        unique_categories_and_types = []
        categoroes_and_types_dict = []
        for folder in category_type_folder_list:
            try:
                category, type = folder.split('_')
            except:
                continue
            if category not in unique_categories_and_types:
                unique_categories_and_types.append(category)
            if type not in unique_categories_and_types:
                unique_categories_and_types.append(type)

        for index, value in enumerate(unique_categories_and_types, start=1):
            item_category = {"id": str(index), "value": value}
            categoroes_and_types_dict.append(item_category)
        return categoroes_and_types_dict

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

                for subfolder in subfolders_names:
                    if os.path.isdir(os.path.join(extract_dir, subfolder)):
                        subfolders_path = os.path.join(extract_dir, subfolder)
                
                category_type_folder_list = self.find_category_type_folders(subfolders_path)
                
                unique_categories_types_dict = self.find_categories_types_dict(category_type_folder_list)
                    
                category_type_folder_dict = []
                for index, folder in enumerate(category_type_folder_list, start=1):
                    item = {"id": str(index), "value": folder}
                    category_type_folder_dict.append(item)

                return {
                    'categories_types': unique_categories_types_dict,
                    'list_folders': category_type_folder_dict,
                    'zip_folder': uploaded_file.name
                }
        else:
            raise serializers.ValidationError("Uploaded file is not the Zip file.")



class LabelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Labels
        fields = "__all__"

class OptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Options
        fields = "__all__"



class CategoryTypeSerializer(serializers.ModelSerializer):
    image_list = serializers.SerializerMethodField()
    labels = LabelsSerializer(many = True, read_only = True)
    options = OptionsSerializer(many = True, read_only = True)
    class Meta:
        model = Category_Type
        fields = "__all__"

    def get_image_list(self, obj):
        image_list = obj.image.all().values()
        for image in image_list:
            image['image'] = f"media/{image['image']}"
            
        return image_list

class ReferenceFolderSerializer(serializers.ModelSerializer):
    image_list =  serializers.SerializerMethodField()
    class Meta:
        model = Reference_Folder
        fields = ["reference_name", "image_list"]

    def get_image_list(self, obj):
        image_list = obj.image.all().values()
        for image in image_list:
            image['image'] = f"media/{image['image']}"
        return image_list
    




class CategoryTypeItemSerializer(serializers.Serializer):
    obj_id = serializers.IntegerField()
    slice = serializers.IntegerField()
    zoom_level = serializers.IntegerField()
    options = OptionsSerializer(many = True, write_only = True)
    labels = LabelsSerializer(many = True)

class Slice_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Slice
        fields = "__all__"

class  Slice_Fields_Serializer(serializers.Serializer):
    project_id = serializers.IntegerField(write_only = True)
    case_id = serializers.IntegerField(write_only = True)
    category_type = serializers.IntegerField(write_only = True)
    image_id = serializers.IntegerField(write_only = True)
    labels = serializers.ListField(write_only = True)
    options = serializers.ListField(write_only = True)
    score = serializers.IntegerField(write_only = True)
        

class CustomSliceSerializer(serializers.Serializer):
    slices = Slice_Serializer(many = True, read_only = True)
    slices_data = Slice_Fields_Serializer(many = True, write_only = True)
    
    
    def create(self, validated_data):
        try:
            slices = validated_data.pop("slices_data")
            session_obj = SliceSession.objects.create()
            project_obj = Project.objects.get(id = slices[0]["project_id"])
            slice_list = []
            for slice in slices:

                options = ""
                for option in slice["options"]:
                    options = option + "," + options
                    
                labels = ""
                for label in slice["labels"]:
                    labels = label + "," + labels
                
                project_obj = Project.objects.get(id = slice["project_id"])
                case_obj = Case.objects.get(id = slice["case_id"])
                category_type_obj = Category_Type.objects.get(id = slice["category_type"])
                category_type_name = f"{category_type_obj.category}_{category_type_obj.type}"

                slice_obj = Slice.objects.create(project_name = project_obj.project_name, case_name = case_obj.case_name, category_type_name = category_type_name, image_id = slice["image_id"], labels = labels, options = options, score = slice["score"])
                slice_list.append(slice_obj)
            
            session_list = project_obj.sliceSession.all()
            session_list = list(session_list)
            session_obj.slice.set(slice_list)
            session_obj.save()
            session_list.append(session_obj)
            
            project_obj.sliceSession.set(session_list)
        
        except KeyError as e:
            return serializers.ValidationError(f"Field '{e.args[0]}' is missing")
        except IndexError as e:
            return serializers.ValidationError("Index out of range")
        except AttributeError as e:
            return serializers.ValidationError(f"AttributeError, raised during assigning of object: {e}")
        except Exception as e:
            return serializers.ValidationError(f"An exception occurred: {e}")
        
        return session_obj
    

class CaseSerializer(serializers.ModelSerializer):
    category_type = CategoryTypeSerializer(many = True, read_only=True)
    reference_folder = ReferenceFolderSerializer()
    labels = LabelsSerializer(many = True)
    options = OptionsSerializer(many = True, write_only = True)
    class Meta:
        model = Case
        fields = "__all__"
        

class Session_Serializer(serializers.ModelSerializer):
    case = CaseSerializer(many = True)
    class Meta:
        model = Session
        fields = "__all__"
    


class ProjectSerializer(serializers.ModelSerializer):
    zip_folder = serializers.CharField(max_length = 150, write_only = True)
    rows_list = serializers.ListField(max_length = 50, write_only = True)
    columns_list = serializers.ListField(max_length = 50, write_only = True)
    session = Session_Serializer(many = True, read_only = True)
    case = CaseSerializer(many = True, write_only = True)
    
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
                                    import pdb; pdb.set_trace
        return list_folders

    def find_images(self, list_cases_in_zip, subfolders_path, file_folder):
        for case in list_cases_in_zip:
            if os.path.isdir(os.path.join(subfolders_path, case)):
                if file_folder in os.listdir(os.path.join(subfolders_path, case)):
                    image_folder_path = os.path.join(subfolders_path, case, file_folder)
                    list_images = os.listdir(image_folder_path)
                    return {"list_images": list_images, 
                            "image_folder_path": image_folder_path}
                
    def create_category_type(self, list_cases_in_zip, subfolders_path, file_folder, row_data, column_data, option_list):
        images_and_path = self.find_images(list_cases_in_zip, subfolders_path, file_folder)
        category_type = Category_Type.objects.create(category = row_data, type = column_data)
        category_type.options.set(option_list)

        for image in images_and_path.get("list_images"):
            file_path = os.path.join(images_and_path.get("image_folder_path"), image)
            dicom_file = open(file_path, "rb")
            image = Image(image=File(dicom_file, name=image))
            image.save()
            category_type.image.add(image)
            dicom_file.close()
        return category_type


    def create(self, validated_data):
        try:
            zip_folder = validated_data.pop('zip_folder')
            rows_list = validated_data.pop('rows_list')
            columns_list = validated_data.pop('columns_list') 
            case_data_item = validated_data.pop("case")
        
            zip_folder_path = os.path.join(settings.MEDIA_ROOT, zip_folder)
            subfolders_names = os.listdir(zip_folder_path)
            if '__MACOSX' in subfolders_names:
                        subfolders_names.remove('__MACOSX') 
                        
            subfolders_path = os.path.join(zip_folder_path, subfolders_names[0])
            list_cases_in_zip = os.listdir(subfolders_path)
        
            randomize_cases = case_data_item[0].pop('randomize_cases')
            randomize_categories = case_data_item[0].pop('randomize_categories')
            if randomize_cases:
                random.shuffle(list_cases_in_zip)
            if randomize_categories:
                random.shuffle(rows_list)
                random.shuffle(columns_list)

            
            cols_number = case_data_item[0].get('cols_number')
            rows_number = case_data_item[0].get('rows_number')

            labels_data = case_data_item[0].get('labels')
            options_data = case_data_item[0].pop('options')

            user_reference_folder = case_data_item[0].pop('reference_folder')
            user_reference_folder = user_reference_folder.get("reference_name")

            notes = case_data_item[0].pop('notes')

            session_list = []
            case_list = []
            label_list = []
            option_list = []

            for label_data in labels_data:
                    label, _ = Labels.objects.get_or_create(value=label_data['value'])
                    label_list.append(label)

            for option_data in options_data:
                option, _ = Options.objects.get_or_create(value=option_data['value'])
                option_list.append(option)

            for case in list_cases_in_zip:
                if not os.path.isdir(os.path.join(subfolders_path, case)):
                    continue

                list_folders_in_zip = self.find_list_folders(subfolders_path)
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
                
                category_type_list = []
                for row_data in rows_list:
                    for column_data in  columns_list:
                    
                        if f"{row_data}_{column_data}" in list_folders_in_zip:
                            file_folder = f"{row_data}_{column_data}"
                            category_type = self.create_category_type(list_cases_in_zip, subfolders_path, file_folder, row_data, column_data, option_list)
                            category_type_list.append(category_type)

                        elif f"{column_data}_{row_data}" in list_folders_in_zip:
                            file_folder = f"{column_data}_{row_data}"
                            category_type = self.create_category_type(list_cases_in_zip, subfolders_path, file_folder, column_data, row_data, option_list)
                            category_type_list.append(category_type)

                        else:
                            category_type = Category_Type.objects.create(category = column_data, type = row_data)
                            category_type.options.set(option_list)
                            category_type_list.append(category_type)

                        case_obj.category_type.set(category_type_list)
                        case_obj.save()
                        case_list.append(case_obj)
        
            session = Session.objects.create()
            session.case.add(*case_list)
            session_list.append(session)
            project = Project.objects.create(**validated_data)
            project.session.set(session_list)

        except KeyError as e:
            return serializers.ValidationError(f"Field '{e.args[0]}' is missing")
        except IndexError as e:
            return serializers.ValidationError("Index out of range")
        except AttributeError as e:
            return serializers.ValidationError(f"AttributeError, raised during assigning of object: {e}")
        except Exception as e:
            return serializers.ValidationError(f"An exception occurred: {e}")
        
        
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