from django.urls import path
from . import views

app_name = 'bars'

urlpatterns = [
    path('', views.BarListView.as_view(), name='home'),
    path('bar/<uuid:pk>/', views.BarDetailView.as_view(), name='detail'),
    path('add/', views.BarCreateView.as_view(), name='add'),
    path('bar/<uuid:pk>/edit/', views.BarUpdateView.as_view(), name='edit'),
    path('bar/<uuid:pk>/quick-note/', views.quick_note, name='quick_note'),
    path('bar/<uuid:pk>/quick-photo/', views.quick_photo, name='quick_photo'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    path('admin-login/', views.admin_login, name='admin_login'),
]