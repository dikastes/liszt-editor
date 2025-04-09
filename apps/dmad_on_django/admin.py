from django.contrib import admin
from .models import Person, PersonName, Place, PlaceName

# Register your models here.
class PlaceNameInline(admin.TabularInline):
    model = PlaceName

class PersonNameInline(admin.TabularInline):
    model = PersonName

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    inlines = [PlaceNameInline]

@admin.action(description="Update these entities from the GND")
def update_from_gnd(modeladmin, request, queryset):
    for entity in queryset:
        entity.fetch_raw()
        entity.update_from_raw()
        entity.save()

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = [PersonNameInline]
    actions = [update_from_gnd]
