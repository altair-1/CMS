from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('content/', views.content_list, name='content_list'),
    path('create/', views.create_content, name='create_content'),
    path('content/<slug:slug>/', views.content_detail, name='content_detail'),
    path('content/<slug:slug>/edit/', views.edit_content, name='edit_content'),
    path('content/<slug:slug>/delete/', views.delete_content, name='delete_content'),
    path('content/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('profile/', views.user_profile, name='user_profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
]