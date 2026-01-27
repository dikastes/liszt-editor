from .period_calculation import MONTHS, PERIOD_CODES, resolve_month, resolve_period
from calendar import monthrange
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.conf import settings
import re
from re import split
from datetime import date, datetime
from .base import DocumentationStatus


class Period(models.Model):
    not_before = models.DateField(
            null=True,
            blank=True,
            verbose_name = _("not before")
        )
    not_after = models.DateField(
            null=True,
            blank=True,
            verbose_name = _("not after")
        )
    display = models.TextField(
            null=True,
            blank=True,
            verbose_name = _("standardized date")
        )
    status = models.TextField(
            choices = DocumentationStatus,
            max_length = 1,
            null = True,
            blank = True,
            verbose_name = _("status")
        )
    inferred = models.BooleanField(
            default=False,
            verbose_name = _("inferred")
        )
    assumed = models.BooleanField(
            default=False,
            verbose_name = _("assumed")
        )

    def render_detailed(self):
        if self.not_before == self.not_after:
            return f"{self.display} ({self.not_before})"
        return f"{self.display} ({self.not_before}–{self.not_after})"

    def __str__(self):
        return self.display or ''

    def parse_display(self):
        self.initialize_patterns()

        ASSUMED_TOKEN = '[?]'
        display_value = self.display
        INFERRED_TOKEN = ']'

        if ASSUMED_TOKEN in display_value:
            self.assumed = True
            display_value = display_value.replace(ASSUMED_TOKEN, '').strip()
        else:
            self.assumed = False
        if INFERRED_TOKEN in display_value:
            self.inferred = True
        else:
            self.inferred = False

        if '[' in display_value:
            if ']' in display_value:
                display_value = display_value.replace('[', '').replace(']', '').strip()
            else:
                raise Exception('Invalid display date. A [ was provided but no ].')
        if not '[' in display_value and ']' in display_value:
            raise Exception('Invalid display date. A ] was provided but no [.')

        # 2 dates
        if '/' in display_value:
            if self.year_pattern.match(display_value):
                dates = [ display_value ]
            else:
                dates = [ date.strip() for date in display_value.split('/') ]
                if len(dates[1]) == 2:
                    dates[1] = dates[0][:2] + dates[1]
        elif '-' in display_value:
            dates = [ date.strip() for date in display_value.split('-') ]
        elif str(_('and')) in display_value:
            dates = [ date.strip() for date in display_value.split(str(_('and'))) ]
        else:
            dates = [ display_value ]

        self.not_before = self._parse_date(dates[0], 'lower')
        if len(dates) == 2:
            self.not_after = self._parse_date(dates[1], 'upper')
        else:
            self.not_after = self._parse_date(dates[0], 'upper')

    def initialize_patterns(self):
        prefix_pipe_string = '|'.join(str(_(prefix)) for prefix in PERIOD_CODES)
        month_pipe_string = '|'.join(str(_(month)) for month in MONTHS)

        self.month_pattern = re.compile(rf'^({prefix_pipe_string})\s+({month_pipe_string})\s+(\d{{4}})$', re.IGNORECASE)
        self.year_pattern = re.compile(rf'^({prefix_pipe_string})\s+(\d{{4}})(/\d{{2}})?$', re.IGNORECASE)
        decade_suffix = _('ies')
        self.decade_pattern = re.compile(rf'^({prefix_pipe_string + "|"})\s*(\d{{3}}0){decade_suffix}$', re.IGNORECASE)

    def _parse_date(self, date_string, bound):

        match = re.search(r"[\d?]{4}", date_string)
        if match:
            year = int(match.group())
        else:
            raise ValueError(f'No year found in {date_string}')

        month_match = self.month_pattern.match(date_string)

        if month_match:
            year = int(month_match.group(3))
            month = MONTHS[resolve_month(month_match.group(2))]
            prefix = resolve_period(month_match.group(1))
            if bound == 'lower':
                day = PERIOD_CODES[prefix]['month']['lower']['day']
            else:
                if PERIOD_CODES[prefix]['month']['upper']['day'] == 'max':
                    day = monthrange(year, month)[1]
                else:
                    day = PERIOD_CODES[prefix]['month']['upper']['day']
            return date(year, month, day)

        year_match = self.year_pattern.match(date_string)

        if year_match:
            year = int(year_match.group(2))
            prefix = resolve_period(year_match.group(1))
            if bound == 'lower':
                day = PERIOD_CODES[prefix]['year']['lower']['day']
                month = PERIOD_CODES[prefix]['year']['lower']['month']
                year = year + PERIOD_CODES[prefix]['year']['lower']['year']
            else:
                day = PERIOD_CODES[prefix]['year']['upper']['day']
                month = PERIOD_CODES[prefix]['year']['upper']['month']
                year = year + PERIOD_CODES[prefix]['year']['upper']['year']
            return date(year, month, day)

        decade_match = self.decade_pattern.match(date_string)

        if decade_match:
            year = int(decade_match.group(2))
            if decade_match.group(1):
                prefix = resolve_period(decade_match.group(1))
                if bound=='lower':
                    day = PERIOD_CODES[prefix]['decade']['lower']['day']
                    month = PERIOD_CODES[prefix]['decade']['lower']['month']
                    year = year + PERIOD_CODES[prefix]['decade']['lower']['year']
                else:
                    day = PERIOD_CODES[prefix]['decade']['upper']['day']
                    month = PERIOD_CODES[prefix]['decade']['upper']['month']
                    year = year + PERIOD_CODES[prefix]['decade']['upper']['year']
            else:
                if bound=='lower':
                    day = 1
                    month = 1
                    year = year
                else:
                    day = 31
                    month = 12
                    year = year + 9
            return date(year, month, day)

        date_parts = date_string.split('.')
        #day = self._parse_date_part(date_parts, bound, 'day')
        if len(date_parts) == 3:
            day = self._parse_date_part(date_parts[0], bound, 'day')
            month = self._parse_date_part(date_parts[1], bound, 'month')
            if month > 12:
                month = 12
            year = self._parse_date_part(date_parts[2], bound, 'year')
            if day > monthrange(year, month)[1]:
                day = monthrange(year, month)[1]
        if len(date_parts) == 2:
            month = self._parse_date_part(date_parts[0], bound, 'month')
            if month > 12:
                month = 12
            year = self._parse_date_part(date_parts[1], bound, 'year')
            if bound == 'lower':
                day = 1
            else:
                day = monthrange(year, month)[1]
        if len(date_parts) == 1:
            year = self._parse_date_part(date_parts[0], bound, 'year')
            if bound == 'lower':
                month = 1
                day = 1
            else:
                month = 12
                day = monthrange(year, month)[1]

        return date(year, month, day)

    def _parse_date_part(self, date_part_string, bound, date_part):
        date_part_chars = [ char for char in date_part_string ]
        century = ''
        first_char = ''
        second_char = ''

        if len(date_part_chars) == 4:
            if '?' in date_part_string[:2]:
                century = '18'
            else:
                century = date_part_string[:2]
            first_char = date_part_chars[2]
            second_char = date_part_chars[3]
        elif len(date_part_chars) == 2:
            first_char = date_part_chars[0]
            second_char = date_part_chars[1]
        else:
            first_char = date_part_chars[0]

        if first_char + second_char == '??' or first_char + second_char == '?':
            if bound == 'lower':
                return 1
            if bound == 'upper':
                if date_part == 'day':
                    return 31
                return 12

        if first_char == '?':
            if bound == 'lower':
                if second_char and date_part != 'day':
                    first_part = '0'
                if second_char > '0':
                    first_part = '0'
                else:
                    first_part = '1'
            else:
                first_part = '9'
                if date_part == 'day':
                    if second_char < '2':
                        first_part = '3'
                    else:
                        first_part = '2'
                if date_part == 'month':
                    if second_char < '3':
                        first_part = '1'
                    else:
                        first_part = '0'
            if bound == 'upper':
                if date_part == 'day':
                    first_part = '3'
                    if second_char > '1':
                        first_part = '2'
        else:
            first_part = first_char

        if second_char:
            if second_char == '?':
                if bound == 'lower':
                    if date_part == 'month' and first_char == '0':
                        return 1
                    second_part = '0'
                if bound == 'upper':
                    second_part = '9'
                    if date_part == 'month' and first_part == '1':
                        second_part = '2'
            else:
                second_part = second_char
        else:
            second_part = first_part
            first_part = '0'

        return int(century + first_part + second_part)

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

    def parse(string):
        components = split('-|–|\$|\|', string)
        is_range = True if len(components) > 5 else False

        not_before = date(
                settings.EDWOCA_FIXED_DATES['birth']['year'],
                settings.EDWOCA_FIXED_DATES['birth']['month'],
                settings.EDWOCA_FIXED_DATES['birth']['day'],
            )
        not_after = date(
                settings.EDWOCA_FIXED_DATES['death']['year'],
                settings.EDWOCA_FIXED_DATES['death']['month'],
                settings.EDWOCA_FIXED_DATES['death']['day'],
            )

        not_before_year = components[0].strip()

        if len(components) > 1:
            not_before_month = components[1].strip()
        else:
            not_before_month = 'xx'

        if len(components) > 2:
            not_before_day = components[2].strip()
        else:
            not_before_day = 'xx'

        if not_before_year.isnumeric():
            not_before = not_before.replace(year = int(not_before_year))
            if not is_range:
                not_after = not_after.replace(year = int(not_before.year))
            if not_before_month.isnumeric():
                not_before = not_before.replace(day = 1, month = int(not_before_month))
                if not is_range:
                    not_after = not_after.replace(day = 1, month = int(not_before_month))
                if not_before_day.isnumeric():
                    not_before = not_before.replace(day = int(not_before_day))
                    if not is_range:
                        not_after = not_after.replace(day = int(not_before_day))
                else:
                    not_before = not_before.replace(day = 1)
                    if not is_range:
                        not_after = not_after.replace(day = monthrange(int(not_before_year), int(not_before_month))[1])
            else:
                not_before = not_before.replace(month = 1)
                not_before = not_before.replace(day = 1)
                if not is_range:
                    not_after = not_after.replace(month = 12)

        if is_range:
            not_after_year = components[3].strip()
            not_after_month = components[4].strip()
            not_after_day = components[5].strip()

            if not_after_year.isnumeric():
                not_after = not_after.replace(year = int(not_after_year))
                if not_after_month.isnumeric():
                    not_after = not_after.replace(day = 1, month = int(not_after_month))
                    if not_after_day.isnumeric():
                        not_after = not_after.replace(day = int(not_after_day))
                    else:
                        not_after = not_after.replace(day = monthrange(int(not_after_year), int(not_after_month))[1])
                else:
                    not_after = not_after.replace(month = 12)

        if is_range:
            if '$' in string or '|' in string:
                display = f'{not_before_day}.{not_before_month}.{not_before_year}, {not_after_day}.{not_after_month}.{not_after_year}'
            else:
                display = f'{not_before_day}.{not_before_month}.{not_before_year}–{not_after_day}.{not_after_month}.{not_after_year}'
        else:
            display = f'{not_before_day}.{not_before_month}.{not_before_year}'

        if not_before > not_after:
            not_before, not_after = not_after, not_before

        return Period.objects.create(
                not_before = not_before,
                not_after = not_after,
                display = display
            )

