from django.urls import path
from . import views

urlpatterns = [
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
    path('profile/<int:user_id>/', views.profile, name='profile'),

    # Вакансии
    path('vacancies/', views.vacancy_list, name='vacancy_list'),
    path('vacancy/<int:vacancy_id>/', views.vacancy_detail, name='vacancy_detail'),
    path('vacancy/create/', views.create_vacancy, name='create_vacancy'),
    path('vacancy/favorite/', views.favorite_vacancies, name='favorite_vacancies'),
    path('vacancy/favorite/add/<int:vacancy_id>/', views.add_to_favorite, name='add_to_favorite'),
    path('vacancy/favorite/remove/<int:vacancy_id>/', views.remove_from_favorite, name='remove_from_favorite'),
    path('vacancy/<int:vacancy_id>/apply/', views.apply_for_vacancy, name='apply_for_vacancy'),
    
    
    # Админка (для суперпользователя)
    path('admin/vacancies/', views.admin_vacancy_list, name='admin_vacancy_list'),
    path('admin/vacancy/approve/<int:vacancy_id>/', views.approve_vacancy, name='approve_vacancy'),
    path('admin/vacancy/reject/<int:vacancy_id>/', views.reject_vacancy, name='reject_vacancy'),

    # Чат
    path('chats/', views.chat_list, name='chat_list'),
    path('chat/<int:receiver_id>/', views.chat, name='chat'),

    # Поиск
    path('search/', views.search, name='search'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('chat/<int:receiver_id>/video/', views.video_call, name='video_call'),
    
    path('resume/<int:resume_id>/', views.resume_detail, name='resume_detail'),
    path('resume-builder/', views.resume_builder, name='resume_builder'),
    path('resume/edit/', views.edit_resume, name='edit_resume'),
    path('politics/', views.politics, name='politics'),
    path('conf/', views.conf, name='conf'),
    path('personal_data/', views.personal_data, name='personal_data'),
    path('vacancy/edit/<int:vacancy_id>/', views.edit_vacancy, name='edit_vacancy'),
    path('answers/', views.answers, name='answers'),
    path('video_call/<int:receiver_id>/', views.video_call, name='video_call'),

    path('resume/edit/<int:resume_id>/', views.edit_resume, name='edit_resume'),
    path('resume/delete/<int:resume_id>/', views.delete_resume, name='delete_resume'),
    path('vacancy/delete/<int:vacancy_id>/', views.delete_vacancy, name='delete_vacancy'),
]