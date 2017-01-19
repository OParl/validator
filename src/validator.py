import sys
import requests
import json

import gi
gi.require_version('OParl', '0.2')

from gi.repository import OParl

class Validator:
    url = ""
    system = None

    def __init__(self, url):
        self.url = url

        client = OParl.Client()
        client.connect("resolve_url", Validator.resolve_url)

        self.system = client.open(url)

    def resolve_url(_, url):
        try:
            r = requests.get(url)
            r.raise_for_status()

            return r.text
        except Exception as e:
            return None

if __name__ == "__main__":
    validator = Validator(sys.argv[1])
