from django import template

register = template.Library()

@register.filter
def dict_item(dictionary, key):
    """Template filter to get dictionary item by key"""
    if dictionary and key:
        return dictionary.get(key, {})
    return {}

@register.filter  
def get_item(dictionary, key):
    """Get item from dictionary"""
    if hasattr(dictionary, 'get'):
        return dictionary.get(key)
    return None

@register.filter
def multiply(value, arg):
    """Multiply filter"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, total):
    """Calculate percentage"""
    try:
        if float(total) == 0:
            return 0
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError):
        return 0