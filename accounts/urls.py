from django.urls import path
from . import views

urlpatterns = [
    path('manage-accounts/',views.manage_accounts,name='manage-accounts'),
    path('view-qr/<int:user_id>/',views.get_qr_code,name='view-qr-code'),
    path('edit-user/<int:user_id>/',views.edit_user,name='edit-user'),
    path('delete/<int:user_id>/',views.delete_user,name='delete-user'),
    path('password/<int:user_id>/',views.change_password,name='change-password'),
    path('user/password/<int:user_id>/',views.user_change_password,name='user-change-password'),
    path('manage-group/',views.manage_group,name='manage-groups'),
    path('create-group/',views.create_group,name='create-group'),
    path('edit-group/<int:group_id>/',views.edit_group,name='edit-group'),
    path('delete-group/<int:group_id>/',views.delete_group,name='delete-group'),
    path('login/',views.login,name='login'),
    path('profile/<str:user_id>/',views.user_profile,name='user-profile'),
    path('logout/',views.logout_view, name='logout'),
    # path('register/',views.register,name='register'),
]
