from django.contrib import admin
from .models import Person, PersonName, Place, PlaceName, SubjectTerm, SubjectTermName, Status, GNDSubjectCategory, Work, WorkName
# Register your models here.
class PlaceNameInline(admin.TabularInline):
    model = PlaceName

class PersonNameInline(admin.TabularInline):
    model = PersonName

class SubjectTermInline(admin.TabularInline):
    model = SubjectTermName

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

@admin.register(SubjectTerm)
class SubjectTermAdmin(admin.ModelAdmin):
    inlines = [SubjectTermInline]
    actions = [update_from_gnd]
    readonly_fields = ['show_parents']

    def show_parents(self, obj):
        return ", ".join(p.__str__() for p in obj.parent_subjects.all())

    show_parents.short_description = "Parent subject list"

@admin.register(GNDSubjectCategory)
class GNDSubjectCategoryAdmin(admin.ModelAdmin):
    pass

class WorkInline(admin.TabularInline):
    model = WorkName

@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    inlines = [WorkInline]
    actions = [update_from_gnd]

    

    
