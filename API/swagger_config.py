from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="Image Labeling",
        default_version="v1",
        description="Testing unzip file api and save data of project along with images",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License")
    ),
    public=True,
    url="https://5549-45-117-104-111.ngrok-free.app/",
    permission_classes=(permissions.AllowAny,),
)