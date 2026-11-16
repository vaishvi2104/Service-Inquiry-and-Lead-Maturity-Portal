"""
Template tags and filters for Start-Up Sahay dashboard.
Provides query string manipulation for pagination while preserving search and filters.
"""
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    """
    Update or append GET parameters to preserve search queries and filters during pagination.
    Usage: {% query_transform page=leads.next_page_number %}
    """
    request = context.get('request')
    if not request:
        return ''
    query_dict = request.GET.copy()
    for key, value in kwargs.items():
        if value is not None and value != '':
            query_dict[key] = value
        elif key in query_dict:
            del query_dict[key]
    encoded = query_dict.urlencode()
    return f"?{encoded}" if encoded else '?'
