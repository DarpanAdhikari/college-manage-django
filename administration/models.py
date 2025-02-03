from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class ContactInfo(models.Model):
    contact_id = models.AutoField(primary_key=True)
    mobile_no = models.BigIntegerField()
    other_phone = models.BigIntegerField(null=True, blank=True)

class Address(models.Model):
    address_id = models.AutoField(primary_key=True)
    permanent_address = models.CharField(max_length=150)
    current_address = models.CharField(max_length=150)

class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_code = models.CharField(max_length=10)
    course_name = models.CharField(max_length=50)
    fee_per_sem = models.DecimalField(max_digits=10, decimal_places=2)
    exam_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    no_of_year = models.PositiveIntegerField()

    def __str__(self):
        return self.course_name

class Semester(models.Model):
    sem_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='semesters')
    semester = models.PositiveIntegerField()
    
    def __str__(self):
       return str(self.semester)

class CourseSubject(models.Model):
    sub_id = models.AutoField(primary_key=True)
    subject_code = models.CharField(max_length=10)  
    subject_name = models.CharField(max_length=50)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subjects')
    sem = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='subjects')
    credit_hours = models.PositiveIntegerField()
    full_marks = models.PositiveIntegerField()
    pass_marks = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.course.course_name}:- {self.subject_name}"

class Degree(models.Model):
    deg_id = models.AutoField(primary_key=True)
    sym = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.sym
    
class Examination(models.Model):
    ex_id = models.AutoField(primary_key=True)
    sym = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class StudentInfo(models.Model):
    YES = True
    NO = False

    APPLICANT_DISCOUNT_CHOICES = [
        (YES, 'Applied'),
        (NO, 'Not Applied')
    ]
    APPLICANT_STATUS_CHOICES = [
        (YES, 'Addmited'),
        (NO, 'Not Addmited')
    ]
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sem = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='students')
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30)
    father_name = models.CharField(max_length=30)
    roll_no = models.CharField(max_length=20, null=True, blank=True)
    contact = models.ForeignKey(ContactInfo, on_delete=models.CASCADE)
    discount = models.BooleanField(default=False,choices=APPLICANT_DISCOUNT_CHOICES)
    dsc_amt = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    applicant_status = models.BooleanField(default=False,choices=APPLICANT_STATUS_CHOICES)
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], default='male')
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    ten_completion_date = models.DateField()
    ten_examination = models.ForeignKey(Examination, on_delete=models.CASCADE,related_name='students_ten_exam')
    ten_passed_certificate = models.ImageField(upload_to='student_certificate/', blank=True, null=True)
    twelve_completion_date = models.DateField()
    twelve_examination = models.ForeignKey(Examination, on_delete=models.CASCADE, related_name='students_twelve_exam')
    twelve_passed_certificate = models.ImageField(upload_to='student_certificate/',blank=True, null=True)
    profile_image = models.ImageField(upload_to='student_profile_images/',blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.discount and not self.dsc_amt:
            raise ValidationError('Discount ammount is required when discount is applied.')
        
    def __str__(self):
        return self.user.username

class StudentFee(models.Model):
    fee_id = models.AutoField(primary_key=True)
    invoice_num = models.CharField(max_length=100)
    student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE, related_name='fees')
    semester_fee = models.ForeignKey(Semester, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='submitted_fees')  # Using User as the submitter
    paid_date = models.DateTimeField(auto_now=True)

class StudentAttendance(models.Model):
    attendance_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE, related_name='attendances')
    sem = models.ForeignKey(Semester, on_delete=models.CASCADE)
    attendance_date = models.DateTimeField(auto_now_add=True)

class Salary(models.Model):
    salary_id = models.AutoField(primary_key=True)
    salary_position = models.CharField(max_length=100)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    hr_allowance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.salary_position

class TeacherInfo(models.Model):
    PERMANENT = 1
    PART_TIME = 2

    APPLICANT_STATUS_CHOICES = [
        (PERMANENT, 'Permanent'),
        (PART_TIME, 'Part Time')
    ]

    teacher_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30)
    contact = models.ForeignKey(ContactInfo, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    applicant_status = models.IntegerField(choices=APPLICANT_STATUS_CHOICES)
    salary = models.ForeignKey(Salary, on_delete=models.CASCADE)
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], default='male')
    higher_edu_cmp = models.DateField()
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
    graduation_certificate = models.ImageField(upload_to='teacher_certificate/',blank=True, null=True)
    profile_image = models.ImageField(upload_to='teacher_profile_images/',blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_applicant_status_display()}"

class TeacherCourses(models.Model):
    tc_id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(TeacherInfo, on_delete=models.CASCADE, related_name='courses')
    subject = models.ManyToManyField(CourseSubject)

    def __str__(self):
        return f"{self.teacher} : {self.subject}"

class TeacherAttendance(models.Model):
    attendance_id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(TeacherInfo, on_delete=models.CASCADE, related_name='attendances')
    attendance_date = models.DateTimeField(auto_now_add=True)

class TeacherSalaryReport(models.Model):
    salary_report_id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(TeacherInfo, on_delete=models.CASCADE, related_name='salary_reports')
    salary = models.ForeignKey(Salary, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now=True)