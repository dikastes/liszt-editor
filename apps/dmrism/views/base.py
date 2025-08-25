from django.shortcuts import redirect

def index(request):
    return redirect('dmrism:manifestation_search')
