from django.forms.renderers import TemplatesSetting

class EdwocaFormRenderer(TemplatesSetting):
    form_template_name = 'edwoca/form_snippet.html'
