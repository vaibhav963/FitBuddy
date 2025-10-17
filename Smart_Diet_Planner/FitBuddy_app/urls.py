from django.urls import path
from . import views


urlpatterns = [
    path('',views.home,name = 'home'),
    path('login/',views.login,name = 'login'),
    path('About/',views.about,name = 'about'),
    path('Contact/',views.contact,name = 'contact'),
    path('logout/',views.logout_view,name='logout'),
    path('form/', views.form, name='form'),
    path('welcome/', views.welcome, name='welcome'),
    path('plan/', views.plan, name='plan'),
    path('policy/', views.policy, name='policy'),
    path('terms/', views.terms, name='terms'),
    path('roadmap/', views.roadmap, name='roadmap'),
    path('feature/', views.features, name='features'),
    path('recipe-query/', views.recipe_query, name='recipe-query'),
    path('save-profile/', views.save_profile, name='save_profile'),
    path('ai-meal-planner/', views.ai_meal_planner, name='ai_meal_planner'),
    path('meal-recipe-detail/<str:recipe_name>/', views.meal_plan_recipe_detail, name='meal_recipe_detail'),
    path('test-ai-setup/', views.test_ai_setup, name='test_ai_setup'),
    
    # Meal Logging URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-meal/', views.add_meal_log, name='add_meal_log'),
    path('quick-add-meal/', views.quick_add_meal, name='quick_add_meal'),
    path('edit-meal/<int:log_id>/', views.edit_meal_log, name='edit_meal_log'),
    path('delete-meal/<int:log_id>/', views.delete_meal_log, name='delete_meal_log'),
    path('meal-history/', views.meal_history, name='meal_history'),

]