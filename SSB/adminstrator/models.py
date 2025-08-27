from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import date
from django.contrib.auth.models import User
# Create your models here.

GENDERS = (
    ('M', 'Male'),
    ('F', 'Female')
)


USER_TYPES = (
    ("tutor", "tutor"),
    ("admin", "admin"),
    ("student", "student"),
)


USER_STATUS_CHOICES = (
    ("active", "active"),
    ("pending", "pending"),
    ("dropped", "dropped"),
    ("graduated", "graduated"),
    ("transferred", "transferred"),

)


class Departments(models.Model):
    department_id = models.AutoField(primary_key=True, null=False)
    department_code = models.CharField(max_length=4, null=False)
    department_name = models.CharField(max_length=100, null=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    def __str__(this):
        return this.department_id


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_detail_id = models.AutoField(validators=[MaxValueValidator(
        999999999), MinValueValidator(0)], null=False, primary_key=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    academic_number = models.IntegerField(
        validators=[MaxValueValidator(999999999), MinValueValidator(0)], null=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=1, choices=GENDERS, default=GENDERS[0][0], null=True)
    department_id = models.ForeignKey(
        Departments, on_delete=models.PROTECT, null=True, blank=True)
    profession = models.CharField(max_length=50, null=True)
    user_type = models.CharField(
        max_length=20, choices=USER_TYPES, default=USER_TYPES[0][0], null=True, blank=True)
    major = models.CharField(max_length=50, null=True)
    school = models.CharField(max_length=50, null=True)
    start_date = models.DateField(auto_now_add=True, null=True, blank=True)
    current_semester = models.IntegerField(
        validators=[MaxValueValidator(10), MinValueValidator(1)], null=True, default=1)
    gpa = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, default=0)
    total_credits_earned = models.IntegerField(
        validators=[MaxValueValidator(999)], null=True, default=0)
    status = models.CharField(
        choices=USER_STATUS_CHOICES, default=USER_STATUS_CHOICES[0][0], null=False)
    email = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.user.username
