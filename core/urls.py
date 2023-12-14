
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('API.urls')),
    path('saml2/', include('djangosaml2.urls'), name="saml2_login"),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)