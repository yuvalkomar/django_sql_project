from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('query_results/', views.query_results, name='query_results'),
    path('add_new_hiker/', views.add_new_hiker, name='add_new_hiker'),
    path('Records_Management/', views.Records_Management, name='Records_Management'),
]
