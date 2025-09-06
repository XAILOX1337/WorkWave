from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth import login, logout, authenticate
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.utils.html import strip_tags
from django.contrib import messages
from django.db.models import Q
from .models import UserProfile, Company, Vacancy, FavoriteVacancy, ChatMessage, Application, Tag, User, Resume,Skill,Education,WorkExperience,PortfolioFile,EmailVerificationCode
from .forms import UserRegistrationForm, CompanyRegistrationForm, VacancyForm, ChatMessageForm, UserProfileForm, ApplicationForm,ResumeForm, EducationForm, WorkExperienceForm,CustomPasswordResetForm, CustomSetPasswordForm
from django.contrib.auth.models import User
from django.forms import formset_factory
from django.http import JsonResponse
from django.contrib.auth import get_user_model
import random
from django.core.cache import cache
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


User = get_user_model()
# Главная страница
def home(request):
    query = request.GET.get('query', '')  # Поисковый запрос
    latest_vacancies = Vacancy.objects.filter(is_approved=True).order_by('-created_at')[:12]
    selected_tags = request.GET.getlist('tags')  # Выбранные теги (может быть несколько)

    # Фильтрация вакансий
    vacancies = Vacancy.objects.filter(is_approved=True)

    # Поиск по ключевым словам
    if query:
        vacancies = vacancies.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # Фильтрация по тегам
    if selected_tags:
        vacancies = vacancies.filter(tags__id__in=selected_tags).distinct()

    # Получаем все теги для отображения в фильтре
    tags = Tag.objects.all()

    return render(request, 'core/home.html', {
        'latest_vacancies': latest_vacancies,
        'vacancies': vacancies,
        'query': query,
        'tags': tags,
        'selected_tags': selected_tags,  # Передаем выбранные теги для сохранения состояния фильтров
    })  
# Регистрация пользователя
def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                full_name=form.cleaned_data['full_name'],
                photo=form.cleaned_data['photo'],
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data['email'],
                birth_date=form.cleaned_data['birth_date'],
                bio=form.cleaned_data['bio']
            )
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/register_user.html', {'form': form})

# Регистрация компании
def register_company(request):
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()  # Создаем пользователя
            Company.objects.create(  # Создаем профиль компании
                user=user,
                name=form.cleaned_data['name'],
                photo=form.cleaned_data['photo'],
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data['email'],
                bio=form.cleaned_data['bio']
            )
            login(request, user)  # Авторизуем пользователя
            return redirect('home')
    else:
        form = CompanyRegistrationForm()
    return render(request, 'core/register_company.html', {'form': form})

# Вход в систему
def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST['username']  # Поле теперь может содержать и email, и username
        password = request.POST['password']
        
        # Используем стандартный authenticate, но с нашим бэкендом
        user = authenticate(request, username=username_or_email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Вход выполнен успешно!')
            return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя/email или пароль.')
    return render(request, 'core/login.html')
# Выход из системы
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Вы вышли из системы.')
    return redirect('home')

# Профиль пользователя
@login_required
def profile(request, user_id=None):
    # Если user_id не указан, отображаем профиль текущего пользователя
    if user_id is None:
        user_id = request.user.id

    # Получаем пользователя по ID
    user = get_object_or_404(User, id=user_id)

    # Проверяем, является ли пользователь компанией
    if hasattr(user, 'company'):
        company = user.company
        vacancies = company.vacancies.all()
        applications = Application.objects.filter(vacancy__company=company)
        return render(request, 'core/company_dashboard.html', {
            'company': company,
            'vacancies': vacancies,
            'applications': applications
        })
    else:
        is_company = hasattr(request.user, 'company')
        user_profile = get_object_or_404(UserProfile, user=user)
        applications = Application.objects.filter(user=user)
        
        # Всегда получаем резюме пользователя, чей профиль просматриваем
        resumes = Resume.objects.filter(user=user)
        
        return render(request, 'core/profile.html', {
            'resumes': resumes,
            'profile': user_profile,
            'applications': applications,
            'is_company': is_company,
            'is_own_profile': request.user == user,
            'profile_user': user,  # Добавляем пользователя, чей профиль просматриваем
        })

# Профиль компании
@login_required
def company_profile(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    # Получаем все одобренные вакансии компании
    vacancies = company.vacancies.filter(is_approved=True)
    is_company = hasattr(request.user, 'company')
    return render(request, 'core/company_profile.html', {
        'company': company,
        'vacancies': vacancies,
        'is_company': is_company,  # True, если текущий пользователь — компания
    })

# Список вакансий
def vacancy_list(request):
    query = request.GET.get('query', '')
    selected_tags = request.GET.getlist('tags')
    salary_min = request.GET.get('salary_min')
    salary_max = request.GET.get('salary_max')
    experience = request.GET.get('experience')
    education = request.GET.getlist('education')
    employment = request.GET.getlist('employment')
    sort = request.GET.get('sort', 'relevance')

    vacancies = Vacancy.objects.filter(is_approved=True)

    if query:
        vacancies = vacancies.filter(
            Q(title__icontains=query) | 
            Q(general_info__icontains=query) |
            Q(responsibilities__icontains=query) |
            Q(ideal_candidate__icontains=query) |
            Q(we_offer__icontains=query) |
            Q(skills__icontains=query)
        )
    if request.user.is_authenticated:
        favorite_vacancies_ids = request.user.favorite_vacancies.values_list('vacancy_id', flat=True)
    else:
        favorite_vacancies_ids = []    
    if selected_tags:
        vacancies = vacancies.filter(tags__id__in=selected_tags).distinct()

    if salary_min:
        vacancies = vacancies.filter(salary__gte=salary_min)
    if salary_max:
        vacancies = vacancies.filter(salary__lte=salary_max)

    if experience and experience != 'any':
        vacancies = vacancies.filter(experience=experience)

    if education:
        vacancies = vacancies.filter(education__in=education)

    if employment:
        vacancies = vacancies.filter(employment_type__in=employment)

    if sort == 'date':
        vacancies = vacancies.order_by('-created_at')
    elif sort == 'salary_desc':
        vacancies = vacancies.order_by('-salary')
    elif sort == 'salary_asc':
        vacancies = vacancies.order_by('salary')

    tags = Tag.objects.all()
    

    return render(request, 'core/vacancy_list.html', {
        'vacancies': vacancies,
        'favorite_vacancies_ids': list(favorite_vacancies_ids),
        'query': query,
        'tags': tags,
        'selected_tags': selected_tags,
    })

# Детали вакансии
def vacancy_detail(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    is_favorite = False
    is_company = False

    if request.user.is_authenticated:
        is_favorite = FavoriteVacancy.objects.filter(user=request.user, vacancy=vacancy).exists()
        is_company = hasattr(request.user, 'company')  # Проверяем, является ли пользователь компанией

    return render(request, 'core/vacancy_detail.html', {
        'vacancy': vacancy,
        'is_favorite': is_favorite,
        'is_company': is_company,  # Передаем информацию о том, является ли пользователь компанией
    })

# Создание вакансии (для компаний)
@login_required
def create_vacancy(request):
    if not hasattr(request.user, 'company'):
        messages.error(request, 'Только компании могут создавать вакансии.')
        return redirect('home')

    if request.method == 'POST':
        form = VacancyForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                vacancy = form.save(commit=False)
                vacancy.company = request.user.company
                vacancy.save()
                form.save_m2m()  # Сохраняем теги
                messages.success(request, 'Вакансия успешно создана! Она появится после модерации.')
                return redirect('company_profile', company_id=request.user.company.id)
            except Exception as e:
                messages.error(request, f'Ошибка при создании вакансии: {str(e)}')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = VacancyForm()

    return render(request, 'core/create_vacancy.html', {'form': form})

# Добавление вакансии в избранное
@login_required
def add_to_favorite(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    FavoriteVacancy.objects.get_or_create(user=request.user, vacancy=vacancy)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    messages.success(request, 'Вакансия добавлена в избранное.')
    return redirect('vacancy_detail', vacancy_id=vacancy.id)
@login_required
def delete_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    if request.method == 'POST':
        resume.delete()
        messages.success(request, 'Резюме успешно удалено!')
        return redirect('profile')
    
    return render(request, 'core/confirm_delete.html', {
        'object': resume,
        'type': 'резюме',
        'cancel_url': 'resume_detail',
        'cancel_id': resume.id
    })

@login_required
def delete_vacancy(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id, company__user=request.user)
    
    if request.method == 'POST':
        vacancy.delete()
        messages.success(request, 'Вакансия успешно закрыта!')
        return redirect('profile')
    
    return render(request, 'core/confirm_delete.html', {
        'object': vacancy,
        'type': 'вакансию',
        'cancel_url': 'vacancy_detail',
        'cancel_id': vacancy.id
    })
@login_required
def remove_from_favorite(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    FavoriteVacancy.objects.filter(user=request.user, vacancy=vacancy).delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    messages.success(request, 'Вакансия удалена из избранного.')
    return redirect('vacancy_detail', vacancy_id=vacancy.id)

# Список избранных вакансий
@login_required
def favorite_vacancies(request):
    favorites = FavoriteVacancy.objects.filter(user=request.user)
    return render(request, 'core/favorite_vacancies.html', {'favorites': favorites})

# Админка: список вакансий для модерации
@login_required
def admin_vacancy_list(request):
    if not request.user.is_superuser:
        messages.error(request, 'Доступ запрещен.')
        return redirect('home')

    vacancies = Vacancy.objects.filter(is_approved=False)
    return render(request, 'core/admin_vacancy_list.html', {'vacancies': vacancies})

# Админка: одобрение вакансии
@login_required
def approve_vacancy(request, vacancy_id):
    if not request.user.is_superuser:
        messages.error(request, 'Доступ запрещен.')
        return redirect('home')

    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    vacancy.is_approved = True
    vacancy.save()
    messages.success(request, 'Вакансия одобрена и опубликована.')
    return redirect('admin_vacancy_list')

# Админка: отклонение вакансии
@login_required
def reject_vacancy(request, vacancy_id):
    if not request.user.is_superuser:
        messages.error(request, 'Доступ запрещен.')
        return redirect('home')

    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    vacancy.delete()
    messages.success(request, 'Вакансия отклонена и удалена.')
    return redirect('admin_vacancy_list')

# Чат: список чатов
@login_required
def chat_list(request):
    # Получаем всех пользователей, с которыми есть переписка
    users = User.objects.filter(
        Q(sent_messages__receiver=request.user) | Q(received_messages__sender=request.user)
    ).distinct()

    return render(request, 'core/chat_list.html', {'users': users})
# Чат: страница чата

@login_required
def chat(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)

    # Исключаем возможность писать самому себе
    if request.user == receiver:
        return redirect('chat_list')

    # Получаем все сообщения между текущим пользователем и получателем
    messages = ChatMessage.objects.filter(
        (Q(sender=request.user) & Q(receiver=receiver)) |
        (Q(sender=receiver) & Q(receiver=request.user))
    ).order_by('timestamp')

    # Отмечаем сообщения как прочитанные
    messages.filter(receiver=request.user, is_read=False).update(is_read=True)

    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.save()
            return redirect('chat', receiver_id=receiver.id)
    else:
        form = ChatMessageForm()

    return render(request, 'core/chat.html', {
        'receiver': receiver,
        'messages': messages,
        'form': form,
    })
# Поиск
def search(request):
    query = request.GET.get('query', '')
    if query:
        results = Vacancy.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            is_approved=True
        )
    else:
        results = Vacancy.objects.none()
    return render(request, 'core/search.html', {'results': results, 'query': query})

@login_required
def edit_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'core/edit_profile.html', {'form': form})

@login_required
def apply_for_vacancy(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    
    # Проверяем, является ли пользователь компанией
    if hasattr(request.user, 'company'):
        messages.error(request, 'Компании не могут откликаться на вакансии.')
        return redirect('vacancy_detail', vacancy_id=vacancy.id)
    
    # Проверяем, откликался ли пользователь уже на эту вакансию
    if Application.objects.filter(vacancy=vacancy, user=request.user).exists():
        messages.error(request, 'Вы уже откликались на эту вакансию.')
        return redirect('vacancy_detail', vacancy_id=vacancy.id)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.vacancy = vacancy
            application.user = request.user
            application.save()
            messages.success(request, 'Ваш отклик успешно отправлен!')
            return redirect('vacancy_detail', vacancy_id=vacancy.id)
    else:
        form = ApplicationForm()
    
    return render(request, 'core/apply_for_vacancy.html', {'form': form, 'vacancy': vacancy})



@login_required
def video_call(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)
    
    # Запрет звонка самому себе
    if request.user == receiver:
        return redirect('chat_list')
    
    # Генерация уникального имени комнаты
    user_ids = sorted([str(request.user.id), str(receiver_id)])
    room_name = f"video_call_{'_'.join(user_ids)}"
    
    return render(request, 'core/video_call.html', {
        'receiver': receiver,
        'room_name': room_name
    })



@login_required
def resume_builder(request):
    EducationFormSet = formset_factory(EducationForm, extra=1)
    WorkExperienceFormSet = formset_factory(WorkExperienceForm, extra=1)
    
    if request.method == 'POST':
        resume_form = ResumeForm(request.POST)
        education_formset = EducationFormSet(request.POST, prefix='education')
        experience_formset = WorkExperienceFormSet(request.POST, prefix='experience')
        
        # Проверяем валидность всех форм
        forms_valid = resume_form.is_valid()
        forms_valid &= education_formset.is_valid()
        forms_valid &= experience_formset.is_valid()
        
        if forms_valid:
            try:
                # Сохраняем основное резюме
                resume = resume_form.save(commit=False)
                resume.user = request.user
                resume.save()
                resume_form.save_m2m()  # Для сохранения ManyToMany полей
                
                # Сохраняем образование
                for form in education_formset:
                    if form.cleaned_data:  # Проверяем, что форма не пустая
                        education = form.save(commit=False)
                        education.resume = resume
                        education.save()
                
                # Сохраняем опыт работы
                for form in experience_formset:
                    if form.cleaned_data:  # Проверяем, что форма не пустая
                        experience = form.save(commit=False)
                        experience.resume = resume
                        experience.save()
                
                messages.success(request, 'Резюме успешно сохранено!')
                return redirect('profile')
            
            except Exception as e:
                messages.error(request, f'Ошибка при сохранении: {str(e)}')
                # Для отладки:
                print(f"Ошибка сохранения резюме: {e}")
    else:
        # GET запрос - инициализируем пустые формы
        resume_form = ResumeForm()
        education_formset = EducationFormSet(prefix='education')
        experience_formset = WorkExperienceFormSet(prefix='experience')
    
    context = {
        'resume_form': resume_form,
        'education_formset': education_formset,
        'experience_formset': experience_formset,
    }
    return render(request, 'core/resume_builder.html', context)


@login_required
def resume_detail(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id)
    is_company = hasattr(request.user, 'company')
    is_owner = request.user == resume.user
    
    # Проверка прав доступа
    if not is_owner and not is_company:
        raise PermissionDenied("У вас нет доступа к этому резюме")
    
    return render(request, 'core/resume_detail.html', {
        'resume': resume,
        'is_company': is_company,
        'is_owner': is_owner,
    })

def send_verification_email(email, code):
    """Отправка email с кодом подтверждения"""
    subject = 'Код подтверждения для сброса пароля'
    
    # Убедитесь, что шаблон существует по пути core/email/password_reset_email.html
    html_message = render_to_string('core/email/password_reset_email.html', {
        'code': code,  # Передаем код в шаблон
    })
    
    plain_message = f"Ваш код подтверждения: {code}"  # Простая текстовая версия
    
    send_mail(
        subject=subject,
        message=plain_message,  # Текстовая версия
        from_email=None,  # Используется DEFAULT_FROM_EMAIL из settings.py
        recipient_list=[email],
        html_message=html_message,  # HTML версия
        fail_silently=False,
    )

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Генерируем код
            code = ''.join([str(random.randint(0, 9)) for _ in range(6)])  # 6 цифр
            
            # Сохраняем в базе
            EmailVerificationCode.objects.create(
                email=email,
                code=code,
                purpose='password_reset'
            )
            
            # Отправляем письмо (добавьте логирование для отладки)
            print(f"Отправка кода {code} на {email}")  # Проверьте в консоли
            send_verification_email(email, code)
            
            request.session['reset_email'] = email
            return redirect('password_reset_verify_code')
            
        except User.DoesNotExist:
            messages.error(request, 'Пользователь с таким email не найден')
    return render(request, 'core/password_reset_request.html')

def password_reset_verify_code(request):
    """Второй шаг - проверка кода"""
    email = request.session.get('reset_email')
    if not email:
        return redirect('password_reset_request')
    
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            verification = EmailVerificationCode.objects.get(
                email=email,
                code=code,
                purpose='password_reset',
                is_used=False
            )
            verification.is_used = True
            verification.save()
            request.session['verified_email'] = email
            return redirect('password_reset_confirm')
        except EmailVerificationCode.DoesNotExist:
            messages.error(request, 'Неверный код подтверждения')
    
    return render(request, 'core/password_reset_verify_code.html')

def password_reset_confirm(request):
    """Третий шаг - установка нового пароля"""
    email = request.session.get('verified_email')
    if not email:
        return redirect('password_reset_request')
    
    if request.method == 'POST':
        password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Пароли не совпадают')
            return redirect('password_reset_confirm')
        
        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            del request.session['verified_email']
            del request.session['reset_email']
            messages.success(request, 'Пароль успешно изменен!')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'Ошибка изменения пароля')
    
    return render(request, 'core/password_reset_confirm.html')



@login_required
def edit_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    EducationFormSet = formset_factory(EducationForm, extra=1)
    WorkExperienceFormSet = formset_factory(WorkExperienceForm, extra=1)
    
    if request.method == 'POST':
        resume_form = ResumeForm(request.POST, instance=resume)
        education_formset = EducationFormSet(request.POST, prefix='education')
        experience_formset = WorkExperienceFormSet(request.POST, prefix='experience')
        
        forms_valid = resume_form.is_valid()
        forms_valid &= education_formset.is_valid()
        forms_valid &= experience_formset.is_valid()
        
        if forms_valid:
            try:
                # Сохраняем основное резюме
                resume = resume_form.save()
                
                # Удаляем старые записи об образовании и опыте
                resume.educations.all().delete()
                resume.work_experiences.all().delete()
                
                # Сохраняем новое образование
                for form in education_formset:
                    if form.cleaned_data:
                        education = form.save(commit=False)
                        education.resume = resume
                        education.save()
                
                # Сохраняем новый опыт работы
                for form in experience_formset:
                    if form.cleaned_data:
                        experience = form.save(commit=False)
                        experience.resume = resume
                        experience.save()
                
                messages.success(request, 'Резюме успешно обновлено!')
                return redirect('resume_detail', resume_id=resume.id)
            
            except Exception as e:
                messages.error(request, f'Ошибка при сохранении: {str(e)}')
    else:
        # Инициализируем формы с текущими данными
        resume_form = ResumeForm(instance=resume)
        
        # Подготавливаем данные для формсетов
        education_data = [{
            'institution': edu.institution,
            'specialization': edu.specialization,
            'year_start': edu.year_start,
            'year_end': edu.year_end
        } for edu in resume.educations.all()]
        
        experience_data = [{
            'company': exp.company,
            'position': exp.position,
            'responsibilities': exp.responsibilities,
            'achievements': exp.achievements,
            'date_start': exp.date_start,
            'date_end': exp.date_end,
            'currently_working': exp.currently_working
        } for exp in resume.work_experiences.all()]
        
        education_formset = EducationFormSet(initial=education_data, prefix='education')
        experience_formset = WorkExperienceFormSet(initial=experience_data, prefix='experience')
    
    context = {
        'resume_form': resume_form,
        'education_formset': education_formset,
        'experience_formset': experience_formset,
        'resume': resume,
    }
    return render(request, 'core/edit_resume.html', context)

def politics(request):
    return render(request, 'core/politics.html')
def conf(request):
    return render(request, 'core/confeditional.html')
def answers(request):
    return render(request, 'core/answers.html')
def personal_data(request):
    return render(request, 'core/personal_data.html')


@login_required
def edit_vacancy(request, vacancy_id):
    # Проверяем, что пользователь - компания и владелец вакансии
    if not hasattr(request.user, 'company'):
        messages.error(request, 'Только компании могут редактировать вакансии.')
        return redirect('home')

    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    
    # Проверяем, что текущий пользователь - владелец вакансии
    if vacancy.company.user != request.user:
        messages.error(request, 'Вы не можете редактировать эту вакансию.')
        return redirect('company_profile', company_id=request.user.company.id)

    if request.method == 'POST':
        form = VacancyForm(request.POST, request.FILES, instance=vacancy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Вакансия успешно обновлена!')
            return redirect('company_profile', company_id=request.user.company.id)
    else:
        form = VacancyForm(instance=vacancy)

    return render(request, 'core/edit_vacancy.html', {
        'form': form,
        'vacancy': vacancy
    })
    
    
@csrf_exempt
@require_POST
def set_peer_id(request):
    try:
        data = json.loads(request.body)
        room_name = data.get('room_name')
        username = data.get('username')
        peer_id = data.get('peer_id')
        
        if not all([room_name, username, peer_id]):
            return JsonResponse({'status': 'error', 'message': 'Missing parameters'}, status=400)
        
        # Сохраняем в кеше на 5 минут
        cache_key = f'peer_id_{room_name}_{username}'
        cache.set(cache_key, peer_id, timeout=300)
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def get_peer_id(request):
    room_name = request.GET.get('room_name')
    username = request.GET.get('username')
    
    if not all([room_name, username]):
        return JsonResponse({'status': 'error', 'message': 'Missing parameters'}, status=400)
    
    cache_key = f'peer_id_{room_name}_{username}'
    peer_id = cache.get(cache_key)
    
    return JsonResponse({'peer_id': peer_id})