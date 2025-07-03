from django.urls import resolve

def current_app_name(request):
    try:
        return {'current_app_name': request.resolver_match.app_name}
    except AttributeError:
        return {'current_app_name': None}
