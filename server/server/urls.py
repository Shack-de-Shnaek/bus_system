"""
URL configuration for server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from django.urls import path

# import admin urls
from django.contrib import admin

from main.views import index, pay_ride, refill, register

urlpatterns = [
    path("admin/", admin.site.urls),
    path("pay/<str:card_id>/<str:bus_line>/", pay_ride, name="pay"),
    path("refill/<str:card_id>/", refill, name="refill"),
    path("register/", register, name="register"),
    path("", index, name="index"),
]
