from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm,AdminPasswordChangeForm,AuthenticationForm
from django.contrib.auth import logout, update_session_auth_hash,authenticate,login as auth_login
from django.contrib import messages
from django.urls import reverse
from .form import CustomUserChangeForm, GroupForm
from django.contrib.auth.models import Permission, Group, User
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import ADDITION, CHANGE, DELETION
from django.utils.timezone import now
from accounts.utils.logging_utils import log_action
import qrcode,json
from io import BytesIO
import base64
from django.core.exceptions import PermissionDenied
from PIL import Image
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styledpil import StyledPilImage

# Create your views here.
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        checkuser = authenticate(username=username, password=pass1)
        
        if checkuser is not None:
            auth_login(request, checkuser)
            messages.success(request, "Logged In Successfully!!")
            next_url = request.GET.get('next', 'manage-accounts')
            return redirect(next_url)
        else:
            messages.error(request, "Bad Credentials!!")
            return render(request, 'accounts/login.html', {
                'username': username
            })
    return render(request, 'accounts/login.html')

@login_required
@permission_required('auth.view_user', raise_exception=True)
def manage_accounts(request):
    users = User.objects.all().prefetch_related('groups')
    log_entries = LogEntry.objects.all().select_related('content_type', 'user').order_by('-action_time')[:10]
    return render(request,'users.html',{'users':users,'log':log_entries})

@login_required
@permission_required('auth.change_user', raise_exception=True)
def edit_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            obj = form.save()
            log_action(request.user, CHANGE, obj)
            return redirect('manage-accounts')
        else:
            messages.error(request,"please fix given error to fix problem")
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'edit-user.html', {'form': form, 'username': user.username,'user_id':user_id})

@login_required
@permission_required('auth.view_user', raise_exception=True)
def get_qr_code(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_data = {
     "Username": user.username,
     "First Name": user.first_name,
     "Last Name": user.last_name,
     "Email": user.email
    }
    qr_data = json.dumps(user_data)
    qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=7,
    border=5
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer())
    logo_path = 'media/site-default/logo.png'
    logo = Image.open(logo_path)
    logo_size = 100
    logo = logo.resize((logo_size, logo_size))
    qr_width, qr_height = img.size
    logo_position = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
    img.paste(logo, logo_position, mask=logo) 
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return render(request, 'view-qr-code.html', {
        'user': user,
        'qr_code_base64': img_base64
    })

@login_required
@permission_required('auth.delete_user', raise_exception=True)
def delete_user(request,user_id):
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        user.delete()
        log_action(request.user, DELETION, user)
        messages.success(request, 'User and all related data were successfully deleted!')
        return redirect('manage-accounts')
    related_permissions = Permission.objects.filter(user=user)
    related_groups = user.groups.all()
    related_data = {
        'user': user,
        'permissions': related_permissions,
        'groups': related_groups
    }
    
    return render(request, 'user-delete-confirm.html', related_data)

@login_required
@permission_required('auth.change_user', raise_exception=True)
def change_password(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = AdminPasswordChangeForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            if request.user == user:
                update_session_auth_hash(request, user)
            messages.success(request, 'Password was successfully updated!')
            return redirect('edit-user', user_id=user_id)
    else:
        form = AdminPasswordChangeForm(user=user)
    
    return render(request, 'change-user-password.html', {'form': form})

@login_required
@permission_required('auth.view_group', raise_exception=True)
def manage_group(request):
    groups = Group.objects.all()
    log_entries = LogEntry.objects.all().select_related('content_type', 'user').order_by('-action_time')[:10]
    return render(request,'groups.html',{'groups': groups,'log':log_entries})

@login_required
@permission_required('auth.add_group', raise_exception=True)
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            obj = form.save()
            log_action(request.user, ADDITION, obj)
            messages.success(request, 'Group Created successfully!')
            return redirect('manage-groups')
    else:
        form = GroupForm()
    return render(request, 'group-creation.html', {'form': form})

@login_required
@permission_required('auth.change_group', raise_exception=True)
def edit_group(request,group_id):
    group = get_object_or_404(Group, pk=group_id)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            log_action(request.user, CHANGE, group)
            return redirect('manage-groups')
    else:
        form = GroupForm(instance=group)
    return render(request, 'edit-group.html', {'form': form})

@login_required
@permission_required('auth.delete_group', raise_exception=True)
def delete_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    
    if request.method == 'POST':
        group_name = group.name  
        group.delete() 
        log_action(request.user, DELETION, group)
        messages.success(request, f'Group "{group_name}" deleted successfully!')
        return redirect('manage-groups')
    
    permissions = group.permissions.all()
    relate_info = {
        'group_name': group.name, 
        'permissions': permissions
    }

    return render(request, 'delete-group.html', relate_info)

@login_required
def user_change_password(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.user != user and not request.user.is_superuser:
        raise PermissionDenied
    if request.method == 'POST':
        form = PasswordChangeForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            if request.user == user:
                update_session_auth_hash(request, user) 
            messages.success(request, 'Password was successfully updated!')
            return redirect('edit-user', user_id=user_id)
    else:
        form = PasswordChangeForm(user=user)
    
    return render(request, 'change-user-password.html', {'form': form})

def user_profile(request,user_id):
    user = get_object_or_404(User,username=user_id)
    return render(request,'user-profile.html',{'user':user})

def logout_view(request):
    if request.method == 'POST':
       logout(request)
    return redirect(reverse('index'))

# default login system------------------------------------------------

# def login(request):
#     if request.method == 'POST':
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             return redirect('dashboard')
#     else:
#         form = AuthenticationForm()
#     return render(request,'accounts/login.html',{'form':form})

# def register(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user) 
#             return redirect('dashboard')
#     else:
#         form = UserCreationForm()
#     return render(request,'accounts/register.html',{'form':form})