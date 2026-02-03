import dominate.tags as tags
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea, CharField, DateTimeField, SelectDateWidget, BooleanField
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.utils.safestring import mark_safe
from dominate.util import raw
from dmad_on_django.forms import SearchForm
from dmad_on_django.models import Period


class SimpleFormMixin:
    text_area_classes = 'textarea textarea-bordered w-full bg-white border-black'
    text_input_classes = 'input input-bordered w-full border-black bg-white'
    text_label_classes = 'input input-bordered w-full border-black bg-white flex gap-2 items-center'
    autocomplete_classes = 'autocomplete-select select select-bordered w-full border-black bg-white'
    select_classes = 'select select-bordered w-full border-black bg-white'
    toggle_classes = 'toggle'
    palette_classes = 'flex w-full gap-10 my-5'
    form_control_classes = 'form-control'
    palette_form_control_classes = 'form-control flex-1'
    label_classes = 'label'
    toggle_label_classes = 'cursor-pointer label'
    label_text_classes = 'label-text'

    def as_daisy(self):
        form = tags.div()
        for field in self.Meta.fields:
            wrap = tags.label(cls='form-control')
            label_div = tags.div(cls='label')
            field_label = tags.span(self[field].label, cls='label-text')
            label_div.add(field_label)
            wrap.add(label_div)
            wrap.add(raw(str(self[field])))
            form.add(wrap)

        return mark_safe(str(form))


class TitleForm(ModelForm):
    class Meta:
        fields = ['title', 'language', 'status', 'id']
        widgets = {
                'title': TextInput( attrs = {
                        'class': 'grow w-full'
                    }),
                'language': Select( attrs = {
                        'class': 'autocomplete-select select select-bordered w-full'
                    }),
                'status': Select( attrs = {
                        'class': 'select w-full select-bordered'
                    }),
                'id': HiddenInput(),
                'DELETE': CheckboxInput( attrs = {
                        'class': 'flex-0'
                    })
            }

    def as_daisy(self):
        class_name = self.Meta.model.__name__.lower().replace('title', '')
        form = div(cls='mb-10')

        if self.instance.pk:
           form.add(raw(str(self['id'])))
        form.add(raw(str(self[class_name])))

        title_field = self['title']
        lang_field = self['language']
        status_field = self['status']

        title_field_label = label(title_field.label, cls='input input-bordered flex items-center gap-2 my-5')
        title_field_label.add(raw(str(title_field)))

        status_container = div(cls='flex-1')
        status_container.add(raw(str(status_field)))

        lang_container = div(cls='flex-1')
        lang_container.add(raw(str(lang_field)))

        palette = div(cls='flex flex-rows w-full gap-10 my-5')
        palette.add(lang_container)
        palette.add(status_container)

        # checken ob das form initialisiert ist, sonst kein delete-button
        if 'DELETE' in self.fields and self.instance.pk:
            del_field = self['DELETE']
            del_field_label = label(del_field.label, cls='input input-bordered flex-0 flex items-center gap-2')
            del_field_label.add(raw(str(del_field)))
            palette.add(del_field_label)

        form.add(title_field_label)
        form.add(palette)

        return mark_safe(str(form))


class SkipEmptyTitleFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue

            if not form.cleaned_data.get('title'):
                form.cleaned_data['DELETE'] = True

            raw_title = form.cleaned_data.get('title', '').strip()
            if not raw_title:
                form.cleaned_data['DELETE'] = True


class ContributorForm(ModelForm):
    class Meta:
        fields = [ 'person', 'role', 'id' ]
        widgets = {
                'person': HiddenInput(),
                'role': Select( attrs = {
                        'class': 'select w-full select-bordered'
                    }),
                'id': HiddenInput(),
                'DELETE': CheckboxInput( attrs = {
                        'class': 'flex-0'
                    })
            }

    def as_daisy(self):
        form = div(cls='mb-10')

        role_container = div(cls='flex-1')
        role_container.add(raw(str(self['role'])))

        form.add(role_container)

        return mark_safe(str(form))


class CommentForm(ModelForm, SimpleFormMixin):
    class Meta:
        fields = ['private_comment', 'public_comment']
        widgets = {
                'private_comment': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    }),
                'public_comment': Textarea( attrs = {
                        'class': SimpleFormMixin.text_area_classes
                    })
            }


class BaseBibForm(ModelForm):
    class Meta:
        fields = [ 'bib', 'id' ]
        widgets = {
                'bib': Select( attrs = {
                        'class': 'autocomplete-select select select-bordered w-full'
                    }),
                'id': HiddenInput()
            }

    def as_daisy(self):
        form = div(cls='mb-10')

        if self.instance.pk:
           form.add(raw(str(self['id'])))

        bib_field = self['bib']

        bib_container = div(cls='flex-1')
        bib_container.add(raw(str(bib_field)))

        form.add(bib_container)

        return mark_safe(str(form))


class EdwocaSearchForm(SearchForm):
    q = CharField(required=False, widget=TextInput())


class HandwritingForm(ModelForm):
    class Meta:
        fields = ['medium', 'dubious_writer']
        widgets = {
                'medium': TextInput( attrs = {
                        'class': 'grow',
                        'form': 'form'
                    }),
                'dubious_writer': CheckboxInput( attrs = {
                        'class': 'toggle',
                        'form': 'form'
                    })
            }

    def as_daisy(self):
        form = tags.div(cls='flex gap-5 my-5 items-center')

        # Medium field
        medium_field = self['medium']
        medium_label = tags.label(medium_field.label, _for=medium_field.id_for_label, cls='input input-bordered border-black bg-white flex items-center gap-2 flex-1')
        medium_label.add(raw(str(medium_field)))
        form.add(medium_label)

        # Dubious writer toggle
        dubious_writer_field = self['dubious_writer']
        dubious_writer_label = tags.label(cls='label cursor-pointer flex items-center gap-2')
        dubious_writer_label.add(tags.span(dubious_writer_field.label, cls='label-text'))

        dubious_writer_field.field.widget.attrs.update({
            'onchange': 'this.form.submit()',
            'form': 'form'
        })
        dubious_writer_label.add(raw(str(dubious_writer_field)))

        form.add(dubious_writer_label)

        return mark_safe(str(form))


class DateFormMixin:
    # these properties need to be copied to every inheriting form class
    kwargs = {
            'years': range(settings.EDWOCA_FIXED_DATES['birth']['year'], 1900),
            'attrs': {
                'class': SimpleFormMixin.select_classes,
                'form': 'form'
            }
        }
    not_before = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    not_after = DateTimeField(widget = SelectDateWidget(**kwargs), required = False)
    display = CharField(required=False, widget = TextInput( attrs = { 'class': 'grow'}))
    inferred = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)
    assumed = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.is_bound:
            return

        period = getattr(self.instance, 'period', None)
        if period:
            self.initial.update({
                'not_before': period.not_before,
                'not_after': period.not_after,
                'display': period.display,
                'inferred': period.inferred,
                'assumed': period.assumed
            })

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Ensure period exists or create it
        if not instance.period:
            instance.period = Period.objects.create()

        period_instance = instance.period
        period_instance.not_before = self.cleaned_data['not_before']
        period_instance.not_after = self.cleaned_data['not_after']
        period_instance.display = self.cleaned_data['display']
        period_instance.inferred = self.cleaned_data['inferred']
        period_instance.assumed = self.cleaned_data['assumed']

        if commit:
            period_instance.save()
            instance.save()
        else:
            self._pending_save_period = period_instance

        return instance

    def get_date_div(self):
        date_div = tags.div()
        not_before_field = self['not_before']
        not_after_field = self['not_after']
        display_field = self['display']
        #history_field = self['history']

        not_before_container = tags.label(cls='form-control flex-0')
        not_before_label = tags.div(_('not before'), cls='label-text')
        not_before_selects = tags.div(cls='flex')
        not_before_selects.add(raw(str(not_before_field)))
        not_before_container.add(not_before_label)
        not_before_container.add(not_before_selects)
        if not_before_field.errors:
            not_before_container.add(div(span(not_before_field.errors, cls='text-primary text-sm'), cls='label'))

        not_after_container = tags.label(cls='form-control flex-0')
        not_after_label = tags.div(_('not after'), cls='label-text')
        not_after_selects = tags.div(cls='flex')
        not_after_selects.add(raw(str(not_after_field)))
        not_after_container.add(not_after_label)
        not_after_container.add(not_after_selects)
        if not_after_field.errors:
            not_after_container.add(div(span(not_after_field.errors, cls='text-primary text-sm'), cls='label'))

        calculate = 'calculate'
        clear = 'clear'
        postfix = 'machine-readable-date'
        calculate_name = f'{self.prefix}-{calculate}-{postfix}' if self.prefix else f'{calculate}-{postfix}'
        calculate_input = tags._input(type='submit', cls='btn btn-outline flex-0', form='form', value=_('calculate'), name=calculate_name)
        clear_name = f'{self.prefix}-{clear}-{postfix}' if self.prefix else f'{clear}-{postfix}'
        clear_input = tags._input(type='submit', cls='btn btn-outline btn-primary flex-0', form='form' ,value=_('clear'), name=clear_name)

        display_container = tags.label(_('standardized date'), _for = display_field.id_for_label, cls=SimpleFormMixin.text_label_classes + ' flex-1')
        display_container.add(raw(str(display_field)))
        if display_field.errors:
            display_container.add(div(span(display_field.errors, cls='text-primary text-sm'), cls='label'))
        display_palette = tags.div(cls='flex flex-rows w-full gap-10 my-5 items-end')
        display_palette.add(display_container)

        assumed_field = self['assumed']
        assumed_label = tags.label(cls='label cursor-pointer flex items-center gap-2')
        assumed_label.add(tags.span(_(assumed_field.label.lower()), cls='label-text'))
        assumed_label.add(raw(str(assumed_field)))

        inferred_field = self['inferred']
        inferred_label = tags.label(cls='label cursor-pointer flex items-center gap-2')
        inferred_label.add(tags.span(_(inferred_field.label.lower()), cls='label-text'))
        inferred_label.add(raw(str(inferred_field)))

        period_palette = tags.div(cls='flex flex-rows w-full gap-10 my-5 items-end')
        period_palette.add(not_before_container)
        period_palette.add(not_after_container)
        period_palette.add(tags.div(cls='flex-1'))

        documentation_label = ''
        if self.instance.period and self.instance.period.assumed:
            if self.instance.period.inferred:
                documentation_label = _('date inferred assumed')
            else:
                documentation_label = _('date assumed')
        else:
            if self.instance.period and self.instance.period.inferred:
                documentation_label = _('date inferred')
            else:
                documentation_label = _('date as documented')

        control_palette = tags.div(cls='flex flex-rows w-full gap-10 my-5 items-center')
        control_palette.add(tags.div(cls='flex-1'))
        control_palette.add(tags.div(documentation_label, cls='flex-0 mr-10'))
        control_palette.add(inferred_label)
        control_palette.add(assumed_label)
        control_palette.add(tags.div(cls='flex-1'))
        control_palette.add(calculate_input)
        control_palette.add(clear_input)

        date_div.add(display_palette)
        date_div.add(period_palette)
        date_div.add(control_palette)

        return date_div
