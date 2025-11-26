"""
URL configuration for facility project.

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

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("register.urls")),
    path("repair_plan/", include("repair_plan.urls")),
    path("repair_plan_simulator/", include("repair_plan_simulator.urls", namespace="repair_plan_simulator")),
    path("repair_plan_cycle/", include("repair_plan_cycle.urls", namespace="repair_plan_cycle")),
    path("parking/", include("parking.urls")),
    path("bicycle/", include("bicycle.urls")),
    path("motorcycle/", include("motorcycle.urls")),
]
