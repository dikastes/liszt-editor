import dominate.tags as tags
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea, CharField, DateField, SelectDateWidget, BooleanField, TypedChoiceField, RadioSelect
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.utils.safestring import mark_safe
from dominate.util import raw
from dmad_on_django.forms import SearchForm
from dmad_on_django.models import Period
from dominate.tags import div, label, span


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
    toggle_label_classes = 'cursor-pointer label flex gap-2'
    toggle_inverted_classes = 'cursor-pointer label justify-start gap-5'
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
        fields = [
                'location',
                'location_type'
            ]
        widgets = {
                'location': TextInput( attrs = {
                        'class': SimpleFormMixin.text_input_classes,
                        'form': 'form'
                    }),
                'location_type': Select( attrs = {
                        'class': SimpleFormMixin.select_classes,
                        'form': 'form'
                    })
            }

    def as_daisy(self):
        form = div()

        location_field = self['location']
        location_type_field = self['location_type']

        with form:
            # palette
            with div(cls=SimpleFormMixin.palette_classes):
                with label(cls=SimpleFormMixin.palette_form_control_classes):
                    with div(cls=SimpleFormMixin.label_classes):
                        span(_(location_type_field.label), cls=SimpleFormMixin.label_text_classes)
                    raw(str(location_type_field))
                with label(cls=SimpleFormMixin.palette_form_control_classes):
                    with div(cls=SimpleFormMixin.label_classes):
                        span(_(location_field.label), cls=SimpleFormMixin.label_text_classes)
                    raw(str(location_field))

        for hidden in self.hidden_fields():
            hidden.field.widget.attrs['form'] = 'form'
            form.add(raw(str(hidden)))

        return mark_safe(str(form))


class EdwocaSearchForm(SearchForm):
    q = CharField(required=False, widget=TextInput())


class HandwritingForm(ModelForm):
    class Meta:
        fields = ['medium', 'dubious_writer']
        widgets = {
                'medium': TextInput( attrs = {
                        'class': SimpleFormMixin.text_input_classes,
                        'form': 'form'
                    }),
                'dubious_writer': CheckboxInput( attrs = {
                        'class': 'toggle',
                        'form': 'form'
                    })
            }

    def as_daisy(self):
        form = tags.div(cls='flex gap-5 items-end')

        medium_field = self['medium']
        dubious_writer_field = self['dubious_writer']

        dubious_writer_field.field.widget.attrs.update({
            'onchange': 'this.form.submit()',
            'form': 'form'
        })

        with form:
            with tags.label(cls='flex-1'):
                with tags.div(cls=SimpleFormMixin.label_classes):
                    tags.span(_(medium_field.label), cls=SimpleFormMixin.label_text_classes)
                raw(str(medium_field))
            with tags.label(cls=SimpleFormMixin.toggle_label_classes + ' flex-0 mb-1 gap-2'):
                tags.span(_(dubious_writer_field.label))
                raw(str(dubious_writer_field))

        #medium_label = tags.label(medium_field.label, _for=medium_field.id_for_label, cls='input input-bordered border-black bg-white flex items-center gap-2 flex-1')
        #medium_label.add(raw(str(medium_field)))
        #form.add(medium_label)

        # Dubious writer toggle
        #dubious_writer_label = tags.label(cls='label cursor-pointer flex items-center gap-2')
        #dubious_writer_label.add(tags.span(dubious_writer_field.label, cls='label-text'))

        #dubious_writer_label.add(raw(str(dubious_writer_field)))

        #form.add(dubious_writer_label)

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
    not_before = DateField(widget = SelectDateWidget(**kwargs), required = False)
    not_after = DateField(widget = SelectDateWidget(**kwargs), required = False)
    display = CharField(required=False, widget = TextInput( attrs = { 'class': SimpleFormMixin.text_input_classes}))
    inferred = TypedChoiceField(
            choices = ((False, _('based on source')), (True, _('inferred'))),
            coerce = lambda x: x == 'True',
            widget = RadioSelect(
                    attrs = { 'class': 'radio', 'form': 'form'}
                ),
            required = False
        )
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
        period_instance.inferred = self.cleaned_data['inferred'] or False
        period_instance.assumed = self.cleaned_data['assumed']

        period_instance.save()
        instance.save()

        return instance

    def get_date_div(self):
        date_div = tags.div()
        not_before_field = self['not_before']
        not_after_field = self['not_after']
        display_field = self['display']
        assumed_field = self['assumed']
        inferred_field = self['inferred']

        calculate = 'calculate'
        clear = 'clear'
        postfix = 'machine-readable-date'

        calculate_name = f'{self.prefix}-{calculate}-{postfix}' if self.prefix else f'{calculate}-{postfix}'
        clear_name = f'{self.prefix}-{clear}-{postfix}' if self.prefix else f'{clear}-{postfix}'

        with date_div:
            # first row: standardized date
            with tags.div(cls='flex gap-5 items-end w-full mb-5'):
                with tags.label(cls=SimpleFormMixin.palette_form_control_classes):
                    with tags.div(cls=SimpleFormMixin.label_classes):
                        tags.label(_('standardized date'), cls=SimpleFormMixin.label_text_classes)
                    raw(str(display_field))
                    if display_field.errors:
                        with div(cls='label'):
                            with span(cls='text-primary text-sm'):
                                display_field.errors
                tags._input(type='submit', cls='btn btn-outline flex-0', form='form', value=_('calculate'), name=calculate_name)
            # second row: not before & not after
            with tags.div(cls='flex flex-col xl:flex-row gap-5'):
                with tags.label(cls='form-control flex-0'):
                    tags.div(_('not before'), cls=SimpleFormMixin.label_text_classes)
                    with tags.div(cls='flex'):
                        raw(str(not_before_field))
                    if not_before_field.errors:
                        with div(cls='label'):
                            with span(cls='text-primary text-sm'):
                                not_before_field.errors
                with tags.label(cls='form-control flex-0'):
                    tags.div(_('not after'), cls=SimpleFormMixin.label_text_classes)
                    with tags.div(cls='flex'):
                        raw(str(not_after_field))
                    if not_after_field.errors:
                        with div(cls='label'):
                            with span(cls='text-primary text-sm'):
                                not_after_field.errors
            # third row: controls
            with tags.div(cls=SimpleFormMixin.palette_classes + ' items-center'):
                with tags.label(cls=SimpleFormMixin.toggle_label_classes):
                    tags.span(_(assumed_field.label.lower()), cls=SimpleFormMixin.label_text_classes)
                    raw(str(assumed_field))
                tags.div(cls='flex-1')
                for sw in inferred_field.subwidgets:
                    with tags.div(cls=SimpleFormMixin.form_control_classes):
                        with tags.label(cls='label cursor-pointer gap-5'):
                            tags.span(_(sw.choice_label), cls=SimpleFormMixin.label_text_classes)
                            tags.input_(
                                    type='radio',
                                    name=sw.data.get('name'),
                                    value=str(sw.data.get('value')),
                                    cls='radio',
                                    checked = sw.data.get('selected', False),
                                    form='form'
                                )
                tags.div(cls='flex-1')
                tags._input(type='submit', cls='btn btn-outline btn-primary flex-0', form='form' ,value=_('clear'), name=clear_name)

        return date_div
