from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    # Главная страница
    path('', views.home, name='home'),

    # Регистрация и вход
    path('register/user/', views.register_user, name='register_user'),
    path('register/company/', views.register_company, name='register_company'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Профили
    path('profile/', views.profile, name='profile'),
    path('profile/company/<int:company_id>/', views.company_profile, name='company_profile'),

    # Вакансии
    path('vacancies/', views.vacancy_list, name='vacancy_list'),
    path('vacancy/<int:vacancy_id>/', views.vacancy_detail, name='vacancy_detail'),
    path('vacancy/create/', views.create_vacancy, name='create_vacancy'),
    path('vacancy/favorite/', views.favorite_vacancies, name='favorite_vacancies'),
    path('vacancy/favorite/add/<int:vacancy_id>/', views.add_to_favorite, name='add_to_favorite'),
    path('vacancy/favorite/remove/<int:vacancy_id>/', views.remove_from_favorite, name='remove_from_favorite'),

    # Админка (для суперпользователя)
    path('admin/vacancies/', views.admin_vacancy_list, name='admin_vacancy_list'),
    path('admin/vacancy/approve/<int:vacancy_id>/', views.approve_vacancy, name='approve_vacancy'),
    path('admin/vacancy/reject/<int:vacancy_id>/', views.reject_vacancy, name='reject_vacancy'),

    # Чат
    path('chats/', views.chat_list, name='chat_list'),
    path('chat/<int:receiver_id>/', views.chat, name='chat'),

    # Поиск
    path('search/', views.search, name='search'),
    path('chat/<int:receiver_id>/video/', views.video_call, name='video_call'),
    path('resume-builder/', views.resume_builder, name='resume_builder'),
    path('resume/<int:resume_id>/', views.resume_detail, name='resume_detail'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/verify-code/', views.password_reset_verify_code, name='password_reset_verify_code'),
    path('password-reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    path('', include('core.urls')),  # подключите URLs из core

]

# Для обслуживания медиафайлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)