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
from shutil import copyfile
from django.core.files import File
from django.core.files.base import ContentFile
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
User = get_user_model()



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
    class Meta:
        model = Session
        fields = ["session_id", "session_name","notes", "created_at", "case"]

    
    def create(self, validated_data):
        try:
            
            session_id = validated_data.pop('session_id')
            session_name = validated_data.pop('session_name')

            existing_session = Session.objects.get(id = session_id)

            new_session = Session.objects.create(session_name = session_name, notes = existing_session.notes)

            case_list = []
            for case in existing_session.case.all():
                
                category_type_list = []
                for category_type_item in case.category_type.all():
                    image_list = []
                    category_type = Category_Type.objects.create(category = category_type_item.category, type = category_type_item.type)
                    for image in category_type_item.image.all():
                        
                        with open(image.image.path, 'rb') as file:
                             file_content = file.read()
                        file_name = os.path.basename(image.image.path)
                        unique_id = str(uuid.uuid4())
                        new_name = f"{unique_id}_{file_name}"
                        new_image_object = Image()
                        new_image_object.image.save(new_name, ContentFile(file_content), save=True,)
                        new_image_object.save()
                        image_list.append(new_image_object)
                    category_type.image.set(image_list)
                        

                    if category_type_item.options.all():
                        option_list = []
                        for option in category_type_item.options.all():
                            option_obj = Options(value = option.value)
                            option_obj.save()
                            option_list.append(option_obj)
                        category_type.options.set(option_list)

                    category_type_list.append(category_type)

                if case.labels.all():
                    label_list = []
                    for label in case.labels.all():
                        label_obj = Labels(value = label.value)
                        label_obj.save()
                        label_list.append(label_obj)

                if case.reference_folder:
                    reference_obj = Reference_Folder.objects.create(reference_name = case.reference_folder.reference_name)
                    reference_image_list = []
                    for image in case.reference_folder.image.all():
                        with open(image.image.path, 'rb') as file:
                            file_content = file.read()
                        file_name = os.path.basename(image.image.path)
                        unique_id = str(uuid.uuid4())
                        new_name = f"{unique_id}_{file_name}"
                        new_image_object = Image()
                        new_image_object.image.save(new_name, ContentFile(file_content), save=True,)
                        new_image_object.save()
                        reference_image_list.append(new_image_object)
                    reference_obj.image.set(reference_image_list)
                    reference_obj.save()
                try:
                    case_obj = Case.objects.create(case_name = case.case_name, cols_number = case.cols_number, rows_number = case.rows_number, reference_folder = reference_obj)
                except:
                    case_obj = Case.objects.create(case_name = case.case_name, cols_number = case.cols_number, rows_number = case.rows_number)
                try:
                    case_obj.labels.set(label_list)
                except:
                    pass
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

        except Exception as e:
            raise serializers.ValidationError({'error_message': str(e)})
        
        

class LabelsDataSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    value = serializers.CharField()
    checked = serializers.BooleanField()
    score = serializers.CharField(max_length = 20)


class SessionUpdateSerializer(serializers.ModelSerializer):
    case = CaseSerializer(many = True, read_only = True)
    slices_data = Slice_Fields_Serializer(many = True, write_only = True, required=False)
    labels = LabelsDataSerializer(many = True, write_only = True, required=False)

    class Meta:
        model = Session
        fields = ["id", "session_name", "notes", "case", "slices_data", "labels"]


    def get_project_question(self, instance):
        
        session_projects = instance.project_set.all()
        return session_projects[0].question

    def to_representation(self, instance):
        # if instance.case.first().randomize_categories:
        #     
        #     categories_types = instance.case.first().category_type.all()
        #     cols_number = instance.case.first().cols_number
        #     rows_number = instance.case.first().rows_number

        #     rows = [categories_types[i * cols_number:(i + 1) * cols_number] for i in range(rows_number)]

        #     # Shuffle the order of category_type instances in each row
        #     for row in rows:
        #         
        #         random.shuffle(row)

        #     # Flatten the shuffled rows back into a single list
        #     shuffled_categories_types = [item for sublist in rows for item in sublist]
        #     # for i in range(0, cols_number):
        # else:
        return {"session": [super().to_representation(instance)],
            "question": self.get_project_question(instance)}    

    def update(self, instance, validated_data):
        try:
            case_id_list = []
            image_index_list = []
            try:
                slice_data = validated_data.pop("slices_data")
                for slice in slice_data:
                    try:
                        image_index_list.append(slice.get("image_id")[0])
                    except:
                        image_index_list.append(-1)
                    
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

                count = 0
                for label in labels:

                    if "-" in label.value:
                        if label.score == '0':
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
                
                if not score_list and not label_list:
                    for index, category_type in enumerate(case_obj.category_type.all()):
                        image_id = str(image_index_list[index])
                        option_string = ""
                        for option in category_type.options.all():
                            if option.checked:
                                option_string = option.value + "," + option_string
                                if option_string.endswith(","):
                                    option_string = option_string[:-1]
                                if image_id == "-1":
                                    slice_obj = Slice.objects.create(email = session_projects[0].user.email, project_name = session_projects[0].project_name, session_name = instance.session_name, case_id = case_obj.id, case_name = case_obj.case_name, category_type_name = f"{category_type.category}_{category_type.type}", score = "", labels = "", options = option_string)
                                else:
                                    slice_obj = Slice.objects.create(email = session_projects[0].user.email, project_name = session_projects[0].project_name, session_name = instance.session_name, case_id = case_obj.id, case_name = case_obj.case_name, category_type_name = f"{category_type.category}_{category_type.type}", image_id = image_id, score = "", labels = "", options = option_string)

                        instance_slices = list(instance.slice.all())
                        instance_slices.append(slice_obj)
                        instance.slice.set(instance_slices)
                for index, (category_type, score, label) in enumerate(zip(case_obj.category_type.all(), score_list, label_list)):
                    
                    image_id = str(image_index_list[index])
                    
                    option_string = ""
                    for option in category_type.options.all():
                        if option.checked:
                            option_string = option.value + "," + option_string
                    if option_string.endswith(","):
                        option_string = option_string[:-1]
                    if not option_string == "" or  (score or  not label == "" ):
                        if image_id == "-1":
                            slice_obj = Slice.objects.create(email = session_projects[0].user.email, project_name = session_projects[0].project_name, session_name = instance.session_name, case_id = case_obj.id, case_name = case_obj.case_name, category_type_name = f"{category_type.category}_{category_type.type}", score = score, labels = label, options = option_string)
                        else:
                            slice_obj = Slice.objects.create(email = session_projects[0].user.email, project_name = session_projects[0].project_name, session_name = instance.session_name, case_id = case_obj.id, case_name = case_obj.case_name, category_type_name = f"{category_type.category}_{category_type.type}", image_id = image_id, score = score, labels = label, options = option_string)

                        instance_slices = list(instance.slice.all())
                        instance_slices.append(slice_obj)
                        instance.slice.set(instance_slices)
            

        except Exception as e:
            raise serializers.ValidationError({'error_message': str(e)})
            
        return instance
    
class SessionSerializer(serializers.ModelSerializer):
    case = CaseSerializer(many = True, read_only = True)
    slices_data = Slice_Fields_Serializer(many = True, write_only = True)
    class Meta:
        model = Session
        fields = ["id", "session_name","notes", "case", "slices_data"]

class ProjectSerializer(serializers.ModelSerializer):
    zip_folder = serializers.CharField(write_only = True)
    rows_list = serializers.ListField(write_only = True)
    columns_list = serializers.ListField(write_only = True)
    notes = serializers.CharField(write_only = True)

    session = SessionSerializer(many = True, read_only = True)
    case = CaseSerializer(many = True, write_only = True)

    class Meta:
        model = Project
        fields = ["id", "project_name", "question", "session", "created_at", "zip_folder", "rows_list", "columns_list", "notes", "session", "case"]

    # def to_representation(self, instance):
    #     if instance.session.first().case.first().randomize_categories:
    #         categories_types = instance.session.first().case.first().category_type.all()
    #         cols_number = instance.session.first().case.first().cols_number
    #         rows_number = instance.session.first().case.first().rows_number

    #         rows = [categories_types[i * cols_number:(i + 1) * cols_number] for i in range(rows_number)]

    #         # Shuffle the order of category_type instances in each row
    #         
    #         for i, row in enumerate(rows):
    #             row_list = list(row)
    #             row_copy = row_list.copy()
    #             count = 0
    #             while row_list == row_copy and count < 5:
    #                 random.shuffle(row_list)
    #                 count += 1
    #             rows[i] = row_list
    #         plane_list = [item for sublist in rows for item in sublist]
    #         
                
                

    #         # Flatten the shuffled rows back into a single list
    #         # shuffled_categories_types = [item for sublist in rows for item in sublist]
    #         instance.session.first().case.first().category_type.set(plane_list)
    #         # for i in range(0, cols_number):
    #     
    #     return super().to_representation(instance)



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
        category_type = Category_Type.objects.create(category = row_data, type = column_data)
        if not len(options_data) == 0:
            for option_data in options_data:
                option = Options.objects.create(value=option_data['value'])
                option_list.append(option)
            category_type.options.set(option_list)

        image_list = []
        for image in images_and_path.get("list_images"):
            file_path = os.path.join(images_and_path.get("image_folder_path"), image)
            dicom_file = open(file_path, "rb")
            image = Image(image=File(dicom_file, name=image))
            image.save()
            dicom_file.close()
            image_list.append(image)
        category_type.image.set(image_list)
        category_type.save()
        return category_type

    def shuffle_rows_columns(self, rows_list, columns_list, subfolders_path):
        unzip_serializer = UnzipSerializer()
        category_type_folder_list = unzip_serializer.find_category_type_folders(subfolders_path)
        category_row_list = []
        category_column_list = []
        for category_type in category_type_folder_list:
            if not '_' in category_type:
                continue
            category, type = category_type.split('_')
            if category in rows_list:
                category_row_list.append(category)
            if category in columns_list:
                category_column_list.append(category)

        category_row_list = set(category_row_list)
        category_column_list = set(category_column_list)
        # Extract the category elements from both lists
        category_elements_rows = [category for category in rows_list if category in category_row_list]
        category_elements_columns = [category for category in columns_list if category in category_column_list]

        # Shuffle the category elements (using a copy to avoid modifying the original lists)
        shuffled_category_elements_rows = category_elements_rows.copy()
        shuffled_category_elements_columns = category_elements_columns.copy()
                
        count = 0
        # 
        while shuffled_category_elements_rows == category_elements_rows and count < 5:
            random.shuffle(shuffled_category_elements_rows)
            count += 1
        count = 0
        while shuffled_category_elements_columns == category_elements_columns and count < 5:
            random.shuffle(shuffled_category_elements_columns)
            count += 1

        # Replace the shuffled category elements in the original lists
        rows_list = [category if category not in category_row_list else shuffled_category_elements_rows.pop(0) for category in rows_list]
        columns_list = [category if category not in category_column_list else shuffled_category_elements_columns.pop(0) for category in columns_list]
        return rows_list, columns_list

    

    def create(self, validated_data):
        token = self.context.get('token')
        try:
            token = RefreshToken(token)
            user_id = token['user_id']
        except Exception as e:
            raise serializers.ValidationError({'error_message': 'Invalid token'})
        
        try:
            project_name = validated_data.get("project_name")
            zip_folder = validated_data.pop('zip_folder')
            columns_list = validated_data.pop('rows_list')
            rows_list= validated_data.pop('columns_list') 
            case_data_item = validated_data.pop("case")
        except Exception as e:
            raise serializers.ValidationError({'error_message': str(e)})
        
        try:
            zip_folder_path = os.path.join(settings.MEDIA_ROOT, zip_folder)
            subfolders_names = os.listdir(zip_folder_path)
            if '__MACOSX' in subfolders_names:
                        subfolders_names.remove('__MACOSX') 
                        
            subfolders_path = os.path.join(zip_folder_path, subfolders_names[0])
            list_cases_in_zip = os.listdir(subfolders_path)
        
            randomize_cases = case_data_item[0].pop('randomize_cases')
            randomize_categories = case_data_item[0].pop('randomize_categories')

            if randomize_cases:
                count = 0
                copy_list_cases_in_zip = list_cases_in_zip.copy()
                while list_cases_in_zip == copy_list_cases_in_zip and count < 5:
                    random.shuffle(list_cases_in_zip)
                    count += 1
            
            # if randomize_categories:
            
                
            
            cols_number = case_data_item[0].get('cols_number')
            rows_number = case_data_item[0].get('rows_number')
            
            labels_data = case_data_item[0].get('labels')
            options_data = case_data_item[0].get('options')

            user_reference_folder = case_data_item[0].get('reference_folder')
            user_reference_folder = user_reference_folder.get("reference_name")
            
            notes = validated_data.get("notes")

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
                    case_obj = Case.objects.create(case_name = case, cols_number = cols_number, rows_number = rows_number, randomize_cases = randomize_cases, randomize_categories = randomize_categories, reference_folder = reference_obj)
                else:
                    case_obj = Case.objects.create(case_name = case, cols_number = cols_number, rows_number = rows_number, randomize_cases = randomize_cases, randomize_categories = randomize_categories)
                if not len(label_list) == 0:
                    case_obj.labels.set(label_list)
                
                category_type_list = []
                if randomize_categories:
                    
                    rows_list, columns_list = self.shuffle_rows_columns(rows_list, columns_list, subfolders_path)
                    
                    for column_data in columns_list:
                        for row_data in  rows_list:
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
                            
                        rows_list, columns_list = self.shuffle_rows_columns(rows_list, columns_list, subfolders_path)
                else:
                    for column_data in columns_list:
                        for row_data in  rows_list:
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
            session = Session.objects.create(session_name = project_name, notes = notes)
            session.case.add(*case_list)
            session_list.append(session)
            
            user = User.objects.get(id = user_id)
            project = Project.objects.create(user = user, project_name = project_name, question = validated_data.get("question"))
        
            project.session.set(session_list)
        
        except Exception as e:
            raise serializers.ValidationError({'error_message': str(e)})
        
        
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
            except Exception as e:
                raise serializers.ValidationError({'error_message': str(e)})
        else:
            print(f"Folder '{zip_folder}' does not exist in media.")
            
        return project
    