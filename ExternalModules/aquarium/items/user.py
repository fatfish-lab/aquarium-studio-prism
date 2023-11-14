# -*- coding: utf-8 -*-
from ..item import Item
from ..element import Element
import logging
logger = logging.getLogger(__name__)


class User(Item):
    """
    This class describes an User object child of Item class.
    """

    def set_data_variables(self, data={}):
        """
        Sets the data variables of the User

        :param      data:  The object item from Aquarium API
        :type       data:  dictionary
        """
        super(Item, self).set_data_variables(data=data)
        self.active = data.get('active', False)

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
            'POST', 'signin', data=payload)

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

    def promote_as_admin(self):
        """
        Promote the user as admin.

        .. tip::
            Admin users can
                - administrate items
                - access administrative panel

        :returns:   Membership edge object
        :rtype:     dict
        """

        domain = self.parent.usergroup('domain')
        domain.add_user(self._key)

    def promote_as_super_admin(self):
        """
        Promote the user as super admin.

        .. tip::
            Super admin users can
                - add/remove licenses, users and files
                - administrate items
                - access administrative panel

        :returns:   A dict with the {user: participant, edge: the created permission edge}
        :rtype:     dict
        """

        domain = self.parent.usergroup('domain')

        try:
            domain.add_user(self._key)
        except:
            pass

        return domain.create_permission(self._key, 'rwsadtlug', False)

    def demote(self):
        """
        Remove admin and super admin privilege.

        :returns:   None
        """

        domain = self.parent.usergroup('domain')

        try:
            domain.remove_user(self._key)
            domain.remove_participant(self._key)
        except:
            pass

    def get_admin_status(self):
        """
        Return user admin status (None, 'admin' or 'super admin')

        :returns: Admin status of the user
        :rtype: None or 'admin' or 'super admin'
        """

        status = None

        domain = self.parent.usergroup('domain')
        members = domain.get_users()

        if (any([m for m in members if m._key == self._key])):
                status = 'admin'

        if status is not None:
            domain_permissions = domain.get_permissions()
            if (any([p for p in domain_permissions if p.user._key == self._key])):
                status = 'super_admin'


        return status

    def forgot_password(self, aquarium_url=None):
        """
        Start forgot password procedure. User will receive an email to reset its password.

        :param      aquarium_url: The Aquarium Studio interface url. Useful if API url is not the same as Aquarium Studio interface.
        :type       aquarium_url: string, optional (default is api_url used during module initialisation)

        :returns: True or False
        :rtype: boolean
        """

        email = self.data.email

        if (email is not None):
            data = {
                'email': email
            }
            headers = {
                'origin': aquarium_url or self.parent.api_url
            }
            self.do_request(
            'POST', 'forgot', json=data, headers=headers)
            return True
        else:
            return False