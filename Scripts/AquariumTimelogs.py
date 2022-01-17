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
    import AquariumTimelogs_ui_ps2 as AquariumTimelogs_ui

logger = logging.getLogger(__name__)

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

class TimelogListModel(QAbstractTableModel):
    def __init__(self, data, origin):
        super(TimelogListModel, self).__init__()
        self._data = data
        self.origin = origin

    def headerData(self, index, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return {
                    0: lambda: 'MAIN PARENT',
                    1: lambda: 'PARENT',
                    2: lambda: 'NAME',
                    3: lambda: 'DURATION',
                    4: lambda: 'DATE'
                }[index]()
            else:
                return index + 1

    def data(self, index, role):
        value = self._data[index.row()][index.column()]
        if role == Qt.DisplayRole:
            return {
                0: lambda value: value,
                1: lambda value: value,
                2: lambda value: value,
                3: lambda value: value,
                4: lambda value: value,
            }[index.column()](value)
        elif role == Qt.TextAlignmentRole:
            return {
                0: lambda value: Qt.AlignCenter,
                1: lambda value: Qt.AlignCenter,
                2: lambda value: Qt.AlignCenter,
                3: lambda value: Qt.AlignCenter,
                4: lambda value: Qt.AlignCenter
            }[index.column()](value)
        else:
            return None

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        if (len(self._data) > 0):
            return len(self._data[0])
        else:
            return 0

class DateListModel(QAbstractListModel):
    def __init__(self, data, origin):
        super(DateListModel, self).__init__()
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

        self.cb_projects.currentIndexChanged.connect(
            lambda: self.loadTimelogsLinkTo()
        )

        connected = self.origin.connectToAquarium()
        
        if connected:
            projects = self.origin.getAqProjects()
            
            for project in projects:
                self.cb_projects.addItem(project['name'], project['_key'])
            if (self.origin.aqProject):
                index = self.cb_projects.findData(self.origin.aqProject._key)
                if index >= 0:
                    self.cb_projects.setCurrentIndex(index)
                else:
                    self.cb_projects.addItem('Select a project', None)

            self.loadTimelogsLinkTo()
        else:
            self.origin.messageWarning(
                message="You are not connected to Aquarium Studio. Please check your settings.",
                title="Aquarium studio timelogs"
            )

        self.connectEvents()
        self.refresh()
    
    @err_catcher(name=__name__)
    def loadTimelogsLinkTo(self):
        selectedProjectKey = self.cb_projects.currentData()
        timelogLocation = self.origin.getTimelogsLocation()
        if selectedProjectKey != self.origin.aqProject._key:
            timelogLocation = selectedProjectKey

        aliases = {
            "view": {
                "name": "item.data.name",
                "_key": "item._key"
            }
        }

        if timelogLocation:
            self.timelogsTemplates = self.origin.aq.item(timelogLocation).traverse(meshql="# -($Child)> $Template AND item.data.templateData.type == 'Job' VIEW $view", aliases=aliases)

            self.cb_templates.clear()
            self.cb_templates.addItem('No timelogs template', None)
            for template in self.timelogsTemplates:
                self.cb_templates.addItem(template["name"], template["_key"])
            if len(self.timelogsTemplates) > 0:
                self.cb_templates.setCurrentIndex(1)

            self.cb_linkto.clear()
            self.cb_linkto.addItem('Default location', timelogLocation)

    @err_catcher(name=__name__)
    def connectEvents(self):
        self.c_calendar.currentPageChanged.connect(lambda year, int: self.refresh())
        self.c_calendar.activated.connect(lambda date: self.refreshSelection(date))
        self.b_today.pressed.connect(self.goToToday)
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
    def goToToday(self): 
       self.c_calendar.setSelectedDate(QDate.currentDate()) 

    @err_catcher(name=__name__)
    def refreshSelection(self, date = None):
        if date is not None:
            if date in self.selectedDates:
                self.selectedDates.remove(date)
            else:
                self.selectedDates.append(date)
            
        self.DateListModel = DateListModel(self.selectedDates, self)
        self.lv_selecteddates.setModel(self.DateListModel)
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
            timelogs = list(filter(lambda timelog: timelog["parent"] is not None, timelogs))
            self.timelogs = [{
                'item': self.origin.aq.cast(timelog['item']),
                'parent': self.origin.aq.cast(timelog['parent']),
                'mainParent': self.origin.aq.cast(timelog['mainParent'])
            } for timelog in timelogs]

            self.refreshCalendar()
            self.refreshTable()
        else:
            self.origin.messageWarning(
                message="You are not connected to Aquarium Studio. Please check your settings.",
                title="Aquarium studio timelogs"
            )
    
    @err_catcher(name=__name__)
    def refreshTable(self):
        timelogs = []
        for timelog in self.timelogs:
            timelogs.append([
                timelog['mainParent'].data.name,
                timelog['parent'].data.name,
                timelog['item'].data.name,
                timelog['item'].data.duration,
                datetime.datetime.strptime(timelog['item'].data.performedAt, "%Y-%m-%dT%H:%M:%S.%f%z").strftime('%a %d %b %Y')
            ])
            
        self.t_timelogs.setModel(TimelogListModel(timelogs, self))
        self.t_timelogs.resizeColumnsToContents()

    @err_catcher(name=__name__)
    def refreshCalendar(self):
        today = datetime.date.today()
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
            elif date < today:
                self.c_calendar.setDateTextFormat(QDate(date.year, date.month, date.day), dateWithoutTimelog)
            else:
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
                    'performedAt': '{isoDate}.000Z'.format(isoDate = performedAt.isoformat())
                }

                # local_tz = get_localzone() 
                # local = pytz.timezone(local_tz)
                # local_dt = local.localize(performedAt, is_dst=None)
                # utc_dt = local_dt.astimezone(pytz.utc)
                applyTemplate = False
                templateKey = self.cb_templates.currentData()
                if templateKey is not None:
                    applyTemplate = True

                logger.debug("Do apply tempalte ? %s", applyTemplate)
                timelog = self.origin.aq.item(self.cb_linkto.currentData()).append(type='Job', data=data, apply_template=applyTemplate, template_key=templateKey)
                if (timelog):
                    self.timelogs.append({'item': timelog.item})

            self.refreshCalendar()
            self.clearSelection()
        else:
            self.origin.messageWarning(
                message="You need to specify at least one duration",
                title="Aquarium studio timelogs"
            )
