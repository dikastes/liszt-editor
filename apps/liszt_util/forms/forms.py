from .layouts import Layouts

from django.utils.safestring import mark_safe
from django.forms import HiddenInput, Textarea, CheckboxInput

from dominate.tags import div, label, span
from dominate.util import raw


class GenericAsDaisyMixin():

    # Default layout, may be overwritten by subclass
    layout : Layouts = Layouts.LABEL_INSIDE

    def as_daisy(self):
        match self.layout:
            case Layouts.CUSTOM:
                raise NotImplementedError("Please override as_daisy or choose a template layout")
            case Layouts.LABEL_INSIDE:
                return mark_safe(self._inside_layout())
            case Layouts.LABEL_OUTSIDE:
                return mark_safe(self._outside_layout())
    
    def _inside_layout(self):
        
        root = div(cls="flex flex-col gap-5")

        for field in self.visible_fields():
            if isinstance(field.field.widget, HiddenInput):
                root.add(raw(field.as_widget()))
                continue

            widget = field.field.widget

            wrapper = label(cls="input input-bordered flex items-center gap-2")

            if field.label:
                wrapper.add(field.label)
                
            cls = "grow"
            if isinstance(widget, Textarea):
                cls = f'textarea textarea-bordered'
                root.add(raw(field.as_widget(attrs={"class": cls, "placeholder" : field.label})))
                continue
            
            if isinstance(widget, CheckboxInput):
                root.add(self._render_checkbox(field))
                continue

            wrapper.add(raw(field.as_widget(attrs={"class": cls})))


            if field.help_text:
                wrapper.add(span(field.help_text, cls="badge badge-info"))

            root.add(wrapper)
                
        return root.render()
    
    def _outside_layout(self):
        root = div(cls="flex flex-col gap-5")

        for field in self.visible_fields():
            if isinstance(field.field.widget, HiddenInput):
                root.add(raw(field.as_widget()))
                continue

            widget = field.field.widget
            wrap = label(cls="form-control w-full")

            top = div(cls="label")
            top.add(span((field.label or field.name), cls="label-text"))
            if field.help_text:
                top.add(span(field.help_text, cls="label-text-alt"))
            wrap.add(top)

            if isinstance(widget, CheckboxInput):
                root.add(self._render_checkbox(field))
                continue

            if isinstance(widget, Textarea):
                cls = "textarea textarea-bordered w-full"
    
            else:
                cls = "input input-bordered w-full"
               
            wrap.add(raw(field.as_widget(attrs={"class" : cls})))

            root.add(wrap)

        return root.render()
    
    def _render_checkbox(self, field):
        wrap = label(cls="label cursor-pointer justify-start gap-3")
        wrap.add(span(field.label or field.name, cls="label-text flex-1"))
        wrap.add(raw(field.as_widget(attrs={"class":"toggle toggle-primary flex-0"})))
            
        return wrap
        
