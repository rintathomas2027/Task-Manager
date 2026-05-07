from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task, CustomUser
from .forms import CustomUserCreationForm, TaskForm
from django.core.paginator import Paginator
from django.db.models import Q, Count

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'tasks/home.html')

def about(request):
    return render(request, 'tasks/about.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome!")
            return redirect('dashboard')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'tasks/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'tasks/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('login')

@login_required
def dashboard(request):
    if request.user.role in ['Admin', 'Manager']:
        return redirect('admin_dashboard')
    return redirect('user_dashboard')

@login_required
def admin_dashboard(request):
    if request.user.role not in ['Admin', 'Manager']:
        messages.error(request, "Access denied. Admins and Managers only.")
        return redirect('dashboard')
        
    total_users = CustomUser.objects.count()
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(is_completed=True).count()
    
    users = CustomUser.objects.annotate(
        completed_count=Count('tasks', filter=Q(tasks__is_completed=True)),
        pending_count=Count('tasks', filter=Q(tasks__is_completed=False))
    )
    
    recent_tasks = Task.objects.all().select_related('user').order_by('-updated_at')[:10]
    
    context = {
        'total_users': total_users,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'users': users,
        'recent_tasks': recent_tasks
    }
    return render(request, 'tasks/admin_dashboard.html', context)

@login_required
def user_dashboard(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    
    tasks = Task.objects.all() if request.user.role in ['Admin', 'Manager', 'Project Lead', 'Auditor'] else Task.objects.filter(user=request.user)
    
    if query:
        tasks = tasks.filter(Q(title__icontains=query) | Q(description__icontains=query))
        
    if status_filter == 'completed':
        tasks = tasks.filter(is_completed=True)
    elif status_filter == 'pending':
        tasks = tasks.filter(is_completed=False)
        
    tasks = tasks.order_by('-created_at')
    
    paginator = Paginator(tasks, 5) # 5 tasks per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter
    }
    return render(request, 'tasks/user_dashboard.html', context)

@login_required
def task_create(request):
    if request.user.role in ['Project Lead', 'Auditor', 'Contributor']:
        messages.error(request, "Project Leads, Auditors, and Contributors cannot create tasks directly.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            if not form.cleaned_data.get('user'):
                task.user = request.user
            else:
                task.user = form.cleaned_data.get('user')
            task.save()
            messages.success(request, "Task created successfully.")
            return redirect('dashboard')
    else:
        form = TaskForm(user=request.user)
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Create'})

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    if request.user.role in ['Project Lead', 'Auditor'] or (request.user.role == 'User' and task.user != request.user):
        messages.error(request, "You don't have permission to edit this task.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully.")
            return redirect('dashboard')
    else:
        form = TaskForm(instance=task, user=request.user)
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Update'})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    if request.user.role in ['Project Lead', 'Auditor'] or (request.user.role == 'User' and task.user != request.user):
        messages.error(request, "You don't have permission to delete this task.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        task.delete()
        messages.success(request, "Task deleted successfully.")
        return redirect('dashboard')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

@login_required
def task_toggle_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    if request.user.role in ['Project Lead', 'Contributor'] or (request.user.role == 'User' and task.user != request.user):
        messages.error(request, "You don't have permission to modify this task.")
        return redirect('dashboard')
        
    task.is_completed = not task.is_completed
    task.save()
    status = "completed" if task.is_completed else "pending"
    messages.success(request, f"Task marked as {status}.")
    return redirect('dashboard')

@login_required
def change_user_role(request, pk):
    if request.user.role != 'Admin':
        messages.error(request, "Only Admins can change roles.")
        return redirect('dashboard')
        
    user_to_change = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role:
            user_to_change.role = new_role
            user_to_change.save()
            messages.success(request, f"Role for {user_to_change.username} updated to {new_role}.")
            
    return redirect('admin_dashboard')
