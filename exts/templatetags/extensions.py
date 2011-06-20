# -*- coding: utf-8 -*-
# Copyright (C) 2011 Daniel Garcia Moreno <dani@danigm.net>
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


from django import template
from exts.models import Extension


register = template.Library()


def do_extension(parser, token):
    tag_name, format_string = token.split_contents()
    return extNode(format_string)


class extNode(template.Node):

    def __init__(self, format_string):
        self.format_string = format_string

    def render(self, context):
        exts = Extension.objects.filter(ext_point=self.format_string)
        if not exts.count():
            return ''
        else:
            content = '<br/>'.join(i.content for i in exts)
            return '<div class="extension" id="ext_%s">%s</div>' % (self.format_string, content)


register.tag('extension', do_extension)
