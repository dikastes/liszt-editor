from django.db import models
import re
from datetime import date, datetime



class Period(models.Model):
    not_before = models.DateField(null=True, blank=True)
    not_after = models.DateField(null=True, blank=True)
    display = models.TextField(null=True, blank=True)

    def render_detailed(self):
        if self.not_before == self.not_after:
            return f"{self.display} ({self.not_before})"
        return f"{self.display} ({self.not_before}–{self.not_after})"

    def __str__(self):
        return self.display
    
    @staticmethod
    def parse_date_with_fallback(datestr: str, fallback_month=1, fallback_day=1):
        """
        Versucht, ein Datum zu parsen. Falls nur das Jahr vorhanden ist, wird ein
        Platzhalterdatum wie 1921-01-01 zurückgegeben.
        """
        try:
            return datetime.strptime(datestr, "%d.%m.%Y").date()
        except ValueError:
            match = re.search(r"\d{4}", datestr)
            if match:
                year = int(match.group())
                return date(year, fallback_month, fallback_day)
        return None

    @staticmethod
    def create_single_period_from_json(json_data):
        est_raw = json_data.get("dateOfEstablishment", [])
        term_raw = json_data.get("dateOfTermination", [])

        # Alle parsebaren Daten mit Fallback holen
        est_dates = [(d, Period.parse_date_with_fallback(d)) for d in est_raw]
        term_dates = [(d, Period.parse_date_with_fallback(d)) for d in term_raw]

        # Nur gültige parsed dates extrahieren
        parsed_est_dates = [d for _, d in est_dates if d]
        parsed_term_dates = [d for _, d in term_dates if d]

        # Früheste Gründung, spätestes Ende bestimmen
        not_before = min(parsed_est_dates) if parsed_est_dates else None
        not_after = max(parsed_term_dates) if parsed_term_dates else None

        # Anzeigeformat: TT.MM.JJJJ - TT.MM.JJJJ
        if not_before and not_after:
            display = f"{not_before.strftime('%d.%m.%Y')} – {not_after.strftime('%d.%m.%Y')}"
        elif not_before:
            display = f"ab {not_before.strftime('%d.%m.%Y')}"
        elif not_after:
            display = f"bis {not_after.strftime('%d.%m.%Y')}"
        else:
            display = "unbekannter Zeitraum"

        return Period.objects.create(
            not_before=not_before,
            not_after=not_after,
            display=display
        )


