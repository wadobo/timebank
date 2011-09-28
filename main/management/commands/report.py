import datetime
from user.models import Profile
from serv.models import Transfer
from serv.models import Service


from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q


def make_report(fields=[], query_filter=None, query_exclude=None):
    users = Profile.objects.all()
    if query_filter:
        users = users.filter(query_filter).distinct()
    if query_exclude:
        users = users.exclude(query_exclude).distinct()

    rep = [','.join(i[0] for i in fields)]
    for user in users:
        data = [v[2](getattr(user, v[1])) if v[2] else getattr(user, v[1]) for v in fields]

        rep.append(u','.join(map(unicode, data)))
    return '\n'.join(rep)


def make_report_total():
    transfers = [i.credit_hours() for i in Transfer.objects.all()]
    rep = []
    rep.append("total transfer,%s" % len(transfers))
    rep.append("total hours,%s" % sum(transfers))
    return '\n'.join(rep)


def make_report2():
    last_date = datetime.datetime.now() - datetime.timedelta(days=6*30)
    query_filter = Q(last_login__gt=last_date)
    return make_report1(query_filter)


def make_report3():
    query_exclude = Q(services=None)
    return make_report1(query_exclude=query_exclude)


def make_report1(query_filter=None, query_exclude=None):
    r = (('username', 'username', None),
         ('fullname', 'get_full_name', lambda x: x()),
         ('birth_date', 'birth_date', lambda x: x.strftime("%d/%m/%Y")),
         ('age', 'birth_date', lambda x: datetime.datetime.now().year - x.year),
         ('balance', 'balance', None),
         ('trec', 'transfers_received', lambda x: x.count()),
         ('tgiv', 'transfers_given', lambda x: x.count()),
         ('hrec', 'transfers_received', lambda x: sum([i.credit_hours() for i in x.all()])),
         ('hgiv', 'transfers_given', lambda x: sum([i.credit_hours() for i in x.all()])),
         ('last_login', 'last_login', lambda x: x.strftime("%d/%m/%Y")))
    return make_report(r, query_filter, query_exclude)


def make_report5():
    servs = Service.objects.all()
    sservs = sorted(servs, key=lambda x: x.creator.username)
    rep = []
    rep.append("username; full name; tlfn; mv; offer/demand; servname; servdesc")
    for s in sservs:
        line = ";".join(map(lambda x: '"%s"' % x, [
        s.creator.username,
        s.creator.get_full_name(),
        s.creator.land_line,
        s.creator.mobile_tlf,
        s.get_is_offer_display(),
        s.short_name(),
        s.description]))
        rep.append(line)

    return '\n'.join(rep)


reports = [make_report1, make_report2, make_report3,
           make_report_total, make_report5]


class Command(BaseCommand):

    def handle(self, reporttype=0, **options):
        if not reporttype:
            print len(reports)
        else:
            print reports[int(reporttype) - 1]()
