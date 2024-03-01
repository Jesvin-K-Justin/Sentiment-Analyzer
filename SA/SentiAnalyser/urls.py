from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import register_user,user_login
from django.contrib.auth import views as auth_views




urlpatterns = [
    path('', views.home, name='home'),  # Root path
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('about/', views.about, name='about'),
    path('about1/', views.about1, name='about1'),
    path('analyzer/', views.analyzer, name='analyzer'),
    path('display/', views.analyzer, name='display'),
    path('home1/', views.home1, name='home1'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register_user/', register_user, name='register_user'),
    path('user_login/', views.user_login, name='user_login'),
    path('youtube_comments_analyzer/', views.youtube_comments_analyzer, name='youtube_comments_analyzer'),
    path('analyze_content/', views.analyze_content, name='analyze_content'),
    path('delete_row/<int:pk>/', views.delete_row, name='delete_row'),
    path('view_content/<path:url>/', views.view_content, name='view_content'),


]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


