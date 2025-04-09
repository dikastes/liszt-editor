import requests
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.shortcuts import render, redirect
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from json import dumps


from . models import ZotItem
from . zot_utils import items_to_dict, create_zotitem, count_zotitems, get_last_version


library_id = settings.Z_ID
library_type = settings.Z_LIBRARY_TYPE
api_key = settings.Z_API_KEY
bulk_size = 50


class Dashboard(ListView):
    model = ZotItem
    paginate_by = 20
    template_name = 'bib/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count'] = ZotItem.objects.all().count()
        return context

def dashboard_info(request):
    context = {}
    count = ZotItem.objects.all().count()
    first_object = ZotItem.objects.all()[:1].get()
    since = first_object.zot_version
    version = get_last_version(library_id, library_type, api_key)
    context['new_items'] = count_zotitems(library_id, library_type, api_key) - count
    context['updates'] = version - since

    return JsonResponse(context)

def sync_zotero(request):
    """ renders a simple template with a button to trigger sync_zotero_action function """
    context = {}
    return render(request, 'bib/synczotero.html', context)


def delete(request):
    ZotItem.objects.all().delete()
    return redirect('bib:dashboard')


def import_complete(request):
    count = count_zotitems(library_id, library_type, api_key)
    bulks = [ reverse('bib:import_bulk', kwargs={'bulk': bulk}) for bulk in range((count // bulk_size) + 1) ]
    context = {
            'count': count,
            'bulks': dumps(bulks)
        }
    return render(request, 'bib/import.html', context)


def import_bulk(request, bulk):
    items = items_to_dict(library_id, library_type, api_key, limit=bulk_size, start=bulk*bulk_size)
    for x in items['bibs']:
        temp_item = create_zotitem(x)
    return HttpResponse('')


@login_required
def update_zotitems(request):
    """ fetches all items with higher version number than the highest stored in db """
    context = {}
    context["saved"] = []
    limit = None
    since = None
    context["books_before"] = ZotItem.objects.all().count()
    first_object = ZotItem.objects.all()[:1].get()
    since = first_object.zot_version
    items = items_to_dict(library_id, library_type, api_key, limit=limit, since_version=since)
    for x in items['bibs']:
        temp_item = create_zotitem(x)
        context["saved"].append(temp_item)
    context["books_after"] = ZotItem.objects.all().count()
    return render(request, 'bib/synczotero_action.html', context)


def update(request):
    return redirect('bib:dashboard')
