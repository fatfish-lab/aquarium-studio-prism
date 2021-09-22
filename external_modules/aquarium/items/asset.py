# -*- coding: utf-8 -*-
from ..item import Item


class Asset(Item):
    """
    This class describes an Asset object child of Item class.
    """

    def upload_on_task(self, task_name='', path=''):
        """
        Uploads new media version on asset task

        :param      task_name:  The task name
        :type       task_name:  string
        :param      path:       The media path to upload
        :type       path:       string

        :returns:   Updated media object
        :rtype:     dictionary
        """
        query="# -($Child)> $Task AND item.data.name == '{0}' VIEW $view".format(task_name)

        aliases={
            'view':{
                "taskKey": "item._key",
                "mediaKey": "# -($Child)> 0,1 $Media VIEW item._key"
            }
        }

        view=self.traverse(meshql=query, aliases=aliases)
        if not view:
            raise RuntimeError('Could not find request')
        view=view[0]
        media_key=view.get('mediaKey')

        if not media_key:
            media=self.parent.task(view.get('taskKey')).append(type='Media')
            media_key=media.item._key

        if isinstance(media_key, list):
            media_key=media_key[0]

        return self.parent.item(media_key).upload_file(path=path)

    def get_tasks(self, task_name='', task_status=''):
        """
        Gets the tasks of the asset

        :param      task_name:    The name of the task
        :type       task_name:    string, optional
        :param      task_status:  The status of the task
        :type       task_status:  string, optional

        :returns:   List of Task object and Edge object
        :rtype:     List of dictionary {item: :class:`~aquarium.items.task.Task`, edge: :class:`~aquarium.edge.Edge`}
        """
        query='# -($Child)> $Task'
        if task_name:
            query+=" AND item.data.name == '{0}'".format(task_name)
        if task_status:
            query+=" AND item.data.status == '{0}'".format(task_status)

        result=self.traverse(meshql=query)
        result=[self.parent.element(data) for data in result]
        return result

    def get_assigned_tasks(self, user_key= '', task_name='', task_status=''):
        """
        Gets the asset's assigned tasks to specific user

        :param      user_key:     The user key
        :type       user_key:     string
        :param      task_name:    The name of the task used to filter
        :type       task_name:    string, optional
        :param      task_status:  The status of the task used to filter
        :type       task_status:  string, optional

        :returns:   List of Task object and Edge object
        :rtype:     List of dictionary {item: :class:`~aquarium.items.task.Task`, edge: :class:`~aquarium.edge.Edge`}
        """
        query="# -($Child)> $Task"

        if task_name:
            query+=" AND item.data.name == '{0}'".format(task_name)
        if task_status:
            query+=" AND item.data.status == '{0}'".format(task_status)

        query+=" AND -($Assigned)> item._key == '{0}'".format(user_key)

        result=self.traverse(meshql=query)
        result=[self.parent.element(data) for data in result]
        return result

    def get_by_task(self, project_key='', task_status='', task_name='', task_completed=False):

        """
        Gets project tasks by filters.

        :param      project_key:     The project key
        :type       project_key:     string
        :param      task_status:     The task status
        :type       task_status:     string
        :param      task_name:       The task name
        :type       task_name:       string, optional
        :param      task_completed:  Task is completed
        :type       task_completed:  boolean

        :returns:   The tasks.
        :rtype:     dictionary
        """
        project=list()
        task=list()

        project.append("(<($Child, 5)- item._key == '{0}' AND path.vertices[*].type NONE == 'User')".format(project_key))

        task.append("(-($Child)> ($Task AND item.data.status == '{0}'".format(task_status))
        task.append("AND item.data.completion {0}= 1".format(['!', '='][task_completed]))

        if task_name:
            task.append("AND item.data.name == '{0}'".format(task_name))
        task.append('))')

        query="# $Asset AND {0} AND {1}".format(' '.join(project), ' '.join(task))

        result=self.parent.query(meshql=query)
        result=[self.parent.element(data) for data in result]
        return result
