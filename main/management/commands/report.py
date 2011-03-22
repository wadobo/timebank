import datetime
from user.models import Profile
from serv.models import Transfer


from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    def handle(self, *args, **options):
        users = Profile.objects.all()
        print "username,birth,age,balance,trecv,tgiven,hrecv,hgiven"
        for user in users:
            transf1 = [i.credit_hours() for i in user.transfers_received.all()]
            transf2 = [i.credit_hours() for i in user.transfers_given.all()]
            data = [user.username,
                    user.birth_date.strftime("%d/%m/%Y"),
                    datetime.datetime.now().year - user.birth_date.year,
                    user.balance,
                    len(transf1), len(transf2), sum(transf1), sum(transf2)]
            print ','.join(map(str, data))

        transfers = [i.credit_hours() for i in Transfer.objects.all()]
        print ""
        print "total transfer,%s" % len(transfers)
        print "total hours,%s" % sum(transfers)
