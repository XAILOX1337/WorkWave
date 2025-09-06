from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import random
import string

# Модель UserProfile
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    full_name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True)
    birth_date = models.DateField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username
    
    def is_user(self):
        return True  # Это пользователь    
    
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# Модель Company
class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company')
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='company_photos/', null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True)
    bio = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    def is_company(self):
        return True  # Это компания    

# Модель Vacancy
class Vacancy(models.Model):
    EXPERIENCE_CHOICES = [
        ('no_experience', 'Нет опыта'),
        ('1_3', 'От 1 года до 3 лет'),
        ('3_6', 'От 3 до 6 лет'),
        ('6_plus', 'Более 6 лет'),
        ('any', 'Не имеет значения'),
    ]
    
    EMPLOYMENT_CHOICES = [
        ('full', 'Полная занятость'),
        ('part', 'Частичная занятость'),
        ('project', 'Проектная работа/разовое задание'),
        ('volunteer', 'Волонтерство'),
    ]
    
    EDUCATION_CHOICES = [
        ('none', 'Не требуется'),
        ('secondary', 'Среднее профессиональное'),
        ('higher', 'Высшее'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='vacancies')
    title = models.CharField(max_length=255, verbose_name='Название вакансии')
    salary = models.PositiveIntegerField(verbose_name='Заработная плата')
    experience = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default='any',
        verbose_name='Требуемый опыт'
    )
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_CHOICES,
        default='full',
        verbose_name='Тип занятости'
    )
    education = models.CharField(
        max_length=20,
        choices=EDUCATION_CHOICES,
        default='none',
        verbose_name='Требуемое образование'
    )
    general_info = models.TextField(verbose_name='Общая информация')
    responsibilities = models.TextField(verbose_name='Чем предстоит заниматься')
    ideal_candidate = models.TextField(verbose_name='Наш идеальный кандидат')
    we_offer = models.TextField(verbose_name='Что мы предлагаем')
    skills = models.TextField(verbose_name='Требуемые навыки')
    photo = models.ImageField(upload_to='vacancy_photos/', null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, related_name='vacancies', blank=True)

    def __str__(self):
        return self.title
class Application(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    

    class Meta:
        unique_together = ('vacancy', 'user')  # Один пользователь может откликнуться на вакансию только один раз

    def __str__(self):
        return f"Отклик от {self.user.username} на вакансию {self.vacancy.title}"

# Модель избранных вакансий
class FavoriteVacancy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_vacancies', verbose_name='Пользователь')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='favorited_by', verbose_name='Вакансия')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    def __str__(self):
        return f"{self.user.username} -> {self.vacancy.title}"

    class Meta:
        verbose_name = 'Избранная вакансия'
        verbose_name_plural = 'Избранные вакансии'
        unique_together = ('user', 'vacancy')  # Один пользователь может добавить вакансию в избранное только один раз

# Модель сообщений чата

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}: {self.message[:20]}"

    class Meta:
        ordering = ['timestamp']  # Сортировка по времени отправки
        
        
class Skill(models.Model):  # Должна быть объявлена перед Resume
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
class Resume(models.Model):
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
    ]
    @property
    def skills_list(self):
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    middle_name = models.CharField(max_length=50, blank=True, verbose_name='Отчество')
    profession = models.CharField(max_length=100, verbose_name='Профессия', help_text='Можно ввести несколько разных')
    birth_date = models.DateField(verbose_name='Дата рождения')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='Пол')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    citizenship = models.CharField(max_length=50, verbose_name='Гражданство')
    skills = models.TextField(
        verbose_name='Ключевые навыки',
        blank=True,
        help_text='Перечислите ваши навыки через запятую'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Резюме {self.last_name} {self.first_name}"

class Education(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=200, verbose_name='Учебное заведение')
    specialization = models.CharField(max_length=200, verbose_name='Специальность')
    year_start = models.PositiveIntegerField(verbose_name='Год начала')
    year_end = models.PositiveIntegerField(verbose_name='Год окончания')

class WorkExperience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='work_experiences')
    company = models.CharField(max_length=200, verbose_name='Компания')
    position = models.CharField(max_length=200, verbose_name='Должность')
    responsibilities = models.TextField(verbose_name='Обязанности')
    achievements = models.TextField(blank=True, verbose_name='Достижения')
    date_start = models.DateField(verbose_name='Дата начала')
    date_end = models.DateField(null=True, blank=True, verbose_name='Дата окончания')
    currently_working = models.BooleanField(default=False, verbose_name='Работаю по настоящее время')

class PortfolioFile(models.Model):
    work_experience = models.ForeignKey(WorkExperience, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='portfolio/', verbose_name='Файл')
    description = models.CharField(max_length=200, blank=True, verbose_name='Описание')
    

def generate_code(length=6):
    return ''.join(random.choice(string.digits) for _ in range(length))

class EmailVerificationCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)  # Должно быть достаточно для 6-значного кода
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    purpose = models.CharField(max_length=20, choices=[
        ('password_reset', 'Сброс пароля'),
        ('email_verification', 'Подтверждение email')
    ])

    def __str__(self):
        return f"{self.email} - {self.code}"