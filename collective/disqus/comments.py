# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from zope.component import getUtility
from plone.uuid.interfaces import IUUID
from plone.registry.interfaces import IRegistry

from plone.app.layout import viewlets
from plone.app.discussion.interfaces import IConversation

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.disqus import interfaces
from collective.disqus.utils import get_disqus_sso_message
from collective.disqus.userdata import IDisqusSSOUserDataProvider


class DisqusBaseViewlet(viewlets.common.ViewletBase):
    """ A base class to be used for Disqus viewlets """

    def is_discussion_allowed(self):
        context = aq_inner(self.context)
        conversation = IConversation(context)
        super_enabled = conversation.enabled()
        return super_enabled and self._activated()

    def _activated(self):
        settings = self.settings()
        return settings.activated and bool(settings.forum_short_name)

    def settings(self):
        registry = getUtility(IRegistry)
        return registry.forInterface(interfaces.IDisqusSettings)


class CommentsViewlet(DisqusBaseViewlet):
    """Viewlet to display disqus"""
    index = ViewPageTemplateFile('comments.pt')

    def javascriptvars(self):
        """
        Return javascripts vars
        Documented in http://help.disqus.com/customer/portal/articles/472098
        """
        vars = {}
        settings = self.settings()
        vars['disqus_shortname'] = settings.forum_short_name
        if settings.developer_mode:
            vars['disqus_developer'] = 1
        uid = IUUID(self.context, None)
        if not uid:
            uid = self.context.UID()
        vars['disqus_identifier'] = uid
        vars['disqus_url'] = self.context.absolute_url()
        vars['disqus_title'] = self.context.pretty_title_or_id()

        user = getMultiAdapter((self.context, self.request),
            IDisqusSSOUserDataProvider).getUserData()
        vars['disqus_config'] = """function() {
            this.page.remote_auth_s3 = '%(sso_message)s';
            this.page.api_key = '%(sso_public_key)s';
        }
        """ % {
            'sso_message': get_disqus_sso_message(settings.app_secret_key,
                user),
            'sso_public_key': settings.app_public_key,
        }

        def to_string(key):
            return "var %s='%s';" % (key, str(vars[key]))

        output = ''
        for k, v in vars.items():
            if k == 'disqus_config':
                output += "var %s=%s;" % (k, v)
            else:
                output += to_string(k)
        return output


class CommentsCountViewlet(DisqusBaseViewlet):
    """ Viewlet that will display the number of comments """

    def get_counter_js(self):
        """ Get the js mentioned in
        http://disqus.com/admin/universal/ for counting comments
        """
        settings = self.settings()

        short_name = settings.forum_short_name

        if short_name:
            result = ("<script type=\"text/javascript\" async=\"async\""
                      "        src=\"http://%s.disqus.com/count.js\" >"
                      "</script>" % short_name)

        else:
            result = ""

        return result
