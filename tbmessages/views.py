# the absolute_import ensures that the import of utils.py is from parent dir
from __future__ import absolute_import
import datetime
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from timebank.utils import login_required, ViewClass
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_noop
from django.core.urlresolvers import reverse
from django.conf import settings

from tbmessages.models import Message
from tbmessages.forms import ComposeForm
from tbmessages.utils import format_quote

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

class Inbox(ViewClass):
    @login_required
    def GET(self, template_name='messages/inbox.html'):
        """
        Displays a list of received messages for the current user.
        Optional Arguments:
            ``template_name``: name of the template to use.
        """
        message_list = Message.objects.inbox_for(self.request.user)
        return self.context_response(template_name, {
            'message_list': message_list,
            'current_tab': 'messages',
            'subtab': 'inbox'
        })
inbox = Inbox()

class Outbox(ViewClass):
    @login_required
    def GET(self, template_name='messages/outbox.html'):
        """
        Displays a list of sent messages by the current user.
        Optional arguments:
            ``template_name``: name of the template to use.
        """
        message_list = Message.objects.outbox_for(self.request.user)
        return self.context_response(template_name, {
            'message_list': message_list,
            'current_tab': 'messages',
            'subtab': 'outbox'
        })
outbox = Outbox()

class Trash(ViewClass):
    @login_required
    def GET(self, template_name='messages/trash.html'):
        """
        Displays a list of deleted messages.
        Optional arguments:
            ``template_name``: name of the template to use
        Hint: A Cron-Job could periodicly clean up old messages, which are deleted
        by sender and recipient.
        """
        message_list = Message.objects.trash_for(self.request.user)
        return self.context_response(template_name, {
            'message_list': message_list,
            'current_tab': 'messages',
            'subtab': 'trash'
        })
trash = Trash()

class Compose(ViewClass):
    """
    Displays and handles the ``form_class`` form to compose new messages.
    Required Arguments: None
    Optional Arguments:
        ``recipient``: username of a `django.contrib.auth` User, who should
                       receive the message, optionally multiple usernames
                       could be separated by a '+'
        ``form_class``: the form-class to use
        ``template_name``: the template to use
        ``success_url``: where to redirect after successfull submission
    """
    @login_required
    def GET(self, recipient=None, form_class=ComposeForm,
            template_name='messages/compose.html', success_url=None, recipient_filter=None):
        form = form_class()
        if recipient is not None:
            recipients = [u for u in User.objects.filter(username__in=[r.strip() for r in recipient.split('+')])]
            form.fields['recipient'].initial = recipients
        return self.context_response(template_name, {
            'form': form,
            'current_tab': 'messages',
            'subtab': 'new'
        })

    @login_required
    def POST(self, recipient=None, form_class=ComposeForm,
            template_name='messages/compose.html', success_url=None, recipient_filter=None):
        sender = self.request.user
        form = form_class(self.request.POST, recipient_filter=recipient_filter)
        if form.is_valid():
            form.save(sender=self.request.user)
            self.flash(_(u"Message successfully sent."))
            if success_url is None:
                success_url = reverse('messages_inbox')
            if self.request.GET.has_key('next'):
                success_url = self.request.GET['next']
            return HttpResponseRedirect(success_url)
        return self.context_response(template_name, {
            'form': form,
            'current_tab': 'messages',
            'subtab': 'new'
        })
compose = Compose()

class Reply(ViewClass):
    @login_required
    def GET(self, message_id, form_class=ComposeForm,
            template_name='messages/compose.html', success_url=None, recipient_filter=None):
        """
        Prepares the ``form_class`` form for writing a reply to a given message
        (specified via ``message_id``). Uses the ``format_quote`` helper from
        ``messages.utils`` to pre-format the quote.
        """
        parent = get_object_or_404(Message, id=message_id)

        if parent.sender.username != self.request.user.username and parent.recipient.username != self.request.user.username:
            raise Http404

        form = form_class({
            'body': _(u"%(sender)s wrote:\n%(body)s") % {
                'sender': parent.sender,
                'body': format_quote(parent.body)
                },
            'subject': _(u"Re: %(subject)s") % {'subject': parent.subject},
            'recipient': [parent.sender,]
        })
        return self.context_response(template_name, {
            'form': form,
            'current_tab': 'messages',
            'subtab': 'new'
        })

    @login_required
    def POST(self, message_id, form_class=ComposeForm,
            template_name='messages/compose.html', success_url=None, recipient_filter=None):
        """
        Prepares the ``form_class`` form for writing a reply to a given message
        (specified via ``message_id``). Uses the ``format_quote`` helper from
        ``messages.utils`` to pre-format the quote.
        """
        parent = get_object_or_404(Message, id=message_id)

        if parent.sender.username != self.request.user.username and parent.recipient.username != self.request.user.username:
            raise Http404

        sender = self.request.user
        form = form_class(self.request.POST, recipient_filter=recipient_filter)
        if form.is_valid():
            form.save(sender=self.request.user, parent_msg=parent)
            self.flash(_(u"Message successfully sent."))
            if success_url is None:
                success_url = reverse('messages_inbox')
            return HttpResponseRedirect(success_url)
        return self.context_response(template_name, {
            'form': form,
            'current_tab': 'messages',
            'subtab': 'new'
        })
reply = Reply()

class Delete(ViewClass):
    @login_required
    def GET(self, message_id, success_url=None):
        """
        Marks a message as deleted by sender or recipient. The message is not
        really removed from the database, because two users must delete a message
        before it's save to remove it completely.
        A cron-job should prune the database and remove old messages which are
        deleted by both users.
        As a side effect, this makes it easy to implement a trash with undelete.

        You can pass ?next=/foo/bar/ via the url to redirect the user to a different
        page (e.g. `/foo/bar/`) than ``success_url`` after deletion of the message.
        """
        user = self.request.user
        now = datetime.datetime.now()
        message = get_object_or_404(Message, id=message_id)
        deleted = False
        if success_url is None:
            success_url = reverse('messages_inbox')
        if self.request.GET.has_key('next'):
            success_url = self.request.GET['next']
        if message.sender.username == user.username:
            message.sender_deleted_at = now
            deleted = True
        if message.recipient.username == user.username:
            message.recipient_deleted_at = now
            deleted = True
        if deleted:
            message.save()
            self.flash(_(u"Message successfully deleted."))
            if notification:
                notification.send([user], "messages_deleted", {'message': message,})
            return HttpResponseRedirect(success_url)
        raise Http404
delete = Delete()

class Undelete(ViewClass):
    @login_required
    def GET(self, message_id, success_url=None):
        """
        Recovers a message from trash. This is achieved by removing the
        ``(sender|recipient)_deleted_at`` from the model.
        """
        user = self.request.user
        message = get_object_or_404(Message, id=message_id)
        undeleted = False
        if success_url is None:
            success_url = reverse('messages_inbox')
        if self.request.GET.has_key('next'):
            success_url = self.request.GET['next']
        if message.sender.username == user.username:
            message.sender_deleted_at = None
            undeleted = True
        if message.recipient.username == user.username:
            message.recipient_deleted_at = None
            undeleted = True
        if undeleted:
            message.save()
            self.flash(_(u"Message successfully recovered."))
            if notification:
                notification.send([user], "messages_recovered", {'message': message,})
            return HttpResponseRedirect(success_url)
        raise Http404
undelete = Undelete()

class View(ViewClass):
    @login_required
    def GET(self, message_id, template_name='messages/view.html'):
        """
        Shows a single message.``message_id`` argument is required.
        The user is only allowed to see the message, if he is either
        the sender or the recipient. If the user is not allowed a 404
        is raised.
        If the user is the recipient and the message is unread
        ``read_at`` is set to the current datetime.
        """
        user = self.request.user
        now = datetime.datetime.now()
        message = get_object_or_404(Message, id=message_id)
        if (message.sender.username != user.username) and (message.recipient.username != user.username):
            raise Http404
        if message.read_at is None and message.recipient.username == user.username:
            message.read_at = now
            message.save()
        return self.context_response(template_name, {
            'message': message,
            'current_tab': 'messages'
        })
view = View()
