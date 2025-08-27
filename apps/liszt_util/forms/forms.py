from .layouts import Layouts
from django.utils.safestring import mark_safe

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
        pass
    
    def _outside_layout(self):
        pass