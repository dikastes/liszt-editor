from django.db import models


class Period(models.Model):
    not_before = models.DateField(null=True, blank=True)
    not_after = models.DateField(null=True, blank=True)
    display = models.TextField()

    def render_detailed(self):
        if self.not_before == self.not_after:
            return f"{self.display} ({self.not_before})"
        return f"{self.display} ({self.not_before}–{self.not_after})"

    def __str__(self):
        return self.display
