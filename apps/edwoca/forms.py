from django.forms.renderers import TemplatesSetting
from django.forms import ModelForm
from .models import Work, WorkTitle

class EdwocaFormRenderer(TemplatesSetting):
    form_template_name = 'edwoca/form_snippet.html'

class WorkTitleForm(ModelForm):
    class Meta:
        model = WorkTitle
        fields = '__all__'

    #def init(self, *args, **kwargs):

