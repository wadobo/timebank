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

from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate, login as django_login
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from datetime import datetime, timedelta

from utils import ViewClass, login_required, mail_owners, send_mail, I18nString
from forms import (RegisterForm, EditProfileForm, RemoveForm,
    PublicMessageForm, FindPeopleForm, FindPeople4AdminsForm,
    SendEmailToAllForm)
from models import Profile
from serv.models import Service
from messages.models import Message

class Register(ViewClass):
    def GET(self):
        form = RegisterForm()
        return self.context_response('user/register.html', {'form': form,
            'current_tab': 'register'})

    def POST(self):
        form = RegisterForm(self.request.POST)
        if not form.is_valid():
            return self.context_response('user/register.html', {'form': form,
            'current_tab': 'register'})

        # Register user
        new_user = form.save(commit=False)
        new_user.is_active = settings.AUTOACCEPT_REGISTRATION
        new_user.save()

        if not settings.AUTOACCEPT_REGISTRATION:
            # Send an email to admins and another to the user
            subject = I18nString(_("[%(site_name)s] User %(username)s joined"), {
                'site_name': settings.SITE_NAME,
                'username': new_user.username
            })
            message = I18nString(_("A new user has joined with the name %s . Please review his"
                " data and make it active."), new_user.username)
            mail_owners(subject, message)

            current_site = Site.objects.get_current()
            subject = I18nString(_("You have joined as %(username)s in %(site_name)s"), {
                'username': new_user.username,
                'site_name': settings.SITE_NAME
                })
            message = I18nString(_("Hello %(username)s!\n You just joined to http://%(url)s/ ."
                " Soon the creation of your user will be reviewed by one of our"
                " admins and if everything is ok, we will enable your user and you"
                " will be able to start participating in our community."
                u"\n\n- The team of %(site_name)s."), {
                    'username': new_user.username,
                    'url': current_site.domain,
                    'site_name': settings.SITE_NAME
                })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                [new_user], fail_silently=True)

            self.flash(_("You just joined us, <strong>%(username)s</strong>. We"
                " have sent you an email to <strong>%(email)s</strong> confirming"
                " your inscription request. As soon as our admins review your"
                " request we will send you an email and you will be able to start"
                " to participate in our community.") % {
                    'username': new_user.username,
                    'email': new_user.email
                },
                title=_("User created successfully"))
        else:
            current_site = Site.objects.get_current()
            subject = I18nString(_("You have joined as %(username)s in %(site_name)s"), {
                'username': new_user.username,
                'site_name': settings.SITE_NAME
                })
            message = I18nString(_("Hello %(username)s!\n You just joined to http://%(url)s/ ."
                " Now you can start participating in our community!"
                u"\n\n- The team of %(site_name)s."), {
                    'username': new_user.username,
                    'url': current_site.domain,
                    'site_name': settings.SITE_NAME
                })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                [new_user], fail_silently=True)

            self.flash(_("You just joined us, <strong>%(username)s</strong>. We"
                " have sent you a confirmation email to"
                " <strong>%(email)s</strong>. Now you can start to participate"
                " in our community.") % {
                    'username': new_user.username,
                    'email': new_user.email
                },
                title=_("User created successfully"))

        return redirect('main.views.index')


class Login(ViewClass):
    def GET(self):
        return redirect('main.views.index')

    def POST(self, *args):
        username = self.request.POST['username']
        password = self.request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                django_login(self.request, user)
                self.flash(_("Welcome %s") % user.username)
            else:
                self.flash(_("Your account is disabled,  contact the admins"),
                    "error")
        else:
            self.flash(_("Invalid username or password"), "error")
        return redirect('main.views.index')


class PasswordResetDone(ViewClass):
    def GET(self):
        self.flash(_("We have sent you an email to your address with"
            " instructions to recover your password. It might take a bit to"
            " arrive  to your inbox so please be patient. If it seems that it"
            " doesn't arrive, you might want to check your spam folder."),
            title=_("Password recovery in process"))
        return redirect('main.views.index')


class PasswordResetComplete(ViewClass):
    def GET(self):
        self.flash(_("Your password was changed successfully, now you can"
            " login using your username and the new password using the login"
            " form in the grey box at the left."),
            title=_("Password changed successfully"))
        return redirect('main.views.index')


class EditProfile(ViewClass):
    @login_required
    def GET(self):
        form = EditProfileForm(request=self.request, instance=self.request.user)
        return self.context_response('user/profile.html', {'form': form})

    @login_required
    def POST(self):
        form = EditProfileForm(self.request, self.request.POST,
            instance=self.request.user)
        if not form.is_valid():
            return self.context_response('user/profile.html', {'form': form})

        # Send an email to admins with old data
        old_user = self.request.user
        subject = I18nString(_("[%(site_name)s] %(username)s modified his data"), {
            'site_name': settings.SITE_NAME,
            'username': old_user.username
        })
        message = I18nString(_("Username %(username)s modified his profile. Old data:\n\n"
            u" - Name: %(old_name)s\n"
            u" - Last name: %(old_surnames)s\n"
            u" - Email address: %(old_email)s\n"
            u" - Address: %(old_address)s\n"
            u" - Birth date: %(old_birth_date)s\n"
            u" - Description: %(old_description)s\n\n"
            u"New data:\n\n"
            u" - Name: %(name)s\n"
            u" - Last name: %(surnames)s\n"
            u" - Email address: %(email)s\n"
            u" - Address: %(address)s\n"
            u" - Birth date: %(birth_date)s\n"
            u" - Description: %(description)s\n\n"), {
                'username': old_user.username,
                'old_name': old_user.first_name,
                'old_surnames': old_user.last_name,
                'old_email': old_user.email,
                'old_address': old_user.address,
                'old_birth_date':  old_user.birth_date,
                'old_description': old_user.description,
                'name': form.cleaned_data["first_name"],
                'surnames': form.cleaned_data["last_name"],
                'email': form.cleaned_data["email"],
                'address': form.cleaned_data["address"],
                'birth_date': form.cleaned_data["birth_date"],
                'description': form.cleaned_data["description"]
            })
        mail_owners(subject, message)
        form.save()

        self.flash(_("Profile updated: <a href=\"%s\">view your profile</a>.") %
            reverse("user-view-current"))

        return self.context_response('user/profile.html', {'form': form})


class Preferences(ViewClass):
    @login_required
    def GET(self):
        return self.context_response('user/preferences.html',
            {'current_tab': 'user-preferences'})


class PasswordChangeDone(ViewClass):
    @login_required
    def GET(self):
        self.flash(_("Password changed."))
        return redirect('user-preferences')


class Remove(ViewClass):
    @login_required
    def GET(self):
        form = RemoveForm()
        return self.context_response('user/remove.html', {'form': form})

    @login_required
    def POST(self):
        form = RemoveForm(self.request.POST)
        if not form.is_valid():
            return self.context_response('user/remove.html', {'form': form})

        # TODO: do not remove user, only marks it as inactive
        user = self.request.user
        user.is_active = False
        user.save()

        # Send an email to admins and another to the user
        subject = I18nString(_("[%(site_name)s] User %(username)s disabled"), {
            'site_name': settings.SITE_NAME,
            'username': user.username
        })
        message = I18nString(_("The user %(username)s has requested being removed from the"
            " website. The reason given was:\n\n%(reason)s"), {
                'username': user.username,
                'reason': form.cleaned_data["reason"]
            })
        mail_owners(subject, message)

        current_site = Site.objects.get_current()
        subject = I18nString(_("You removed your profile %(username)s in %(site_name)s"), {
            'username': user.username,
            'site_name': settings.SITE_NAME
            })
        message = I18nString(_("Hello %(username)s!\n You removed your profile in"
            " http://%(url)s/ . We regret your decision to take this"
            " step. We'll read the reason why you removed yourself from this"
            " community that you provided to us and we'll have it in mind to"
            " improve our service in the future."
            "\n\n- The team of %(site_name)s."), {
                'username': user.username,
                'url': current_site.domain,
                'site_name': settings.SITE_NAME
            })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user],
            fail_silently=True)

        self.flash(_("We regret your decision to take this step.We'll read the"
            " reason why you removed yourself from this community that you"
            " provided to us and we'll have it in mind to improve our service"
            " in the future."), title=_("User removed"))

        return redirect("user-logout")


class ViewProfile(ViewClass):
    @login_required
    def GET(self, user_id=None):
        user = user_id and get_object_or_404(Profile, id=user_id, is_active=True) or self.request.user

        send_message_form = None
        if self.request.user.is_authenticated():
            send_message_form = PublicMessageForm()

        messages = Message.objects.public_inbox_for(user)

        return self.context_response('user/view.html', {'profile': user,
            'form': send_message_form, 'message_list': messages})


class ListUserServices(ViewClass):
    @login_required
    def GET(self, user_id=None):
        user = user_id and get_object_or_404(Profile, id=user_id)
        services = user.services.all()

        try:
            page = int(self.request.GET.get('page', '1'))
        except ValueError:
            page = 1

        paginator = Paginator(services, 10)
        try:
            services = paginator.page(page)
        except (EmptyPage, InvalidPage):
            services = paginator.page(paginator.num_pages)

        context = dict(
            services=services,
            profile=user,
            current_tab="people",
            subtab="user-view-services"
        )
        return self.context_response('user/list_user_services.html', context)


class FindPeople(ViewClass):
    @login_required
    def GET(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            form = FindPeople4AdminsForm(self.request.GET)
        else:
            form = FindPeopleForm(self.request.GET)

        form.fields["user_status"].label=_("User connected")
        people = Profile.objects.filter(is_active=True)

        try:
            page = int(self.request.GET.get('page', '1'))
        except ValueError:
            page = 1

        if form.data.get("username", ''):
            username = form.data["username"]
            people = people.filter(username__contains=username)

        user_status = form.data.get("user_status", '0')
        if user_status != '0':
            if (self.request.user.is_staff or self.request.user.is_superuser) \
                and int(user_status) > 6:
                if user_status == '7': # 1 week
                    last_date = datetime.now() - timedelta(days=7)
                elif user_status == '8': # 1 month
                    last_date = datetime.now() - timedelta(days=30)
                elif user_status == '9': # 3 months
                    last_date = datetime.now() - timedelta(days=3*30)
                elif user_status == '10': # 6 months
                    last_date = datetime.now() - timedelta(days=6*30)
                elif user_status == '11':  # 1 year
                    last_date = datetime.now() - timedelta(days=365)
                people = people.filter(last_login__lt=last_date)
            else:
                if user_status == '1':
                    last_date = datetime.now() - timedelta(days=1)
                elif user_status == '2':
                    last_date = datetime.now() - timedelta(days=7)
                elif user_status == '3':
                    last_date = datetime.now() - timedelta(days=30)
                elif user_status == '4':
                    last_date = datetime.now() - timedelta(days=3*30)
                elif user_status == '5':
                    last_date = datetime.now() - timedelta(days=6*30)
                elif user_status == '6':
                    last_date = datetime.now() - timedelta(days=365)
                people = people.filter(last_login__gt=last_date)

        if (self.request.user.is_staff or self.request.user.is_superuser) \
            and form.data.get("without_services", ''):
            people = people.exclude(id__in=Service.objects.values_list(
                'creator_id', flat=True))

        paginator = Paginator(people, 10)
        try:
            people = paginator.page(page)
        except (EmptyPage, InvalidPage):
            people = paginator.page(paginator.num_pages)

        context = dict(
            people=people,
            current_tab="people",
            form=form
        )
        return self.context_response('user/find_people.html', context)


class SendMessage(ViewClass):
    @login_required
    def POST(self, recipient_id=None):
        recipient = get_object_or_404(Profile, id=recipient_id)
        form = PublicMessageForm(self.request.POST)
        new_message = form.save(commit=False)
        new_message.sender = self.request.user
        new_message.recipient = recipient
        new_message.is_public = True
        new_message.save()
        self.flash(_("Message added to %s public profile") %\
            recipient.username)
        return redirect("user-view", user_id=recipient_id)


class SendEmailToAll(ViewClass):
    @login_required
    def GET(self):
        # check permissions
        if not self.request.user.is_staff or\
            not self.request.user.is_superuser:
            self.flash(_("You don't have permission to send an email to all"
                " users"))
            return redirect('main.views.index')

        form = SendEmailToAllForm()
        return self.context_response('user/send_email_to_all.html',
            {'form': form, 'current_tab': 'admin-panel'})

    def POST(self):
        # check permissions
        if not self.request.user.is_staff or\
            not self.request.user.is_superuser:
            self.flash(_("You don't have permission to send an email to all"
                " users"))
            return redirect('main.views.index')

        form = SendEmailToAllForm(self.request.POST)
        if not form.is_valid():
            return self.context_response('user/send_email_to_all.html',
                {'form': form, 'current_tab': 'admin-panel'})

        mass_email = EmailMessage(form.cleaned_data["subject"], form.cleaned_data["message"],
            from_email=settings.DEFAULT_FROM_EMAIL, to=[],
            bcc=[user.email for user in Profile.objects.filter(is_active=True)])
        mass_email.send()
        self.flash(_("Email sent to all users"))
        return redirect('main.views.index')


login = Login()
register = Register()
password_reset_done = PasswordResetDone()
password_reset_complete = PasswordResetComplete()
edit_profile = EditProfile()
preferences = Preferences()
password_change_done = PasswordChangeDone()
remove = Remove()
view_profile = ViewProfile()
send_message = SendMessage()
find_people = FindPeople()
send_email_to_all = SendEmailToAll()
list_user_services = ListUserServices()
