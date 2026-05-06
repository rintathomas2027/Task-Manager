from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('User', 'User'),
        ('Manager', 'Manager'),
        ('Project Lead', 'Project Lead'),
        ('Contributor', 'Contributor'),
        ('Auditor', 'Auditor'),
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='User')

    def __str__(self):
        return f"{self.username} ({self.role})"

class Task(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
