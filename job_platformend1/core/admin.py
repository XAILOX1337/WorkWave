from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Company, Vacancy, FavoriteVacancy, ChatMessage,Tag, Resume,Skill,Education,WorkExperience,PortfolioFile

# Расширение стандартной модели User для отображения профиля в админке
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профили пользователей'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    
    
    
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Отображаем имя тега в списке

# Регистрация моделей
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'email', 'phone')
    search_fields = ('user__username', 'full_name', 'email', 'phone')
    list_filter = ('user__is_active',)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('user__is_active',)

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'salary', 'is_approved', 'created_at')
    search_fields = ('title', 'company__name', 'description')
    list_filter = ('is_approved', 'created_at')
    actions = ['approve_vacancies']
    filter_horizontal = ('tags',)

    def approve_vacancies(self, request, queryset):
        queryset.update(is_approved=True)
    approve_vacancies.short_description = "Одобрить выбранные вакансии"

@admin.register(FavoriteVacancy)
class FavoriteVacancyAdmin(admin.ModelAdmin):
    list_display = ('user', 'vacancy', 'added_at')
    search_fields = ('user__username', 'vacancy__title')
    list_filter = ('added_at',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp', 'is_read')
    search_fields = ('sender__username', 'receiver__username', 'message')
    list_filter = ('timestamp', 'is_read')

# Перерегистрация стандартной модели User с кастомной админкой
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)