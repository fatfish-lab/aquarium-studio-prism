# -*- coding: utf-8 -*-
from ..item import Item


class Organisation(Item):
    """
    This class describes an Organisation object child of Item class.
    """

    def get_member_by_email(self, email):
        """
        Get an exising member of the organisation by his/her email

        :returns:   User object
        :rtype:     :class:`~aquarium.items.user.User`
        """
        member = None
        members = self.get_all_members()
        filtered = [member for member in members if member.data.email == email]

        if (len(filtered) > 0):
            member = filtered[0]

        return member

    def get_all_members(self, limit=200, offset=None):
        """
        Gets all members of the organisation

        :param      limit:   Maximum limit number of returned members
        :type       limit:   integer
        :param      offset:  Number of skipped members. Used for pagination
        :type       offset:  integer

        :returns:   List of User object
        :rtype:     List of :class:`~aquarium.items.user.User`
        """
        params = {}
        if (limit is not None):
            params['limit'] = limit
        if (offset is not None):
            params['offset'] = offset

        result=self.do_request('GET', 'organisations/{0}/members/all'.format(self._key), params=params)
        result=[self.parent.user(user) for user in result]
        return result

    def get_active_members(self, limit=200, offset=None):
        """
        Gets all active members of the organisation

        :param      limit:   Maximum limit number of returned members
        :type       limit:   integer
        :param      offset:  Number of skipped members. Used for pagination
        :type       offset:  integer

        :returns:   List of User object
        :rtype:     List of :class:`~aquarium.items.user.User`
        """
        params = {}
        if (limit is not None):
            params['limit'] = limit
        if (offset is not None):
            params['offset'] = offset

        result = self.do_request(
            'GET', 'organisations/{0}/members/active'.format(self._key), params=params)
        result=[self.parent.user(user) for user in result]
        return result

    def get_inactive_members(self, limit=200, offset=None):
        """
        Gets all inactive members of the organisation

        :param      limit:   Maximum limit number of returned members
        :type       limit:   integer
        :param      offset:  Number of skipped members. Used for pagination
        :type       offset:  integer

        :returns:   List of User object
        :rtype:     List of :class:`~aquarium.items.user.User`
        """
        params = {}
        if (limit is not None):
            params['limit'] = limit
        if (offset is not None):
            params['offset'] = offset

        result = self.do_request(
            'GET', 'organisations/{0}/members/inactive'.format(self._key), params=params)
        result=[self.parent.user(user) for user in result]
        return result

    def add_member(self, user_key):
        """
        Add an existing user in your organisation

        :param      user_key:  The user key of the user to add in the organisation
        :type       user_key:  string

        :returns:   User object
        :rtype:     :class:`~aquarium.items.user.User`
        """

        payload = dict(userKey=user_key)

        member = self.do_request(
            'POST', 'organisations/{organisationKey}/members'.format(
                organisationKey=self._key
            ), json=payload)

        member = self.parent.cast(member)

        return member

    def create_member(self, email, name=None, aquarium_url=None):
        """
        Create a new member in your organisation

        :param      email:        The email of the new member
        :type       email:        string
        :param      name:         The name of the new member
        :type       name:         string, optional
        :param      aquarium_url: The Aquarium Studio interface url. Useful if API url is not the same as Aquarium Studio interface.
        :type       aquarium_url: string, optional (default is api_url used during module initialisation)

        :returns:   User object
        :rtype:     :class:`~aquarium.items.user.User`
        """

        member = self.parent.create_user(email, name, aquarium_url)

        self.add_member(member._key)

        return member

    def get_suborganisations(self, limit=200, offset=None):
        """
        Gets all suborganisations

        :param      limit:   Maximum limit number of returned organisations
        :type       limit:   integer
        :param      offset:  Number of skipped organisations. Used for pagination
        :type       offset:  integer

        :returns:   List of Organisation object
        :rtype:     List of :class:`~aquarium.items.organisation.Organisation`
        """
        params = {}
        if (limit is not None):
            params['limit'] = limit
        if (offset is not None):
            params['offset'] = offset

        result = self.do_request(
            'GET', 'organisations/{0}/suborganisations'.format(self._key), params=params)
        result = [self.parent.organisation(
            organisation) for organisation in result]
        return result
