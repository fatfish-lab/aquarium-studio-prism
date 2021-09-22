# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
from logging import NullHandler


JSON_CONTENT_TYPE={"Content-Type": "application/json"}
URL_CONTENT_TYPE={"Content-Type": "application/x-www-form-urlencoded"}

DEFAULT_STATUSES=dict(
	toDo={'status':'TO DO', 'color': '#FBEB06', 'valid': False, 'completion': 0},
	wip={'status':'WIP', 'color': '#F3A215', 'valid': False, 'completion': 0.3},
	rtk={'status':'RTK', 'color': '#f35415', 'valid': False, 'completion': 0.5},
	pendingReview={'status':'PENDING REVIEW', 'color': '#15c8f3', 'valid': False, 'completion': 0.9},
	done={'status':'DONE', 'color': '#9cde4d', 'valid': True, 'completion': 1},
	cancelled={'status':'CANCELLED', 'color': '#918F89', 'valid': False, 'completion': 0}
)

# Set default logging handler to avoid "No handler found" warnings.
logging.getLogger(__name__).addHandler(NullHandler())

from .aquarium import Aquarium
