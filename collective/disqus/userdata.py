from zope.interface import Interface, implements

from Products.CMFCore.utils import getToolByName

class IDisqusSSOUserDataProvider(Interface):
    """This class adapts context and request and then returns data
    of authenticated user suitable for DISQUS SSO message generation.
    """

    def getUserData():
        """Returns dictionary of authenticated user data.

        Returns dictinary with the next keys:
          id - any unique user ID number associated with that account within
               your user database. This will be used to generate a unique
               username to reference in the Disqus system.
          username - the displayed name for that account
          email - the registered email address for that account
          avatar (optional) - A link to that user's avatar
          url (optional) - A link to the user's website

        Returns empty dictionary for anonymous users.
        """

class DisqusSSOUserDataProvider(object):

    implements(IDisqusSSOUserDataProvider)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getUserData(self):
        mt = getToolByName(self.context, 'portal_membership')
        mdt = getToolByName(self.context, 'portal_memberdata')
        member = mt.getAuthenticatedMember()
        if member is None or getattr(member, 'name', '') == 'Anonymous User':
            return {}

        userid = member.getId()
        username = member.getProperty('fullname') or userid
        email = member.getProperty('email')
        if not email:
            email = '%s@email.address' % userid

        data = {'id': userid,
                'username': username,
                'email': email}

        url = member.getProperty('home_page')
        if url:
            data['url'] = url

        portrait = mdt._getPortrait(userid)
        if portrait is not None:
            data['avatar'] = portrait.absolute_url()

        return data
