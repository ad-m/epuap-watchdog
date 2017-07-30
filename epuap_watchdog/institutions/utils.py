import re
from functools import reduce

REPLACE_MAP = ((' We ', ' we '),
               (' W ', ' w '),
               (' Z Siedz.W ', ' z siedzibą w '),
               (' I ', ' i '),
               (' Dr ', ' dr '),
               (' Im. ', ' im. '),
               (' Z ', ' z '),
               (' Nr ', ' nr '),
               (' Siedzibą ', ' siedzibą '),
               (' w Likwidacji', ' w likwidacji'),
               (' M.St.Warszawy', ' m. st. Warszawy'),
               (' Do ', ' do '),
               (' i I II St. ', ' I i II St. '),
               (' Im.', ' im. '),
               ('  ', ' '),
               (' Dla ', ' dla '),
               ('\'\'', '"'),
               (' Samorzadowy ', ' samorządowy '),
               (' Miasta Stołecznego Warszawy ', ' m. st. Warszawy '))
RE_SPACE = re.compile(' {1,}')
RE_ROMAN = re.compile(r'( [IiXxVv]{2,}|^[IiXxVv]{2,})')


def normalize(name):
    name = RE_SPACE.sub(' ', name)
    if name[0] == '"' and name[-1] == '"':
        name = name[1:-1]
    name = name.title()
    name = RE_ROMAN.sub(lambda x: x.group(0).upper(), name)
    name = reduce(lambda x, y: x.replace(y[0], y[1]), REPLACE_MAP, name)
    name = RE_SPACE.sub(' ', name)
    return name


def normalize_regon(regon):
    if regon:
        regon = regon.replace(' ', '').replace('-', '')
    if regon and len(regon) == 14 and regon[-5:] == "0"*5:
        return regon[:14-5]
    return regon
