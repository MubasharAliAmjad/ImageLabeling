from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import os
from django.utils import timezone
# Create your models here.

class Labels(models.Model):
    value = models.CharField(max_length=100)
    checked = models.BooleanField(default=False)

    def __str__(self):
        return self.value
    
class ZipFile(models.Model):
    uploaded_file = models.FileField(upload_to="API/ZipFile")

class Options(models.Model):
    value= models.CharField(max_length=100)
    checked = models.BooleanField(default=False)

    def __str__(self):
        return self.value

class Slice(models.Model):
    project_name = models.CharField(max_length=200)
    # session_id = models.PositiveBigIntegerField()
    case_name = models.CharField(max_length=200)
    category_type_name = models.CharField(max_length=200)
    image_id = models.PositiveIntegerField(default=0)
    labels = models.CharField(max_length=500)
    options = models.CharField(max_length=500)
    score = models.IntegerField(default=0)
    # opacity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add = True)
    # options = models.ManyToManyField(Options)
    # labels = models.ManyToManyField(Labels)

class SliceSession(models.Model):
    slice = models.ManyToManyField(Slice)

class Image(models.Model):
    image = models.ImageField(upload_to='API/dicom_images/')

    def __str__(self):
        # f'media/{instance.image.url}'
        return f'media/{self.image.name}'
    
class Reference_Folder(models.Model):
    reference_name = models.CharField(max_length=100)
    image = models.ManyToManyField(Image, blank=True)

    def __str__(self) :
        return self.reference_name



class Category_Type(models.Model):
    category = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    image = models.ManyToManyField(Image, blank=True)
    options = models.ManyToManyField(Options)
    # slice = models.ManyToManyField(Slice,  default=0, blank=True)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.category} _ {self.type}"
    
    
class Case(models.Model):
    case_name = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
    cols_number = models.PositiveIntegerField()
    rows_number =models.PositiveIntegerField()

    category_type = models.ManyToManyField(Category_Type, blank=True)
    labels = models.ManyToManyField(Labels)
    randomize_cases = models.BooleanField(default=False)
    randomize_categories = models.BooleanField(default=False)
    # after removing migrations then change null attribute
    reference_folder = models.ForeignKey(Reference_Folder, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.case_name

class Session(models.Model):
    case = models.ManyToManyField(Case)
    # row_data = models.
    created_at = models.DateTimeField(auto_now_add = True)
    # category = models.ManyToManyField(Category)
    # type = models.ManyToManyField(Type)

    def __str__(self):
        return f"sesion {self.id}"

class Project(models.Model):
    project_name = models.CharField(max_length=255)
    question = models.CharField(max_length=255)
    session = models.ManyToManyField(Session, blank=True)
    created_at = models.DateTimeField(auto_now_add = True)
    sliceSession = models.ManyToManyField(SliceSession, blank=True)

    def __str__(self):
        return self.project_name
    # Folder Reference
    # ref_path = models.CharField(max_length=255)
    # Meaning of layout is not confirmed yet
    # layout = models.CharField(max_length=10)

@receiver(pre_delete, sender = Image)
def delete_image_file(sender, instance, **kwargs):
    # Delete the associated image file
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path) 