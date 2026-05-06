from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Task

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('role',)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow all roles on public signup for demonstration
        self.fields['role'].choices = [('User', 'User'), ('Manager', 'Manager'), ('Project Lead', 'Project Lead'), ('Contributor', 'Contributor'), ('Auditor', 'Auditor')]

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'user', 'is_completed']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-400 bg-white/70'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-400 bg-white/70', 'rows': 4}),
            'user': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-400 bg-white/70'}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'h-5 w-5 text-purple-600 border-gray-300 rounded focus:ring-purple-500'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.role not in ['Admin', 'Manager']:
            self.fields.pop('user')
        elif user:
            self.fields['user'].queryset = CustomUser.objects.exclude(role='Admin')
            self.fields['user'].empty_label = "Select Employee to Assign"
            self.fields['user'].required = False
