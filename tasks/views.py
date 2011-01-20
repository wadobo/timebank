# -*- coding: utf-8 -*-
# Copyright (C) 2010 Eduardo Robles Elvira <edulix AT gmail DOT com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.core.paginator import Paginator
from django.shortcuts import redirect

from datetime import datetime, timedelta

from utils import ViewClass, login_required
from user.models import Profile
from tasks.models import Task
from serv.models import Transfer, Service
from messages.models import Message

class SendEmailUpdates(ViewClass):
    '''
    If emails should be sent or not it's something will be checked every
    <update_period>. Note that the period needs to be at least the same
    as the lesser "every" period, and it's best to make them multiples of each
    other.
    '''
    update_period = timedelta(hours=6)

    '''
    Email periods: List of tuples with periods. For example:
        * first day, send an email each day
        * first week, send an email
        ..
    '''
    email_periods = [
        {"period": timedelta(days=1), 'every': timedelta(days=1)},
        {"period": timedelta(weeks=1), 'every': timedelta(weeks=1)},
        {"period": timedelta(days=30), 'every': timedelta(days=15)},
        {"period": timedelta(days=365), 'every': timedelta(days=30)}
    ]

    @login_required
    def GET(self):
        if not self.request.user.is_staff and \
            not self.request.user.is_superuser:
            self.flash(_("You don't have permission to execute the task of"
                " sending email updates to the users"), "error")
            return redirect("/")

        # if the task exists, retrieve it, or create it
        task_list = Task.objects.filter(name=self.__class__.__name__)
        if task_list:
            task = task_list[0]
        else:
            task = Task()
            task.name = self.__class__.__name__
            # ensure that the task will be executed
            self.flash(_(u"Update task postponed"))

        # NOTE: force update, just for development/debug, remove later!
        task.last_update = datetime.now() - 2*self.update_period

        if datetime.now() - task.last_update > self.update_period:
            self.__execute(task)
            task.last_update = datetime.now()
            task.save()
            self.flash(_(u"Update task done"))
        else:
            self.flash(_(u"Update task postponed"))
        return redirect("/")

    def __execute(self, task):
        '''
        Sends an email update when needed. We will send for each user only one
        update email each time, with all the the user update info. Updates will
        be sent in periods.
        '''
        for user in Profile.objects.all():
            if not user.email_updates:
                continue
            unread_messages = Message.objects.inbox_for(user).filter(read_at__isnull=True)
            unread_comments = Message.objects.public_inbox_for(user).\
                filter(read_at__isnull=True)
            transfers_pending = user.transfers_pending()
            send_update_data = [
                {"data": unread_messages, "date_field": "sent_at"},
                {"data": unread_comments, "date_field": "sent_at"},
                {"data": transfers_pending, "date_field": "request_date"},
            ]

            if self.__should_send_update(task, send_update_data):
                subject = _(u"Updates from %s" % settings.SITE_NAME)
                default_protocol = getattr(settings, 'DEFAULT_HTTP_PROTOCOL', 'http')
                new_services = Service.objects.filter(activo=True)
                paginator = Paginator(new_services, 5)
                new_services = paginator.page(1)

                message = render_to_string("tasks/email_update.html", dict(
                    site_url='%s://%s' % (default_protocol, Site.objects.get_current().domain),
                    site_name=settings.SITE_NAME,
                    unread_messages=unread_messages,
                    unread_comments=unread_comments,
                    transfers_pending=transfers_pending,
                    new_services=new_services,
                    recipient=user,
                    context_instance=RequestContext(self.request)
                ))
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                    [user.email])
                return

    def __should_send_update(self, task, data):
        '''
        Given an array of arrays of objects, each object having field with a
        date to be checked, returns if it's needed to send an email.
        '''
        current_date = datetime.now()
        update_period_seconds = self.update_period.total_seconds
        for dict_item in data:
            for obj in dict_item["data"]:
                start_date = getattr(obj, dict_item["date_field"])
                email_period_date = start_date

                # For each object, find the email period we are in
                for email_period in self.email_periods:
                    max_period_date = email_period_date + email_period["period"]
                    if max_period_date < current_date:
                        # we're not in this period, maybe in the following one
                        email_period_date = max_period_date
                        continue
                    # we found the period we are in! if task.last_update is
                    # from an older period, then we should send the email update
                    if task.last_update < email_period_date:
                        return True
        return False

send_email_updates = SendEmailUpdates()
