from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserRole, StudentProfile, ParentProfile


@receiver(post_save, sender=User)
def create_or_sync_user_profile(sender, instance, created, **kwargs):
    """Foydalanuvchi yaratilganda uning roliga mos profilni avtomatik ochish."""
    if instance.role == UserRole.STUDENT:
        StudentProfile.objects.get_or_create(user=instance)
    elif instance.role == UserRole.PARENT:
        ParentProfile.objects.get_or_create(user=instance)
