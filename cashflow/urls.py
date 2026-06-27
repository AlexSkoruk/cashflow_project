from django.urls import path
from . import views

app_name = 'cashflow'

urlpatterns = [
    # Главная
    path('', views.index, name='index'),
    
    # Записи
    path('record/create/', views.record_create, name='record_create'),
    path('record/edit/<int:pk>/', views.record_edit, name='record_edit'),
    path('record/delete/<int:pk>/', views.record_delete, name='record_delete'),
    
    # AJAX
    path('ajax/categories-by-type/', views.get_categories_by_type, name='get_categories_by_type'),
    path('ajax/subcategories-by-category/', views.get_subcategories_by_category, name='get_subcategories_by_category'),
    
    # Справочники
    path('directories/', views.directory_list, name='directory_list'),  # ← ЭТОТ МАРШРУТ НУЖЕН
    path('directories/status/create/', views.status_create, name='status_create'),
    path('directories/status/edit/<int:pk>/', views.status_edit, name='status_edit'),
    path('directories/status/delete/<int:pk>/', views.status_delete, name='status_delete'),
    path('directories/type/create/', views.type_create, name='type_create'),
    path('directories/type/edit/<int:pk>/', views.type_edit, name='type_edit'),
    path('directories/type/delete/<int:pk>/', views.type_delete, name='type_delete'),
    path('directories/category/create/', views.category_create, name='category_create'),
    path('directories/category/edit/<int:pk>/', views.category_edit, name='category_edit'),
    path('directories/category/delete/<int:pk>/', views.category_delete, name='category_delete'),
    path('directories/subcategory/create/', views.subcategory_create, name='subcategory_create'),
    path('directories/subcategory/edit/<int:pk>/', views.subcategory_edit, name='subcategory_edit'),
    path('directories/subcategory/delete/<int:pk>/', views.subcategory_delete, name='subcategory_delete'),
]