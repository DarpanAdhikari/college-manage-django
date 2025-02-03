from django import template
from django.urls import resolve

register = template.Library()

@register.simple_tag
def active(request, *patterns):
    try:
        # Get the URL name from the request path
        url_name = resolve(request.path).url_name
    except:
        # In case resolve fails, return an empty string
        return ''
    
    # Check if the URL name matches any of the provided patterns
    for pattern in patterns:
        if pattern == url_name:
            return 'active'
    
    return ''
