import sys
import requests
import json

import gi
gi.require_version('OParl', '0.2')

from gi.repository import OParl

def resolve(_, url):
    try:
        r = requests.get(url)
        r.raise_for_status()

        return r.text
    except Exception as e:
        return None

if __name__ == "__main__":
    client = OParl.Client()
    client.connect("resolve_url", resolve)
    system = client.open(sys.argv[1])

    print(system.get_name())
