from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import date
from django.contrib.auth.models import User
from django.urls import reverse

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

COURSE_CREDITS = (
    (5, "5"),
    (15, "15"),
    (60, "60")
)

SCHEDULE_TYPES = (
    ("lab", "lab"),
    ("lec", "lec"),
    ("lec/lab", "lec,lab")
)

DAYS = (
    ("Sunday", "sunday"),
    ("Monday", "monday"),
    ("Tuesday", "tuesday"),
    ("Wednesday", "wednesday"),
    ("Thursday", "thursday"),
    ("Friday", "friday"),
    ("Saturday", "saturday"),
)


COURSE_CREDITS = (
    (5, "5"),
    (15, "15"),
    (60, "60")
)

SCHEDULE_TYPES = (
    ("lab", "lab"),
    ("lec", "lec"),
    ("lec/lab", "lec,lab")
)

DAYS = (
    ("Sunday", "sunday"),
    ("Monday", "monday"),
    ("Tuesday", "tuesday"),
    ("Wednesday", "wednesday"),
    ("Thursday", "thursday"),
    ("Friday", "friday"),
    ("Saturday", "saturday"),
)


class Semester(models.Model):
    semester_id = models.AutoField(primary_key=True, null=False)
    year = models.IntegerField(validators=[MaxValueValidator(
        2), MinValueValidator(1)], null=False)
    semester = models.IntegerField(null=False)
    registration_start = models.DateField(null=False)
    registration_end = models.DateField(null=False)
    is_current = models.BooleanField(null=False)

    def get_absolute_url(self):
        return reverse('semester_detail', kwargs={'pk': self.semester_id})

    def __str__(this):
        return str(this.semester_id)


class Departments(models.Model):
    department_id = models.AutoField(primary_key=True, null=False)
    department_code = models.CharField(max_length=4, null=False)
    department_name = models.CharField(max_length=100, null=False)

    def __str__(this):
        return str(this.department_name)


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
    current_semester = models.IntegerField(validators=[MaxValueValidator(10), MinValueValidator(1)], null=True, default=1)
    gpa = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, default=0)
    total_credits_earned = models.IntegerField(
        validators=[MaxValueValidator(999)], null=True, default=0)
    status = models.CharField(
        choices=USER_STATUS_CHOICES, default=USER_STATUS_CHOICES[0][0], null=False)
    email = models.CharField(max_length=50, null=True)
    personal_email = models.CharField(max_length=50, null=True)
    avatar = models.ImageField(
        upload_to='adminstrator/static/user_profiles', default='')

    def __str__(self):
        return str(self.user.username)

#########################################################################

class Course(models.Model):
    course_id = models.AutoField(primary_key=True, null=False)
    department = models.ForeignKey(Departments, models.CASCADE, null=False)
    code = models.IntegerField(
        validators=[MaxValueValidator(9999)], null=False)
    name = models.CharField(max_length=50, null=False)
    description = models.CharField(max_length=200, null=False)
    credit_hours = models.IntegerField(choices=COURSE_CREDITS, null=False)
    schedule_type = models.CharField(choices=SCHEDULE_TYPES, null=False)
    prerequisit_course = models.ForeignKey(
        "Course", on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=False, null=False)
    semester = models.ForeignKey(
        Semester, on_delete=models.SET_NULL, null=True)

    def __str__(this):
        return f"{this.code} -{this.name}"

    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'pk': self.course_id})


class Section(models.Model):
    crn = models.AutoField(
        validators=[MaxValueValidator(999999)], primary_key=True, null=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=False)
    tutor = models.ForeignKey(User, on_delete=models.PROTECT, null=False)
    schedule_type = models.CharField(choices=SCHEDULE_TYPES, null=False)
    semester = models.IntegerField(
        validators=[MaxValueValidator(10),MinValueValidator(1)], null=False)

    def get_absolute_url(self):
        return reverse('section_detail', kwargs={'pk': self.crn})

    def __str__(self):
        return f"Section {self.crn}: {self.course.name} ({self.tutor.username})"


class Location(models.Model):
    location_id = models.AutoField(primary_key=True, null=False)
    room_number = models.IntegerField(
        validators=[MaxValueValidator(999)], null=False)
    building_code = models.IntegerField(
        validators=[MaxValueValidator(999)], null=False)

    def __str__(this):
        return str(this.location_id)


class Time(models.Model):
    time_id = models.AutoField(primary_key=True, null=False)
    start_time = models.TimeField(null=False)
    end_time = models.TimeField(null=False)
    period = models.IntegerField(null=False, validators=[MaxValueValidator(2), MinValueValidator(1)])

    def __str__(this):
        return str(this.time_id)


class Section_schedules(models.Model):
    schedule_id = models.AutoField(primary_key=True, null=False)
    day_of_week = models.CharField(choices=DAYS, null=False)
    crn = models.ForeignKey(Section, on_delete=models.CASCADE, null=False)
    location = models.ForeignKey(
        Location, on_delete=models.PROTECT, null=False)
    time = models.ForeignKey(Time, on_delete=models.PROTECT, null=False)

    def __str__(this):
        return str(this.schedule_id)


class Student_registration(models.Model):
    registration = models.AutoField(primary_key=True, null=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    registration_status = models.CharField(null=False)
    registered_date = models.DateField(null=False)
    crn = models.ForeignKey(Section, on_delete=models.PROTECT)

    def __str__(this):
        return str(this.registration)


class Configurations(models.Model):
    Section_limit = models.IntegerField(
        validators=[MaxValueValidator(200), MinValueValidator(0)], null=False)
    credits_limit = models.IntegerField(null=False, default=60)
    time_limit = models.IntegerField(null=False)


ATTENDANCE_CHOICES = (
    ('P', 'Present'),
    ('A', 'Absent'),
    ('L', 'Late'),
    ('E', 'Excused'),
)


class Attendance(models.Model):
    attendance_id = models.AutoField(primary_key=True, null=False)
    date = models.DateField(null=False)
    status = models.CharField(max_length=1, null=False,
                              choices=ATTENDANCE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True, null=False)
    tutor = models.ForeignKey(User, on_delete=models.PROTECT, null=False)
    registration = models.ForeignKey(
        Student_registration, on_delete=models.CASCADE)

    def __str__(self):
        return f"Attendance {self.attendance_id}"




class Admissions(models.Model):
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    CPR = models.IntegerField(null=False)
    gender = models.CharField(
        max_length=1, choices=GENDERS, default=GENDERS[0][0], null=True)
    school = models.CharField(max_length=50, null=True)
    dob = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.CPR} - admission"

GRADE_CHOICES = (
    ('A', 'A'),
    ('B', 'B'), 
    ('C', 'C'),
    ('D', 'D'),
    ('F', 'F'),
)

class Grades(models.Model):    
    grade_id = models.AutoField(primary_key=True,null=False)    
    grade = models.CharField(max_length=1, choices=GRADE_CHOICES)    
    registration_id = models.ForeignKey(Student_registration, on_delete=models.CASCADE)    
    def __str__(this):
        return f"{this.grade_id} - {this.grade}"
