# -*- coding: utf-8 -*-
import os
from ..item import Item


class Asset(Item):
    """
    This class describes an Asset object child of Item class.
    """

    def upload_on_task(self, task_name='', path=None, data={}, version_name=None, override_media = True, message = None):
        """
        Uploads new media version on asset task

        :param      task_name:      The task name
        :type       task_name:      string
        :param      path:           The media path to upload, optional
        :type       path:           string
        :param      data:           The data you want to upload with the file, optional
        :type       data:           dict
        :param      version_name:   The name of the version where you want to upload the file. Without version_name, the media is uploaded in the task, optional
        :type       version_name:   string
        :param      override_media: If the media already exist, a new history is created to override the existing one, optional
        :type       override_media: boolean
        :param      message:        The message associated with the upload, optional
        :type       message:        string

        :returns:   Updated media object
        :rtype:     dictionary
        """

        mediaName = data.get('name', '')
        if (path is not None):
            file_dir, file_name = os.path.split(path)
            if (file_name is not None):
                mediaName = file_name
        query = "# -($Child, 2)> 0,1 $Task AND item.data.name == '{0}' VIEW $view".format(
            task_name)

        aliases={
            'view':{
                "item": "item",
                "mediaKey": "FIRST(# -($Child)> 0,1 $Media VIEW item._key)"
            }
        }

        tasks=self.traverse(meshql=query, aliases=aliases)
        if not tasks or len(tasks) == 0:
            raise RuntimeError('Could not find request')

        media_key = tasks[0].get('mediaKey')
        task = self.parent.cast(tasks[0]['item'])

        if version_name == None:
            if not media_key or override_media == False:
                return task.append(type='Media', data=data, path=path)
            else:
                return self.parent.item(media_key).upload_file(path=path, data=data, message=message)
        else:
            versions = task.get_children(types='Version', names=version_name)

            if len(versions) > 0:
                version = versions[0].item
            else:
                version = task.append(
                    type='Version', data=dict(name=version_name)).item

            if override_media:
                medias = version.get_children(types='Media')

                if len(medias) > 0:
                    existing_medias = [media for media in medias if media.item.data.originalname == mediaName]
                    if len(existing_medias) > 0:
                        if path is None:
                            return existing_medias[0]

                        media = existing_medias[0].item
                        return media.upload_file(
                            path=path, data=data, message=message)
                    else:
                        return version.append(type='Media', data=data, path=path)
                else:
                    return version.append(type='Media', data=data, path=path)
            else:
                return version.append(type='Media', data=data, path=path)


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
