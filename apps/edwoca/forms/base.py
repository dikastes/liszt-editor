import dominate.tags as tags
from liszt_util.forms import GenericAsDaisyMixin
from liszt_util.forms.layouts import Layouts
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.forms import ModelForm, TextInput, Select, HiddenInput, CheckboxInput, Textarea, CharField, DateField, SelectDateWidget, BooleanField, TypedChoiceField, RadioSelect, DateTimeField, ChoiceField
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.utils.safestring import mark_safe
from dominate.util import raw
from dmad_on_django.forms import SearchForm
from dmad_on_django.models import Period
from dominate.tags import div, label, span, a


class SimpleFormMixin:
    text_area_classes = 'textarea textarea-bordered w-full bg-white border-black'
    text_input_classes = 'input input-bordered w-full border-black bg-white disabled:border-black'
    text_label_classes = 'input input-bordered w-full border-black bg-white flex gap-2 items-center'
    autocomplete_classes = 'autocomplete-select select select-bordered w-full border-black bg-white'
    select_classes = 'select select-bordered w-full border-black bg-white'
    toggle_classes = 'toggle'
    radio_classes = 'radio'
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
    imprecision = ChoiceField(
            choices = Period.Imprecision,
            label = _('imprecision'),
            widget = Select(attrs = {'class': SimpleFormMixin.select_classes, 'form': 'form'}),
            required = False
        )
    time_mode = ChoiceField(
            choices = Period.TimeMode,
            label = _('time mode'),
            widget = Select(attrs = {'class': SimpleFormMixin.select_classes, 'form': 'form'}),
            required = False
        )
    start_qualifier = ChoiceField(
            label = _('not before mode'),
            choices = Period.StartQualifier,
            widget = Select(attrs = {'class': 'select border border-black bg-white w-40'}),
            required = False
        )
    end_qualifier = ChoiceField(
            label = _('not after mode'),
            choices = Period.EndQualifier,
            widget = Select(attrs = {'class': 'select border border-black bg-white w-40'}),
            required = False
        )
    not_before = DateField(
            label = _('start'),
            widget = SelectDateWidget(**kwargs),
            required = False
        )
    not_after = DateField(
            label = _('end'),
            widget = SelectDateWidget(**kwargs),
            required = False
        )
    display = CharField(required=False, widget = TextInput( attrs = { 'class': SimpleFormMixin.text_input_classes}), label=Period.display.field.verbose_name)
    inferred = TypedChoiceField(
            choices = ((False, _('based on source')), (True, _('inferred'))),
            coerce = lambda x: x == 'True',
            widget = RadioSelect(
                    attrs = { 'class': SimpleFormMixin.radio_classes, 'form': 'form'}
                ),
            required = False
        )
    assumed = BooleanField(widget = CheckboxInput(attrs = { 'class': 'toggle', 'form': 'form'}), required = False)
    period_instance = None

    def __init__(self, *args, **kwargs):
        self.period_property = kwargs.pop('period_property', 'period')
        super().__init__(*args, **kwargs)

        self.period_instance = getattr(self.instance, self.period_property)

        if not self.period_instance:
            self.period_instance = Period.objects.create()

        self.is_precise_date = (
                self.period_instance.imprecision == Period.Imprecision.PRECISE and
                self.period_instance.time_mode == Period.TimeMode.POINT
            )

        if self.period_instance.imprecision == Period.Imprecision.PRECISE:
            self.fields['start_qualifier'].widget.attrs['disabled'] = True
            self.fields['end_qualifier'].widget.attrs['disabled'] = True

        if self.is_bound:
            return

        period = getattr(self.instance, self.period_property, None)
        if period:
            self.initial.update({
                'not_before': period.not_before,
                'not_after': period.not_after,
                'display': period.display,
                'inferred': period.inferred,
                'time_mode': period.time_mode,
                'start_qualifier': period.start_qualifier,
                'end_qualifier': period.end_qualifier,
                'assumed': period.assumed,
                'imprecision': period.imprecision
            })

    def clean(self):
        cleaned_data = super().clean()

        time_mode = cleaned_data.get('time_mode')
        imprecision = cleaned_data.get('imprecision')
        not_before = cleaned_data.get('not_before')

        is_point_and_precise = (
            time_mode == Period.TimeMode.POINT and
            imprecision == Period.Imprecision.PRECISE
        )

        if is_point_and_precise and 'not_after' in self._errors:
            del self._errors['not_after']
            cleaned_data['not_after'] = not_before

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Ensure period exists or create it
        if not getattr(self.instance, self.period_property):
            setattr(self.instance, self.period_property, Period.objects.create())

        self.period_instance.not_before = self.cleaned_data['not_before']
        self.period_instance.time_mode = self.cleaned_data['time_mode']
        self.period_instance.imprecision = self.cleaned_data['imprecision']
        self.period_instance.not_after = self.cleaned_data['not_after']

        if self.period_instance.imprecision == Period.Imprecision.PRECISE:
            self.period_instance.start_qualifier = Period.StartQualifier.EXACT
            self.period_instance.end_qualifier = Period.EndQualifier.EXACT
        else:
            self.period_instance.start_qualifier = self.cleaned_data['start_qualifier']
            self.period_instance.end_qualifier = self.cleaned_data['end_qualifier']

        self.period_instance.display = self.cleaned_data['display']
        self.period_instance.inferred = self.cleaned_data['inferred'] or False
        self.period_instance.assumed = self.cleaned_data['assumed']

        self.period_instance.save()
        instance.save()

        return instance

    def get_date_div(self, disable_inferred = False):
        date_div = tags.div()
        time_mode_field = self['time_mode']
        start_qualifier_field = self['start_qualifier']
        end_qualifier_field = self['end_qualifier']
        not_before_field = self['not_before']
        not_after_field = self['not_after']
        display_field = self['display']
        assumed_field = self['assumed']
        inferred_field = self['inferred']
        imprecision_field = self['imprecision']

        calculate = 'calculate'
        clear = 'clear'
        postfix = 'machine-readable-date'

        calculate_name = f'{self.prefix}-{calculate}-{postfix}' if self.prefix else f'{calculate}-{postfix}'
        clear_name = f'{self.prefix}-{clear}-{postfix}' if self.prefix else f'{clear}-{postfix}'

        with date_div:
            # first row: standardized date
            with tags.label(cls=SimpleFormMixin.palette_form_control_classes):
                with tags.div(cls=SimpleFormMixin.label_classes):
                    # display_field.label retrieves for some reason display instead of standardized date
                    tags.label(display_field.label, cls=SimpleFormMixin.label_text_classes)
                raw(str(display_field))
                if display_field.errors:
                    with div(cls='label'):
                        with span(cls='text-primary text-sm'):
                            display_field.errors
            # second row: time mode and imprecision
            with tags.div(cls='flex flex-col lg:flex-row gap-5 w-full my-5'):
                with tags.label(cls=SimpleFormMixin.palette_form_control_classes):
                    with tags.div(cls=SimpleFormMixin.label_classes):
                        tags.label(time_mode_field.label, cls=SimpleFormMixin.label_text_classes)
                    raw(str(time_mode_field))
                with tags.label(cls=SimpleFormMixin.palette_form_control_classes):
                    with tags.div(cls=SimpleFormMixin.label_classes):
                        tags.label(imprecision_field.label, cls=SimpleFormMixin.label_text_classes)
                    raw(str(imprecision_field))
            # third row: controls
            with tags.div(cls='flex gap-5 w-full my-5'):
                tags._input(type='submit', cls='btn btn-outline flex-1', form='form', value=_('calculate'), name=calculate_name)
                tags._input(type='submit', cls='btn btn-outline btn-primary flex-1', form='form' ,value=_('clear'), name=clear_name)
            # fourth row: not before
            with tags.div(cls='flex flex-col lg:flex-row lg:gap-5 mb-5'):
                with tags.label(cls='form-control flex-none date-container'):
                    with tags.div(cls=SimpleFormMixin.label_classes):
                        if self.period_instance.time_mode == Period.TimeMode.POINT and self.period_instance.imprecision == Period.Imprecision.PRECISE:
                            tags.span(_('point in time'), cls=SimpleFormMixin.label_text_classes)
                        else:
                            tags.span(not_before_field.label, cls=SimpleFormMixin.label_text_classes)
                    with tags.div(cls='flex'):
                        raw(str(not_before_field))
                    if not_before_field.errors:
                        with div(cls='label'):
                            with span(cls='text-primary text-sm'):
                                not_before_field.errors
                tags.div(cls='flex-1')
                with tags.label(cls=SimpleFormMixin.form_control_classes + ' flex-none'):
                    with tags.div(cls=SimpleFormMixin.label_classes + ''):
                        tags.label(start_qualifier_field.label, cls=SimpleFormMixin.label_text_classes)
                    raw(str(start_qualifier_field))
            # fifth row: not after
            if not self.is_precise_date:
                with tags.div(cls='flex flex-col lg:flex-row lg:gap-5 mb-5'):
                    with tags.label(cls='form-control flex-none date-container'):
                        with tags.div(cls=SimpleFormMixin.label_classes):
                            tags.span(not_after_field.label, cls=SimpleFormMixin.label_text_classes)
                        with tags.div(cls='flex'):
                            raw(str(not_after_field))
                        if not_after_field.errors:
                            with div(cls='label'):
                                with span(cls='text-primary text-sm'):
                                    not_after_field.errors
                    tags.div(cls='flex-1')
                    with tags.label(cls=SimpleFormMixin.form_control_classes + ' flex-none'):
                        with tags.div(cls=SimpleFormMixin.label_classes):
                            tags.label(end_qualifier_field.label, cls=SimpleFormMixin.label_text_classes)
                        raw(str(end_qualifier_field))
            # third row: controls
            with tags.div(cls='flex flexcol lg:flex-row gap-5'):
                tags.div(cls='flex-1')
                with tags.label(cls=SimpleFormMixin.toggle_label_classes + ' flex-none'):
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
                                    form='form',
                                    disabled = disable_inferred
                                )

        return date_div


class BaseSignatureForm(GenericAsDaisyMixin, ModelForm):
    layout = Layouts.LABEL_OUTSIDE

    class Meta:
        fields = ['library', 'signature', 'status', 'id']
        widgets = {
                'library': Select( attrs = {
                        'class': SimpleFormMixin.autocomplete_classes,
                        'form': 'form'
                    }),
                'signature': TextInput( attrs = {
                        'class': SimpleFormMixin.text_input_classes,
                        'form': 'form'
                    }),
                'status': Select( attrs = {
                        'class': SimpleFormMixin.select_classes,
                        'form': 'form'
                    }),
                'id': HiddenInput()
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lib_field = self.fields['library']
        lib_field.label = f'{lib_field.label}*'
        sig_field = self.fields['signature']
        sig_field.label = f'{sig_field.label}*'

    def as_daisy(self):
        form_wrapper = div(cls='mb-10')

        library_field = self['library']
        signature_field = self['signature']
        status_field = self['status']

        library_container = label(cls='form-control w-full flex-1')
        library_span = span(library_field.label, cls='label-text')
        library_div = div(cls='label')
        library_div.add(library_span)
        library_container.add(library_div)
        library_container.add(raw(str(library_field)))

        signature_container = label(cls='form-control w-full flex-1')
        signature_span = span(signature_field.label, cls='label-text')
        signature_div = div(cls='label')
        signature_div.add(signature_span)
        signature_container.add(signature_div)
        signature_container.add(raw(str(signature_field)))

        status_container = label(cls='form-control w-full max-w-xs flex-0')
        status_span = span(status_field.label, cls='label-text')
        status_div = div(cls='label')
        status_div.add(status_span)
        status_container.add(status_div)
        status_container.add(raw(str(status_field)))

        upper_palette = div(cls='flex flex-rows w-full gap-10 my-5')
        lower_palette = div(cls='flex flex-rows w-full gap-10 my-5')

        upper_palette.add(library_container)
        upper_palette.add(status_container)
        lower_palette.add(signature_container)

        form_wrapper.add(upper_palette)
        form_wrapper.add(lower_palette)

        return mark_safe(str(form_wrapper))


class BaseDigitizedCopyForm(GenericAsDaisyMixin, ModelForm, SimpleFormMixin):
    layout = Layouts.LABEL_OUTSIDE
    class Meta:
        fields = ['url', 'link_type']
        widgets = {
                'url': TextInput(attrs={'class': SimpleFormMixin.text_input_classes, 'form': 'form'}),
                'link_type': Select(attrs={'class': SimpleFormMixin.select_classes, 'form': 'form'})
        }

    def as_daisy(self):
        form = div(cls='mb-5')

        url_field = self['url']
        link_type_field = self['link_type']

        with form:
            with div(cls='flex gap-5 items-end'):
                with label(cls=SimpleFormMixin.palette_form_control_classes):
                    with div(cls=SimpleFormMixin.label_classes):
                        span(_(url_field.label), cls=SimpleFormMixin.label_text_classes)
                    raw(str(url_field))
                if self.instance.url:
                    a(_('open'), cls='flex-0 btn btn-outline', href=self.instance.url, target='_blank')
            with label(cls=SimpleFormMixin.form_control_classes):
                with div(cls=SimpleFormMixin.label_classes):
                    span(_(link_type_field.label), cls=SimpleFormMixin.label_text_classes)
                raw(str(link_type_field))

        return mark_safe(str(form))


class BaseTrackedModelForm:
    class Meta:
        fields = [
                'first_editor',
                'editing_history',
                'needs_review'
            ]
        widgets = {
                'first_editor': TextInput( attrs ={
                    'class': SimpleFormMixin.text_input_classes,
                    'form': 'form'
                    }),
                'editing_history': Textarea( attrs ={
                    'class': SimpleFormMixin.text_area_classes,
                    'form': 'form'
                    }),
                'needs_review': CheckboxInput( attrs = {
                        'class': 'toggle',
                        'form': 'form'
                    })
            }

    # these fields must be copied to the inheriting classes
    first_save = DateTimeField(
            label=_('first save') + '*',
            required = False,
            disabled = True,
            widget = SelectDateWidget( attrs = { 'class': SimpleFormMixin.select_classes + ' disabled:!bg-white disabled:!border-black disabled:!text-black' })
        )
    last_save = DateTimeField(
            label=_('last save'),
            required = False,
            disabled = True,
            widget = SelectDateWidget( attrs = { 'class': SimpleFormMixin.select_classes + ' disabled:!bg-white disabled:!border-black disabled:!text-black'})
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['first_save'].initial = self.instance.first_save
            self.fields['last_save'].initial = self.instance.last_save
        fe_field = self.fields['first_editor']
        fe_field.label = f'{fe_field.label}*'

    def get_editing_history_div(self):
        editing_history_div = div()

        first_editor_field = self['first_editor']
        first_save_field = self['first_save']
        last_save_field = self['last_save']
        needs_review_field = self['needs_review']
        editing_history_field = self['editing_history']

        with editing_history_div:
            tags.h2(_('editing history'), cls='my-5')
            tags.h3(_('initial recording'), cls='my-5')
            with tags.label(cls=SimpleFormMixin.form_control_classes):
                with tags.div(cls=SimpleFormMixin.label_classes):
                    tags.span(first_editor_field.label, cls=SimpleFormMixin.label_text_classes)
                raw(str(first_editor_field))
            with tags.label(cls=SimpleFormMixin.form_control_classes):
                with tags.div(cls=SimpleFormMixin.label_classes):
                    tags.span(first_save_field.label, cls=SimpleFormMixin.label_text_classes)
                with tags.div(cls='flex'):
                    with tags.div(cls='flex'):
                        raw(str(first_save_field))
                    tags.div(cls='flex-1')
            tags.h3(_('further recording'), cls='my-5')
            with tags.label(cls=SimpleFormMixin.form_control_classes):
                with tags.div(cls=SimpleFormMixin.label_classes):
                    tags.span(editing_history_field.label, cls=SimpleFormMixin.label_text_classes)
                raw(str(editing_history_field))
            with tags.div(cls='flex flex-col lg:flex-row gap-2 my-5 lg:items-end'):
                with tags.label(cls=SimpleFormMixin.palette_form_control_classes):
                    with tags.div(cls=SimpleFormMixin.label_classes):
                        tags.span(last_save_field.label, cls=SimpleFormMixin.label_text_classes)
                    with tags.div(cls='flex'):
                        with tags.div(cls='flex'):
                            raw(str(last_save_field))
                        tags.div(cls='flex-1')
                tags.div(cls='flex-1')
                with tags.label(cls=SimpleFormMixin.toggle_label_classes + ' flex-0'):
                    tags.span(needs_review_field.label, cls=SimpleFormMixin.label_text_classes)
                    raw(str(needs_review_field))

        return editing_history_div


class BaseTextTypeForm(ModelForm, SimpleFormMixin):
    class Meta:
        fields = ['is_lyrics', 'is_program', 'is_explanation']
        widgets = {
                'is_lyrics': CheckboxInput( attrs = {
                        'class': 'toggle',
                        'form': 'form'
                    }),
                'is_program': CheckboxInput( attrs = {
                        'class': 'toggle',
                        'form': 'form'
                    }),
                'is_explanation': CheckboxInput( attrs = {
                        'class': 'toggle',
                        'form': 'form'
                    })
            }

    def as_daisy(self):
        lyrics_field = self['is_lyrics']
        program_field = self['is_program']
        explanation_field = self['is_explanation']

        form = div()

        with form:
            tags.h3(_('text type'), cls='text-lg my-5')
            with tags.label(cls=SimpleFormMixin.toggle_inverted_classes):
                raw(str(lyrics_field))
                tags.span(lyrics_field.label, cls=SimpleFormMixin.label_text_classes)
            with tags.label(cls=SimpleFormMixin.toggle_inverted_classes):
                raw(str(program_field))
                tags.span(program_field.label, cls=SimpleFormMixin.label_text_classes)
            with tags.label(cls=SimpleFormMixin.toggle_inverted_classes):
                raw(str(explanation_field))
                tags.span(explanation_field.label, cls=SimpleFormMixin.label_text_classes)

        return mark_safe(str(form))
