from rest_framework import serializers
from .models import Slice, Image, Category_Type, Labels, Session, Project, Case, Reference_Folder, Options, ZipFile
import uuid
from django.conf import settings
import os, zipfile
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
import random
from django.utils import timezone

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



class  Slice_Fields_Serializer(serializers.Serializer):
    # project_id = serializers.IntegerField(write_only = True)
    case_id = serializers.IntegerField(write_only = True)
    category_type = serializers.IntegerField(write_only = True)
    image_id = serializers.ListField(write_only = True,  child=serializers.IntegerField())
    option = serializers.ListField(write_only = True,  child=serializers.IntegerField())
    options = serializers.ListField(write_only = True)
        

class CaseSerializer(serializers.ModelSerializer):
    category_type = CategoryTypeSerializer(many = True, read_only=True)
    reference_folder = ReferenceFolderSerializer()
    labels = LabelsSerializer(many = True)
    options = OptionsSerializer(many = True, write_only = True, )
    class Meta:
        model = Case
        fields = "__all__"

    def to_representation(self, instance):
        data = super(CaseSerializer, self).to_representation(instance)
        labels = data['labels']
        no_of_rows = data["rows_number"]
        try:
            no_of_item_in_each_row = len(labels)/no_of_rows
            count = 1
            
            labels_list = []
            items_list = []
            for item in labels:
                items_list.append(item)
                
                if count == no_of_item_in_each_row:
                    labels_list.append(items_list)
                    items_list = []
                    count = 0
                count = count + 1

            data['labels'] = labels_list
        except:
            pass

        return data
        

class SessionCreateSerializer(serializers.ModelSerializer):
    case = CaseSerializer(many = True, read_only = True)
    session_id = serializers.IntegerField(write_only = True)
    # slices_data = Slice_Fields_Serializer(many = True, write_only = True)
    # session_name = serializers.CharField(max_length = 200, write_only = True)
    class Meta:
        model = Session
        fields = ["session_id", "session_name", "created_at", "case"]

    
    def create(self, validated_data):
        try:
            session_id = validated_data.pop('session_id')
            session_name = validated_data.pop('session_name')

            existing_session = Session.objects.get(id = session_id)

            new_session = Session.objects.create(session_name = session_name)

            case_list = []
            for case in existing_session.case.all():
                
                category_type_list = []
                for category_type_item in case.category_type.all():
                    category_type = Category_Type.objects.create(category = category_type_item.category, type = category_type_item.type)
                    image_list = []
                    for image in category_type_item.image.all():
                        
                        image_obj = Image(image = image.image)
                        image_obj.save()
                        category_type.image.add(image)

                    option_list = []
                    for option in category_type_item.options.all():
                        option_obj = Options(value = option.value)
                        option_obj.save()
                        option_list.append(option_obj)

                    category_type.options.set(option_list)
                    category_type_list.append(category_type)

                label_list = []
                for label in case.labels.all():
                    label_obj = Labels(value = label.value)
                    label_obj.save()
                    label_list.append(label_obj)

                reference_obj = Reference_Folder.objects.create(reference_name = case.reference_folder.reference_name)
                for image in case.reference_folder.image.all():

                    image_obj = Image(image = image.image)
                    image_obj.save()
                    reference_obj.image.add(image)
                    reference_obj.save()
                
                case_obj = Case.objects.create(case_name = case.case_name, notes = case.notes, cols_number = case.cols_number, rows_number = case.rows_number, reference_folder = reference_obj)
                case_obj.labels.set(label_list)
                case_obj.category_type.set(category_type_list)
                case_obj.save()
                case_list.append(case_obj)

            new_session.case.add(*case_list)

            
            projects_related_to_session = existing_session.project_set.all()
        
            session_list = projects_related_to_session[0].session.all()
            session_list = list(session_list)
            session_list.append(new_session)
            projects_related_to_session[0].session.set(session_list)

            return new_session

        
        except KeyError as e:
            return serializers.ValidationError(f"Field is missing")
        except IndexError as e:
            return serializers.ValidationError("Index out of range")
        except AttributeError as e:
            return serializers.ValidationError(f"AttributeError, raised during assigning of object: {e}")
        except Exception as e:
            return serializers.ValidationError(f"An exception occurred: {e}")
        

class LabelsDataSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    value = serializers.CharField(max_length = 200)
    checked = serializers.BooleanField()
    score = serializers.CharField(max_length = 200)


class SessionUpdateSerializer(serializers.ModelSerializer):
    case = CaseSerializer(many = True, read_only = True)
    slices_data = Slice_Fields_Serializer(many = True, write_only = True, required=False)
    labels = LabelsDataSerializer(many = True, write_only = True, required=False)
    # updated_case_id = serializers.ListField(write_only = True,  child=serializers.IntegerField())
    class Meta:
        model = Session
        fields = ["id", "session_name", "case", "slices_data", "labels"]

    def to_representation(self, instance):
        # Assuming instance is your data
        return {"session": [super().to_representation(instance)]}

    def update(self, instance, validated_data):

        try:
            case_id_list = []
            try:
                slice_data = validated_data.pop("slices_data")
                for slice in slice_data:
                    case_id = slice["case_id"]
                    if case_id not in case_id_list:
                        case_id_list.append(case_id)
                    instance_cases = instance.case.all()
                    for instance_case in instance_cases:
                        
                        if instance_case.id == case_id:
                            instance_categories_types = instance_case.category_type.all()
                            for instance_category_type in instance_categories_types:
                                category_type_id = slice["category_type"]
                                if instance_category_type.id == category_type_id:
                                    for image_id in slice["image_id"]:
                                        validated_image_id = int(image_id)
                                        image_instance = instance_category_type.image.get(id = validated_image_id)
                                        image_instance.checked = True
                                        image_instance.save()
                                    for option in instance_category_type.options.all():
                                        if option.id in slice["option"]:
                                            option.checked = True
                                            option.save()
                                        else:
                                            option.checked = False
                                            option.save()
                                    instance.created_at = timezone.now()
                    
                                    instance.save()
            except: 
                pass

            label_case_id = []
            try:
                label_data = validated_data.pop("labels")
                for label in label_data:
                    instance_obj = Labels.objects.get(id = label["id"])
                    instance_obj.value = label.get("value")
                    instance_obj.checked = label.get("checked")
                    instance_obj.score = label.get("score")
                    instance_obj.save()
                    
                    related_cases = instance_obj.case_set.all()
                    if related_cases[0].id not in label_case_id:
                        label_case_id.append(related_cases[0].id)
            except:
                pass
            
            if len(case_id_list) > 0:
                pass
            else:
                case_id_list = label_case_id
            
            for case in case_id_list:
                case_obj = Case.objects.get(id = case)
                session_projects = instance.project_set.all()
                label_string = ""
                score_string = ""
                score_list = []
                
                no_of_category_type = len(case_obj.category_type.all())
                instance_score_list_size = no_of_category_type * len(case_id_list)
                instance_score_list = ['' for _ in range(instance_score_list_size)]
                label_list = []
                instance_score_index = 0
                
                labels = case_obj.labels.all()
                rows_number = case_obj.rows_number
                cols_number = case_obj.cols_number
                no_of_item_in_each_row = len(labels)/rows_number
                count = 0
                
                for label in labels:
                    if label.checked == True:
                        if not label_string:
                            label_string = label.value
                        else:
                            label_string = label_string + "," + label.value
                    count  += 1

                    if no_of_item_in_each_row == count:
                        for label_index in range(cols_number):
                            label_list.append(label_string)
                        label_string = ""
                        count = 0

                # instance_score_index = 0
                count = 0
                for label in labels:

                    if "-" in label.value:
                        # score_string = instance_score_list[instance_score_index]
                        if label.score == '0':
                            # score_string = label.score
                            pass
                        else:
                            score_string = label.score + ","  + score_string
                    count  += 1
                    if score_string:
                            if score_string.endswith(","):
                                score_string = score_string[:-1]

                    if no_of_item_in_each_row == count:
                        for label_index in range(cols_number):
                            score_list.append(score_string)
                        score_string = ""
                        count = 0

                            # for instance_score_index in range(cols_number):
                            #     score_list.append(score_string)
                            #     instance_score_index = instance_score_index
                                
                            # for index in range(len(score_list) - 2, -1, -1):
                            #     if score_list[index] != "":
                            #         instance_score_index = index + 1
                            #         break
                            
                            # instance_score_index += 1

                            # score_string = ""
                
                for category_type, score, label in zip(case_obj.category_type.all(), score_list, label_list):
                    image_id = ""
                    for image in category_type.image.all():
                        image_id = str(image.id) + "," +  image_id
                    
                    option_string = ""
                    for option in category_type.options.all():
                        if option.checked:
                            option_string = option.value + "," + option_string

                    if option_string.endswith(","):
                                option_string = option_string[:-1]
                    if not option_string == "" or  (score or  not label == "" ):
                        slice_obj = Slice.objects.create(project_name = session_projects[0].project_name, session_name = instance.session_name, case_id = case_obj.id, case_name = case_obj.case_name, category_type_name = f"{category_type.category}_{category_type.type}", image_id = image_id, score = score, labels = label, options = option_string)
                        instance_slices = list(instance.slice.all())
                        instance_slices.append(slice_obj)
                        instance.slice.set(instance_slices)
            

        except KeyError as e:
            field_name = e.args[0] if e.args else 'unknown'
            return serializers.ValidationError(f"Field '{field_name}' is missing")
        except IndexError as e:
            return serializers.ValidationError("Index out of range")
        except AttributeError as e:
            return serializers.ValidationError(f"AttributeError, raised during assigning of object: {e}")
        except Exception as e:
            return serializers.ValidationError(f"An exception occurred: {e}")
            
        return instance
    
class SessionSerializer(serializers.ModelSerializer):
    case = CaseSerializer(many = True, read_only = True)
    slices_data = Slice_Fields_Serializer(many = True, write_only = True)
    class Meta:
        model = Session
        fields = ["id", "session_name", "case", "slices_data"]

class ProjectSerializer(serializers.ModelSerializer):
    zip_folder = serializers.CharField(max_length = 150, write_only = True)
    rows_list = serializers.ListField(max_length = 50, write_only = True)
    columns_list = serializers.ListField(max_length = 50, write_only = True)

    session = SessionSerializer(many = True, read_only = True)
    case = CaseSerializer(many = True, write_only = True)
    
    class Meta:
        model = Project
        fields = ["id", "project_name", "question", "session", "created_at", "zip_folder", "rows_list", "columns_list", "session", "case"]

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

    def find_images(self, case, subfolders_path, file_folder):
        if file_folder in os.listdir(os.path.join(subfolders_path, case)):
            image_folder_path = os.path.join(subfolders_path, case, file_folder)
            list_images = os.listdir(image_folder_path)
            dcm_images = [file for file in list_images if file.lower().endswith('.dcm')]
            return {"list_images": dcm_images, 
                    "image_folder_path": image_folder_path}
                
    def create_category_type(self, case, subfolders_path, file_folder, row_data, column_data, options_data):
        images_and_path = self.find_images(case, subfolders_path, file_folder)
        option_list = []
        if not len(options_data) == 0:
            for option_data in options_data:
                option = Options.objects.create(value=option_data['value'])
                option_list.append(option)
            category_type.options.set(option_list)
        category_type = Category_Type.objects.create(category = row_data, type = column_data)

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
            
            project_name = validated_data.get("project_name")
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
            options_data = case_data_item[0].get('options')

            user_reference_folder = case_data_item[0].get('reference_folder')
            user_reference_folder = user_reference_folder.get("reference_name")

            notes = case_data_item[0].pop('notes')

            session_list = []
            case_list = []
            slice_list = []


            for case in list_cases_in_zip:
                if not os.path.isdir(os.path.join(subfolders_path, case)):
                    continue
                
                label_list = []

                for i in  range(rows_number):
                    for label_data in labels_data:
                        label = Labels.objects.create(value=label_data['value'])
                        label_list.append(label)
                
                
                list_folders_in_zip = self.find_list_folders(subfolders_path)
                images_and_path = self.find_images(case, subfolders_path, user_reference_folder)
                if user_reference_folder:
                    reference_obj = Reference_Folder.objects.create(reference_name = user_reference_folder)
                    for image in images_and_path.get("list_images"):
                        file_path = os.path.join(images_and_path.get("image_folder_path"), image)
                        dicom_file = open(file_path, "rb")
                        image = Image(image=File(dicom_file, name=image))
                        image.save()
                        reference_obj.image.add(image)
                        dicom_file.close()
                if user_reference_folder:              
                    case_obj = Case.objects.create(case_name = case, notes = notes, cols_number = cols_number, rows_number = rows_number, randomize_cases = randomize_cases, randomize_categories = randomize_categories, reference_folder = reference_obj)
                else:
                    case_obj = Case.objects.create(case_name = case, notes = notes, cols_number = cols_number, rows_number = rows_number, randomize_cases = randomize_cases, randomize_categories = randomize_categories)
                if not len(label_list) == 0:
                    case_obj.labels.set(label_list)
                
                category_type_list = []
                for row_data in rows_list:
                    
                    for column_data in  columns_list:
                    
                        if f"{row_data}_{column_data}" in list_folders_in_zip:
                            file_folder = f"{row_data}_{column_data}"
                            category_type = self.create_category_type(case, subfolders_path, file_folder, row_data, column_data, options_data)
                            category_type_list.append(category_type)

                        elif f"{column_data}_{row_data}" in list_folders_in_zip:
                            file_folder = f"{column_data}_{row_data}"
                            category_type = self.create_category_type(case, subfolders_path, file_folder, column_data, row_data, options_data)
                            category_type_list.append(category_type)

                        else:
                            category_type = Category_Type.objects.create(category = column_data, type = row_data)

                            option_list = []
                            if not len(options_data) == 0:
                                for option_data in options_data:
                                    option = Options.objects.create(value=option_data['value'])
                                    option_list.append(option)
                                category_type.options.set(option_list)
                            category_type_list.append(category_type)

                case_obj.category_type.set(category_type_list)
                case_obj.save()
                case_list.append(case_obj)

            # slice_list = []
            # for case in case_list:
            #     for category_type in case.category_type.all():
            #         image_id = ""
            #         for image in category_type.image.all():
            #             image_id = str(image.id) + "," +  image_id
            #         slice_obj = Slice.objects.create(project_name = project_name, session_name = project_name, case_id = case.id, case_name = case.case_name, category_type_name = f"{category_type.category}_{category_type.type}", image_id = image_id, score = 0, labels = "", options = "")
            #         slice_list.append(slice_obj)

            session = Session.objects.create(session_name = project_name)
            # session.slice.set(slice_list)
            session.case.add(*case_list)
            session_list.append(session)
            project = Project.objects.create(**validated_data)
            project.session.set(session_list)

        except KeyError as e:
            field_name = e.args[0] if e.args else 'unknown'
            return serializers.ValidationError(f"Field '{field_name}' is missing")
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
    