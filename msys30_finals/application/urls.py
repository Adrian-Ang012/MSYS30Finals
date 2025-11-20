from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.add_product, name='add_product'),
    path('inventory/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('inventory/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('reorder/', views.reorder_suggestions, name='reorder_suggestions'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('suppliers/edit/<int:pk>/', views.edit_supplier, name='edit_supplier'),
    path('suppliers/delete/<int:pk>/', views.delete_supplier, name='delete_supplier'),

]
