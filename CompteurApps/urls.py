from django.contrib import admin
from django.urls import path, include, re_path
from .views import AlertEpViewSet



urlpatterns = [
    path('admin/', admin.site.urls),

    # path('', AlertEpViewSet.as_view({'get': 'list'}), name="alerte-ep"),
]