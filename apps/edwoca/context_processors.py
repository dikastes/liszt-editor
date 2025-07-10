def entity_type(request):
    return {'entity_type': getattr(request, 'entity_type', None)}
