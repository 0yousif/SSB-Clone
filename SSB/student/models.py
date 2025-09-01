from django.db import models
from django.contrib.auth.models import User 
from adminstrator.models import Section 
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.

class Student_plan(models.Model):
    plan_id = models.AutoField(primary_key=True,null=False)
    name = models.CharField(max_length=100, null=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    sections = models.ManyToManyField(Section)

    def __str__(this):
        return str(this.name)


        