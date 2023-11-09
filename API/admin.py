from django.contrib import admin
from .models import Slice, Category_Type, Labels, Session, Project, Image, Case, Options, Reference_Folder, SliceSession, ZipFile

# Register your models here.
admin.site.register([Project, Session, Labels, Case, Category_Type, Slice, Image, Reference_Folder, Options, SliceSession, ZipFile])