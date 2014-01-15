# -*- coding: utf-8 -*-
# Copyright (C) 2010 Daniel Garcia Moreno <dani@danigm.net>
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

from timebank.utils import ViewClass, login_required
from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.http import Http404
from django.conf import settings
from django.shortcuts import redirect
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.views.decorators.csrf import csrf_protect

from serv.models import Service, Area, Category, Transfer
from serv.forms import (ServiceForm, ListServicesForm, AddTransferForm,
    AddCommentForm, NewTransferForm)
from user.models import Profile
from messages.models import Message

class ListServices(ViewClass):
    @login_required
    @csrf_protect
    def GET(self):
        form = ListServicesForm(self.request.GET)

        if not self.request.user.is_authenticated():
            del form.fields['mine']

        try:
            page = int(self.request.GET.get('page', '1'))
        except ValueError:
            page = 1

        services = Service.objects.filter(creator__is_active=True)

        if self.request.user.is_authenticated() and form.data.get("mine", ''):
            services = services.filter(creator=self.request.user)
            subtab = "my"
        else:
            services = services.filter(is_active=True)
            subtab = "find"

        if form.data.get("the_type", '') == "1":
            services = services.filter(is_offer=True)
        elif form.data.get("the_type", '') == "2":
            services = services.filter(is_offer=False)

        if form.data.get("category", ''):
            category = get_object_or_404(Category, id=int(form.data["category"]))
            services = services.filter(category=category)

        if form.data.get("area", ''):
            area = get_object_or_404(Area,
                id=int(form.data["area"]))
            services = services.filter(area=area)

        user_status = form.data.get("user_status", '0')
        if user_status != '0':
            if user_status == '1': # one day
                last_date = datetime.now() - timedelta(days=1)
            elif user_status == '2': # 1 week
                last_date = datetime.now() - timedelta(days=7)
            elif user_status == '3': # 1 month
                last_date = datetime.now() - timedelta(days=30)
            elif user_status == '4': # 3 months
                last_date = datetime.now() - timedelta(days=3*30)
            elif user_status == '5': # 6 months
                last_date = datetime.now() - timedelta(days=6*30)
            elif user_status == '6': # 1 year
                last_date = datetime.now() - timedelta(days=365)
            services = services.filter(creator__last_login__gt=last_date)

        if form.data.get("username", ''):
            username = form.data["username"]
            services = services.filter(creator__username__contains=username)

        if form.data.get("text", ''):
            text = form.data['text']
            services = services.filter(description__contains=text)

        paginator = Paginator(services, 10)
        try:
            services = paginator.page(page)
        except (EmptyPage, InvalidPage):
            services = paginator.page(paginator.num_pages)

        context = dict(
            services=services,
            current_tab="services",
            subtab=subtab,
            form=form
        )
        return self.context_response('serv/services.html', context)


class AddService(ViewClass):
    @login_required
    def GET(self):
        form = ServiceForm()
        context = dict(form=form, instance=None, current_tab="services",
            subtab="add")
        return self.context_response('serv/edit_service.html', context)

    @login_required
    def POST(self):
        form = ServiceForm(self.request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.creator = self.request.user
            service.save()
            self.flash(_(u"Service added successfully"))
            return redirect('serv-myservices')
        context = dict(form=form, instance=None, current_tab="services",
            subtab="add")
        return self.context_response('serv/edit_service.html', context)


class EditService(ViewClass):
    @login_required
    def GET(self, sid):
        instance = get_object_or_404(Service, pk=sid)
        if not instance.creator == self.request.user:
            self.flash(_(u"You can't modify a service that isn't yours"),
                       "error")
            return redirect('serv-myservices')
        form = ServiceForm(instance=instance)
        context = dict(form=form, instance=instance, current_tab="services",
            subtab="my-services")
        return self.context_response('serv/edit_service.html', context)

    @login_required
    def POST(self, sid):
        instance = get_object_or_404(Service, pk=sid)
        if not instance.creator == self.request.user:
            self.flash(_(u"You can't modify a service that isn't yours"),
                       "error")
            return redirect('serv-myservices')
        form = ServiceForm(self.request.POST, instance=instance)

        if form.is_valid():
            current_is_offer = instance.is_offer
            service = form.save(commit=False)

            # If there are ongoing transfers, oferta field cannot be changed or
            # else havoc will follow:
            if Transfer.objects.filter(service=instance,
                status__in=["q", "a"]).count() > 0 and\
                service.is_offer != current_is_offer:
                self.flash(_(u"You can't change the type of service between"
                    " offer and demand with transfers while there are ongoing"
                    " transfers."), "error")
                return redirect('serv-myservices')
            service.save()
            self.flash(_(u"Service modified successfully"))
            return redirect('serv-myservices')
        context = dict(form=form, instance=instance, current_tab="services",
            subtab="my-services")
        return self.context_response('serv/edit_service.html', context)


class DeleteService(ViewClass):
    @login_required
    def POST(self, sid):
        instance = get_object_or_404(Service, pk=sid)
        if instance.creator == self.request.user:
            instance.delete()
            self.flash(_(u"Service removed successfully"))
        else:
            self.flash(_(u"You can't remove a service that isn't yours"),
                       "error")
        return redirect('serv-myservices')


class ActiveService(ViewClass):
    @login_required
    def POST(self, sid):
        instance = get_object_or_404(Service, pk=sid)
        if instance.creator == self.request.user:
            instance.is_active = True
            instance.save()
            self.flash(_(u"Service enabled successfully"))
        else:
            self.flash(_(u"You can't modify a service that isn't yours"),
                       "error")
        return redirect('serv-myservices')


class DeactiveService(ViewClass):
    @login_required
    def POST(self, sid):
        instance = get_object_or_404(Service, pk=sid)
        if instance.creator == self.request.user:
            instance.is_active = False
            instance.save()
            self.flash(_(u"Service disabled successfully"))
        else:
            self.flash(_(u"You can't modify a service that isn't yours"),
                       "error")
        return redirect('serv-myservices')


class NewTransfer(ViewClass):
    @login_required
    def GET(self, user_id=None):
        if user_id:
            user = get_object_or_404(Profile, pk=user_id)
            if self.request.user.is_authenticated and self.request.user == user:
                self.flash(_(u"You can't transfer credits to yourself"),
                    "error")
                return redirect("serv-transfer-new")
            else:
                form_data = dict(username=user.username)
                form = NewTransferForm(form_data)
        else:
            form = NewTransferForm()
        context = dict(form=form, current_tab="transfers", subtab="new")
        return self.context_response('serv/new_transfer.html', context)

    @login_required
    def POST(self, user_id=None):
        # check user is not doing an "auto-transfer"
        if self.request.user.is_authenticated and\
            self.request.POST["username"] == self.request.user.username:
            self.flash(_(u"You can't transfer credits to yourself"),
                "error")
            return redirect("serv-transfer-new")

        form = NewTransferForm(data=self.request.POST)
        context = dict(form=form, instance=None, current_tab="transfers",
            subtab="new")
        if not form.is_valid():
            return self.context_response('serv/new_transfer.html', context)

        transfer = form.save(commit=False)
        transfer.is_public = False
        transfer.direct_transfer_creator = self.request.user
        # the other user will always have to accept the transfer first
        transfer.status = 'q'
        if form.data["service_type"] == '0':
            # give credits
            transfer.credits_payee = form.user
            transfer.credits_debtor = self.request.user
        else:
            # request credits
            transfer.credits_payee = self.request.user
            transfer.credits_debtor = form.user

        # Check user would not surpass max balance
        if transfer.credits_payee.balance + transfer.credits > settings.MAX_CREDIT:
            self.flash(_(u"The transfer would exceed the credit limit of the"
                " credits receiver"), 'error')
            return self.context_response('serv/new_transfer.html', context)

        # Check user would not minimum min balance
        if transfer.credits_debtor.balance - transfer.credits < settings.MIN_CREDIT:
            self.flash(_(u"The transfer would exceed the minimum credit limit"
                " of the person giving the credits"),
                'error')
            return self.context_response('serv/new_transfer.html', context)

        transfer.save()
        self.flash(_(u"Transfer created successfully"))
        return redirect('serv-transfers-mine')

class AddTransfer(ViewClass):
    @login_required
    def GET(self, service_id):
        service = get_object_or_404(Service, pk=service_id)
        ongoing_transfers = service.ongoing_transfers(self.request.user)
        if ongoing_transfers:
            return redirect("serv-transfer-edit", ongoing_transfers[0].id)
        form = AddTransferForm()
        context = dict(form=form, current_tab="transfers", subtab="add",
            service=service)
        return self.context_response('serv/add_transfer.html', context)

    @login_required
    def POST(self, service_id):
        service = get_object_or_404(Service, pk=service_id)
        ongoing_transfers = service.ongoing_transfers(self.request.user)
        if ongoing_transfers:
            return redirect("serv-transfer-edit", ongoing_transfers[0].id)
        form = AddTransferForm(data=self.request.POST)
        # Check user would not surpass min balance
        if self.request.user.balance < settings.MIN_CREDIT and\
            service.is_offer:
            self.flash(_(u"You don't have enough credit"), 'error')
            return redirect('serv-transfers-mine')

        if service.creator == self.request.user:
            self.flash(_(u"You can't demand a service to yourself"))
            return redirect('serv-transfers-mine')

        if form.is_valid():
            transfer = form.save(commit=False)
            # Set remaining transfer settings
            transfer.service = service
            transfer.status = 'q'
            transfer.is_public = False
            if transfer.service.is_offer:
                transfer.credits_debtor = self.request.user
                transfer.credits_payee = transfer.service.creator
            else:
                transfer.credits_payee = self.request.user
                transfer.credits_debtor = transfer.service.creator

            # Check user would not surpass max balance
            if transfer.credits_payee.balance + transfer.credits > settings.MAX_CREDIT:
                self.flash(_(u"The transfer would exceed the credit limit of the"
                " credits receiver"), 'error')
                return redirect('serv-transfers-mine')

            # Check user would not minimum min balance
            if transfer.credits_debtor.balance - transfer.credits < settings.MIN_CREDIT:
                self.flash(_("The transfer would exceed the minimum credit limit"
                    " of the person receiving the service"), 'error')
                return redirect('serv-transfers-mine')

            # Check there's no current ongoing transfer for this service and
            # self.request.user
            if Transfer.objects.filter(credits_payee=transfer.credits_payee,
                credits_debtor=transfer.credits_debtor,
                service=service, status__in=['q', 'a']).count() > 0:
                self.flash(_("You already have an ongoing transfer for this"
                    " service"),'error')
                return redirect('serv-transfers-mine')

            transfer.save()
            self.flash(_(u"Transfer created successfully"))
            return redirect('serv-transfers-mine')

        context = dict(form=form, instance=None, current_tab="transfers",
            subtab="add", service=service)
        return self.context_response('serv/add_transfer.html', context)


class EditTransfer(ViewClass):
    @login_required
    def GET(self, transfer_id):
        transfer = get_object_or_404(Transfer, pk=transfer_id)
        if transfer.creator() != self.request.user:
            self.flash(_(u"You can't modify a transfer that isn't yours"),
                "error")
            return redirect('serv-transfers-mine')
        if transfer.status != "q":
            self.flash(_("You can only modify transfers that haven't been"
                " accepted"), "error")
            return redirect('serv-transfers-mine')
        form = AddTransferForm(instance=transfer)
        context = dict(form=form, transfer=transfer, current_tab="transfers",
            subtab="mine")
        return self.context_response('serv/edit_transfer.html', context)

    @login_required
    def POST(self, transfer_id):
        transfer = get_object_or_404(Transfer, pk=transfer_id)
        if transfer.creator() != self.request.user:
            self.flash(_("You can't modify a transfer that isn't yours"), "error")
            return redirect('serv-transfers-mine')
        if transfer.status != "q":
            self.flash(_("You can only modify transfers that haven't been"
                " accepted"), "error")
            return redirect('serv-transfers-mine')

        form = AddTransferForm(self.request.POST, instance=transfer)
        if form.is_valid():
            transfer = form.save(commit=False)
            # Check user would not surpass max balance
            if transfer.credits_payee.balance + transfer.credits > settings.MAX_CREDIT:
                self.flash(_("The transfer would exceed the credit limit of the"
                    "credits receiver"), 'error')
                return redirect('serv-transfers-mine')

            # Check user would not minimum min balance
            if transfer.credits_debtor.balance - transfer.credits < settings.MIN_CREDIT:
                self.flash(_(u"The transfer would exceed the minimum credit"
                    " limit of the person receiving the service"),
                    'error')
                return redirect('serv-transfers-mine')

            transfer.save()
            self.flash(_(u"Transfer modified successfully"))
            return redirect('serv-transfers-mine')
        context = dict(form=form, transfer=transfer, current_tab="transfer",
            subtab="mine")
        return self.context_response('serv/edit_transfer.html', context)


class CancelTransfer(ViewClass):
    @login_required
    def POST(self, transfer_id):
        transfer = get_object_or_404(Transfer, pk=transfer_id)
        if transfer.credits_debtor != self.request.user and\
            transfer.credits_payee != self.request.user:
            self.flash(_(u"You can't cancel a transfer that isn't yours"),
                "error")
            return redirect('serv-transfers-mine')
        if not transfer.status in ["q", "a"]:
            self.flash(_(u"You can only cancel transfers that haven't been"
                " done"), "error")
            return redirect('serv-transfers-mine')
        transfer.status = "r"
        transfer.save()
        self.flash(_("Transfer cancelled"))
        return redirect('serv-transfers-mine')


class AcceptTransfer(ViewClass):
    @login_required
    def POST(self, transfer_id):
        transfer = get_object_or_404(Transfer, pk=transfer_id)

        # Check user would not surpass max balance
        if transfer.credits_payee.balance + transfer.credits > settings.MAX_CREDIT:
            self.flash(_("The transfer would exceed the credit limit of the"
                " credits receiver"), 'error')
            return redirect('serv-transfers-mine')

        # Check user would not minimum min balance
        if transfer.credits_debtor.balance - transfer.credits < settings.MIN_CREDIT:
            self.flash(_("The transfer would exceed the minimum credit limit"
                " of the person receiving the service"),
                'error')
            return redirect('serv-transfers-mine')

        if transfer.creator() == self.request.user:
            self.flash(_(u"You can't accept a transfer of a service that isn't"
                " yours"), "error")
            return redirect('serv-transfers-mine')

        if (transfer.status != "a" or not transfer.is_direct()) and\
            transfer.status != "q":
            self.flash(_(u"You can only modify transfers that haven't been"
                " done"), "error")
            return redirect('serv-transfers-mine')
        transfer.status = "a"
        transfer.save()
        self.flash(_("Transfer accepted"))
        return redirect('serv-transfers-mine')


class ConfirmTransfer(ViewClass):
    @login_required
    def POST(self, transfer_id):
        transfer = get_object_or_404(Transfer, pk=transfer_id)

        # Check user would not surpass max balance
        if transfer.credits_payee.balance + transfer.credits > settings.MAX_CREDIT:
            self.flash(_(u"The transfer would exceed the credit limit of the"
                " person receiving the credits"), 'error')
            return redirect('serv-transfers-mine')

        # Check user would not minimum min balance
        if transfer.credits_debtor.balance - transfer.credits < settings.MIN_CREDIT:
            self.flash(_("The transfer would exceed the minimum credit limit"
                " of the person receiving the service"),
                'error')
            return redirect('serv-transfers-mine')

        if transfer.credits_debtor != self.request.user:
            self.flash(_("You can't confirm a transfer of a service that isn't"
                " yours"), "error")
            return redirect('serv-transfers-mine')

        if transfer.status != "a":
            self.flash(_(u"You can only confirm accepted transfers"),
                "error")
            return redirect('serv-transfers-mine')
        transfer.status = "d"
        transfer.confirmation_date = datetime.now()
        transfer.credits_debtor.balance -= transfer.credits
        transfer.credits_payee.balance += transfer.credits
        transfer.credits_debtor.save()
        transfer.credits_payee.save()
        transfer.save()

        self.flash(_("Transfer done"))
        return redirect('serv-transfers-mine')


class ViewService(ViewClass):
    @login_required
    def GET(self, service_id):
        service = get_object_or_404(Service, pk=service_id)
        context = dict(service=service, complete_description=True)
        return self.context_response('serv/view_service.html', context)


class ViewTransfer(ViewClass):
    @login_required
    def GET(self, transfer_id):
        transfer = get_object_or_404(Transfer, id=int(transfer_id))
        if transfer.credits_debtor != self.request.user and\
            transfer.credits_payee != self.request.user and\
            not transfer.is_public:
            self.flash(_(u"You don't have permissions to see this transfer"),
                "error")
            return redirect('/')

        context = dict(transfer=transfer, subtab="view")
        return self.context_response('serv/view_transfer.html', context)


class MyTransfers(ViewClass):
    @login_required
    def GET(self):
        transfers = Transfer.objects.filter(
            Q(credits_debtor=self.request.user)
            |Q(credits_payee=self.request.user)).order_by('-request_date')

        try:
            page = int(self.request.GET.get('page', '1'))
        except ValueError:
            page = 1

        paginator = Paginator(transfers, 10)
        try:
            transfers = paginator.page(page)
        except (EmptyPage, InvalidPage):
            transfers = paginator.page(paginator.num_pages)

        context = dict(transfers=transfers, subtab="mine")
        return self.context_response('serv/view_transfers.html', context)

class RateTransfer(ViewClass):
    @login_required
    def POST(self, transfer_id):
        try:
            rating = int(self.request.POST['rating'])
        except:
            self.flash(_(u"Error receiving the rating"))
            return redirect('serv-transfer-view', transfer_id)
        transfer = get_object_or_404(Transfer, id=int(transfer_id))

        if transfer.credits_debtor != self.request.user:
            self.flash(_(u"You don't have permissions to rate this transfer"),
                "error")
            return redirect('serv-transfer-view', transfer_id)

        if 1 > rating > 5:
            self.flash(_(u"Rating must be between 1 and 5"), "error")
            return redirect('serv-transfer-view', transfer_id)

        transfer.rating.add(score=rating, user=self.request.user,
            ip_address=self.request.META['REMOTE_ADDR'])
        self.flash(_(u"Transfer rating updated successfully"))

        return redirect('serv-transfer-view', transfer_id)

class AddComment(ViewClass):
    @login_required
    def GET(self, service_id):
        service = get_object_or_404(Service, pk=service_id)
        form = AddCommentForm()
        context = dict(form=form, service=service, current_tab="services",
            subtab="comment")
        return self.context_response('serv/service_add_comment.html', context)

    @login_required
    def POST(self, service_id):
        service = get_object_or_404(Service, pk=service_id)
        if not service.is_active:
            self.flash(_(u"You can't comment inactive services"),
                "error")
            return redirect('/')

        form = AddCommentForm(self.request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = self.request.user
            message.recipient = service.creator
            message.is_public = True
            message.service = service
            message.save()
            self.flash(_(u"Comment added successfully"))
            return redirect('serv-view', message.service.id)
        context = dict(form=form, current_tab="services",
            subtab="comment")
        return self.context_response('serv/service_add_comment.html', context)


class DeleteComment(ViewClass):
    @login_required
    def POST(self, comment_id):
        message = get_object_or_404(Message, pk=comment_id)
        service = None
        recipient = None

        if message.service:
            service = message.service
        else:
            recipient = message.recipient

        service = message.service
        if message.sender.id != self.request.user.id:
            self.flash(_(u"You can't remove a message that isn't yours"),
                "error")
        else:
            message.delete()
            self.flash(_(u"Comment removed successfully"))

        if service:
            return redirect('serv-view', service.id)
        else:
            return redirect('user-view', recipient.id)

list_services = ListServices()
add = AddService()
edit = EditService()
view = ViewService()
delete = DeleteService()
active = ActiveService()
deactive = DeactiveService()
new_transfer = NewTransfer()
add_transfer = AddTransfer()
edit_transfer = EditTransfer()
cancel_transfer = CancelTransfer()
accept_transfer = AcceptTransfer()
confirm_transfer = ConfirmTransfer()
view_transfer = ViewTransfer()
rate_transfer = RateTransfer()
my_transfers = MyTransfers()
add_comment = AddComment()
delete_comment = DeleteComment()
