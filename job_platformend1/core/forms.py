from django import forms
from django.contrib.auth.forms import UserCreationForm,PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import UserProfile, Company, Vacancy, ChatMessage, Application,Tag, Resume,Skill,Education,WorkExperience,PortfolioFile,EmailVerificationCode

# Форма регистрации пользователя
class UserRegistrationForm(UserCreationForm):
    username = forms.CharField( label='Имя пользователя',widget=forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Введите имя пользователя',}))
    password1 = forms.CharField( label='Пароль',widget=forms.PasswordInput(attrs={'class': 'input-field', 'placeholder': 'Придумайте пароль',}))
    password2 = forms.CharField( label='Повтор пароля',widget=forms.PasswordInput(attrs={'class': 'input-field', 'placeholder': 'Повторите пароль',}))
    full_name = forms.CharField(max_length=255, label='ФИО',widget=forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Введите ФИО',}))
    photo = forms.ImageField(required=False, label='Фото', widget=forms.ClearableFileInput(attrs={'class': 'input-field',}))
    phone = forms.CharField(max_length=20, required=False, label='Телефон', widget=forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Введите телефон',}))
    email = forms.EmailField(required=True, label='Email', widget=forms.EmailInput(attrs={'class': 'input-field', 'placeholder': 'Введите почту',}))
    birth_date = forms.DateField(required=False, label='Дата рождения', widget=forms.DateInput(attrs={'type': 'date'}))
    bio = forms.CharField(required=False, label='О себе', widget=forms.Textarea(attrs={'class': 'input-field', 'placeholder': 'Расскажите о себе',}))

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'full_name', 'photo', 'phone', 'email', 'birth_date', 'bio']

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.error_messages = {'required': ''} 

# Форма регистрации компании
class CompanyRegistrationForm(UserCreationForm):
    username = forms.CharField( label='Имя пользователя',widget=forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Введите имя пользователя',}))
    password1 = forms.CharField( label='Пароль',widget=forms.PasswordInput(attrs={'class': 'input-field', 'placeholder': 'Придумайте пароль',}))
    password2 = forms.CharField( label='Повтор пароля',widget=forms.PasswordInput(attrs={'class': 'input-field', 'placeholder': 'Повторите пароль',}))
    name = forms.CharField(max_length=255, label='Название компании', widget=forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Введите имя компании',}))
    photo = forms.ImageField(required=False, label='Логотип', widget=forms.ClearableFileInput(attrs={'class': 'input-field',}))
    phone = forms.CharField(max_length=20, required=False, label='Телефон', widget=forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Введите телефон',}))
    email = forms.EmailField(required=True, label='Email', widget=forms.EmailInput(attrs={'class': 'input-field', 'placeholder': 'Введите почту',}))
    bio = forms.CharField(required=False, label='О себе', widget=forms.Textarea(attrs={'class': 'input-field', 'placeholder': 'Расскажите о своей компании',}))

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'name', 'photo', 'phone', 'email', 'bio']

class VacancyForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
        
    class Meta:
        model = Vacancy
        fields = [
            'title', 'salary', 'experience', 'employment_type', 'education',
            'general_info', 'responsibilities', 'ideal_candidate', 'we_offer',
            'skills', 'photo', 'tags'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Введите название вакансии'}),
            'salary': forms.NumberInput(attrs={'class': 'input-field', 'placeholder': 'Укажите зарплату'}),
            'general_info': forms.Textarea(attrs={'class': 'input-field', 'rows': 3, 'placeholder': 'Общая информация о вакансии'}),
            'responsibilities': forms.Textarea(attrs={'class': 'input-field', 'rows': 3, 'placeholder': 'Опишите обязанности'}),
            'ideal_candidate': forms.Textarea(attrs={'class': 'input-field', 'rows': 3, 'placeholder': 'Опишите идеального кандидата'}),
            'we_offer': forms.Textarea(attrs={'class': 'input-field', 'rows': 3, 'placeholder': 'Опишите условия работы и бонусы'}),
            'skills': forms.Textarea(attrs={'class': 'input-field', 'rows': 3, 'placeholder': 'Перечислите требуемые навыки'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'input-field'}),
        }
        labels = {
            'title': 'Название вакансии',
            'salary': 'Заработная плата',
            'experience': 'Требуемый опыт',
            'employment_type': 'Тип занятости',
            'education': 'Требуемое образование',
            'general_info': 'Общая информация',
            'responsibilities': 'Чем предстоит заниматься',
            'ideal_candidate': 'Наш идеальный кандидат',
            'we_offer': 'Что мы предлагаем',
            'skills': 'Требуемые навыки',
            'photo': 'Фото (необязательно)',
            'tags': 'Теги',
        }

# Форма отправки сообщения в чате
class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Введите ваше сообщение...'}),
        }
        
        
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'photo', 'phone', 'email', 'birth_date', 'bio']
        
        
class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Напишите сообщение...'}),
        }
class ResumeForm(forms.ModelForm):
    skills = forms.CharField(
        label='Ключевые навыки',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Например: Python, Django, HTML, CSS, JavaScript'
        }),
        help_text='Перечислите ваши навыки через запятую'
    )
    
    class Meta:
        model = Resume
        fields = ['profession', 'first_name', 'last_name', 'middle_name', 
                 'birth_date', 'gender', 'phone', 'citizenship', 'skills']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'profession': forms.TextInput(attrs={'placeholder': 'Можно ввести несколько профессий'}),
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['institution', 'specialization', 'year_start', 'year_end']

class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = ['company', 'position', 'responsibilities', 
                 'achievements', 'date_start', 'date_end', 'currently_working']
        widgets = {
            'date_start': forms.DateInput(attrs={'type': 'date'}),
            'date_end': forms.DateInput(attrs={'type': 'date'}),
        }

class PortfolioFileForm(forms.ModelForm):
    class Meta:
        model = PortfolioFile
        fields = ['file', 'description']
        
        
class EmailVerificationForm(forms.Form):
    email = forms.EmailField()
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже используется")
        return email

class CodeVerificationForm(forms.Form):
    code = forms.CharField(max_length=6, min_length=6)

class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(self, *args, **kwargs):
        # Переопределяем для использования нашего шаблона
        pass

class CustomSetPasswordForm(SetPasswordForm):
    pass