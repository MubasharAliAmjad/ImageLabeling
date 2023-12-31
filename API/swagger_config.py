from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="Pixel Peek",
        default_version="v1",
        description="DICOM Image Viewer",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License")
    ),
    public=True,
    # url="https://8d24-119-155-3-247.ngrok-free.app/",
    permission_classes=(permissions.AllowAny,),
)