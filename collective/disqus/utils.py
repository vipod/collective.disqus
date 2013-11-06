# -*- coding: utf-8 -*-
import base64
import hmac
import time
import json
import logging
import urllib
import hashlib

from urlparse import urlparse

from zope.component import getUtility

from plone.registry.interfaces import IRegistry

from collective.disqus.config import PROJECTNAME
from collective.disqus.interfaces import IDisqusSettings

logger = logging.getLogger(PROJECTNAME)


def disqus_list_hot(forum, max_results):
    """
    Gets a list of most recommended threads.
    """
    base_url = ("https://disqus.com/api/3.0/threads/listHot.json?"
                "access_token=%s&api_key=%s&api_secret=%s&"
                "forum=%s&limit=%s")

    registry = getUtility(IRegistry)
    disqus = registry.forInterface(IDisqusSettings)
    url = base_url % (disqus.access_token,
                      disqus.app_public_key,
                      disqus.app_secret_key,
                      forum,
                      max_results)

    return get_disqus_results(url)


def disqus_list_popular(forum, max_results, interval):
    """
    Gets a list of most popular threads.
    """
    base_url = ("https://disqus.com/api/3.0/threads/listPopular.json?"
                "access_token=%s&api_key=%s&api_secret=%s&"
                "forum=%s&limit=%s&interval=%s")

    registry = getUtility(IRegistry)
    disqus = registry.forInterface(IDisqusSettings)
    url = base_url % (disqus.access_token,
                      disqus.app_public_key,
                      disqus.app_secret_key,
                      forum,
                      max_results,
                      interval)

    return get_disqus_results(url)


def get_disqus_results(url):
    """
    Creates a request to Disqus API, using the url parameter.
    """
    try:
        request = urllib.urlopen(url)
    except IOError:
        url_parse = urlparse(url)
        logger.error('IOError accessing %s://%s%s' % (url_parse.scheme,
                                                      url_parse.netloc,
                                                      url_parse.path))
        return []

    response = request.read()

    items = []
    if response:
        try:
            disqus = json.loads(response)
        except:
            logger.error('Response error with url: %s (see http://disqus.com/api/docs/errors/ '
                         'for more details)' % url)
            return []

        if disqus['code'] != 0:
            logger.error('Disqus API error: %s (see http://disqus.com/api/docs/errors/ '
                         'for more details)' % disqus['response'])
            return []

        items = disqus['response']

    return items

def get_disqus_sso_message(secret_key, user):
    """Generated DISQUS SSO message based on Application
    secret key and user.

    @user should be dictionary with at least id, username and email
    keys. Optionally it may contain: avatar (url to user image) and
    url (url to user's website) keys.
    """
    if not user:
        return ''

    # create a JSON packet of our data attributes
    data = json.dumps(user)

    # encode the data to base64
    message = base64.b64encode(data)

    # generate a timestamp for signing the message
    timestamp = int(time.time())

    # generate our hmac signature
    sig = hmac.HMAC(secret_key.encode('utf-8'), '%s %s' % (message, timestamp),
        hashlib.sha1).hexdigest()

    # return the sso message
    return "%(message)s %(sig)s %(timestamp)s" % dict(message=message,
        timestamp=timestamp, sig=sig)
