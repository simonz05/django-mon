import datetime
import calendar

from django.http import HttpResponse
from piston.handler import BaseHandler

from mon.models import Record


def create_date(dates, end=False):
    l = len(dates)
    d = list(dates)

    if l == 1:
        d.extend((1, 1) if not end else (12, 31))
    elif l == 2:
       d.append(1 if not end else calendar.monthrange(d[0], d[1])[1])

    return datetime.date(*d)

def interpret_dates(from_date, to_date=None):
    f_d = create_date(from_date)

    if not to_date:
        t_d = create_date(from_date, end=True)
        if t_d == f_d:
            t_d = t_d + datetime.timedelta(days=1)
    else:
        t_d = create_date(to_date, end=True)

    return (f_d, t_d)

def query(fields, dates={}):
    dates.update(dict([('%s__isnull' % f, False) for f in fields]))
    return Record.objects.values(*fields).filter(**dates)

class MonHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Record
    fields = Record.data_fields()

    def read(self, request, pattern=None):
        if not pattern:
            return query(self.fields)

        words = [f.lower() for f in pattern.split('/') if f.isalpha()]
        fields = [f for f in words if f in self.fields] if len(words) > 0 else self.fields

        digits = [[int(o) for o in v.split('/') if o.isdigit()] for v in pattern.split('-') if len(v) > 0]

        dates = dict()
        if len(digits[0]) > 0:
            dates['created__range'] = interpret_dates(*digits[:len(digits)])

        return query(fields, dates)
