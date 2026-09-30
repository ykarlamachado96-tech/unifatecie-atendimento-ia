from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/students/", include("apps.students.urls")),
    path("api/support/", include("apps.support.urls")),
    path("api/evaluations/", include("apps.evaluations.urls")),
]
