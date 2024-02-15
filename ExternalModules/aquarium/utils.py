# -*- coding: utf-8 -*-
import sys
import datetime
import re
import pytz
import logging
logger = logging.getLogger(__name__)


class Utils():
    """
    This class is a utility class.
    """

    @staticmethod
    def duration(days = 0, hours = 0, minutes = 0):
        """
        Generate an ISO 8601 duration string.

        :param      days:     The number of days to add
        :type       days:     number
        :param      hours:    The number of hours to add
        :type       hours:    number
        :param      minutes:  The number of minutes to add
        :type       minutes:  number

        :returns:   ISO 8601 duration string
        :rtype:     string
        """
        return 'P{days}{time}{hours}{minutes}'.format(
            days='{days}D'.format(days=days) if days > 0 else '',
            time='T' if hours > 0 or minutes > 0 else '',
            hours='{hours}H'.format(hours=hours) if hours > 0 else '',
            minutes='{minutes}M'.format(minutes=minutes) if minutes > 0 else '')

    @staticmethod
    def humanize_duration(duration):
        """
        Humanize an ISO duration.

        :param      duration:     The ISO duration string
        :type       duration:     string

        :returns:   Humanized duration string
        :rtype:     string
        """
        humanized = ''
        regex = r'^P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)W)?(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:.\d+)?)S)?$'
        parsedDuration = re.findall(regex, duration)
        if (len(parsedDuration) > 0):
            parsedDuration = parsedDuration[0]
            years = parsedDuration[0] or 0
            months = parsedDuration[1] or 0
            weeks = parsedDuration[2] or 0
            days = parsedDuration[3] or 0
            hours = parsedDuration[4] or 0
            minutes = parsedDuration[5] or 0
            seconds = parsedDuration[6] or 0.0

            humanized = '{years}{months}{weeks}{days}{hours}{minutes}{seconds}'.format(
                years='{years} year '.format(years=years) if years > 0 else '',
                months='{months} month '.format(months=months) if months > 0 else '',
                weeks='{weeks} week '.format(weeks=weeks) if weeks > 0 else '',
                days='{days}d '.format(days=days) if days > 0 else '',
                hours='{hours}h '.format(hours=hours) if hours > 0 else '',
                minutes='{minutes}m '.format(minutes=minutes) if minutes > 0 else '',
                seconds='{seconds}s '.format(seconds=seconds) if seconds > 0 else '',
            )

        return humanized

    @staticmethod
    def date():
        """
        Alias of :func:`~aquarium.aquarium.Utils.now`.

        :returns:   ISO 8601 date string
        :rtype:     string
        """

        return Utils.now()

    @staticmethod
    def now():
        """
        Get current date/time as an ISO 8601 date string.

        :returns:   ISO 8601 date string
        :rtype:     string
        """

        date = datetime.datetime.now(pytz.UTC)

        if sys.version_info[0] > 2:
            return date.isoformat(timespec='milliseconds')
        else:
            return date.isoformat()

    @staticmethod
    def format_date(date, format='%Y/%m/%d'):
        """
        Format the date.

        :param      date:   The ISO date string
        :type       date:   string
        :param      format: The desired date format. Default is '%Y/%m/%d'
        :type       format: string, optional

        .. tip::
            Check the [Python documentation](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) to customize the format

        :returns:   Formated date string
        :rtype:     string
        """

        return datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z").strftime(format)


    @staticmethod
    def datetime(date):
        """
        Transform the ISO string date into a Python datetime object.

        :param      datetime:   The ISO date string
        :type       datetime:   string

        :returns:   The datetime object from the date string
        :rtype:     datetime
        """

        return datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z")
