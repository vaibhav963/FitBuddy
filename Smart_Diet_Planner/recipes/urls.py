from django.urls import path
from . import views

urlpatterns = [
    path('detail/<int:pk>/', views.recipe_view, name='recipe_detail'),
    path('by-diet/', views.recipes_by_diet, name='recipes_by_diet'),
    path('', views.recipes_by_diet, name='recipes_home'),
]