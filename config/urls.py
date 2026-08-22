from django.contrib import admin
from django.urls import include, path

from core.views import health

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", health, name="health"),
    path("health/", health, name="health-slash"),
    path("api/v1/", include("commerce.urls")),
    path("api/v1/", include("core.urls")),
]
