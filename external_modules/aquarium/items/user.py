# -*- coding: utf-8 -*-
from .. import URL_CONTENT_TYPE
from ..item import Item
from ..element import Element
import logging
logger = logging.getLogger(__name__)


class User(Item):
    """
    This class describes an User object child of Item class.
    """

    def signin(self, email='', password=''):
        """
        Sign in a user with it's email and password

        :param      email:     The email of the user
        :type       email:     string
        :param      password:  The password of the user
        :type       password:  string

        :returns: Dictionary User object
        :rtype: Dict {user: :class:`~aquarium.items.user.User`}
        """
        logging.debug('Connect user %s', email)
        # Authenticate and retrieve the access token
        payload = dict(email=email, password=password)
        result = self.do_request(
            'POST', 'signin', headers=URL_CONTENT_TYPE, data=payload)

       # Store authentification information
        token = result.pop("token")
        self.parent.token = token
        result = self.parent.element(result)

        return result

    def connect(self, email='', password=''):
        """
        Alias of :func:`~aquarium.items.user.User.signin`
        """
        return self.signin(email, password)

    def signout(self):
        """
        Sign out the current user by clearing the stored authentication token

        .. note::
            After a :func:`~aquarium.items.user.User.signout`, you need to use a :func:`~aquarium.items.user.User.signin` before sending authenticated requests

        :returns: None
        """
        self.do_request(
            'POST', 'signout', decoding=False)

       # Remove authentification information
        self.parent.token = None

        return None

    def get_profile(self):
        """
        Get the current profil.

        :returns:   User, Usergroups and Organisations object
        :rtype:     Dict {user: :class:`~aquarium.items.user.User`, usergroups: [:class:`~aquarium.items.usergroup.Usergroup`], organisations: [:class:`~aquarium.items.organisation.Organisation`]}
        """
        result = self.do_request('GET', 'users/me')
        result = self.parent.element(result)
        return result

    def get_current(self):
        """
        Get the current user.

        :returns:   User object
        :rtype:     :class:`~aquarium.items.user.User`
        """
        result = self.get_profile().user
        return result

    def get_tasks(self, project_key='', task_status='', task_name='', task_completed=False):
        """
        Gets the assigned task of the user

        :param      project_key:      The project key used to filter
        :type       project_key:      string
        :param      task_status:      The task status used to filter
        :type       task_status:      string, optional
        :param      task_name:        The task nam used to filtere
        :type       task_name:        string, optional
        :param      task_completed:   Filter the completed tasks
        :type       task_completed:  boolean, optional

        :returns:   List of Task object with there edge
        :rtype:     List of dict {item: :class:`~aquarium.items.task.Task`, edge: :class:`~aquarium.edge.Edge`}
        """
        task = list()
        query = list()

        task.append("($Task")
        if task_completed:
            task.append("AND item.data.completion == 1")
        if task_status:
            task.append("AND item.data.status == '{0}'".format(task_status))
        if task_name:
            task.append("AND item.data.name == '{0}'".format(task_name))

        task.append(')')

        query.append("# <($Assigned)- ({0}".format(' '.join(task)))

        if project_key:
            query.append(
                "AND (<($Child, 5)- item._key == '{0}' AND path.vertices[*].type NONE == 'User')".format(project_key))

        query.append(")")

        result = self.traverse(meshql=' '.join(query))
        result = [self.parent.element(data) for data in result]
        return result
