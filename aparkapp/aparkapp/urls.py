from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="AparkApp Backend API",
        default_version='v1',
        description="API to connect AparkApp Backend and Frontend",
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
