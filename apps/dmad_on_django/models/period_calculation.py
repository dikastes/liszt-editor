from django.utils.translation import gettext_lazy as _

MONTHS = {
    'january': 1,
    'february': 2,
    'march': 3,
    'april': 4,
    'may': 5,
    'june': 6,
    'july': 7,
    'august': 8,
    'september': 9,
    'october': 10,
    'november': 11,
    'december': 12
}

MONTH_ALIASES = {
    'january': _('january'),
    'february': _('february'),
    'march': _('march'),
    'april': _('april'),
    'may': _('may'),
    'june': _('june'),
    'july': _('july'),
    'august': _('august'),
    'september': _('september'),
    'october': _('october'),
    'november': _('november'),
    'december': _('december'),
}


def resolve_month(month_name):
    for key, alias in MONTH_ALIASES.items():
        if month_name.casefold() == alias.casefold():
            return key
    raise Exception(f'Error trying to resolve month name: {month_name} not found')


def resolve_period(period_name):
    for key, alias in PERIOD_ALIASES.items():
        if period_name.casefold() == alias.casefold():
            return key
    raise Exception(f'Error trying to resolve period name: {period_name} not found')


PERIOD_CODES = {
    'beginning': {
        # the beginning of a month is the first to the tenth day
        'month': {
            'lower': {
                'day': 1
            },
            'upper': {
                'day': 10
            },
        },
        # the beginning of a year is january to april
        'year': {
            'lower': {
                'day': 1,
                'month': 1,
                'year': 0
            },
            'upper': {
                'day': 30,
                'month': 4,
                'year': 0
            }
        },
        # the beginning of a decade is from the first to the third year
        'decade': {
            'lower': {
                'day': 1,
                'month': 1,
                'year': 0
            },
            'upper': {
                'day': 31,
                'month': 12,
                'year': 3
            }
        }
    },
    'mid': {
        # the mid of a month is the 11th to the 20th day
        'month': {
            'lower': {
                'day': 11
            },
            'upper': {
                'day': 20
            }
        },
        # the mid of a year is may to august
        'year': {
            'lower': {
                'day': 1,
                'month': 5,
                'year': 0
            },
            'upper': {
                'day': 31,
                'month': 8,
                'year': 0
            }
        },
        # the mid of a decade is from the fourth to the sixth year
        'decade': {
            'lower': {
                'day': 1,
                'month': 1,
                'year': 4
            },
            'upper': {
                'day': 31,
                'month': 12,
                'year': 6
            }
        }
    },
    'end': {
        # the end of a month is after the 21st day
        'month': {
            'lower': {
                'day': 21
            },
            'upper': {
                'day': 'max'
            }
        },
        # the end of a year is september to december
        'year': {
            'lower': {
                'day': 1,
                'month': 9,
                'year': 0
            },
            'upper': {
                'day': 31,
                'month': 12,
                'year': 0
            }
        },
        # the end of a decade is from the seventh to the nineth year
        'decade': {
            'lower': {
                'day': 1,
                'month': 1,
                'year': 7
            },
            'upper': {
                'day': 31,
                'month': 12,
                'year': 9
            }
        }
    },
    'first half': {
        # the first half of a month
        'month': {
            'lower': {
                'day': 1
            },
            'upper': {
                'day': 14
            }
        },
        # the first half of a year
        'year': {
            'lower': {
                'day': 1,
                'month': 1,
                'year': 0
            },
            'upper': {
                'day': 30,
                'month': 6,
                'year': 0
            }
        },
        # the first half of a decade
        'decade': {
            'lower': {
                'day': 1,
                'month': 1,
                'year': 0
            },
            'upper': {
                'day': 31,
                'month': 12,
                'year': 4
            }
        }
    },
    'second half': {
        # the second half of a month
        'month': {
            'lower': {
                'day': 15
            },
            'upper': {
                'day': 'max'
            }
        },
        # the second half of a year
        'year': {
            'lower': {
                'day': 1,
                'month': 7,
                'year': 0
            },
            'upper': {
                'day': 31,
                'month': 12,
                'year': 0,
            }
        },
        # the second half of a decade
        'decade': {
            'lower': {
                'day': 1,
                'month': 1,
                'year': 5
            },
            'upper': {
                'day': 31,
                'month': 12,
                'year': 9
            }
        }
    },
    'spring': {
        'year': {
            'lower': {
                'day': 1,
                'month': 3,
                'year': 0
            },
            'upper': {
                'day': 31,
                'month': 5,
                'year': 0
            }
        }
    },
    'summer': {
        'year': {
            'lower': {
                'day': 1,
                'month': 6,
                'year': 0
            },
            'upper': {
                'day': 31,
                'month': 8,
                'year': 0
            }
        }
    },
    'fall': {
        'year': {
            'lower': {
                'day': 1,
                'month': 9,
                'year': 0
            },
            'upper': {
                'day': 30,
                'month': 11,
                'year': 0
            }
        }
    },
    'winter': {
        'year': {
            'lower': {
                'day': 1,
                'month': 12,
                'year': 0
            },
            'upper': {
                'day': 31,
                'month': 1,
                'year': 1
            }
        }
    }
}

PERIOD_ALIASES = {
    'beginning': _('beginning'),
    'mid': _('mid'),
    'end': _('end'),
    'first half': _('first half'),
    'second half': _('second half'),
    'spring': _('spring'),
    'summer': _('summer'),
    'fall': _('fall'),
    'winter': _('winter')
}
