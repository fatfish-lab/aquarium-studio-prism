# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AquariumPublish.ui'
#
# Created: Sun Jan 07 20:22:31 2018
#      by: pyside2-uic @pyside_tools_VERSION@ running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_dlg_aqPublish(object):
    def setupUi(self, dlg_aqPublish):
        dlg_aqPublish.setObjectName("dlg_aqPublish")
        dlg_aqPublish.resize(292, 450)
        self.verticalLayout = QtWidgets.QVBoxLayout(dlg_aqPublish)
        self.verticalLayout.setContentsMargins(9, 9, 9, 9)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtWidgets.QWidget(dlg_aqPublish)
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.rb_asset = QtWidgets.QRadioButton(self.widget)
        self.rb_asset.setObjectName("rb_asset")
        self.horizontalLayout.addWidget(self.rb_asset)
        self.rb_shot = QtWidgets.QRadioButton(self.widget)
        self.rb_shot.setObjectName("rb_shot")
        self.horizontalLayout.addWidget(self.rb_shot)
        spacerItem = QtWidgets.QSpacerItem(40, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addWidget(self.widget)
        self.widget_2 = QtWidgets.QWidget(dlg_aqPublish)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.cb_items = QtWidgets.QComboBox(self.widget_2)
        self.cb_items.setObjectName("cb_items")
        self.horizontalLayout_3.addWidget(self.cb_items)
        self.verticalLayout.addWidget(self.widget_2)
        self.l_task = QtWidgets.QLabel(dlg_aqPublish)
        self.l_task.setObjectName("l_task")
        self.verticalLayout.addWidget(self.l_task)
        self.widget_3 = QtWidgets.QWidget(dlg_aqPublish)
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.cb_task = QtWidgets.QComboBox(self.widget_3)
        self.cb_task.setObjectName("cb_task")
        self.horizontalLayout_2.addWidget(self.cb_task)
        self.b_addTask = QtWidgets.QPushButton(self.widget_3)
        self.b_addTask.setMaximumSize(QtCore.QSize(23, 16777215))
        self.b_addTask.setObjectName("b_addTask")
        self.horizontalLayout_2.addWidget(self.b_addTask)
        self.verticalLayout.addWidget(self.widget_3)
        self.l_description = QtWidgets.QLabel(dlg_aqPublish)
        self.l_description.setObjectName("l_description")
        self.verticalLayout.addWidget(self.l_description)
        self.te_description = QtWidgets.QPlainTextEdit(dlg_aqPublish)
        self.te_description.setObjectName("te_description")
        self.verticalLayout.addWidget(self.te_description)
        # self.chb_proxyVid = QtWidgets.QCheckBox(dlg_aqPublish)
        # self.chb_proxyVid.setChecked(True)
        # self.chb_proxyVid.setObjectName("chb_proxyVid")
        # self.verticalLayout.addWidget(self.chb_proxyVid)
        # self.gb_playlist = QtWidgets.QGroupBox(dlg_aqPublish)
        # self.gb_playlist.setCheckable(True)
        # self.gb_playlist.setChecked(False)
        # self.gb_playlist.setObjectName("gb_playlist")
        # self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.gb_playlist)
        # self.verticalLayout_2.setObjectName("verticalLayout_2")
        # self.cb_playlist = QtWidgets.QComboBox(self.gb_playlist)
        # self.cb_playlist.setObjectName("cb_playlist")
        # self.verticalLayout_2.addWidget(self.cb_playlist)
        # self.verticalLayout.addWidget(self.gb_playlist)
        spacerItem1 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem1)
        self.b_aqPublish = QtWidgets.QPushButton(dlg_aqPublish)
        self.b_aqPublish.setMinimumSize(QtCore.QSize(0, 35))
        self.b_aqPublish.setObjectName("b_aqPublish")
        self.verticalLayout.addWidget(self.b_aqPublish)

        self.retranslateUi(dlg_aqPublish)
        QtCore.QMetaObject.connectSlotsByName(dlg_aqPublish)

    def retranslateUi(self, dlg_aqPublish):
        dlg_aqPublish.setWindowTitle(QtWidgets.QApplication.translate("dlg_aqPublish", "Aquarium Publish", None, -1))
        self.rb_asset.setText(QtWidgets.QApplication.translate("dlg_aqPublish", "Asset", None, -1))
        self.rb_shot.setText(QtWidgets.QApplication.translate("dlg_aqPublish", "Shot", None, -1))
        self.l_task.setText(QtWidgets.QApplication.translate("dlg_aqPublish", "Task:", None, -1))
        self.b_addTask.setText(QtWidgets.QApplication.translate("dlg_aqPublish", "+", None, -1))
        self.l_description.setText(QtWidgets.QApplication.translate("dlg_aqPublish", "Description:", None, -1))
        # self.chb_proxyVid.setText(QtWidgets.QApplication.translate("dlg_aqPublish", "Upload proxy video", None, -1))
        # self.gb_playlist.setTitle(QtWidgets.QApplication.translate("dlg_aqPublish", "Add to dailies playlist", None, -1))
        self.b_aqPublish.setText(QtWidgets.QApplication.translate("dlg_aqPublish", "Publish to Aquarium", None, -1))

