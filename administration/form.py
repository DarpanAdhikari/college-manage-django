from django import forms
from .models import *
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.db.models import Sum

class TeacherForm(forms.ModelForm):
    class Meta:
        model = TeacherInfo
        fields = ['first_name', 'middle_name', 'last_name', 'dob', 'gender', 'applicant_status', 'salary', 'profile_image', 'higher_edu_cmp', 'degree', 'graduation_certificate']
        salary = forms.ModelChoiceField(
        queryset=Salary.objects.all(), 
        widget=forms.Select(attrs={'class': 'form-control'}), 
        empty_label="Select Salary",
        to_field_name="salary_id",
        )
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Middle Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'dob': forms.DateInput(attrs={'class': 'form-control pastDate', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'applicant_status': forms.Select(attrs={'class': 'form-select'}),
            'salary': forms.Select(attrs={'class': 'form-select'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            'higher_edu_cmp': forms.DateInput(attrs={'class': 'form-control pastDate', 'type': 'date'}),
            'degree': forms.Select(attrs={'class': 'form-select'}),
            'graduation_certificate': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactInfo
        fields = ['mobile_no', 'other_phone']
        widgets = {
            'mobile_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Mobile Number','type':'number'}),
            'other_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Other Number','type':'number'}),
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['permanent_address', 'current_address']
        widgets = {
            'permanent_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Permanent Address'}),
            'current_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Current Address'}),
        }

class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = ['salary_position','basic_salary','medical_allowance','hr_allowance']
        widgets = {
            'salary_position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Post Name'}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Basic Salary','type':'number'}),
            'medical_allowance': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Medical Allowance','type':'number'}),
            'hr_allowance': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'House Rent Allowance','type':'number'}),
        }
    def clean_basic_salary(self):
        basic_salary = self.cleaned_data.get('basic_salary')
        if basic_salary < 0:
            raise forms.ValidationError('Basic salary cannot be negative.')
        return basic_salary

    def clean_medical_allowance(self):
        medical_allowance = self.cleaned_data.get('medical_allowance')
        if medical_allowance is not None and medical_allowance < 0:
            raise forms.ValidationError('Medical allowance cannot be negative.')
        return medical_allowance

    def clean_hr_allowance(self):
        hr_allowance = self.cleaned_data.get('hr_allowance')
        if hr_allowance is not None and hr_allowance < 0:
            raise forms.ValidationError('Home rent allowance cannot be negative.')
        return hr_allowance

class assignSubjectForm(forms.ModelForm):
    class Meta:
        model = TeacherCourses
        fields = ['teacher','subject']
        widgets = {
            'teacher':forms.Select(attrs={'class':'form-select'}),
            'subject':forms.SelectMultiple(attrs={'class':'form-select'}),
        }   

class StudentForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), required=True, empty_label="Select a course")
    class Meta:
        model = StudentInfo
        fields = ['first_name', 'middle_name', 'last_name', 'father_name', 'roll_no', 'discount', 'dsc_amt', 'applicant_status', 'dob', 'gender', 'ten_completion_date', 'ten_passed_certificate', 'ten_examination','twelve_completion_date', 'twelve_passed_certificate', 'profile_image', 'twelve_examination','course','sem']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter First Name'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter Middle Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter Last Name'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control','placeholder':'Students Father Name'}),
            'roll_no': forms.TextInput(attrs={'class': 'form-control','placeholder':'TU Registered Symbol'}),
            'discount': forms.Select(attrs={'class': 'form-select'}),
            'dsc_amt': forms.NumberInput(attrs={'class': 'form-control','placeholder':'Enter Disscount Amount'}),
            'applicant_status': forms.Select(attrs={'class': 'form-select'}),
            'dob': forms.DateInput(attrs={'class': 'form-control pastDate', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'ten_completion_date': forms.DateInput(attrs={'class': 'form-control pastDate', 'type': 'date'}),
            'ten_passed_certificate': forms.FileInput(attrs={'class': 'form-control'}),
            'ten_examination': forms.Select(attrs={'class': 'form-select'}),
            'twelve_completion_date': forms.DateInput(attrs={'class': 'form-control pastDate', 'type': 'date'}),
            'twelve_examination': forms.Select(attrs={'class': 'form-select'}),
            'twelve_passed_certificate': forms.FileInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-select','id':'course_code'}),
            'sem': forms.Select(attrs={'class': 'form-select','id':'semester'}),
        }

class CourseForm(forms.ModelForm):
    no_of_semesters = forms.IntegerField(
        label='Number of Semesters', 
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control criticalInput',
            'placeholder': 'Number of semesters (e.g., 8)',
        })
    )

    class Meta:
        model = Course
        fields = [
            'course_code', 
            'course_name', 
            'fee_per_sem', 
            'exam_fee', 
            'no_of_year', 
            'no_of_semesters'
        ]
        widgets = {
            'course_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter course code'}),
            'course_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Write Course Full Name'}),
            'fee_per_sem': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Fee per Semester'}),
            'exam_fee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Exam Fee'}),
            'no_of_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Years to complete (e.g., 4)'}),
        }

    def __init__(self, *args, **kwargs):
        course_instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        if course_instance:
            self.fields['no_of_semesters'].initial = course_instance.semesters.count()

    def clean(self):
        cleaned_data = super().clean()
        course_code = cleaned_data.get('course_code')
        course_name = cleaned_data.get('course_name')

        if Course.objects.exclude(course_id=self.instance.course_id).filter(course_code=course_code).exists():
            raise ValidationError('Course code must be unique.')

        if Course.objects.exclude(course_id=self.instance.course_id).filter(course_name=course_name).exists():
            raise ValidationError('Course name must be unique.')

        return cleaned_data

    def save(self, commit=True):
        course = super().save(commit=False)
        
        if commit:
            course.save()
            no_of_semesters = self.cleaned_data['no_of_semesters']
            current_semesters = list(course.semesters.all())
            current_count = len(current_semesters)
            if no_of_semesters > current_count:
                for sem_number in range(current_count + 1, no_of_semesters + 1):
                    Semester.objects.create(course=course, semester=sem_number)
            elif no_of_semesters < current_count:
                surplus_semesters = current_semesters[no_of_semesters:]
                for semester in surplus_semesters:
                    semester.delete()

        return course

class SubjectForm(forms.ModelForm):
    class Meta:
        model = CourseSubject
        fields = ['subject_code','subject_name','credit_hours','full_marks','pass_marks']

class StudentFeeForm(forms.ModelForm):
    payment_method = forms.ChoiceField(
        choices=[('manual', 'Manual'), ('e-sewa', 'Esewa')],
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'payment'}),
        required=True
    )
    class Meta:
        model = StudentFee
        fields = ['invoice_num', 'student', 'semester_fee', 'amount', 'payment_method']  # Add 'payment_method' here
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
            'invoice_num': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Transaction code'}),
        }
    def clean(self):
     cleaned_data = super().clean()
     amount = cleaned_data.get('amount')
     semester_fee = cleaned_data.get('semester_fee')
     student = cleaned_data.get('student')

     if amount and semester_fee and student:
        max_fee = semester_fee.course.fee_per_sem + semester_fee.course.exam_fee
        existing_payments = StudentFee.objects.filter(
            student=student,
            semester_fee=semester_fee,
        ).aggregate(total_paid=Sum('amount'))['total_paid'] or Decimal('0')

        remaining_fee = max_fee - existing_payments

        if remaining_fee < Decimal('1000'):
            # If remaining fee is less than 1000, the user must pay the exact remaining fee
            if amount != remaining_fee:
                raise ValidationError(f"You must pay the exact remaining fee of {remaining_fee}.")
        else:
            # If remaining fee is greater than or equal to 1000, the user must pay at least 1000
            if amount < Decimal('1000'):
                raise ValidationError("The amount must be at least 1000.")
            elif amount > remaining_fee:
                raise ValidationError(f"The amount exceeds the remaining fee. You can only add up to {remaining_fee}.")

     return cleaned_data
