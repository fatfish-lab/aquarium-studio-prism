# -*- coding: utf-8 -*-
from . import URL_CONTENT_TYPE
import json
from .utils import to_string_url
from .entity import Entity
import logging
logger = logging.getLogger(__name__)


class Item(Entity):
    """
    This class describes an Item object child of Aquarium class.
    """

    def create(self, type='', data={}):
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
        :param      data:  The newitem data, optional
        :type       data:  dictionary

        :returns:   Item object
        :rtype:     :class:`~aquarium.item.Item` or subclass : :class:`~aquarium.items.asset.Asset` | :class:`~aquarium.items.project.Project` | :class:`~aquarium.items.shot.Shot` | :class:`~aquarium.items.task.Task` | :class:`~aquarium.items.template.Template` | :class:`~aquarium.items.user.User` | :class:`~aquarium.items.usergroup.Usergroup`
        """

        payload = dict(type=type, data=data)
        result = self.do_request('POST', 'items', data=json.dumps(payload))
        result = self.parent.cast(result)
        return result

    def append(self, type='', data={}, edge_type='Child', edge_data={}, apply_template=None, template_key=None):
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

        :returns:   Dictionary composed by an item and its edge.
        :rtype:     dict {item: :class:`~aquarium.item.Item` or subclass : :class:`~aquarium.items.asset.Asset` | :class:`~aquarium.items.project.Project` | :class:`~aquarium.items.shot.Shot` | :class:`~aquarium.items.task.Task` | :class:`~aquarium.items.template.Template` | :class:`~aquarium.items.user.User` | :class:`~aquarium.items.usergroup.Usergroup`, edge: :class:`~aquarium.edge.Edge}`
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

        if apply_template:
            payload["applyTemplate"] = apply_template

        if template_key:
            payload["templateKey"] = template_key

        result = self.do_request(
            'POST', 'items/'+self._key+'/append', data=json.dumps(payload))
        result = self.parent.element(result)
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
            'POST', 'items/'+self._key+'/traverse', data=json.dumps(data))
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
            'PUT', 'items/'+self._key, data=json.dumps(data))

        result = self.parent.cast(result)
        return result

    def update_data(self, data={}):
        """
        Update the item data by merging the existing ones with the new ones

        :param      data:  The new item data
        :type       data:  dictionary

        :returns:   Item object
        :rtype:     :class:`~aquarium.item.Item`
        """
        logger.debug('Updating data on item %s with %r', self._key, data)
        data = dict(data=data)
        result = self.do_request(
            'PATCH', 'items/'+self._key, data=json.dumps(data))
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
            'POST', 'items/'+self._key+'/copy', data=json.dumps(data))

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
            'POST', 'items/'+self._key+'/convertToTemplate', data=json.dumps(data))
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
            'POST', 'items/'+self._key+'/template', data=json.dumps(data))
        result = self.parent.cast(result)
        return result

    def reapply_template(self, template_key=''):
        """
        Re-apply the template previously used

        :returns:   Item object
        :rtype:     :class:`~aquarium.item.Item` or subclass : :class:`~aquarium.items.asset.Asset` | :class:`~aquarium.items.project.Project` | :class:`~aquarium.items.shot.Shot` | :class:`~aquarium.items.task.Task` | :class:`~aquarium.items.template.Template` | :class:`~aquarium.items.user.User` | :class:`~aquarium.items.usergroup.Usergroup`
        """
        logger.debug('Re-apply existing template on item %s', self._key)
        result = self.do_request(
            'POST', 'items/' + self._key + '/template/reapply')
        result = self.parent.cast(result)
        return result

    def get(self, populate=False, versions=False):
        """
        Get item object with its _key

        :param      populate:  Populate `item.createdBy` and `item.updatedBy` with User object
        :type       populate:  boolean
        :param      versions:  Get previous item's data versions
        :type       versions:  boolean, optional

        :returns:   Item object
        :rtype:     :class:`~aquarium.item.Item` or subclass : :class:`~aquarium.items.asset.Asset` | :class:`~aquarium.items.project.Project` | :class:`~aquarium.items.shot.Shot` | :class:`~aquarium.items.task.Task` | :class:`~aquarium.items.template.Template` | :class:`~aquarium.items.user.User` | :class:`~aquarium.items.usergroup.Usergroup`
        """
        result = self.do_request('GET', 'items/{0}/?populate={1}&versions={2}'.format(
            self._key, int(populate), int(versions)), headers=URL_CONTENT_TYPE)
        result = self.parent.cast(result)
        return result

    def get_versions(self, populate=False):
        """
        Get the previous item's data versions

        :param      populate:  Populate `item.createdBy` and `item.updatedBy` with User object
        :type       populate:  boolean, optional

        :returns:   The versions values
        :rtype:     list
        """
        result = self.do_request(
            'GET', 'items/{0}/versions?populate={1}'.format(self._key, to_string_url(populate)))
        result = [self.parent.cast(data) for data in result]
        return result

    def get_shortest_path(self, key=''):
        """
        Get the shortest path between the current item and the item _key

        :param      key:  The destination key
        :type       key:  string

        :returns:   List of item Object
        :rtype:     list of :class:`~aquarium.item.Item` or subclass : :class:`~aquarium.items.asset.Asset` | :class:`~aquarium.items.project.Project` | :class:`~aquarium.items.shot.Shot` | :class:`~aquarium.items.task.Task` | :class:`~aquarium.items.template.Template` | :class:`~aquarium.items.user.User` | :class:`~aquarium.items.usergroup.Usergroup`
        """
        result = self.do_request(
            'GET', 'items/'+self._key+'/path/'+key, headers=URL_CONTENT_TYPE)
        result = [self.parent.cast(data) for data in result]
        return result

    def get_permissions(self, filters={}, populate=False):
        """
        Gets the permissions of the item

        :param      filters:   The filters
        :type       filters:   dictionary, optional
        :param      populate:  Populate with User object
        :type       populate:  boolean, optional

        :returns:   List of edge and user
        :rtype:     list
        """
        result = self.do_request('GET', 'items/{0}/permissions?filters={1}&populate={2}'.format(
            self._key, str(filters).replace("'", '"'), to_string_url(populate)), headers=URL_CONTENT_TYPE)
        result = [self.parent.element(data) for data in result]
        return result

    def get_parents(self):
        """
        Gets the parents of the item

        :returns:   List of item and edge object
        :rtype:     list of {item: :class:`~aquarium.item.Item`, edge: :class:`~aquarium.edge.Edge`}
        """
        query = "# <($Child)- *"
        result = self.traverse(meshql=query)
        result = [self.parent.element(data) for data in result]
        return result

    def get_children(self, show_hidden=False):
        """
        Gets the children of the item

        :param      show_hidden:  Show hidden items
        :type       show_hidden:  boolean, optional

        :returns:   List of item and edge object
        :rtype:     list of {item: :class:`~aquarium.item.Item`, edge: :class:`~aquarium.edge.Edge`}
        """
        query = "# -($Child)> *"
        if not show_hidden:
            query += ' AND edge.data.isHidden != true'
        result = self.traverse(meshql=query)
        result = [self.parent.element(data) for data in result]
        return result

    def get_trash(self):
        """
        Gets the trashed items

        :returns:   List of trashed item and edge object
        :rtype:     list of {item: :class:`~aquarium.item.Item`, edge: :class:`~aquarium.edge.Edge`}
        """
        query = '# -($Trash)> *'
        result = self.traverse(meshql=query)
        result = [self.parent.cast(data['item']) for data in result]
        return result

    def trash(self, parent_key=''):
        """
        Move item from parent item to trash

        :param      parent_key:  The key of the parent
        :type       parent_key:  string

        :returns:   Trashed item
        :rtype:     dictionary
        """
        logger.debug('Trash item %s from parent %s', self._key, parent_key)
        data = dict(itemKey=self._key)
        result = self.do_request(
            'POST', 'items/'+parent_key+'/trash', data=json.dumps(data))
        result = self.parent.element(result)
        return result

    def restore(self, parent_key=''):
        """
        Restore an item from trash to parent item

        :param      parent_key:  The key of the parent
        :type       parent_key:  string

        :returns:   Restored edge
        :rtype:     :class:`~aquarium.edge.Edge`
        """
        logger.debug('Restore item %s from parent %s', self._key, parent_key)
        data = dict(itemKey=self._key)
        result = self.do_request(
            'POST', 'items/'+parent_key+'/restore', data=json.dumps(data))
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
            'DELETE', 'items/'+self._key, headers=URL_CONTENT_TYPE)
        return result

    def upload_file(self, path=''):
        """
        Upload a file on the item

        :param      path:  The path of the file to upload
        :type       path:  string

        :returns:   item object from API
        :rtype:     dictionary
        """
        logger.debug('Upload file %s on item %s', path, self._key)
        files = dict(file=open(path, 'rb'))
        result = self.do_request(
            'POST', 'items/'+self._key+'/upload', headers={'Content-Type': None}, files=files)
        files['file'].close()
        return result

    def download_file(self, path=''):
        """
        Download the item's file to the path

        :param      path:  The path used to store the download
        :type       path:  string
        """
        logger.debug('Download from item %s to file %s', self._key, path)
        result = self.do_request(
            'GET', 'items/'+self._key+'/download', headers=URL_CONTENT_TYPE, decoding=False)
        with open(path, 'wb') as f:
            for chunk in result:
                f.write(chunk)
        result = result.json()
        return result

    def import_json(self, content={}):
        """
        Import item hierarchy from json content

        :param      content:  The json content
        :type       content:  dictionary

        :returns:   Dictionary of imported items and edges
        :rtype:     dictionary
        """
        result = self.do_request(
            'POST', 'items/'+self._key+'/import/json', data=json.dumps(content))
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
