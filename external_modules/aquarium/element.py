# -*- coding: utf-8 -*-
from .utils import pretty_print_format
from inspect import ismethod

class Element(object):
    def __init__(self, parent=None):
        self.parent=parent

    def __call__(self, data={}):
        inst=self.__class__()
        for key, value in data.items():
            if isinstance(value, dict):
                value=self.parent.cast(value)
            elif isinstance(value, list):
                value=[self.parent.cast(v) if isinstance(v, dict) else v for v in value]
            setattr(inst, key, value)
        return inst

    def __getattr__(self, name):
        attrs_names=list(vars(self).keys())
        msg=['"{0}" object has no attribute "{1}".'.format(self.__class__.__name__, name)]

        for n in attrs_names:
            instance = getattr(self, n)
            if hasattr(instance, name):
                if 'You should try to call this attribute under' not in msg:
                    msg.append('You should try to call this attribute under')
                if len(msg)>2:
                    msg.append('or')
                msg.append('.'.join([self.__class__.__name__, n, name]))
        raise AttributeError(' '.join(msg))

    def __str__(self):
        entity=vars(self).copy()
        entity.pop('parent', None)
        return '\n\n[%s]\n%s' % (self.__class__.__name__, pretty_print_format(entity, indent=4))

    def __repr__(self):
        return str(self)

    def pop(self, attr_name):
        value=getattr(self, attr_name)
        delattr(self, attr_name)
        return value
