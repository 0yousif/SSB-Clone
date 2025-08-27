from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from adminstrator.models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    print("instance", instance)
    if created:
        Profile.objects.create(
            user=instance)  


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):

    instance.profile.save()
