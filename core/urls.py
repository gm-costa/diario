from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('diario/', include('diario.urls')),
    path('', lambda request: redirect('diario'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
