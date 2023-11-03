from django.urls import path, include
from . import views
from  rest_framework.routers import DefaultRouter
from .swagger_config import schema_view

router = DefaultRouter()
router.register(r'image', views.Image_View, basename='image')
# router.register(r'slice', views.Slice_View, basename='slice')
# router.register(r'type', views.Type_View, basename='type')
# router.register(r'category', views.Category_View, basename='category')
# router.register(r'category_type', views.Category_Type_View, basename='category_type')
# router.register(r'labels', views.Labels_View, basename='labels')
# router.register(r'session', views.Session_View, basename='session')
router.register(r'project', views.Project_View, basename='project')
router.register(r'unzip', views.UnZip_View, basename='unzip')

urlpatterns = [
    path('swagger<str:format>', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),    
    path('', include(router.urls)),
    # path('index/', views.index, name="index"),
    # path('dashboard/', views.dashboard, name="dashboard"),
    # path('test/', views.test, name="test"),
    # path('show/', views.show, name="show"),
]
