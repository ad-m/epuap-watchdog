from difflib import SequenceMatcher

from django import template
from django.template.defaultfilters import safe
from teryt_tree.models import JednostkaAdministracyjna

register = template.Library()


@register.assignment_tag
def get_voivodeship():
    return JednostkaAdministracyjna.objects.voivodeship().all()


@register.simple_tag
def diff_text(a, b):
    s = SequenceMatcher(None, a, b)
    opcode = {'replace': lambda i1, i2, j1, j2: "<strike>%s</strike><strong>%s</strong>" % (a[i1:i2], b[j1:j2]),
              'delete': lambda i1, i2, j1, j2: "<strike>%s</strike>" % (a[i1:i2], ),
              'insert': lambda i1, i2, j1, j2: "<strong>%s</strong>" % (b[j1:j2], ),
              'equal': lambda i1, i2, j1, j2: a[i1:i2]}
    return safe("".join(opcode[tag](*args) for tag, *args in s.get_opcodes()))


@register.filter
def format_postcode(code):
    return code[0:2]+"-"+code[2:5]
