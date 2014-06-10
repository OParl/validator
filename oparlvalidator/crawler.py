# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
from .validator import OParl


class Crawler(object):

    def __init__(self, url, _types=None, _whole_system=False):
        self.visited = set()
        self.to_visit = set([url])

    def _load(self, _source):
        return '{}'

    def validate(self, _num_docs=None):
        while len(self.to_visit) > 0:
            url = self.to_visit.pop()
            if url not in self.visited:
                self.visited.add(url)
                content = self._load(url)
                oparl = OParl()
                oparl.validate(content)
                self.to_visit.update(oparl.links)
        return True
