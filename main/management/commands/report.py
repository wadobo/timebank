import datetime
from user.models import Profile
from serv.models import Transfer


from django.core.management.base import BaseCommand, CommandError


def make_report():
    users = Profile.objects.all()
    rep = ["username,birth,age,balance,trecv,tgiven,hrecv,hgiven"]
    for user in users:
        transf1 = [i.credit_hours() for i in user.transfers_received.all()]
        transf2 = [i.credit_hours() for i in user.transfers_given.all()]
        data = [user.username,
                user.birth_date.strftime("%d/%m/%Y"),
                datetime.datetime.now().year - user.birth_date.year,
                user.balance,
                len(transf1), len(transf2), sum(transf1), sum(transf2)]
        rep.append(','.join(map(str, data)))

    transfers = [i.credit_hours() for i in Transfer.objects.all()]
    rep.append("")
    rep.append("total transfer,%s" % len(transfers))
    rep.append("total hours,%s" % sum(transfers))
    return '\n'.join(rep)


class Command(BaseCommand):

    def handle(self, *args, **options):
        print make_report()
