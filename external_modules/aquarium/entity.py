# -*- coding: utf-8 -*-
from . import JSON_CONTENT_TYPE
from .utils import evaluate, pretty_print_format
from dotmap import DotMap
import requests
import logging
logger=logging.getLogger(__name__)


class Entity(object):
    """
    This class describes an Entity object child of Aquarium class
    """
    def __init__(self, parent=None):
        """
        Constructs a new instance.

        :param      parent:  The parent
        :type       parent:  Aquarium instance
        """
        self.parent=parent
        self._key=None

    def __call__(self, data={}):
        """
        Callable to create new instance from a hierarchy or a key

        :param      data:  The data or the key
        :type       key:  string or int or dictionary

        :returns:   Entity instance
        :rtype:     Entity object
        """
        # Data variables

        inst=self.__class__(parent=self.parent)

        inst._key=''
        inst._id=''
        inst._rev=''
        inst.type=''
        inst.createdAt=''
        inst.updatedAt=''
        inst.createdBy=dict()
        inst.updatedBy=dict()
        inst.data=dict()

        if data:
            # As number or string
            if isinstance(data, str) or isinstance(data, int):
                inst._key=str(data)

            # As dict
            elif isinstance(data, dict):
                inst.set_data_variables(data=data)

        return inst

    def __str__(self):
        entity=vars(self).copy()
        entity.pop('parent', None)
        dash = '—' * ((len(self.__class__.__name__)) + 2)
        return '\n\t[%s]\n\t%s\n%s ' % (self.__class__.__name__, dash, pretty_print_format(entity, indent=8))
    def __repr__(self):
        return str(self)

    @property
    def session(self):
        return self.parent.session

    def set_data_variables(self, data={}):
        """
        Sets the data variables.

        :param      data:  The data
        :type       data:  dictionary
        """
        self._key=data.get('_key')
        self._id=data.get('_id')
        self._rev=data.get('_rev')
        self.type=data.get('type')
        self.createdAt=data.get('createdAt')
        self.updatedAt=data.get('updatedAt')
        self.createdBy=data.get('createdBy')
        self.updatedBy=data.get('updatedBy')

        entity_data=data.get('data')
        if entity_data:
            self.data=DotMap(entity_data)

    def do_request(self, *args, **kwargs):
        """
        Execute a request

        :param      args:    The arguments used to launch the process
        :type       args:    tuple
        :param      kwargs:  The keywords arguments used to launch the process
        :type       kwargs:  dictionary

        :returns:   request response
        :rtype:  list or dictionary
        """
        result=self.parent.do_request(*args, **kwargs)
        return result
