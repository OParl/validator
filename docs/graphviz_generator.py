# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import re
import sys
import os

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from oparlvalidator.schema import OPARL

OUTPUT_FILE = 'graph.dot'


def get_links(data):
    """searches for oparl:linksTo in a schema"""
    result = []
    for key in data:
        if key == 'oparl:linksTo':
            result.append(data[key])

        if type(data) is dict:  # recusion
            result = result + get_links(data[key])

    return list(set(result))  # remove duplicates


def convertBacklinks(data):
    """Converts:
       a -> b
       b -> a

       To:
       a -> b [dir=both]
    """
    lst = data.split('\n')

    for i, link in enumerate(lst):
        backlink = re.sub(r'(.*)->(.*)', r'\2->\1', link)
        if backlink != link and backlink in lst:
            lst.remove(backlink)
            lst[i] = lst[i] + '[dir=both]'

    return '\n'.join(lst)


output = ''

for key in OPARL:
    links = get_links(OPARL[key])

    for link in links:
        output += ('{}->{}\n'.format(key, link))

output = convertBacklinks(output)
output = output.replace('oparl:', '')

output = """digraph G {
concentrate=true;
overlap=false;
splines=true;
sep=.2;
""" + output + "}"

print (output)
print ('wrote file: ' + OUTPUT_FILE)

open(OUTPUT_FILE, 'w').write(output)
