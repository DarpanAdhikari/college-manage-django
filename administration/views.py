import random,requests
from django.http import HttpResponse,HttpResponseBadRequest,JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout
from django.urls import reverse
from accounts.form import user_email_form
from django.contrib.auth.models import User
from django.contrib import messages
from accounts.utils.logging_utils import log_action
from django.contrib.admin.models import ADDITION, CHANGE, DELETION

from django.conf import settings
from .form import *
from .models import *
from django.db.models import Count
from django.core.cache import cache
from django.core.paginator import Paginator
from django.utils import timezone
from django.forms import modelformset_factory
import hashlib,uuid,hmac,base64,json
from django.core.mail import send_mail
# Create your views here.
def index(request):
    return render(request,'index.html',)

def generate_random_number():
    part1 = str(random.randint(0, 9999)).zfill(4)
    part2 = str(random.randint(0, 9999)).zfill(4)
    return f"{part1}-{part2}"

def get_unique_user_id():
    while True:
        user_id = generate_random_number()
        if not User.objects.filter(username=user_id).exists():
            return user_id
        
@login_required
def register_teacher(request, teacher_id=None):
    is_edit_mode = teacher_id is not None
    teachers = TeacherInfo.objects.select_related('user', 'address', 'contact', 'salary').all().order_by('-teacher_id')
    paginator = Paginator(teachers, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    paging = {
        'page_obj': page_obj,
    }

    if is_edit_mode:
        teacher_instance = get_object_or_404(TeacherInfo, pk=teacher_id)
        user_instance = teacher_instance.user
        contact_instance = teacher_instance.contact
        address_instance = teacher_instance.address
    else:
        teacher_instance = None
        user_instance = None
        contact_instance = None
        address_instance = None

    if request.method == 'POST':
        teacher_form = TeacherForm(request.POST, request.FILES, instance=teacher_instance)
        contact_form = ContactForm(request.POST, instance=contact_instance)
        address_form = AddressForm(request.POST, instance=address_instance)
        user_form = user_email_form(request.POST, instance=user_instance)

        if teacher_form.is_valid() and contact_form.is_valid() and address_form.is_valid() and user_form.is_valid():
            firstName = request.POST.get('first_name')
            lastName = request.POST.get('last_name')
            email = request.POST.get('email')
            user = user_form.save(commit=False)
            if not user_instance:
                user.is_staff = 1 
                user.username = get_unique_user_id() 
                user.first_name = firstName
                user.last_name = lastName
                user.password = make_password(firstName)
            user.save()
            contact = contact_form.save()
            address = address_form.save()
            teacher = teacher_form.save(commit=False)
            teacher.user = user
            teacher.contact = contact
            teacher.address = address
            teacher.save()
            cache.delete('teachers_data')
            if not is_edit_mode:
              send_mail(
               'Account created',
               'We glad to welcome you in our college. Your username is:'+str(user.username)+' and password:'+str(firstName),
               settings.EMAIL_HOST_USER,
               [email],
               fail_silently=False,
              )
            log_action(request.user, CHANGE if is_edit_mode else ADDITION, teacher)
            messages.success(request, "Teacher details have been {}.".format("updated" if is_edit_mode else "created"))
            return redirect('register-teacher')
        else:
            messages.error(request, "Please correct the form errors and try again.")
    else:
        teacher_form = TeacherForm(instance=teacher_instance)
        contact_form = ContactForm(instance=contact_instance)
        address_form = AddressForm(instance=address_instance)
        user_form = user_email_form(instance=user_instance)

    return render(request, 'register_teacher.html', {
        'teacher_form': teacher_form,
        'contact_form': contact_form,
        'address_form': address_form,
        'user_form': user_form,
        'related_info': {
            'salaries': Salary.objects.all()
        },
        'is_edit_mode': is_edit_mode,
        'teacher_id':teacher_id,
        'paging':paging,
    })

@login_required
def delete_teacher(request,teacher_id):
    teacher = get_object_or_404(TeacherInfo, teacher_id=teacher_id)
    TeacherCourse = TeacherCourses.objects.filter(teacher=teacher).count()
    Attendance = TeacherAttendance.objects.filter(teacher=teacher).count()
    salaryReport = TeacherSalaryReport.objects.filter(teacher=teacher).count()
    account = User.objects.get(id=teacher.user_id)
    contacts = ContactInfo.objects.get(contact_id=teacher.contact_id)
    address = Address.objects.get(address_id=teacher.address_id)
    if request.method == 'POST':
        teacher.delete()
        address.delete()
        contacts.delete()
        account.delete()
        messages.success(request,"Teacher Successfully deleted")
        return redirect('register-teacher') 
    related_items = {
            'Assigned_courses':TeacherCourse,
            'Teachers_attendance': Attendance,
            'salary_report':salaryReport,
            'User Account':StopIteration(account.username),
            'contacts':StopIteration(contacts.mobile_no,contacts.other_phone),
            'addresse': StopIteration(address.permanent_address,address.current_address),
        }
    return render(request,'delete-data.html',{'name':teacher.first_name+" "+teacher.last_name,'related_items':related_items})

@login_required
def teacher_attendance(request):
    current_date = timezone.now().date()
    pre_attendance = TeacherAttendance.objects.select_related('teacher').filter(attendance_date__date=current_date)
    return render(request,'teacher_attendance.html',{'pre_attendance':pre_attendance})

@login_required
def teachers_salary(request, salary_id=None):
    salaries = Salary.objects.all()
    paginator = Paginator(salaries, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    paging = {
        'page_obj': page_obj,
    }
    is_edit_mode = salary_id is not None
    if request.method == 'POST':
        if is_edit_mode:
            salary_instance = get_object_or_404(Salary, salary_id=salary_id)
            form = SalaryForm(request.POST, instance=salary_instance)
        else:
            form = SalaryForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('teachers-salary') 
    else:
        form = SalaryForm(instance=get_object_or_404(Salary, salary_id=salary_id)) if is_edit_mode else SalaryForm()

    related_data = {
        'is_edit_mode': is_edit_mode,
        'salary_id' : salary_id,
    }
    return render(request, 'teachers_salary.html', {'data': related_data,'paging':paging, 'form': form})

@login_required
def delete_salary(request, salary_id):
    salary = get_object_or_404(Salary, salary_id=salary_id)
    teachers = TeacherInfo.objects.filter(salary=salary).values_list('first_name','last_name')
    full_names = [' '.join(name) for name in teachers]
    report_salary = TeacherSalaryReport.objects.filter(salary=salary).count()
    if request.method == 'POST':
        salary.delete()
        messages.success(request,f"{salary.salary_position} Successfully deleted")
        return redirect('teachers-salary') 

    return render(request, 'delete-data.html', {
        'name': salary.salary_position,
        'related_items': {
            'teachers':full_names,
            'salary_report': report_salary,
        },
    })

@login_required
def assign_subject_teacher(request, assign_id=None):
    is_edit_mode = assign_id is not None
    teacherCourses = TeacherCourses.objects.select_related('teacher').prefetch_related('subject')
    paginator = Paginator(teacherCourses, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    paging = {
        'page_obj': page_obj,
    }
    
    if request.method == 'POST':
        if is_edit_mode:
            assign_instance = get_object_or_404(TeacherCourses, tc_id=assign_id)
            form = assignSubjectForm(request.POST, instance=assign_instance)
        else:
            form = assignSubjectForm(request.POST)
        
        if form.is_valid():
            assign_instance = form.save(commit=False)
            assign_instance.save() 
            form.save_m2m()
            return redirect('assign-teacher')
    else:
        form = assignSubjectForm(instance=get_object_or_404(TeacherCourses, tc_id=assign_id)) if is_edit_mode else assignSubjectForm()

    related_data = {
        'is_edit_mode': is_edit_mode,
        'assign_id':assign_id,
    }
    return render(request, 'subject-to-teacher.html', {'paging':paging,'data': related_data, 'form': form})

@login_required
def delete_assigned_subjects(request,assign_id):
    teacherCourses = get_object_or_404(TeacherCourses, tc_id=assign_id)
    if request.method == 'POST':
        teacherCourses.delete()
        messages.success(request,"Successfully deleted")
        return redirect('assign-teacher') 

    return render(request, 'delete-data.html', {
        'name': "subject assigned to teacher "+ teacherCourses.teacher.first_name,
        'related_items': {
            'dismiss subject': teacherCourses.subject.all(),
        },
    })

@login_required
def register_student(request, student_id=None):
    sem = request.GET.get('sem') 
    courses = Course.objects.all() 
    if not sem:
         return render(request, 'register_student.html', {
        'courses': courses,
        'sem_set': True,
       })
    students = StudentInfo.objects.select_related('user', 'address', 'contact')\
        .filter(sem=sem).all().order_by('-id')
    is_edit_mode = student_id is not None

    if is_edit_mode:
        student_instance = get_object_or_404(StudentInfo, pk=student_id)
        user_instance = student_instance.user
        contact_instance = student_instance.contact
        address_instance = student_instance.address
    else:
        student_instance = None
        user_instance = None
        contact_instance = None
        address_instance = None

    if request.method == 'POST':
        student_form = StudentForm(request.POST, request.FILES, instance=student_instance)
        contact_form = ContactForm(request.POST, instance=contact_instance)
        address_form = AddressForm(request.POST, instance=address_instance)
        user_form = user_email_form(request.POST, instance=user_instance)

        if student_form.is_valid() and contact_form.is_valid() and address_form.is_valid() and user_form.is_valid():
            firstName = request.POST.get('first_name')
            lastName = request.POST.get('last_name')
            email = request.POST.get('email')
            user = user_form.save(commit=False)
            if not user_instance:
                user.is_staff = False
                user.username = get_unique_user_id() 
                user.first_name = firstName
                user.last_name = lastName
                user.password = make_password(firstName)
            user.save()
            contact = contact_form.save()
            address = address_form.save()
            student = student_form.save(commit=False)
            student.user = user
            student.contact = contact
            student.address = address
            student.save()
            log_action(request.user, CHANGE if is_edit_mode else ADDITION, student)
            if not is_edit_mode:
              send_mail(
               'Account created',
               'We glad to welcome you in our college. Your username is:'+str(user.username)+' and password:'+str(firstName),
               settings.EMAIL_HOST_USER,
               [email],
               fail_silently=False,
              )
            messages.success(request, "Student details have been {}.".format("updated" if is_edit_mode else "created"))
            url = reverse('register-student')
            return redirect(f"{url}?sem={sem}")
        else:
            messages.error(request, "Please correct the form errors and try again.")
    else:
        student_form = StudentForm(instance=student_instance)
        contact_form = ContactForm(instance=contact_instance)
        address_form = AddressForm(instance=address_instance)
        user_form = user_email_form(instance=user_instance)
    
    semester = Semester.objects.filter(semester=sem).first()
    return render(request, 'register_student.html', {
        'student_form': student_form,
        'contact_form': contact_form,
        'address_form': address_form,
        'user_form': user_form,
        'students':students,
        'is_edit_mode': is_edit_mode,
        'student_id': student_id,
        'sem':sem,
        'select_course':semester.course.course_id,
        'courses':courses,
    })

@login_required
def delete_student(request,student_id):
    student = get_object_or_404(StudentInfo, id=student_id)
    studentFee = StudentFee.objects.filter(student=student).count()
    Attendance = StudentAttendance.objects.filter(student=student).count()
    account = User.objects.get(id=student.user_id)
    contacts = ContactInfo.objects.get(contact_id=student.contact_id)
    address = Address.objects.get(address_id=student.address_id)
    if request.method == 'POST':
        student.delete()
        address.delete()
        contacts.delete()
        account.delete()
        messages.success(request,"student Successfully deleted")
        return redirect('register-student') 
    related_items = {
            'students_attendance': Attendance,
            'Fee Details':studentFee,
            'User Account':StopIteration(account.username),
            'contacts':StopIteration(contacts.mobile_no,contacts.other_phone),
            'addresse': StopIteration(address.permanent_address,address.current_address),
        }
    return render(request,'delete-data.html',{'name':student.first_name+" "+student.last_name,'related_items':related_items})

@login_required
def student_attendance(request):
    sem = request.GET.get('sem') 
    course = None 
    courses = Course.objects.all() 
    current_date = timezone.now().date()
    pre_attendance = StudentAttendance.objects.select_related('student','sem').filter(attendance_date__date=current_date)
    if sem:
        course = Semester.objects.filter(sem_id=sem).values_list('course_id', flat=True).first()

    formDet = {
        'course': course, 
        'sem': sem 
    }

    return render(request, 'student_attendance.html', {'courses': courses, 'data': formDet,'pre_attendance':pre_attendance})

@login_required
def students_fee_manage(request):
    sem = request.GET.get('sem')
    student = request.GET.get('stud')
    courses = Course.objects.all()
    semester = Semester.objects.filter(semester=sem).first()
    students = StudentInfo.objects.filter(sem=sem)
    fee_records = StudentFee.objects.filter(semester_fee=semester)
    student_fee_amounts = {}
    student_fee_dates = {}
    pay = None
    for fee_record in fee_records:
       student_id = fee_record.student.id
       amount = int(fee_record.amount)
       formatted_date = fee_record.paid_date.strftime("%b %d, %Y")
       paid_date = f"{formatted_date} ({fee_record.amount} : {fee_record.invoice_num})"
       if student_id not in student_fee_dates:
        student_fee_dates[student_id] = []
       student_fee_dates[student_id].append(paid_date)
       if student_id in student_fee_amounts:
        student_fee_amounts[student_id] += amount
       else:
        student_fee_amounts[student_id] = amount
    if sem and not student:
        return render(request, 'fee_management.html', {
            'courses': courses,
            'students': students,
            'select_course': semester.course.course_id,
            'sem': sem,
            'student_fee_amounts': student_fee_amounts,
            'student_fee_dates':student_fee_dates,
        })
    if sem and student:
        feeForm = StudentFeeForm()
        if request.method == "POST":
            student_id = request.POST.get('student') 
            semest = request.POST.get('semester_fee') 
            amount = request.POST.get('amount') 
            invoice = request.POST.get('invoice_num')
            paymentMode = request.POST.get('payment_method')
            fee_record = StudentFee.objects.filter(student=student_id, semester_fee=semest, invoice_num=invoice).first()
            if fee_record:
                feeForm = StudentFeeForm(request.POST, instance=fee_record)
            else:
                feeForm = StudentFeeForm(request.POST)
            if feeForm.is_valid():
                fee_instance = feeForm.save(commit=False)
                fee_instance.submitted_by = request.user 
                fee_instance.save()  
                url = reverse('student-fee')
                return redirect(f"{url}?sem={sem}")
            else:
                if amount and semest and student_id and not invoice and paymentMode == 'e-sewa' and int(amount) > 999:
                  pay = send_payment_request(amount,semest,student_id)
                  if pay:
                    return render(request, 'fee_management.html', {
                        'courses': courses,
                        'students': students,
                        'select_course': semester.course.course_id,
                        'sem': sem,
                        'form': feeForm,
                        'student': student,
                        'student_fee_amounts': student_fee_amounts,
                        'student_fee_dates':student_fee_dates,
                        'pay':pay,
                       })
                      
        return render(request, 'fee_management.html', {
            'courses': courses,
            'students': students,
            'select_course': semester.course.course_id,
            'sem': sem,
            'form': feeForm,
            'student': student,
            'student_fee_amounts': student_fee_amounts,
            'student_fee_dates':student_fee_dates,
        })

    return render(request, 'fee_management.html', {'courses': courses})

def genSha256(key, message):
    key = key.encode('utf-8')
    message = message.encode('utf-8')
    hmac_sha256 = hmac.new(key, message, hashlib.sha256)
    digest = hmac_sha256.digest()
    signature = base64.b64encode(digest).decode('utf-8')
    return signature
 
@login_required
def send_payment_request(amount,sem,stud):
    SECRET_KEY = "8gBm/:&EnhH.1/q"
    transaction_uuid = str(uuid.uuid4())
    product_code = "EPAYTEST"
    amount = int(amount)
    taxAmount = 0
    total_amount = amount + taxAmount
    data_to_sign = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    payUrl = "https://rc-epay.esewa.com.np/api/epay/main/v2/form"
    data = {
        "amount": str(amount),
        "tax_amount": str(taxAmount),
        "total_amount": str(total_amount),
        "transaction_uuid": transaction_uuid,
        "product_code": product_code,
        "product_service_charge": 0,
        "product_delivery_charge": 0,
        "success_url": f"http://localhost:8000/payment/{sem}/{stud}/",
        "failure_url": f"http://localhost:8000/student-fee-management/?sem={sem}&stud={stud}",
        "signed_field_names": "total_amount,transaction_uuid,product_code",
        "signature": genSha256(SECRET_KEY, data_to_sign),
    }
    return {'payUrl': payUrl, 'data': data}

@login_required
def esewa_payment_verify(request,sem_id,stud_id):
    data = request.GET.get('data')
    decoded_bytes = base64.b64decode(data)
    decoded_string = decoded_bytes.decode('utf-8')
    decoded_json = json.loads(decoded_string)
    try:
       decoded_json = json.loads(decoded_string)
       transaction_code = decoded_json.get('transaction_code')
       total_amount = decoded_json.get('total_amount')
       total_amount = total_amount.replace(",", "")
       fee = StudentFee(
        invoice_num=transaction_code,
        student=StudentInfo.objects.get(id=stud_id),
        semester_fee=Semester.objects.get(sem_id=sem_id),
        amount=Decimal(total_amount),
        submitted_by=request.user
       )
       fee.save()
       user_info = StudentInfo.objects.filter(id=stud_id).first()
       email = user_info.user.email
       if email:
        send_mail(
            'Payment Successfull',
            'Thanks for your payment. This message is to inform we have got fee. Transaction Code: '+transaction_code+ ' Amount: '+total_amount,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
            )
       url = reverse('student-fee')
       return redirect(f"{url}?sem={sem_id}")
    except (json.JSONDecodeError, TypeError) as e:
        print("Error decoding JSON or invalid data:", e)

@login_required
def courses(request,course_id=None):
    course = Course.objects.annotate(semester_count=Count('semesters'))
    paginator = Paginator(course, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    paging = {
        'page_obj': page_obj,
    }
    is_edit_mode = course_id is not None
    if request.method == 'POST':
        if is_edit_mode:
            course_instance = get_object_or_404(Course, course_id=course_id)
            form = CourseForm(request.POST, instance=course_instance)
        else:
            form = CourseForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('courses') 
    else:
        form = CourseForm(instance=get_object_or_404(Course, course_id=course_id)) if is_edit_mode else CourseForm()

    related_data = {
        'is_edit_mode': is_edit_mode,
        'course_id' : course_id,
    }
    return render(request,'courses.html',{'paging':paging,'form':form,'data':related_data})

@login_required
def delete_course(request,course_id):
    course = get_object_or_404(Course, course_id=course_id)
    semester = Semester.objects.filter(course=course).count()
    subjects = CourseSubject.objects.filter(course=course).values_list('subject_name', flat=True)
    studentFee = StudentFee.objects.filter(semester_fee=semester).count()
    if request.method == 'POST':
        course.delete()
        messages.success(request,"Course Successfully deleted")
        return redirect('courses') 
    related_items ={
        'semesters':semester,
        'subjets': subjects,
        'studentFee':studentFee,
    }
    return render(request,'delete-data.html',{'name':course.course_name,'related_items':related_items})

@login_required
def subjects(request,course_id=None):
    courses = Course.objects.values('course_id','course_name')
    subjects = CourseSubject.objects.filter(course_id=course_id).order_by('sem') if course_id else None
    subjects_by_sem = {}
    subject_data = None
    semester_id = None

    if course_id and request.GET.get('semester'):
        semester_id = request.GET.get('semester')
        subjects = CourseSubject.objects.filter(course_id=course_id, sem_id=semester_id)
        
        subject_data = [{
            'subject_id': subject.sub_id,
            'subject_code': subject.subject_code,
            'subject_name': subject.subject_name,
            'full_marks': subject.full_marks,
            'pass_marks': subject.pass_marks,
            'credit_hours': subject.credit_hours,
        } for subject in subjects]

    if subjects:
        for subject in subjects:
            sem_id = subject.sem_id
            if sem_id not in subjects_by_sem:
                subjects_by_sem[sem_id] = {
                    'semester_name': subject.sem.semester,
                    'subjects': []
                }
            subjects_by_sem[sem_id]['subjects'].append(subject)

    if request.method == 'POST':
        course_id = request.POST.get('course_code')
        semester_id = request.POST.get('semester')

        subject_ids = request.POST.getlist('subject_id[]')
        subject_codes = request.POST.getlist('subject_code[]')
        subject_names = request.POST.getlist('subject_name[]')
        full_marks = request.POST.getlist('full_marks[]')
        pass_marks = request.POST.getlist('pass_marks[]')
        credit_hours = request.POST.getlist('credit_hours[]')

        try:
            course = Course.objects.get(course_id=course_id)
            semester = Semester.objects.get(sem_id=semester_id)
        except (Course.DoesNotExist, Semester.DoesNotExist):
            messages.error(request, "Invalid course or semester")
            return render_subjects_template(request, courses, subjects_by_sem, course_id, subject_data, semester_id)

        if not any(subject_codes):  
            messages.error(request, "At least one subject must be submitted.")
            return render_subjects_template(request, courses, subject_codes, subject_names, full_marks, pass_marks, credit_hours, course_id, semester_id)

        for i in range(len(subject_codes)):
            if not (subject_codes[i] and subject_names[i] and full_marks[i] and pass_marks[i] and credit_hours[i]):
                messages.error(request, f"All fields are required for subject {i + 1}")
                return render_subjects_template(request, courses, subjects_by_sem, course_id, subject_data, semester_id)

            subject_id = subject_ids[i] if i < len(subject_ids) and subject_ids[i] else None
            if subject_id: 
                try:
                    existing_subject = CourseSubject.objects.get(sub_id=subject_id)
                    existing_subject.subject_code = subject_codes[i]
                    existing_subject.subject_name = subject_names[i]
                    existing_subject.credit_hours = credit_hours[i]
                    existing_subject.full_marks = full_marks[i]
                    existing_subject.pass_marks = pass_marks[i]
                    existing_subject.save()
                except CourseSubject.DoesNotExist:
                    messages.error(request, f"Subject {i + 1} does not exist.")
                    return render_subjects_template(request, courses, subjects_by_sem, course_id, subject_data, semester_id)
            else: 
                CourseSubject.objects.create(
                    subject_code=subject_codes[i],
                    subject_name=subject_names[i],
                    course=course,
                    sem=semester,
                    credit_hours=credit_hours[i],
                    full_marks=full_marks[i],
                    pass_marks=pass_marks[i]
                )

        messages.success(request, "Subjects added successfully")
        return redirect('subjects')

    return render_subjects_template(request, courses, subjects_by_sem, course_id, subject_data, semester_id)

@login_required
def render_subjects_template(request, courses, subjects_by_sem, course_id, subject_data=None, selected_semester_id=None):
    return render(request, 'subjects.html', {
        'courses': courses,
        'subjects_by_sem': subjects_by_sem,
        'course_id': course_id,
        'subject_data': subject_data or [], 
        'selected_semester_id': selected_semester_id,
    })

def delete_subject(request,sub_id):
    subject = get_object_or_404(CourseSubject,sub_id=sub_id)
    teacherCourse = TeacherCourses.objects.filter(subject=subject).count()
    related_items ={
        "assignedCoursesToTeacher":teacherCourse,
    }
    if request.method == 'POST':
        subject.delete()
        messages.success(request,"Subject Successfully deleted")
        return redirect('subjects') 
    return render(request,'delete-data.html',{'name':subject.course.course_name+"-"+subject.subject_name,'related_items':related_items})

@login_required
def scanner(request):
    return render(request,'scanner.html')