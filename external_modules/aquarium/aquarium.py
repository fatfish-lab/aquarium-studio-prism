# -*- coding: utf-8 -*-
from . import JSON_CONTENT_TYPE
from .item import Item
from .edge import Edge
from .utils import evaluate
from .items.user import User
from .items.template import Template
from .items.project import Project
from .items.task import Task
from .items.shot import Shot
from .items.asset import Asset
from .items.usergroup import Usergroup
from .element import Element

import requests
import json
import logging
logger=logging.getLogger(__name__)


class Aquarium(object):
    """
    This class describes the main class of Aquarium

    :param api_url: Specify the URL of the API. Don't forget to add the version you use ex: `/v1`
    :type api_url: string
    :param token: Specify the authentication token, to avoid :func:`~aquarium.aquarium.Aquarium.connect`
    :type token: string

    :ivar edge: Access to :class:`~aquarium.edge.Edge`
    :ivar item: Access to :class:`~aquarium.item.Item`
    :ivar asset: Access to subclass :class:`~aquarium.items.asset.Asset`
    :ivar project: Access to subclass :class:`~aquarium.items.project.Project`
    :ivar shot: Access to subclass :class:`~aquarium.items.shot.Shot`
    :ivar task: Access to subclass :class:`~aquarium.items.task.Task`
    :ivar template: Access to subclass :class:`~aquarium.items.template.Template`
    :ivar user: Access to subclass :class:`~aquarium.items.user.User`
    :ivar usergroup: Access to subclass :class:`~aquarium.items.usergroup.Usergroup`
    """

    def __init__(self, api_url='', token=''):
        """
        Constructs a new instance.
        """
        # Session
        self.session=requests.Session()

        self.api_url=api_url
        self.token=token
        # Classes
        self.element=Element(parent=self)
        self.item=Item(parent=self)
        self.edge=Edge(parent=self)
        self.user=User(parent=self)
        self.usergroup=Usergroup(parent=self)
        self.template=Template(parent=self)
        # SubClasses
        self.project=Project(parent=self)
        self.task=Task(parent=self)
        self.shot=Shot(parent=self)
        self.asset=Asset(parent=self)

    def do_request(self, *args, **kwargs):
        """
        Execute a request to the API

        :param      args:    Parameters used to send the request : HTTP verb, API endpoint
        :type       args:    tuple
        :param      kwargs:  Headers, data and parameters used for the request
        :type       kwargs:  dictionary

        :returns:   Request response
        :rtype:     List or dictionary
        """
        token=self.token

        decoding=True
        if 'decoding' in kwargs:
            decoding=kwargs.pop('decoding')

        if 'headers' in kwargs:
            headers=kwargs.pop('headers')
            if headers is not None:
                headers.update(dict(authorization=token))
        else:
            headers=dict(authorization=token)
            headers.update(JSON_CONTENT_TYPE)

        args=list(args)
        typ=args[0]
        path=self.api_url
        if len(args) > 1:
            path += '/'+args[1]

        logger.debug('Send request : %s %s', typ, path)
        self.session.headers.update(headers)
        response=self.session.request(typ, path, **kwargs)
        evaluate(response)
        if decoding:
            response=response.json()
        return response

    def cast(self, data={}):
        """
        Creates an item or edge instance from a dictionary

        :param      data:         The object item or edge from Aquarium API
        :type       data:         dictionary

        :returns:   Instance of Edge or Item or items subclass
        :rtype:     :class:`~aquarium.edge.Edge` | :class:`~aquarium.item.Item` : [:class:`~aquarium.items.asset.Asset` | :class:`~aquarium.items.project.Project` | :class:`~aquarium.items.shot.Shot` | :class:`~aquarium.items.task.Task` | :class:`~aquarium.items.template.Template` | :class:`~aquarium.items.user.User` | :class:`~aquarium.items.usergroup.Usergroup`]
        """
        value=data
        #As Entity
        if data and '_id' in data.keys():
            id=data.get('_id')
            cls=None
            #As Item
            if id.split('/')[0]=='items':
                type=data.get('type')
                if type=='Project':
                    cls=self.project
                elif type=='User':
                    cls=self.user
                elif type=='Template':
                    cls=self.template
                elif type=='Usergroup':
                    cls=self.usergroup
                elif type=='Asset':
                    cls=self.asset
                elif type=='Shot':
                    cls=self.shot
                elif type=='Task':
                    cls=self.task
                else:
                    cls=self.item
            #As Edge
            elif id.split('/')[0]=='connections':
                cls=self.edge
            if cls is not None:
                value=cls(data=data)

        return value

    def connect(self, email='', password=''):
        """
        Sign in a user with its email and password

        :param      email:     The email of the user
        :type       email:     string
        :param      password:  The password of the user
        :type       password:  string
        """
        return self.user.connect(email=email, password=password)

    def logout(self):
        """
        Sign out current user by clearing the stored authentication token

        .. note::
            After a :func:`~aquarium.aquarium.Aquarium.logout`, you need to use a :func:`~aquarium.aquarium.Aquarium.connect` before sending authenticated requests

        :returns: None
        """
        logger.info('Disconnect current user')
        logger.debug('Clear authentication token for logout')
        self.token=''

    def get_current_user(self):
        """
        Gets the user profil of the connected user

        :returns:   A :class:`~aquarium.items.user.User` instance of the connected user.
        :rtype:     :class:`~aquarium.items.user.User` object
        """
        result=self.user.get_current()
        return result

    def get_server_status(self):
        """
        Gets the server status.

        :returns:   The server status
        :rtype:     dictionary
        """
        result=self.do_request('GET', 'status')
        return result

    def upload_file(self, path=''):
        """
        Uploads a file on the server

        .. note::
            The file is just uploaded to Aquarium. The metadata are not saved on any item. Use :func:`~aquarium.item.Item.update_data` to save them on an item.
            You can also directly upload a file on an item with :func:`~aquarium.item.Item.upload_file`.

        :param      path:  The path of the file to upload
        :type       path:  string

        :returns:   The file metadata on Aquarium
        :rtype:     dictionary
        """
        logger.debug('Upload file : %s', path)
        files=dict(file=open(path, 'rb'))
        result = self.do_request('POST', 'upload', headers={'Content-Type': None}, files=files)
        files['file'].close()
        return result

    def query(self, meshql='', aliases={}):
        """
        Query Entitys

        :param      meshql:        The meshql string
        :type       meshql:        string
        :param      aliases:       The aliases used in the meshql query
        :type       aliases:       dictionary

        :returns:   List of item, edge or VIEW used in the meshql query
        :rtype:     list
        """
        logger.debug('Send query : meshql : %s / aliases : %r',
                     meshql, aliases)
        data=dict(query=meshql, aliases=aliases)
        result=self.do_request('POST', 'query', data=json.dumps(data))
        return result
