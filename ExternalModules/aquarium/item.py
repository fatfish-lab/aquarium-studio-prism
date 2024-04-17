# -*- coding: utf-8 -*-
import json
import re
import os
from .tools import jsonify
from .entity import Entity
from .exceptions import Deprecated
import mimetypes
import logging
logger = logging.getLogger(__name__)


class Item(Entity):
    """
    This class describes an Item object child of Aquarium class.
    """

    def create(self, type='', data={}, path=None):
        """
        Create an item

        .. warning::
            We advice you to use :func:`~aquarium.item.Item.append` instead of :func:`~aquarium.item.Item.create`.
            This function will create an item, without inserting it to an existing hiearchy.
            Once the item is created, you should use Edge :func:`~aquarium.edge.Edge.create` function to connect it to an other existing item.
        .. tip::
            The type of the item is case sensitive ! By convention, all items' type start with a capital letter

        :param      type:  The newitem type
        :type       type:  string
        :param      data:  The newitem data
        :type       data:  dictionary, optional
        :param      path:  File path you want to upload on the appended item
        :type       path:  string, optional

        :returns:   Item object
        :rtype:     :class:`~aquarium.item.Item` or subclass : :class:`~aquarium.items.asset.Asset` | :class:`~aquarium.items.project.Project` | :class:`~aquarium.items.shot.Shot` | :class:`~aquarium.items.task.Task` | :class:`~aquarium.items.template.Template` | :class:`~aquarium.items.user.User` | :class:`~aquarium.items.usergroup.Usergroup`
        """

        payload = dict(type=type, data=data)
        result = self.do_request('POST', 'items', json=payload)
        result = self.parent.cast(result)

        if path != None:
            upload = result.upload_file(path=path)
            if upload != None:
                for key in upload.data:
                    result.data[key] = upload.data[key]
        return result

    def append(self, type='', data={}, edge_type='Child', edge_data={}, apply_template=None, template_key=None, path=None):
        """
        Create and append a new item to the current one

        .. tip::
            The type of the item is case sensitive ! By convention, all items' type start with a capital letter


        :param      type:            The new item type
        :type       type:            string
        :param      data:            The new item data, optional
        :type       data:            dictionary
        :param      apply_template:  Do apply template ?
        :type       apply_template:  boolean, optional
        :param      template_key:    The template key to apply. If no template key, `automatic context's template <https://docs.fatfish.app/#/userguide/items?id=templates>`_ will be used.
        :type       template_key:    string, optional
        :param      path:            File path you want to upload on the appended item
        :type       path:            string, optional

        :returns:   Dictionary composed by an item and its edge.
        :rtype:     dict {item: :class:`~aquarium.item.Item` or subclass : :class:`~aquarium.items.asset.Asset` | :class:`~aquarium.items.project.Project` | :class:`~aquarium.items.shot.Shot` | :class:`~aquarium.items.task.Task` | :class:`~aquarium.items.template.Template` | :class:`~aquarium.items.user.User` | :class:`~aquarium.items.usergroup.Usergroup` | :class:`~aquarium.items.organisation.Organisation`, edge: :class:`~aquarium.edge.Edge}`
        """

        payload = {
            "item": {
                "type": type,
                "data": data
            },
            "edge": {
                "type": edge_type,
                "data": edge_data
            }
        }

        if apply_template is not None:
            payload["applyTemplate"] = apply_template

        if template_key:
            payload["templateKey"] = template_key

        result = self.do_request(
            'POST', 'items/'+self._key+'/append', json=payload)
        result = self.parent.element(result)

        if path != None:
            upload = result.item.upload_file(path=path)
            if upload != None:
                for key in upload.data:
                    result.item.data[key] = upload.data[key]

        return result

    def traverse(self, meshql='', aliases={}):
        """
        Execute a traverse from the current item

        :param      meshql:        The meshql string
        :type       meshql:        string
        :param      aliases:       The aliases used in the meshql query
        :type       aliases:       dictionary, optional

        :returns:   List of item and/or edge or VIEW used in the meshql query
        :rtype:     list
        """
        logger.debug('Send traverse : meshql : %s / aliases : %r',
                     meshql, aliases)
        data = dict(query=meshql, aliases=aliases)
        result = self.do_request(
            'POST', 'items/'+self._key+'/traverse', json=data)
        return result

    def traverse_trashed(self, meshql='', aliases={}):
        """
        Execute a traverse from the current item on trashed_items

        :param      meshql:        The meshql string
        :type       meshql:        string
        :param      aliases:       The aliases used in the meshql query
        :type       aliases:       dictionary, optional

        :returns:   List of item and/or edge or VIEW used in the meshql query
        :rtype:     list
        """
        logger.debug('Send traverse trashed_items : meshql : %s / aliases : %r',
                     meshql, aliases)
        data = dict(query=meshql, aliases=aliases)
        result = self.do_request(
            'POST', 'trashed_items/'+self._key+'/traverse', json=data)
        return result

    def replace_data(self, data={}):
        """
        Replace the item data with new ones

        .. danger::
            This is replacing all existing item data. Meaning that you can loose data.


        :param      data:  The new item data
        :type       data:  dictionary

        :returns:   Item object
        :rtype:     :class:`~aquarium.item.Item`
        """
        logger.debug('Replacing data on item %s with %r', self._key, data)
        data = dict(data=data)
        result = self.do_request(
            'PUT', 'items/'+self._key, json=data)

        result = self.parent.cast(result)
        return result

    def update_data(self, data={}, deep_merge=True):
        """
        Update the item data by merging the existing ones with the new ones

        :param      data:        The new item data
        :type       data:        dictionary
        :param      deep_merge:  Merge nested objects
        :type       deep_merge:  boolean, optional

        :returns:   Item object
        :rtype:     :class:`~aquarium.item.Item`
        """
        logger.debug('Updating data on item %s with %r', self._key, data)
        data = dict(
            data=data,
            deepMerge=deep_merge
        )
        result = self.do_request(
            'PATCH', 'items/'+self._key, json=data)
        result = self.parent.cast(result)
        return result

    def copy(self, parent_key=''):
        """
        Copie the item into the parent

        :param      parent_key:  The key of the parent
        :type       parent_key:  string

        :returns:   List of new items object
        :rtype:     List of :class:`~aquarium.item.Item` or subclass : :class:`~aquarium.items.asset.Asset` | :class:`~aquarium.items.project.Project` | :class:`~aquarium.items.shot.Shot` | :class:`~aquarium.items.task.Task` | :class:`~aquarium.items.template.Template` | :class:`~aquarium.items.user.User` | :class:`~aquarium.items.usergroup.Usergroup`
        """
        logger.debug('Copy item %s into %s', self._key, parent_key)
        data = dict(targetKey=parent_key)
        result = self.do_request(
            'POST', 'items/'+self._key+'/copy', json=data)

        result = [self.parent.cast(data) for data in result]
        return result

    def convert_to_template(self, parent_key=''):
        """
        Convert an item and its hierarchy to a template into a parent

        :param      parent_key:  The key of the parent
        :type       parent_key:  string

        :returns:   template object
        :rtype:     :class:`~aquarium.items.template.Template`
        """
        logger.debug('Converting item %s to template in %s',
                     self._key, parent_key)
        data = dict(parentKey=parent_key)
        result = self.do_request(
            'POST', 'items/'+self._key+'/convertToTemplate', json=data)
        result = self.parent.cast(result)
        return result

    def apply_template(self, template_key=''):
        """
        Apply a template on the item

        :param      template_key:  The key of the template
        :type       template_key:  string

        :returns:   Item object
        :rtype:     :class:`~aquarium.item.Item` or subclass : :class:`~aquarium.items.asset.Asset` | :class:`~aquarium.items.project.Project` | :class:`~aquarium.items.shot.Shot` | :class:`~aquarium.items.task.Task` | :class:`~aquarium.items.template.Template` | :class:`~aquarium.items.user.User` | :class:`~aquarium.items.usergroup.Usergroup`
        """
        logger.debug('Apply template %s on item %s', template_key, self._key)
        data = dict(templateKey=template_key)
        result = self.do_request(
            'POST', 'items/'+self._key+'/template', json=data)
        result = self.parent.cast(result)
        return result

    def reapply_template(self, template_key=None):
        """
        Re-apply the specific template

        :param      template_key:   The key of the template to re-apply
        :type       template_key:   string

        :returns:   Item object
        :rtype:     :class:`~aquarium.item.Item` or subclass : :class:`~aquarium.items.asset.Asset` | :class:`~aquarium.items.project.Project` | :class:`~aquarium.items.shot.Shot` | :class:`~aquarium.items.task.Task` | :class:`~aquarium.items.template.Template` | :class:`~aquarium.items.user.User` | :class:`~aquarium.items.usergroup.Usergroup`
        """
        if template_key == None:
            raise Deprecated("You can't use this function without providing the template_key you want to use.")

        logger.debug('Re-apply template %s on item %s', template_key, self._key)
        result = self.do_request(
            'POST', 'templates/{templateKey}/sync/{itemKey}'.format(
                templateKey=template_key,
                itemKey=self._key
            ))
        result = self.parent.cast(result)
        return result

    def get(self, populate=False, history=False):
        """
        Get item object with its _key

        :param      populate:  Populate `item.createdBy` and `item.updatedBy` with User object
        :type       populate:  boolean
        :param      history:   Get previous item's data history
        :type       history:   boolean, optional

        :returns:   Item object
        :rtype:     :class:`~aquarium.item.Item` or subclass : :class:`~aquarium.items.asset.Asset` | :class:`~aquarium.items.project.Project` | :class:`~aquarium.items.shot.Shot` | :class:`~aquarium.items.task.Task` | :class:`~aquarium.items.template.Template` | :class:`~aquarium.items.user.User` | :class:`~aquarium.items.usergroup.Usergroup`
        """

        params = {
            'populate': populate,
            'history': history
        }

        jsonify(params)

        result = self.do_request('GET', 'items/{0}/'.format(
            self._key), params=params)
        result = self.parent.cast(result)
        return result

    def get_history(self, populate=False):
        """
        Get the previous item's data history

        :param      populate:  Populate `item.createdBy` and `item.updatedBy` with User object
        :type       populate:  boolean, optional

        :returns:   The versions values
        :rtype:     list
        """
        params = {
            'populate': populate
        }

        jsonify(params)

        result = self.do_request(
            'GET', 'items/{0}/history'.format(self._key), params=params)
        result = [self.parent.cast(data) for data in result]
        return result

    def get_versions(self, populate=False):
        """
        Alias of :func:`~aquarium.items.item.get_history`
        """
        return self.get_history(populate)

    def get_shortest_path(self, key=''):
        """
        Get the shortest path between the current item and the item _key

        :param      key:  The destination key
        :type       key:  string

        :returns:   List of item Object
        :rtype:     list of :class:`~aquarium.item.Item` or subclass : :class:`~aquarium.items.asset.Asset` | :class:`~aquarium.items.project.Project` | :class:`~aquarium.items.shot.Shot` | :class:`~aquarium.items.task.Task` | :class:`~aquarium.items.template.Template` | :class:`~aquarium.items.user.User` | :class:`~aquarium.items.usergroup.Usergroup`
        """
        result = self.do_request(
            'GET', 'items/'+self._key+'/path/'+key)
        result = [self.parent.cast(data) for data in result]
        return result

    def get_permissions(self, sort=None, populate=False, offset=0, limit=50, depth=1, includeMembers=False):
        """
        Gets the permissions of the item

        :param      sort:  Sort participants with a meshQL expression. Example: 'item.data.name ASC'
        :type       sort:  boolean, optional
        :param      populate:  Populate with User object
        :type       populate:  boolean, optional
        :param      offset:  Number of skipped items. Used for pagination
        :type       offset:  integer, optional
        :param      limit:  Maximum limit of returned items
        :type       limit:  integer, optional
        :param      includeMembers:  Include members of the current item
        :type       includeMembers:  boolean, optional

        :returns:   List of edge and user
        :rtype:     list
        """
        params = dict(
            populate=populate,
            offset=offset,
            limit=limit,
            includeMembers=includeMembers
        )

        if sort != None:
            params['sort'] = sort

        jsonify(params)

        result = self.do_request('GET', 'items/{0}/permissions'.format(
            self._key), params=params)
        result = [self.parent.element(data) for data in result]
        return result

    def create_permission(self, participant_key, permissions, propagate = True):
        """
        Create a new permission on an item. It's like sharing an item to an existing user, usergroup or organisation.

        :param      participant_key:    The _key of the user, usergroup or organisation to invite.
        :type       participant_key:    string
        :param      permissions:        The permissions you want to grant to the participant.
        :type       permissions:        string
        :param      propagate:          Propagate or not this new permission.
        :type       propagate:          boolean, optional

        .. tip::
            Available permissions :
                * Can read is `r`
                * Can write is `w`
                * Can add content is `a`
                * Can trash content is `t`
                * Can link (assign, favorite..) is `l`
                * Can unlink is `u`
                * Can share is `s`
                * Can delete is `d`
                * Can change permissions is `g`

            Examples:
                * Read only is `permissions='r'`
                * Write is `permissions='rwa'`
                * Write & connect is `permissions='rwalu'`
                * Write, connect & trash is `permissions='rwatlu'`
                * Write, connect, trash & share is `permissions='rwatslu'`
                * Admin is `permissions='rwsadtlug'`

            The special permission `*`, is to avoid permissions inheritage when append content.


        :returns:   A dict with the {user: participant, edge: the created permission edge}
        :rtype:     dict
        """
        data = {
            'userKey': participant_key,
            'data': {
                'permissions': permissions
            },
            'propagate': propagate
        }
        result = self.do_request(
            'POST', 'items/{0}/permissions'.format(self._key), json=data)
        result['user'] = self.parent.cast(result['user'])
        return result

    def remove_permission(self, participant_key):
        """
        Remove an existing permission from an item. It's like unsharing an item to an existing user, usergroup or organisation.

        :param      participant_key:    The _key of the user, usergroup or organisation to invite.
        :type       participant_key:    string

        :returns:   A dict with the {user: participant, edge: the removed permission edge}
        :rtype:     dict
        """
        data = {
            'userKey': participant_key
        }
        result = self.do_request(
            'DELETE', 'items/{0}/permissions'.format(self._key), json=data)
        result['user'] = self.parent.cast(result['user'])
        return result

    def update_permission(self, participant_key, permissions, propagate=True):
        """
        Update an existing permission on an item.

        :param      participant_key:    The _key of the user, usergroup or organisation to invite.
        :type       participant_key:    string
        :param      permissions:        The permissions you want to grant to the participant.
        :type       permissions:        string
        :param      propagate:          Propagate or not this new permission.
        :type       propagate:          boolean, optional

        .. tip::
            Available permissions are the same than :func:`~aquarium.item.Item.create_permission`

        :returns:   A dict with the {user: participant, edge: the updated permission edge}
        :rtype:     dict
        """
        data = {
            'userKey': participant_key,
            'data': {
                'permissions': permissions
            },
            'propagate': propagate

        }
        result = self.do_request(
            'PATCH', 'items/{0}/permissions'.format(self._key), json=data)
        result['user'] = self.parent.cast(result['user'])
        return result

    def get_parents(self, limit = 50, offset = 0):
        """
        Gets the parents of the item

        :param      limit:   Maximum limit of returned items
        :type       limit:   integer, optional
        :param      offset:  Number of skipped items. Used for pagination
        :type       offset:  integer, optional

        :returns:   List of item and edge object
        :rtype:     list of {item: :class:`~aquarium.item.Item`, edge: :class:`~aquarium.edge.Edge`}
        """
        query = "# <($Child)- {offset},{limit} *".format(
            offset=offset,
            limit=limit
        )

        result = self.traverse(meshql=query)
        result = [self.parent.element(data) for data in result]
        return result

    def get_children(self, show_hidden=False, types=None, names=None, limit=50, offset=0):
        """
        Gets the children of the item

        :param      show_hidden:  Show hidden items
        :type       show_hidden:  boolean, optional
        :param      types:  One string or list of string items type you want to filter
        :type       types:  string or list, optional
        :param      names:  One string or list of string items name you want to filter
        :type       names:  string or list, optional
        :param      limit:   Maximum limit of returned items
        :type       limit:   integer, optional
        :param      offset:  Number of skipped items. Used for pagination
        :type       offset:  integer, optional

        :returns:   List of item and edge object
        :rtype:     list of {item: :class:`~aquarium.item.Item`, edge: :class:`~aquarium.edge.Edge`}
        """
        query = ["# -($Child)> {offset}, {limit}".format(
            offset=offset,
            limit=limit
        )]
        aliases = dict()

        if types == None:
            query.append('*')
        else:
            query.append('item.type IN @types')
            if not isinstance(types, list): types=[types]
            aliases['types'] = types

        if names != None:
            query.append('AND item.data.name IN @names')
            if not isinstance(names, list): names=[names]
            aliases['names'] = names

        if not show_hidden:
            query.append('AND edge.data.isHidden != true')

        result = self.traverse(meshql=' '.join(query), aliases=aliases)
        result = [self.parent.element(data) for data in result]
        return result

    def get_trash(self, meshql='# -($Child)> *'):
        """
        Gets the trashed items

        :param      meshql:  The meshql string. Default is : # -($Child)> *
        :type       meshql:  string, optional

        :returns:   List of trashed item and edge object
        :rtype:     list of {item: :class:`~aquarium.item.Item`, edge: :class:`~aquarium.edge.Edge`}
        """
        result = self.traverse_trashed(meshql)
        result = [self.parent.element(data) for data in result]
        return result

    def move(self, old_parent_key=None, new_parent_key=None):
        """
        Move item from old parent to new parent

        :param      old_parent_key:  The key of the old parent
        :type       old_parent_key:  string
        :param      new_parent_key:  The key of the new parent
        :type       new_parent_key:  string

        :returns:   New item parent and new child edge
        :rtype:     dictionary {item: :class:`~aquarium.item.Item`,edge: :class:`~aquarium.edge.Edge`}
        """
        logger.debug('Move item %s from parent %s to %s',
                     self._key, old_parent_key, new_parent_key)
        data = dict(
            oldParentKey=old_parent_key,
            newParentKey=new_parent_key
        )

        result = self.do_request(
            'PUT', 'items/'+self._key+'/move', json=data)
        result = self.parent.element(result)
        return result

    def trash(self):
        """
        Move item to the trash

        :returns:   Trashed item
        :rtype:     dictionary
        """
        logger.debug('Trash item %s', self._key)
        result = self.do_request(
            'DELETE', 'items/{itemKey}/trash'.format(
                itemKey=self._key
            ))
        result = self.parent.element(result)
        return result

    def restore(self):
        """
        Restore an item from trash

        :returns:   Restored item
        :rtype:     :class:`~aquarium.item.Item`
        """
        logger.debug('Restore item %s', self._key)
        result = self.do_request(
            'POST', 'trashed_items/{itemKey}/restore'.format(
                itemKey=self._key
            ))
        result = self.parent.cast(result)
        return result

    def delete(self):
        """
        Delete the item.

        .. danger::
            The item will be completely deleted. You can use :func:`~aquarium.item.Item.trash` instead

        :returns:   Deleted item object from API
        :rtype:     dictionary
        """
        logger.debug('Delete item %s', self._key)
        result = self.do_request(
            'DELETE', 'trashed_items/'+self._key)
        return result

    def upload_file(self, path='', data = {}, message = None):
        """
        Upload a file on the item

        .. warning::
            This function will replace the data on the item.
            It's here to replace the existing file's data by creating a new history entry.
            We advice you to use :func:`~aquarium.item.Item.append` if you want to upload the file as a new item.

        :param      path:  The path of the file to upload
        :type       path:  string
        :param      data:  The data you want to upload with the file, optional
        :type       data:  dict
        :param      message:  The message associated with the upload, optional
        :type       message:  string

        :returns:   Item object
        :rtype:     :class:`~aquarium.item.Item`
        """
        logger.debug('Upload file %s on item %s with data %s', path, self._key, data)

        file = open(path, 'rb')
        filename = os.path.basename(path)
        file_content_type = mimetypes.guess_type(filename)

        files = dict(
            file=(filename, file, file_content_type),
            data=(None, json.dumps(data), 'text/plain'),
            message=(None, message, 'text/plain')
        )
        result = self.do_request(
            'POST', 'items/'+self._key+'/upload', files=files)
        file.close()
        result = self.parent.cast(result)
        return result

    def download_file(self, path, versionKey=None):
        """
        Download the item's file to the path

        :param      path:  The path used to store the download. If directory is provided, the file name from original file is used
        :type       path:  string
        :param      versionKey:  The versionKey used to download the file
        :type       versionKey:  string, optional
        """
        logger.debug('Download from item %s to file %s', self._key, path)

        url = 'items/{_key}/download'.format(_key=self._key)
        if (versionKey != None):
            url = '{url}?versionKey=${versionKey}'.format(versionKey=versionKey)

        result = self.do_request(
            'GET', url, decoding=False)

        if (os.path.isdir(path)):
            content_disposition = result.headers['content-disposition']
            filename = re.findall('filename="(.+)"', content_disposition)
            print(content_disposition)
            if len(filename) > 0:
                path = os.path.join(path, str(filename[0]))

        with open(path, 'wb') as f:
            for chunk in result:
                f.write(chunk)

        return path

    def import_json(self, content={}):
        """
        Import item hierarchy from json content

        :param      content:  The json content
        :type       content:  dictionary

        :returns:   Dictionary of imported items and edges
        :rtype:     dictionary
        """
        result = self.do_request(
            'POST', 'items/'+self._key+'/import/json', json=content)
        return result

    def export_json(self):
        """
        Export item hierarchy to json

        :returns:   Exported items and edges
        :rtype:     dictionary
        """
        result = self.do_request('GET', 'items/'+self._key+'/export/json')
        return result

    def compare(self, key=''):
        """
        Compare the item with a given item

        :param      key:  The key of the item to compare with
        :type       key:  string

        :returns:   The comparison result
        :rtype:     dictionary
        """
        result = self.do_request('POST', 'items/'+self._key+'/compare/'+key)
        result = self.parent.element(result)
        return result
