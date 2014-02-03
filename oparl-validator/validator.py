# encoding: utf8

from pyld import jsonld
import requests
import argparse


"""URLs we've visited before, so we don't touch anything twice"""
visited_urls = set()

"""URLs we are going to visit for validation"""
queue = {}


class UrlVisitedException(Exception):
    pass


class Request(Exception):
    pass


def get(url, jsonp=False):
    """Issue a GET request and return JSON"""
    if url in visited_urls:
        raise UrlVisitedException()
    visited_urls.add(url)
    headers = {'User-Agent': 'OParl 1.0 Validator/0.1'}
    r = requests.get(url, headers=headers)
    assert "content-type" in r.headers
    if jsonp == False:
        assert r.headers["content-type"] == "application/ld+json"
    else:
        assert r.headers["content-type"] == "application/json"
    if r.status_code > 300 and r.status_code < 400:
        # redirect
        visited_urls.add(r.url)
    return r.json()


def validate(endpoint):
    result = {}
    result["system"] = validate_system(endpoint)
    return result


def validate_system(url):
    """
    Check if the server is reachable at all
    and actually serves OParl content
    """
    print("Validating System: %s" % url)
    r = get(url)
    assert "@id" in r
    assert "bodies" in r
    queue[r["bodies"]] = {"type": "BODIES_LIST"}
    return True


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='Validate an OParl API endpoint')
    argparser.add_argument("url", metavar="URL",
        help="URL of the API endpoint")
    args = argparser.parse_args()
    result = validate(args.url)
    print(result)
