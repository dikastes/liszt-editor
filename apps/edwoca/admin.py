from django.contrib import admin
from .models import WorkTitle, Work

# Register your models here.
class WorkTitleInline(admin.TabularInline):
    model = WorkTitle

class WorkAdmin(admin.ModelAdmin):
    inlines = [WorkTitleInline]

admin.site.register(Work, WorkAdmin)
