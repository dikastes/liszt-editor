from django.contrib import admin
from .models import Manifestation, Item

# Register your models here.
class ManifestationAdmin(admin.ModelAdmin):
    model = Manifestation

class ItemAdmin(admin.ModelAdmin):
    model = Item

admin.site.register(Manifestation, ManifestationAdmin)
admin.site.register(Item, ItemAdmin)
