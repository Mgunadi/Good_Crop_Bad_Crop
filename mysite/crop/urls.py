from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate/', views.generate_mask_from_geojson, name='generate_mask_from_geojson'),
]