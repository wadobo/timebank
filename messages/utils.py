from django.utils.text import wrap
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.template import Context, loader
from django.template.loader import render_to_string
from django.conf import settings

from timebank.utils import send_mail, I18nString

def format_quote(text):
    """
    Wraps text at 55 chars and prepends each
    line with `> `.
    Used for quoting messages in replies.
    """
    lines = wrap(text, 55).split('\n')
    for i, line in enumerate(lines):
        lines[i] = "> %s" % line
    return '\n'.join(lines)

def new_message_email(sender, instance, signal,
        subject_prefix=_(u'New Message: %(subject)s'),
        template_name="messages/new_message.html",
        default_protocol=None,
        *args, **kwargs):
    """
    This function sends an email and is called via Django's signal framework.
    Optional arguments:
        ``template_name``: the template to use
        ``subject_prefix``: prefix for the email subject.
        ``default_protocol``: default protocol in site URL passed to template
    """
    if default_protocol is None:
        default_protocol = getattr(settings, 'DEFAULT_HTTP_PROTOCOL', 'http')

    if 'created' in kwargs and kwargs['created']:
        try:
            current_domain = Site.objects.get_current().domain
            subject = I18nString(subject_prefix, {'subject': instance.subject})
            message = I18nString(template_name, {
                'site_url': '%s://%s' % (default_protocol, current_domain),
                'message': instance,
            }, True)
            if instance.recipient.email != "":
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                    [instance,], fail_silently=True)
        except Exception, e:
            print e
            pass #fail silently

def new_transfer_email(sender, instance, signal, *args, **kwargs):

    if 'created' not in kwargs or not kwargs['created']:
        update_transfer_email(sender, instance, signal, *args, **kwargs)
        return

    current_domain = Site.objects.get_current().domain
    default_protocol = getattr(settings, 'DEFAULT_HTTP_PROTOCOL', 'http')

    recipient = instance.recipient()
    if instance.service:
        subject=I18nString(_('New transfer request from %s'),
            instance.creator().username)
    else:
        subject=I18nString(_('New direct transfer from %s'),
            instance.creator().username)
    message = I18nString("serv/new_transfer_email.html", {
            'site_url': '%s://%s' % (default_protocol, current_domain),
            'transfer': instance
        }, True)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
        [recipient,], fail_silently=True)


def update_transfer_email(sender, instance, signal, *args, **kwargs):
    current_domain = Site.objects.get_current().domain
    default_protocol = getattr(settings, 'DEFAULT_HTTP_PROTOCOL', 'http')

    if instance.status == 'q':
        recipients = [instance.creator(),]
        subject=I18nString(_('Transfer from %s edited'),
            instance.creator().username)
        template = "serv/edit_transfer_email.html"
    elif instance.status == 'a':
        recipients = [instance.creator(),]
        if instance.service:
            subject=I18nString(_('Transfer of the service from %s accepted'),
                instance.service.creator.username)
        else:
            subject=I18nString(_('Direct transfer from %s accepted'),
                instance.creator().username)
        template = "serv/accept_transfer_email.html"
    elif instance.status == 'r':
        if not instance.is_direct():
            subject=I18nString(_('Transfer to %(user1)s from a service of %(user2)s'
                ' cancelled'), {
                        'user1': instance.creator().username,
                        'user2': instance.service.creator.username
                    })
        else:
            subject=I18nString(_('Direct transfer from %s cancelled'),
                instance.creator().username)
        template = "serv/cancel_transfer_email.html"
        recipients = [instance.credits_debtor, instance.credits_payee]
    elif instance.status == 'd':
        subject=I18nString(_('Transfer of the service you did to %s confirmed'),
                instance.credits_debtor.email)
        template = "serv/done_transfer_email.html"
        recipients = [instance.credits_payee,]
    else:
        print "error, invalid updated transfer status " + instance.service.status
        return

    message = I18nString(template, {
        'site_url': '%s://%s' % (default_protocol, current_domain),
        'transfer': instance
    }, True)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients,
        fail_silently=True)
