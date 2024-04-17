# -*- coding: utf-8 -*-
from ..item import Item
import logging
logger = logging.getLogger(__name__)


class Usergroup(Item):
    """
    This class describes an user group object child of Item class.
    """

    def get_users(self):
        """
        Get the users of the user group

        :returns:   List of User object
        :rtype:     List of :class:`~aquarium.items.user.User`
        """
        result = self.do_request(
            'GET', 'usergroups/'+self._key)

        result = [self.parent.cast(data) for data in result]
        return result

    def add_user(self, user_key=''):
        """
        Add an user in the user group

        :param      user_key:  The user key
        :type       user_key:  string

        :returns:   Membership edge object
        :rtype:     dictionary
        """
        logger.debug('Add user %s to usergroup %s', user_key, self._key)
        payload = dict(userKey=user_key)
        result = self.do_request(
            'POST', 'usergroups/'+self._key, json=payload)
        return result

    def remove_user(self, user_key=''):
        """
        Remove an user from the user group

        :param      user_key:  The user key
        :type       user_key:  string

        :returns:   Deleted membership edge object
        :rtype:     dictionary
        """
        logger.debug('Remove user %s to usergroup %s', user_key, self._key)
        payload = dict(userKey=user_key)
        result = self.do_request(
            'DELETE', 'usergroups/'+self._key, json=payload)
        return result
