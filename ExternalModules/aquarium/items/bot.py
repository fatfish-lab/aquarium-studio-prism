# -*- coding: utf-8 -*-
from .user import User
import logging
logger = logging.getLogger(__name__)


class Bot(User):
    """
    This class describes an Bot object child of Item class.
    """

    def signin(self, secret=''):
        """
        Sign in a bot with it's secret

        :param      secret:  The secret of the bot
        :type       secret:  string

        :returns: Dictionary Bot object
        :rtype: Dict {bot: :class:`~aquarium.items.bot.Bot`}
        """
        logger.debug('Connect bot %s', self._key)
        # Authenticate and retrieve the access token
        payload = dict(secret=secret)
        result = self.do_request(
            'POST', 'bots/{0}/signin'.format(self._key), data=payload)

       # Store authentification information
        token = result.pop("token")
        self.parent.token = token
        result = self.parent.element(result)

        return result

    def connect(self, secret=''):
        """
        Alias of :func:`~aquarium.items.bot.Bot.signin`
        """
        return self.signin(secret)

    def signout(self):
        """
        Sign out the current bot by clearing the stored authentication token

        .. note::
            After a :func:`~aquarium.items.bot.Bot.signout`, you need to use a :func:`~aquarium.items.bot.Bot.signin` before sending authenticated requests

        :returns: None
        """
        self.do_request(
            'POST', 'signout', decoding=False)

       # Remove authentification information
        self.parent.token = None

        return None