# -*- coding: utf-8 -*-
from ..item import Item
from .. import DEFAULT_STATUSES


class Task(Item):
    """
    This class describes a Template object child of Item class.
    """

    def assign_to(self, user_key=''):
        """
        Assign the task to user

        :param      user_key:  The user key
        :type       user_key:  string

        :returns:   Edge object
        :rtype:     :class:`~aquarium.edge.Edge`
        """
        result = self.parent.edge.create(
            type='Assigned', from_key=self._key, to_key=user_key)
        return result

    def add_timelog(self, user_key='', comment='', date='', duration=''):
        """
        Add a timelog to the task

        :param      user_key:  The user key
        :type       user_key:  string
        :param      comment:   The comment
        :type       comment:   string
        :param      date:      The date
        :type       date:      string ISO 8601 (date)
        :param      duration:  The duration
        :type       duration:  string ISO 8601 (duration)

        :returns:   Dictionary of Item object and Edge object
        :rtype:     dictionary {item: :class:`~aquarium.item.Item`, edge: :class:`~aquarium.edge.Edge`}
        """

        data = dict(
            duration=duration,
            comment=comment,
            performedAt=date,
            performedBy=user_key
        )
        result = self.append(type='Job', data=data)
        return result

    def get_statuses(self):
        """
        Gets all the statuses for the task

        :returns:   The statuses
        :rtype:     dictionary
        """
        query = "# <($Child, 40)- path.vertices[*].type NONE == 'User' -($Child)> $Properties VIEW item.data.tasks_status"
        statuses = self.traverse(meshql=query)
        statuses_dct = dict()

        for status in statuses:
            name = status.get('status')
            if name not in statuses_dct:
                statuses_dct[name] = status
        result = statuses_dct or DEFAULT_STATUSES
        return result

    def get_subtasks(self, status='', name='', is_completed=True):
        """
        Gets the subtasks of the task

        :param      status:        The status used to filter
        :type       status:        boolean, optional
        :param      name:          The name used to filter
        :type       name:          boolean, optional
        :param      is_completed:  Get completed subtasks
        :type       is_completed:  boolean, optional

        :returns:   List of Task object and Edge object
        :rtype:     List of dictionary {item: :class:`~aquarium.items.task.Task`, edge: :class:`~aquarium.edge.Edge`}
        """
        query = list()
        query.append("# -($Child)> ($Task")
        query.append(" AND item.data.completion {0}= 1".format(
            ['!', '='][is_completed]))
        if status:
            query.append("AND item.data.status == '{0}'".format(status))
        if name:
            query.append("AND item.data.name == '{0}'".format(name))

        query.append(')')

        result = self.traverse(meshql=' '.join(query))
        result = [self.parent.element(data) for data in result]
        return result

    def get_dependencies(self, mode='BOTH'):
        """
        Gets the dependencies of the task

        :param      mode:  The mode ("BOTH", "IN" or "OUT"). Used to get incoming dependencies, outgoing or both.
        :type       mode:  string, optional

        :returns:   List of Item object and Edge object
        :rtype:     List of dictionary {item: :class:`~aquarium.item.Item` or subclass : :class:`~aquarium.items.asset.Asset` | :class:`~aquarium.items.project.Project` | :class:`~aquarium.items.shot.Shot` | :class:`~aquarium.items.task.Task` | :class:`~aquarium.items.template.Template` | :class:`~aquarium.items.user.User` | :class:`~aquarium.items.usergroup.Usergroup`, edge: :class:`~aquarium.edge.Edge}`
        """
        if mode == 'BOTH':
            query = "# <($Dependency)> *"
        elif mode == 'OUT':
            query = "# -($Dependency)> *"
        elif mode == 'IN':
            query = "# <($Dependency)- *"
        else:
            raise RuntimeError(
                'Wrong value for "mode". Use "BOTH", "IN" or "OUT"')

        result = self.traverse(meshql=query)
        result = [self.parent.element(data) for data in result]
        return result

    def get_assigned_users(self):
        """
        Gets all the assigned users to the task

        :returns:   List of User or Usergroup object and Edge object
        :rtype:     List of dictionary {item: :class:`~aquarium.items.user.User` | :class:`~aquarium.items.usergroup.Usergroup`, edge: :class:`~aquarium.edge.Edge}`
        """
        query = "# -($Assigned)> *"
        result = self.traverse(meshql=query)
        result = [self.parent.element(data) for data in result]
        return result

    def get_attachments(self):
        """
        Gets all the task's attachments

        :returns:   List of Item object and Edge object
        :rtype:     List of dictionary {item: :class:`~aquarium.item.Item` or subclass : :class:`~aquarium.items.asset.Asset` | :class:`~aquarium.items.project.Project` | :class:`~aquarium.items.shot.Shot` | :class:`~aquarium.items.task.Task` | :class:`~aquarium.items.template.Template` | :class:`~aquarium.items.user.User` | :class:`~aquarium.items.usergroup.Usergroup`, edge: :class:`~aquarium.edge.Edge`}
        """
        query = "# -($Attached)> *"
        result = self.traverse(meshql=query)
        result = [self.parent.element(data) for data in result]
        return result
