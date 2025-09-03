from django import forms
from dmrism.models.item import Library

class ManifestationCreateForm(forms.Form):
    temporary_title = forms.CharField(label='Temporärer Titel', max_length=255, required=False)
    signature = forms.CharField(label='Signatur', max_length=255)
    library = forms.ModelChoiceField(queryset=Library.objects.all(), label='Bibliothek', empty_label="Bibliothek auswählen", widget=forms.Select(attrs={'class': 'select select-bordered w-full'}))
