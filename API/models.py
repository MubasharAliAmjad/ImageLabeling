from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import os
from django.utils import timezone
# Create your models here.

class Labels(models.Model):
    value = models.CharField(max_length=100, null=True)
    checked = models.BooleanField(default=False)
    score = models.CharField(max_length=20)

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
    case_name = models.CharField(max_length=200)
    category_type_name = models.CharField(max_length=200)
    image_id = models.PositiveIntegerField(default=0)
    labels = models.CharField(max_length=500)
    options = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add = True)


class Image(models.Model):
    image = models.ImageField(upload_to='API/dicom_images/')
    checked = models.BooleanField(default=False)

    def __str__(self):
        # f'media/{instance.image.url}'
        return f'media/{self.image.name}'
    
class Reference_Folder(models.Model):
    reference_name = models.CharField(max_length=100)
    image = models.ManyToManyField(Image, blank=True)

    def __str__(self) :
        return self.reference_name
    
    def clone(self):
        new_folder = Reference_Folder(reference_name=self.reference_name)
        new_folder.save()

        # Clone and add associated images to the new folder
        for image in self.image.all():
            new_image = Image.objects.create(image  = image.image)
            new_folder.image.add(new_image)

        return new_folder
    


class Category_Type(models.Model):
    category = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    image = models.ManyToManyField(Image, blank=True)
    options = models.ManyToManyField(Options)
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
    reference_folder = models.ForeignKey(Reference_Folder, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.case_name

class Session(models.Model):
    case = models.ManyToManyField(Case)
    session_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"sesion {self.id}"

class Project(models.Model):
    project_name = models.CharField(max_length=255)
    question = models.CharField(max_length=255)
    session = models.ManyToManyField(Session, blank=True)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.project_name

@receiver(pre_delete, sender = Image)
def delete_image_file(sender, instance, **kwargs):
    # Delete the associated image file
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path) 