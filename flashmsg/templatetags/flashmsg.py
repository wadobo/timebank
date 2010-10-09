from django import template


register = template.Library()


def do_flash(parser, token):
    return flashNode()


class flashNode(template.Node):

    def render(self, context):
        flash = context['session'].get('flash', None)
        context['session']['flash'] = None
        if flash:
            return flash.render()
        else:
            return ''



register.tag('flash', do_flash)
