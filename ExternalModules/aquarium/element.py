# -*- coding: utf-8 -*-
from .tools import pretty_print_format
from inspect import ismethod


class Element(dict):
    """
    Dict subclass that also allows attribute-style access.
    """

    def __init__(self, parent=None, *args, **kwargs):
        # Bypass __setattr__ to attach the parent helper
        object.__setattr__(self, 'parent', parent)
        super(Element, self).__init__(*args, **kwargs)

    def __call__(self, data=None):
        """
        Create a new Element instance from a mapping, casting nested dicts.
        """
        data = data or {}
        inst = self.__class__(parent=self.parent)

        for key, value in data.items():
            if isinstance(value, dict) and self.parent:
                value = self.parent.cast(value)
            elif isinstance(value, list) and self.parent:
                value = [self.parent.cast(v) if isinstance(v, dict) else v for v in value]
            inst[key] = value
        return inst

    def __getattr__(self, name):
        if name in self.__dict__:
            return object.__getattribute__(self, name)
        if name in self:
            return self[name]

        # Keep the helpful suggestion when a nested attribute exists
        attrs_names = list(self.keys())
        msg = ['"{0}" object has no attribute "{1}".'.format(self.__class__.__name__, name)]

        for n in attrs_names:
            instance = self[n]
            if hasattr(instance, name):
                if 'You should try to call this attribute under' not in msg:
                    msg.append('You should try to call this attribute under')
                if len(msg) > 2:
                    msg.append('or')
                msg.append('.'.join([self.__class__.__name__, n, name]))
        raise AttributeError(' '.join(msg))

    def __setattr__(self, name, value):
        if name.startswith('_') or name == 'parent':
            object.__setattr__(self, name, value)
        else:
            self[name] = value

    def __delattr__(self, name):
        if name in self.__dict__:
            object.__delattr__(self, name)
        elif name in self:
            del self[name]
        else:
            raise AttributeError(name)

    def __str__(self):
        entity = dict(self)
        return '\n\n[%s]\n%s' % (self.__class__.__name__, pretty_print_format(entity, indent=4))

    def __repr__(self):
        return str(self)

    def pop(self, attr_name, *args):
        if attr_name in self.__dict__:
            return self.__dict__.pop(attr_name)
        return super(Element, self).pop(attr_name, *args)
