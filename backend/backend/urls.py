"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

# -------------------------------------------------------------------------
# Configura todas os caminhos de urls que podem ser acessadas pelo nosso
# programa.
# (As urls por vês são ligadas a views que são APIs ou sites que podem ser
# acessados.
# -------------------------------------------------------------------------

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.produto.urls"))
]
