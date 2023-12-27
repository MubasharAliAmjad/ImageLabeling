from django.urls import path, include
from . import views
from  rest_framework.routers import DefaultRouter
from .swagger_config import schema_view

router = DefaultRouter()

router.register(r'project', views.ProjectView, basename='project')
router.register(r'unzip', views.UnZipView, basename='unzip')

urlpatterns = [
    path('swagger<str:format>', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),    
    path('', include(router.urls)),
    path('create_session/', views.SessionCreateView.as_view(), name="create_session"),
    path('update_session/<int:pk>/', views.SessionUpdateView.as_view(), name="update_session"),
    path('destroy_session/<int:pk>/', views.SessionDestroyView.as_view(), name="destroy_session"),
    path('read_local/', views.ReadFromLocalView.as_view(), name="read_local"),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path('saml_response/', views.SAMLResponseView.as_view(), name="saml_response"),
    path('export_data/<int:id>/', views.ExportDataview.as_view()),
    path('saml2/login/', views.JsonLoginView.as_view(), name="login"),
    path('saml2/', include('djangosaml2.urls'), name="saml2_login"),
    
]
