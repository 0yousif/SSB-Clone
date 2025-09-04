from django.contrib import admin
from .models import Profile, Section, Course, Departments, Semester, Location, Time, Section_schedules,Student_registration, Configurations
from student.models import Student_plan
admin.site.register(Profile)
admin.site.register(Departments)
admin.site.register(Section)
admin.site.register(Course)
admin.site.register(Semester)
admin.site.register(Location)
admin.site.register(Time)
admin.site.register(Section_schedules)
admin.site.register(Student_registration)
admin.site.register(Student_plan)
admin.site.register(Configurations)