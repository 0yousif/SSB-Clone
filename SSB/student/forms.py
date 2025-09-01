from django.forms import ModelForm
from .models import Student_plan

class StudentPlanForm(ModelForm):
    class Meta:
        model = Student_plan
        fields = ['name']
