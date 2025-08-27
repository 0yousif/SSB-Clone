from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from datetime import date

from adminstrator.models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    year = date.today().year
    user_id = instance.id
    num = str(user_id).zfill(5)
    instance.profile.academic_number = int(f"{year}{num}")
    instance.profile.save()
