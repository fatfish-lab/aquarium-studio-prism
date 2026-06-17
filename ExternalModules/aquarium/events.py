# -*- coding: utf-8 -*-
# This SSE integration is inspired by https://github.com/btubbs/sseclient Copyright (c) 2015 Brent Tubbs

import re
import json
import time
import codecs

from .entity import Entity
from .tools import pretty_print_format
from dotmap import DotMap

import logging
logger=logging.getLogger(__name__)

# Technically, we should support streams that mix line endings.  This regex,
# however, assumes that a system will provide consistent line endings.
end_of_field = re.compile(r'\r\n\r\n|\r\r|\n\n')

class Events(object):
    """
    This class describes the Events listenner to listen and process events from Aquarium.

    :param wait: Specify how many seconds to wait before reconnecting to server.
    :type wait: integer
    :param chunk_size: Specify chunk size when reading and parsing an event.
    :type chunk_size: integer
    """

    def __init__(self, parent=None, wait=3000, chunk_size=1024):
        self.parent = parent
        self.wait = wait
        self.chunk_size = chunk_size
        self.buf = ''

        self.listening = False
        self.last_timestamp = None
        self.listeners = {}

        self.headers = {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }

    def listen(self):
        """
        Connect and starts streaming events from the server.

        :returns: Events listener
        :rtype: :class:`~aquarium.events.Events`
        """

        self.listening = True
        if self.last_timestamp:
            self.headers['last-event-id'] = self.last_timestamp

        self.stream = self.parent.do_request('GET', '/events/stream', headers=self.headers, stream=True, decoding=False)
        self.stream_iterator = self._iter_content()

        encoding = self.stream.encoding or self.stream.apparent_encoding
        self.decoder = codecs.getincrementaldecoder(encoding)(errors='replace')

        return self

    def start(self):
        """
        Starts processing events and trigger the callbacks.
        """

        logger.info('Ready to listen to the event stream')
        for event in self:
            # Trigger callback for the exact event topic
            for callback in self.listeners.get(event.topic, []):
                callback(event)

            # Trigger callback for the event native topic
            topic = '{category}.{verb}'.format(category=event._category, verb=event._verb)
            for callback in self.listeners.get(topic, []):
                callback(event)

            # Trigger callback for the event root topic's category
            for callback in self.listeners.get(event._category, []):
                callback(event)


            # Trigger callback for all events
            for callback in self.listeners.get('*', []):
                callback(event)

    def stop(self):
        """
        Stop listening to the event stream
        """
        logger.info('Stopping the event stream')
        if self.stream:
            self.stream.close()
        self.listening = False

    def subscribe(self, event = '*', callback = None):
        """
        Subscribe to an event's topic and define its callback

        :param      event:  The event topic. It can be a specific event (item.created.Media), a part of topic (item.created), or a wildcard (*)
        :type       event:  string
        :param      callback:  The callback function
        :type       callback:  function

        .. tip::
            An event topic is a string, constructed as follows:
                - 'category.verb'
            Some topics can include a detail  at the end to quickly filter events based on type:
                - 'item.created.Media'
                - 'edge.updated.Assigned'


        :returns:   The callback
        :rtype:     Callback object :class:`~aquarium.events._Callback`
        """
        topic = event or '*'
        Callback = _Callback(callback)

        if (not self.listeners.get(topic)):
            self.listeners[topic] = []

        self.listeners[topic].append(Callback)
        return Callback

    def unsubscribe(self, event = '*', callback = None):
        """
        Unsubscribe to an event topic and remove its callback

        :param      event:  The event topic
        :type       event:  string
        :param      callback:  The callback object
        :type       callback:  Callback object :class:`~aquarium.events._Callback`
        """
        topic = event or '*'
        if (self.listeners.get(topic)):
            try:
                self.listeners[topic].remove(callback)
            except Exception as e:
                logger.error('Could not remove the callback')

    def _iter_content(self):
        def iter():
            while True:
                for chunk in self.stream.iter_content(chunk_size=self.chunk_size):
                    if not chunk:
                        break
                    yield chunk

        return iter()

    def _event_complete(self):
        """
        Check if the event is complete
        """
        return re.search(end_of_field, self.buf) is not None

    def __iter__(self):
        return self

    def __next__(self):
        if not self.listening:
            raise StopIteration()
        try:
            while self.listening == True:
                while not self._event_complete():
                    try:
                        next_chunk = next(self.stream_iterator)
                        if not next_chunk:
                            raise EOFError()
                        self.buf += self.decoder.decode(next_chunk)

                    except Exception as e:
                        logger.error(e)
                        time.sleep(self.wait / 1000.0)
                        self.listen()

                        # The SSE spec only supports resuming from a whole message, so
                        # if we have half a message we should throw it out.
                        head, sep, tail = self.buf.rpartition('\n')
                        self.buf = head + sep
                        continue

                # Split the complete event (up to the end_of_field) into event_string,
                # and retain anything after the current complete event in self.buf
                # for next time.
                (event_string, self.buf) = re.split(end_of_field, self.buf, maxsplit=1)
                event = Event.parse(event_string, self.parent)
                if (event):
                    self.last_timestamp = event._timestamp
                    if event._retry:
                        self.wait = event._retry
                    return event
                else:
                    continue
        except KeyboardInterrupt:
            logger.info('Stopping the event stream due to keyboard interrupt')
            raise StopIteration()


class _Callback(object):
    """
    This class describes an Callback object
    """
    def __init__(self, callback=None):
        """
        Constructs a new instance.

        :param      callback:  The callback
        :type       callback:  function
        """
        self.callback=callback

    def __call__(self, event):
        """
        Callable to execute the callback

        :param      event:  The event
        :type       event:  Event object
        """
        if self.callback:
            self.callback(event)

class Event(Entity):
    """
    This class describes an Event object
    """

    def __init__(self, parent=None, rawEvent=''):
        """
        Constructs a new instance.

        :param      parent:  The parent
        :type       parent:  Aquarium instance
        """
        self.parent=parent
        self._key=None

        self._timestamp=None
        self._retry=None
        self._category=None
        self._verb=None

        if (rawEvent):
            return self.parse(rawEvent, self.parent)

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
        inst.topic=''
        inst.createdAt=''
        inst.createdBy=''
        inst.updatedAt=''
        inst.updatedBy=''
        inst.emittedFrom=None
        inst.data=dict()

        if data:
            # As number or string
            if isinstance(data, str) or isinstance(data, int) or isinstance(data, type(u'')):
                inst._key=str(data)
                inst._id='events/%s' % inst._key

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

    def to_dict(self):
        """
        Convert the event to a dictionary

        :returns:   The event as a dictionary
        :rtype:     dictionary
        """
        return super(Event, self).to_dict()

    def set_data_variables(self, data={}):
        """
        Sets the data variables.

        :param      data:  The data
        :type       data:  dictionary
        """
        self._timestamp=data.get('_timestamp')
        self._retry=data.get('_retry')
        self._category=data.get('_category')
        self._verb=data.get('_verb')

        self._key=data.get('_key')
        self._id=data.get('_id')
        self._rev=data.get('_rev')
        self.type=data.get('type')
        self.topic=data.get('topic')
        self.createdAt=data.get('createdAt')
        self.createdBy=data.get('createdBy')
        self.updatedAt=data.get('updatedAt')
        self.updatedBy=data.get('updatedBy')
        self.emittedFrom=data.get('emittedFrom')

        entity_data=data.get('data')
        if entity_data:
            self.data=DotMap(entity_data, _dynamic=(not bool(self.parent.strict_dotmap)))

        topicRegex = r"^(?:custom[.])?(?P<category>\w+)([.](?P<verb>\w+))?([.](\w+))*$"
        topicMatched = re.match(topicRegex, self.topic)
        if topicMatched.group('category'):
            self._category = topicMatched.group('category')

        if topicMatched.group('verb'):
            self._verb = topicMatched.group('verb')

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

    @classmethod
    def parse(cls, raw, parent):
        """
        Given a possibly-multiline string representing an SSE message, parse it
        and return a Event object.
        """
        sse_line_pattern = re.compile('(?P<name>[^:]*):?( ?(?P<value>.*))?')
        event = cls(parent=parent)
        for line in raw.splitlines():
            lineMatched = sse_line_pattern.match(line)
            if lineMatched is None:
                logger.warning("Malformed event data: %s" % line)
                continue

            name = lineMatched.group('name')
            if name == '':
                continue # SSE comment, ignore
            value = lineMatched.group('value')

            if name == 'data':
                try:
                    data = json.loads(value)
                    event.set_data_variables(data)
                except Exception as e:
                    logger.error(e)
            elif name == 'id':
                event._timestamp = value
            elif name == 'retry':
                event._retry = int(value)

        if event._key is None:
            return None

        return event

    def get(self):
        """
        Get the event

        :returns:   The event
        :rtype:     Event object
        """
        if (self._key):
            event = self.do_request('GET', 'events/{key}'.format(key=self._key))
            self.set_data_variables(event)
            return self
        else:
            raise ValueError('The event has no key, so it is not possible to get it')

    def get_context(self):
        """
        Get the context of the event up to the project

        :returns:   The context of the event with the item Project and it's traversal path
        :rtype:     dictionary with the project :class:`~aquarium.item.Item` and path as list of :class:`~aquarium.item.Item`
        """
        endpoint = 'events/{key}/traverse'.format(key=self._key)
        payload = {
            "query": "# <($Emit)- 0,1 * <($Child, 10)- 0,1 item.type IN ['Project'] AND path.vertices[*].type NONE == 'User' SORT null VIEW $view",
            "aliases": {
                "view": {
                    "project": "item",
                    "path": "path.vertices"
                }
            }
        }
        if (self.emittedFrom):
            payload['query'] = "# <($Child, 10)- 0,1 item.type IN ['Project'] AND path.vertices[*].type NONE == 'User' SORT null VIEW $view"
            endpoint = '{emittedFrom}/traverse'.format(emittedFrom=self.emittedFrom)

        context = self.do_request('POST', endpoint, json=payload)
        if (context and len(context) > 0):
            return {
                'project': self.parent.cast(context[0]['project']),
                'path': [self.parent.cast(item) for item in context[0]['path']]
            }
        else:
            raise ValueError('The event has emittedFrom attribute, but the context could not be found')