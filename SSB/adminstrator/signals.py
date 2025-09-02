from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from datetime import date
from .models import Profile, Configurations


# @receiver(post_save, sender=User)
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(
#             user=instance)


# @receiver(post_save, sender=User)
# def save_profile(sender, instance, **kwargs):
#     instance.profile.save()


@receiver(pre_save, sender=Profile)
def save_profile(sender, instance, **kwargs):
    if (instance.user_type == 'student'):

        config = Configurations.objects.all().first()

        # to reset student ids
        if config.year != date.today().year:
            config.year = date.today().year
            config.id_counter = 0

        config.id_counter += 1
        config.save()

        # year = date.today().year
        # user_id = instance.user_id
        num = str(config.id_counter).zfill(5)
        instance.academic_number = int(f"{config.year}{num}")
        student_email = instance.academic_number
        instance.email = f'{student_email}@student.edu.bh'

    elif (instance.user_type == 'tutor'):
        instance.email = f'{instance.first_name}.{instance.last_name}@tutor.edu.bh'
