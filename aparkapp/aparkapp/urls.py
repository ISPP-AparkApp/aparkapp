from django.contrib import admin
from django.urls import path,include, re_path
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="AparkApp Backend API",
        default_version='v1',
        description="This is the API to connect AparkApp Frontend and Backend",
        contact=openapi.Contact(email="aparkapp.info@gmail.com"),
    ),
    public=True,
    permission_classes=(AllowAny,),
)

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0),name='schema-swagger-ui'),
    re_path(r'^docs(?P<format>\.json|\.yaml)$',schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),name='schema-redoc'),  
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]