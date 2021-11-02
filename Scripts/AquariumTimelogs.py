# -*- coding: utf-8 -*-

import os
import sys
import logging
import calendar
import datetime
# import pytz
# import tzlocal 

try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    psVersion = 2
except:
    from PySide.QtCore import *
    from PySide.QtGui import *

    psVersion = 1

sys.path.append(os.path.join(os.path.dirname(__file__), "user_interfaces"))
if psVersion == 1:
    import AquariumTimelogs_ui
else:
    import AquariumTimelogs_ui as AquariumTimelogs_ui

logger = logging.getLogger(__name__)

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

class ListModel(QAbstractListModel):
    def __init__(self, data, origin):
        super(ListModel, self).__init__()
        self._data = data
        self.origin = origin
 
    def data(self, index, role):
        value = self._data[index.row()]
        if role == Qt.DisplayRole:
            return value.toString('ddd dd MMM yyyy')
        elif role == Qt.TextAlignmentRole:
            pass
        elif role == Qt.ForegroundRole:
            pass
        elif role == Qt.CheckStateRole:
            pass
        else:
            return None
 
    def rowCount(self, index):
        return len(self._data)

class aqTimelogs(QDialog, AquariumTimelogs_ui.Ui_dlg_aqTimelogs):
    def __init__(
        self, core, origin, ptype = 'Asset'
    ):
        QDialog.__init__(self)
        self.setupUi(self)

        self.core = core
        self.origin = origin
        self.ptype = ptype
        self.timelogs = []
        self.selectedDates = []
 
        self.c_calendar.paintCell = self.paintCell

        self.b_createtimelogs.setEnabled(False)

        self.cb_tags.addItem('Standard', 'standard')
        self.cb_tags.addItem('Overtime', 'overtime')

        connected = self.origin.connectToAquarium()
        if connected:
            timelogLocation = self.origin.getTimelogsLocation()
            self.cb_linkto.addItem(self.origin.aqProject.data.name, timelogLocation)
        else:
            self.origin.messageWarning(
                message="You are not connected to Aquarium Studio. Please check your settings.",
                title="Aquarium studio timelogs"
            )

        self.connectEvents()
        self.refresh()

    
    @err_catcher(name=__name__)
    def connectEvents(self):
        self.c_calendar.currentPageChanged.connect(lambda year, int: self.refresh())
        self.c_calendar.activated.connect(lambda date: self.refreshSelection(date))
        self.b_refresh.pressed.connect(self.getTimelogs)
        self.b_cleardates.pressed.connect(self.clearSelection)
        self.b_createtimelogs.pressed.connect(self.createTimelogs)

    @err_catcher(name=__name__)
    def refresh(self):
        self.getTimelogs()

    @err_catcher(name=__name__)
    def clearSelection(self):
        self.selectedDates.clear()
        self.refreshSelection()

    @err_catcher(name=__name__)
    def refreshSelection(self, date = None):
        if date is not None:
            if date in self.selectedDates:
                self.selectedDates.remove(date)
            else:
                self.selectedDates.append(date)
            
        self.listModel = ListModel(self.selectedDates, self)
        self.lv_selecteddates.setModel(self.listModel)
        if len(self.selectedDates) == 0:
            self.b_createtimelogs.setEnabled(False)
        else:
            self.b_createtimelogs.setEnabled(True)

    def paintCell(self, painter, rect, date):
        QCalendarWidget.paintCell(self.c_calendar, painter, rect, date)
        if date in self.selectedDates:
            painter.setBrush(QColor('#4dabf7'))
            painter.drawEllipse(rect.topLeft() + QPoint(12, 7), 3, 3)
    
    @err_catcher(name=__name__)
    def getTimelogs(self):
        connected = self.origin.connectToAquarium()
        
        if connected:
            currentYear = self.c_calendar.yearShown()
            currentMonth = self.c_calendar.monthShown()

            startDayOfMonth = 1
            endDayOfMonth = calendar.monthrange(currentYear, currentMonth)[1]
            startOfMonth = datetime.datetime(currentYear, currentMonth, startDayOfMonth).isoformat()
            endOfMonth = datetime.datetime(currentYear, currentMonth, endDayOfMonth).isoformat()
            query = '# 0,0 (item.type == "Job" AND item.data.performedBy == "{userKey}" AND item.data.performedAt > "{startOfMonth}" AND item.data.performedAt <= "{endOfMonth}") SET $set SORT item.data.performedAt DESC VIEW $view'.format(
                userKey=self.origin.aqUser._key,
                startOfMonth=startOfMonth,
                endOfMonth=endOfMonth
            )

            logger.debug('GET TIMELOGS : %s', {
                'startOfMonth':startOfMonth,
                'endOfMonth':endOfMonth
            })

            aliases = {
                'set': {
                    'parents': '# <($Child, 2)- 0,2 * SORT LENGTH(path.vertices) VIEW item'
                },
                'view': {
                    'item': 'item',
                    'parent': 'parents[0]',
                    'mainParent': 'parents[1]'
                }
            }
            timelogs = self.origin.aq.query(query, aliases)
            self.timelogs = [{
                'item': self.origin.aq.cast(timelog['item']),
                'parent': self.origin.aq.cast(timelog['parent']),
                'mainParent': self.origin.aq.cast(timelog['mainParent'])
            } for timelog in timelogs]

            self.refreshCalendar()
        else:
            self.origin.messageWarning(
                message="You are not connected to Aquarium Studio. Please check your settings.",
                title="Aquarium studio timelogs"
            )
    
    @err_catcher(name=__name__)
    def refreshCalendar(self):
            currentYear = self.c_calendar.yearShown()
            currentMonth = self.c_calendar.monthShown()

            endDayOfMonth = calendar.monthrange(currentYear, currentMonth)[1]

            datetimes = list(map(lambda timelog: datetime.datetime.strptime(timelog['item'].data.performedAt, "%Y-%m-%dT%H:%M:%S.%f%z"), self.timelogs))
            dates = list(map(lambda dt: datetime.date(dt.year, dt.month, dt.day), datetimes))
            dateWithTimelog = QTextCharFormat()
            dateWithTimelog.setBackground(QColor('#51cf66'))
            dateWithTimelog.setForeground(QColor('#2b8a3e'))
            dateWithoutTimelog = QTextCharFormat()
            dateWithoutTimelog.setForeground(QColor('#ffc9c9'))
            red = QColor('#ff6b6b')
            red.setAlpha(150)
            dateWithoutTimelog.setBackground(red)

            
            day = 1
            while day <= endDayOfMonth:
                date = datetime.date(currentYear, currentMonth, day)
                isDateWithTimelog = date in dates
                if isDateWithTimelog:
                    self.c_calendar.setDateTextFormat(QDate(date.year, date.month, date.day), dateWithTimelog)
                else:
                    self.c_calendar.setDateTextFormat(QDate(date.year, date.month, date.day), dateWithoutTimelog)
                    pass
                day += 1
    @err_catcher(name=__name__)
    def createTimelogs(self):
        days = self.sb_day.value()
        hours = self.sb_hour.value()
        minutes = self.sb_minute.value()
        if days > 0 or hours > 0 or minutes > 0:
            for date in self.selectedDates:
                performedAt = datetime.datetime(date.year(), date.month(), date.day(), 0, 0, 0, 0)
                data = {
                    'name': 'Job for {name}'.format(
                        name=self.cb_linkto.currentText()
                    ),
                    'duration': 'P{days}{time}{hours}{minutes}'.format(
                        days = '{days}D'.format(days=days) if days > 0 else '',
                        time = 'T' if hours > 0 or minutes > 0 else '',
                        hours = '{hours}H'.format(hours=hours) if hours > 0 else '',
                        minutes = '{minutes}M'.format(minutes=minutes) if minutes > 0 else ''
                    ),
                    'performedBy': self.origin.aqUser._key,
                    'performedAt': '{isoDate}.000Z'.format(isoDate = performedAt.isoformat()),
                    'tags': [self.cb_tags.currentData()]
                }

                # local_tz = get_localzone() 
                # local = pytz.timezone(local_tz)
                # local_dt = local.localize(performedAt, is_dst=None)
                # utc_dt = local_dt.astimezone(pytz.utc)

                timelog = self.origin.aq.item(self.cb_linkto.currentData()).append(type='Job', data=data)
                if (timelog):
                    self.timelogs.append({'item': timelog.item})

            self.refreshCalendar()
            self.clearSelection()
        else:
            self.origin.messageWarning(
                message="You need to specify at least one duration",
                title="Aquarium studio timelogs"
            )
