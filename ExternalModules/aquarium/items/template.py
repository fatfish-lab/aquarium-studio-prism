# -*- coding: utf-8 -*-
from .. import URL_CONTENT_TYPE
from ..item import Item
from ..exceptions import Deprecated
import logging
logger = logging.getLogger(__name__)


class Template(Item):
    """
    This class describes a Template object child of Item class.
    """

    def apply(self, item_key=None):
        """
        Apply the template on all its items.

        :param      item_key:        The key of the item on which to apply the template
        :type       item_key:        string

        :returns:   Item template
        :rtype:     :class:`~aquarium.items.template.Template`
        """
        if item_key == None:
            raise Deprecated("You can't use this function without providing an item_key.")

        logger.debug('Apply template %s on %s', self._key, item_key)

        result = self.do_request(
            'POST', 'templates/{templateKey}/apply/{itemKey}'.format(
                templateKey=self._key,
                itemKey=item_key
            ))
        result = self.parent.cast(result)
        return result
