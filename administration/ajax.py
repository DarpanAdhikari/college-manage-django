from django.http import JsonResponse,HttpResponseNotFound,HttpResponse
from django.template.loader import render_to_string
from .models import CourseSubject,Semester, TeacherInfo, TeacherAttendance,StudentAttendance,StudentInfo
from django.contrib.auth.models import User
import json
from django.utils import timezone
from django.shortcuts import get_object_or_404

def semester_request(request):
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        if course_id:
           semesters = Semester.objects.filter(course_id=course_id).values('sem_id', 'semester')
        else:
           semesters = []
        return JsonResponse({'semesters': list(semesters)})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def teacherAttendance(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8'))
            teacher_data = body.get('teacher') 
            if isinstance(teacher_data, str):
                teacher_data = json.loads(teacher_data) 
            if teacher_data:
                username = teacher_data.get('Username')
                current_date = timezone.now().date()
                if not username:
                    return JsonResponse({'error': 'Invalid request'}, status=400)
                userdata = User.objects.get(username=username)
                teacher = TeacherInfo.objects.get(user=userdata)
                attendance_exists = TeacherAttendance.objects.filter(teacher=teacher, attendance_date__date=current_date).exists()
                if not attendance_exists:
                    attendance = TeacherAttendance.objects.create(teacher=teacher)
                    response_data = {
                    'name': f"{attendance.teacher.first_name} {attendance.teacher.middle_name or ''} {attendance.teacher.last_name}".strip(),
                    'username': attendance.teacher.user.username,
                    'date': attendance.attendance_date.strftime("%b %d, %Y %I:%M %p")
                    }
                    return JsonResponse(response_data)

            return JsonResponse({'error': 'No teacher data provided'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except TeacherInfo.DoesNotExist:
            return JsonResponse({'error': 'Teacher info not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': 'An internal server error occurred'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
    
def studentAttendance(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8'))
            student_data = body.get('student')
            course = body.get('course')
            semester = body.get('sem')

            if not student_data or not course or not semester:
                return JsonResponse({'error': 'Incomplete data'}, status=400)

            username = student_data.get('Username')
            current_date = timezone.now().date()
            if not username:
                return JsonResponse({'error': 'Invalid request'}, status=400)
            userdata = get_object_or_404(User, username=username)
            studentInfo = get_object_or_404(StudentInfo, user=userdata)
            semesterid = get_object_or_404(Semester, sem_id = semester)

            attendance_exists = StudentAttendance.objects.filter(student=studentInfo, attendance_date__date=current_date).exists()

            if not attendance_exists and str(studentInfo.sem).strip() == str(semesterid.sem_id).strip():
                attendance = StudentAttendance.objects.create(student=studentInfo, sem=semesterid)
                response_data = {
                    'name': f"{attendance.student.first_name} {attendance.student.middle_name or ''} {attendance.student.last_name}".strip(),
                    'username': attendance.student.user.username,
                    'date': attendance.attendance_date.strftime("%b %d, %Y %I:%M %p")
                }
                return JsonResponse(response_data)

            return JsonResponse({'error': 'Attendance already exists for today'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
