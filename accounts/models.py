from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import models


class UserManager(DjangoUserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        # createsuperuser shouldn't leave staff logging in with role='cashier' by accident.
        extra_fields.setdefault('role', User.Role.ADMIN)
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MANAGER = 'manager', 'Manager'
        CASHIER = 'cashier', 'Cashier'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CASHIER)
    outlet = models.ForeignKey(
        'outlets.Outlet',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff',
        help_text='Which outlet this staff member is based at. Leave blank for head-office/admin accounts.',
    )

    objects = UserManager()

    def __str__(self):
        return self.username
