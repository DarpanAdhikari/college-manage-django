from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType

def log_action(user, action_flag, content_object):
    content_type = ContentType.objects.get_for_model(content_object)
    LogEntry.objects.create(
        user=user,
        content_type=content_type,
        object_id=content_object.pk,
        object_repr=str(content_object),
        action_flag=action_flag,
        change_message=f'{action_flag} action performed'
    )
