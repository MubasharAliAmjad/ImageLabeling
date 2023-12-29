from django.contrib import admin
from .models import Slice, Category_Type, Labels, Session, Project, Image, Case, Options, Reference_Folder, ZipFile, CustomUser
from django.contrib.auth.admin import UserAdmin
# Register your models here.
admin.site.register([Project, Session, Labels, Case, Category_Type, Slice, Image, Reference_Folder, Options, ZipFile, CustomUser])


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email',)
