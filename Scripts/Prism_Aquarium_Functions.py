# -*- coding: utf-8 -*-
#
####################################################
#
# PRISM - Pipeline for animation and VFX projects
#
# www.prism-pipeline.com
#
# contact: contact@prism-pipeline.com
#
####################################################
#
#
# Copyright (C) 2016-2020 Richard Frangenberg
#
# Licensed under GNU GPL-3.0-or-later
#
# This file is part of Prism.
#
# Prism is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Prism is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Prism.  If not, see <https://www.gnu.org/licenses/>.


import os
import sys
import logging

try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *

if sys.version[0] == "3":
    pVersion = 3
else:
    pVersion = 2

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


logger = logging.getLogger(__name__)

class Prism_Aquarium_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

    @err_catcher(name=__name__)
    def isActive(self):
        return True

    @err_catcher(name=__name__)
    def onProjectChanged(self, origin):
        pass
    
    @err_catcher(name=__name__)
    def messageCreationInfo (self, created, type = 'items', title = "Aquarium Studio sync"):
        message = ""
        if len(created) > 0:
            message = "The following {type} were created:\n\n".format(
                type=type
            )

            created.sort()

            for i in created:
                message += i + "\n"
        else:
            message = "No {type} were created.".format(
                type=type
            )

        QMessageBox.information(self.core.messageParent, title, message)
    
    @err_catcher(name=__name__)
    def messageInfo (self, message = '', title = "Aquarium Studio sync"):
        QMessageBox.information(self.core.messageParent, title, message)
    
    @err_catcher(name=__name__)
    def messageWarning (self, message = '', title = "Aquarium Studio sync"):
        QMessageBox.warning(self.core.messageParent, title, message)
    
    @err_catcher(name=__name__)
    def messageConfirm (self, message = '', title = "Aquarium Studio sync"):
        confirmButton = QMessageBox.question(
            self.core.messageParent,
            title,
            message,
            QMessageBox.Yes | QMessageBox.Cancel,
            QMessageBox.Yes)

        if confirmButton == QMessageBox.Yes:
            return True
        elif confirmButton == QMessageBox.Cancel:
            return False
        else:
            return False

    @err_catcher(name=__name__)
    def prismSettings_loadUI(self, origin):
        # User settings tab
        origin.gb_aqAccount = QGroupBox("Connect to Aquarium Studio")
        lo_aq = QGridLayout()
        origin.gb_aqAccount.setLayout(lo_aq)
        origin.gb_aqAccount.setChecked(False)

        origin.l_aqUserName = QLabel("Email:")
        origin.l_aqUserPassword = QLabel("Password:")
        origin.e_aqUserEmail = QLineEdit()
        origin.e_aqUserPassword = QLineEdit()
        origin.e_aqUserPassword.setEchoMode(QLineEdit.Password)
        origin.b_aqConnect = QPushButton('Signin to Aquarium Studio')
        origin.b_aqConnect.clicked.connect(
            lambda: self.connect(origin)
        )
        origin.l_testConnect = QLabel('')

        lo_aq.addWidget(origin.l_aqUserName)
        lo_aq.addWidget(origin.l_aqUserPassword)
        lo_aq.addWidget(origin.e_aqUserEmail, 0, 1)
        lo_aq.addWidget(origin.e_aqUserPassword, 1, 1)
        lo_aq.addWidget(origin.b_aqConnect, 2, 1)
        lo_aq.addWidget(origin.l_testConnect, 3, 1)

        origin.tabWidgetPage1.layout().insertWidget(1, origin.gb_aqAccount)
        origin.groupboxes.append(origin.gb_aqAccount)

        #Project settings tab
        origin.gb_aqPrjIntegration = QGroupBox("Aquarium Studio integration")
        origin.w_aquarium = QWidget()
        lo_aqI = QHBoxLayout()
        lo_aqI.addWidget(origin.w_aquarium)
        origin.gb_aqPrjIntegration.setLayout(lo_aqI)
        origin.gb_aqPrjIntegration.setCheckable(True)
        origin.gb_aqPrjIntegration.setChecked(False)

        lo_aq = QGridLayout()
        origin.w_aquarium.setLayout(lo_aq)

        origin.l_aqSite = QLabel("Aquarium Studio site:")
        origin.l_aqProject = QLabel("Aquarium project:")
        
        origin.e_aqSite = QLineEdit()
        origin.c_aqProject = QComboBox()
        origin.c_aqProject.currentIndexChanged.connect(
            lambda: self.changeAqProject(origin)
        )
        origin.b_aqRefreshProjects = QPushButton('Refresh projects')
        origin.b_aqRefreshProjects.clicked.connect(
            lambda: self.listAqProjects(origin)
        )
        origin.l_aqProjectChanged = QLabel('')
        origin.l_aqProjectChanged.setStyleSheet("color: #f03e3e;")
        origin.l_aqProjectNoPrismProperties = QLabel('')
        origin.l_aqProjectNoPrismProperties.setStyleSheet("color: #f76707;")
        origin.b_aqConnectUser = QPushButton('Save and go to "User" tab to add your Aquarium credentials')
        origin.b_aqConnectUser.clicked.connect(
            lambda: self.goToUserSettings(origin)
        )
        
        lo_aq.addWidget(origin.l_aqSite, 0, 0)
        lo_aq.addWidget(origin.l_aqProject, 2, 0)
        
        lo_aq.addWidget(origin.e_aqSite, 0, 1)
        lo_aq.addWidget(origin.b_aqConnectUser, 1, 1)
        lo_aq.addWidget(origin.c_aqProject, 2, 1)
        lo_aq.addWidget(origin.b_aqRefreshProjects, 2, 2)
        lo_aq.addWidget(origin.l_aqProjectChanged, 3, 1)
        lo_aq.addWidget(origin.l_aqProjectNoPrismProperties, 4, 1)

        num = origin.w_prjSettings.layout().count() - 1
        origin.w_prjSettings.layout().insertWidget(num, origin.gb_aqPrjIntegration)
        origin.groupboxes.append(origin.gb_aqPrjIntegration)

        origin.gb_aqPrjIntegration.toggled.connect(
            lambda x: self.prismSettings_aqToggled(origin, x)
        )

    @err_catcher(name=__name__)
    def prismSettings_loadSettings(self, origin, settings):
        connected = self.connectToAquarium()
        self.connectedToAquarium(origin, connected=connected)


    @err_catcher(name=__name__)
    def prismSettings_loadPrjSettings(self, origin, settings):
        if "aquarium" in settings:
            if "active" in settings["aquarium"]:
                origin.gb_aqPrjIntegration.setChecked(settings["aquarium"]["active"])

            if "site" in settings["aquarium"]:
                origin.e_aqSite.setText(settings["aquarium"]["site"])

            self.listAqProjects(origin)

        self.prismSettings_aqToggled(origin, origin.gb_aqPrjIntegration.isChecked())

    @err_catcher(name=__name__)
    def prismSettings_saveSettings(self, origin, settings):
        if "aquarium" not in settings:
            settings["aquarium"] = {}
        
        if (self.aq and self.aq.token):
            settings["aquarium"]["token"] = self.aq.token
        else:
            settings["aquarium"]["token"] = ''

    @err_catcher(name=__name__)
    def prismSettings_savePrjSettings(self, origin, settings):
        if "aquarium" not in settings:
            settings["aquarium"] = {}

        settings["aquarium"]["active"] = origin.gb_aqPrjIntegration.isChecked()
        settings["aquarium"]["site"] = origin.e_aqSite.text()
        settings["aquarium"]["projectkey"] = origin.c_aqProject.currentData()
        
        origin.l_aqProjectChanged.setText("")
        origin.l_aqProjectNoPrismProperties.setText("")

    @err_catcher(name=__name__)
    def connect (self, origin):
        connected = self.connectToAquarium()

        if connected:
            self.aq.logout()
            connected = False
        else:
            email = origin.e_aqUserEmail.text()
            password = origin.e_aqUserPassword.text()
            token = self.core.getConfig('aquarium', 'token')
            connected = self.connectToAquarium(email=email, password=password, token=token)
            if (connected):
                settings = self.core.getConfig(configPath=self.core.prismIni)
                self.prismSettings_loadPrjSettings(origin, settings)

        self.connectedToAquarium(origin, connected=connected)
        self.core.ps.saveSettings(changeProject=False)
    
    @err_catcher(name=__name__)
    def connectedToAquarium(self, origin, connected):
        if connected:
            origin.l_testConnect.setText('Hello {username}, your are connected.{information}'.format(
                username=self.aqUser.data.name,
                information='' if self.aqProject else "\nDon't forget to finish to configure the project settings !"))
            origin.e_aqUserEmail.setText(self.aqUser.data.email)
            origin.l_testConnect.setStyleSheet("color: #37b24d;")
            origin.b_aqConnect.setText('Signout')
            origin.e_aqUserPassword.setEnabled(False)
            origin.e_aqUserEmail.setEnabled(False)
        else:
            origin.l_testConnect.setText('You are not connected to Aquarium.')
            origin.l_testConnect.setStyleSheet("color: #f03e3e;")
            origin.b_aqConnect.setText('Signin to Aquarium Studio')
            origin.e_aqUserPassword.setText('')
            origin.e_aqUserPassword.setEnabled(True)
            origin.e_aqUserEmail.setEnabled(True)
            
    @err_catcher(name=__name__)
    def prismSettings_aqToggled(self, origin, checked):
        origin.w_aquarium.setVisible(checked)
        # origin.gb_aqAccount.setVisible(checked)

    @err_catcher(name=__name__)
    def pbBrowser_getMenu(self, origin):
        prjman = self.core.getConfig(
            "aquarium", "active", configPath=self.core.prismIni
        )
        if prjman:
            prjmanMenu = QMenu("Aquarium Studio", origin)

            # actprjman = QAction("Open Aquarium Studio", origin)
            # actprjman.triggered.connect(self.openprjman)
            # prjmanMenu.addAction(actprjman)

            # prjmanMenu.addSeparator()
            
            actSSL = QAction("Sync Aquarium > Prism", origin)
            actSSL.triggered.connect(lambda: self.aqSync(origin, 'prism'))
            prjmanMenu.addAction(actSSL)

            prjmanMenu.addSeparator()
            
            actSSL = QAction("Sync Prism > Aquarium", origin)
            actSSL.triggered.connect(lambda: self.aqSync(origin, 'aquarium'))
            prjmanMenu.addAction(actSSL)
            
            prjmanMenu.addSeparator()
            
            actSSL = QAction("Timelogs", origin)
            actSSL.triggered.connect(lambda: self.aqTimelogs(origin))
            prjmanMenu.addAction(actSSL)

            return prjmanMenu

    @err_catcher(name=__name__)
    def createAsset_open(self, origin):
        isAqActive = self.core.getConfig(
            "aquarium", "active", configPath=self.core.prismIni
        )
        if not isAqActive:
            return

        origin.gb_createInAq = QGroupBox("Create asset in Aquarium Studio")
        lo_aq = QGridLayout()
        origin.gb_createInAq.setLayout(lo_aq)
        origin.gb_createInAq.setCheckable(True)
        origin.gb_createInAq.setChecked(True)

        origin.w_options.layout().insertWidget(0, origin.gb_createInAq)

        connected = self.connectToAquarium()
        if (not connected):
            origin.l_notConnected = QLabel("You are not connected to Aquarium.\nPlease check 'User' and 'Project' settings.")
            origin.l_notConnected.setStyleSheet("color: #f03e3e;")
            lo_aq.addWidget(origin.l_notConnected)
        else:
            origin.chb_applyTemplate = QCheckBox("Use automatic context's template for creation.")
            origin.chb_applyTemplate.setChecked(True)
            lo_aq.addWidget(origin.chb_applyTemplate)

    @err_catcher(name=__name__)
    def createAsset_typeChanged(self, origin, state):
        if hasattr(origin, "gb_createInAq"):
            origin.gb_createInAq.setEnabled(state)

    @err_catcher(name=__name__)
    def assetCreated(self, origin, itemDlg, assetPath):
        if (
            hasattr(itemDlg, "gb_createInAq")
            and itemDlg.gb_createInAq.isChecked()
        ):
            applyTemplate = None
            if (
                hasattr(itemDlg, "chb_applyTemplate")
                and itemDlg.chb_applyTemplate.isChecked()
            ):
                applyTemplate = True

            createdAssets = self.createAqAssets([assetPath], applyTemplate=applyTemplate)
            self.messageCreationInfo(createdAssets, type='assets')

    @err_catcher(name=__name__)
    def editShot_open(self, origin, shotname):
        shotName, seqName = self.core.entities.splitShotname(shotname)
        if not shotName:
            isAqActive = self.core.getConfig(
                "aquarium", "active", configPath=self.core.prismIni
            )
            if not isAqActive:
                return

            origin.gb_createInAq = QGroupBox("Create shot in Aquarium Studio")
            lo_aq = QGridLayout()
            origin.gb_createInAq.setLayout(lo_aq)
            origin.gb_createInAq.setCheckable(True)
            origin.gb_createInAq.setChecked(True)

            origin.widget.layout().insertWidget(0, origin.gb_createInAq)

            connected = self.connectToAquarium()
            if (not connected):
                origin.l_notConnected = QLabel("You are not connected to Aquarium.\nPlease check 'User' and 'Project' settings.")
                origin.l_notConnected.setStyleSheet("color: #f03e3e;")
                lo_aq.addWidget(origin.l_notConnected)
            else:
                origin.chb_applyTemplate = QCheckBox("Use automatic context's template for creation.")
                origin.chb_applyTemplate.setChecked(True)
                lo_aq.addWidget(origin.chb_applyTemplate)

    @err_catcher(name=__name__)
    def editShot_closed(self, itemDlg, shotName):
        if (
            hasattr(itemDlg, "gb_createInAq")
            and itemDlg.gb_createInAq.isChecked()
        ):
            applyTemplate = None
            if (
                hasattr(itemDlg, "chb_applyTemplate")
                and itemDlg.chb_applyTemplate.isChecked()
            ):
                applyTemplate = True

            self.createAqShots([shotName], applyTemplate=applyTemplate)

    @err_catcher(name=__name__)
    def pbBrowser_getPublishMenu(self, origin):
        isAqActive = self.core.getConfig(
            "aquarium", "active", configPath=self.core.prismIni
        )
        if (
            isAqActive and origin.mediaPlaybacks["shots"]["seq"]
        ):
            prjmanAct = QAction("Publish to Aquarium Studio", origin)
            prjmanAct.triggered.connect(lambda: self.aqPublish(origin))
            return prjmanAct

    @err_catcher(name=__name__)
    def listAqProjects(self, origin):
        connected = self.connectToAquarium()
        if connected:
            projects = self.getAqProjects()
            origin.c_aqProject.clear()
            origin.c_aqProject.addItem('Select the corresponding {activeProject} project on Aquarium Studio'.format(
                activeProject=self.core.getConfig('globals', 'project_name', configPath=self.core.prismIni)
                ), None)
            for project in projects:
                origin.c_aqProject.addItem(project['name'], project['_key'])
            if (self.aqProject):
                index = origin.c_aqProject.findData(self.aqProject._key)
                if index >= 0:
                    origin.c_aqProject.setCurrentIndex(index)
        else:
            activeProjectKey = self.core.getConfig('aquarium', 'projectkey', configPath=self.core.prismIni)
            origin.c_aqProject.clear()
            if (activeProjectKey):
                origin.c_aqProject.addItem("Project ({projectKey}) already set, but can't get project from Aquarium yet.".format(
                    projectKey=activeProjectKey
                ), activeProjectKey)
            else:
                origin.c_aqProject.addItem("No project selected yet. Please connect to Aquarium first.", None)

    @err_catcher(name=__name__)
    def changeAqProject(self, origin):
        currentProjectKey = self.core.getConfig('aquarium', 'projectkey', configPath=self.core.prismIni)
        self.aqProject = self.getAqProject(projectKey=origin.c_aqProject.currentData())
        if currentProjectKey != origin.c_aqProject.currentData():
            origin.l_aqProjectChanged.setText("Warning : project changed. Don't forget to save or apply your modifications.")
        else:
            origin.l_aqProjectChanged.setText("")

        if self.aqProject and self.aqProject.prism['properties'] == None:
            origin.l_aqProjectNoPrismProperties.setText("The project seems to have no configuration for Prism. Please check project's settings on Aquarium Studio")
        else:
            origin.l_aqProjectNoPrismProperties.setText("")

    @err_catcher(name=__name__)
    def goToUserSettings(self, origin):
        self.core.ps.saveSettings(changeProject=False)
        
        connected = self.connectToAquarium()
        self.connectedToAquarium(origin, connected=connected)
        if (connected):
            self.listAqProjects(origin)
        
        # TODO: Improve index by loop in tabs
        self.core.ps.tw_settings.setCurrentIndex(1)

    @err_catcher(name=__name__)
    def createAqAssets(self, assets=[], applyTemplate = None):
        createdAssets = []
        connected = self.connectToAquarium()
        location = self.getAssetsLocation()

        folders = [self.aq.cast(sequence) for sequence in self.aq.item(location).traverse(meshql='# -($Child)> $Group VIEW item')]

        if connected:

            aBasePath = self.core.getAssetPath()
            assets = [[os.path.basename(path), path.replace(aBasePath, "").replace(os.path.basename(path), "")[1:-1]] for path in assets]
            
            for assetName, folderName in assets:
                assetLocation = location
                folderNames = (folder for folder in folders if folder.data.name == folderName)
                folder = next(folderNames, None)
                if folder:
                    assetLocation = folder._key
                
                asset = self.aq.item(assetLocation).append(type='Asset', data={'name': assetName}, apply_template=applyTemplate)
                createdAssets.append(asset.item.data.name)
            
        return createdAssets

    @err_catcher(name=__name__)
    def createAqShots(self, shots=[], applyTemplate = None):
        createdShots = []
        connected = self.connectToAquarium()
        location = self.getShotsLocation()

        sequences = [self.aq.cast(sequence) for sequence in self.aq.item(location).traverse(meshql='# -($Child)> $Group VIEW item')]

        if connected:
            for prismShot in shots:
                shotLocation = location
                shotName, seqName = self.core.entities.splitShotname(prismShot)
                if seqName == "no sequence":
                    seqName = ""

                sequenceNames = (sequence for sequence in sequences if sequence.data.name == seqName)
                sequence = next(sequenceNames, None)
                
                if (sequence and sequence._key):
                    shotLocation = sequence._key
                else:
                    logger.debug('Sequence do not exist, create it before shot')
                
                frameIn, frameOut = self.core.entities.getShotRange(prismShot)
                shot = self.aq.item(shotLocation).append(type='Shot', data={'name': shotName, 'frameIn': frameIn, 'frameOut': frameOut}, apply_template=applyTemplate)
                createdShots.append(shot.item.data.name)
            
        return createdShots

    @err_catcher(name=__name__)
    def aqTimelogs(self, origin):
        try:
            del sys.modules["AquariumTimelogs"]
        except:
            pass

        import AquariumTimelogs

        if origin.tbw_browser.currentWidget().property("tabType") == "Assets":
            pType = "Asset"
        else:
            pType = "Shot"

        aqt = AquariumTimelogs.aqTimelogs(
            core=self.core,
            origin=self,
            ptype=pType
        )

        self.core.parentWindow(aqt)
        aqt.exec_()

    @err_catcher(name=__name__)
    def aqSync(self, origin, target):
        try:
            del sys.modules["AquariumSync"]
        except:
            pass

        import AquariumSync

        if origin.tbw_browser.currentWidget().property("tabType") == "Assets":
            pType = "Asset"
        else:
            pType = "Shot"

        aqs = AquariumSync.aqSync(
            core=self.core,
            origin=self,
            ptype=pType,
            target=target
        )

        self.core.parentWindow(aqs)
        aqs.exec_()

    @err_catcher(name=__name__)
    def aqPublish(self, origin):
        try:
            del sys.modules["AquariumPublish"]
        except:
            pass

        import AquariumPublish

        if origin.tbw_browser.currentWidget().property("tabType") == "Assets":
            pType = "Asset"
        else:
            pType = "Shot"

        shotName = os.path.basename(origin.renderBasePath)

        taskName = (
            origin.curRTask.replace(" (playblast)", "")
            .replace(" (2d)", "")
            .replace(" (external)", "")
        )
        versionName = origin.curRVersion.replace(" (local)", "")

        imgPaths = []
        if (
            origin.mediaPlaybacks["shots"]["prvIsSequence"]
            or len(origin.mediaPlaybacks["shots"]["seq"]) == 1
        ):
            if os.path.splitext(origin.mediaPlaybacks["shots"]["seq"][0])[1] in [
                ".mp4",
                ".mov",
            ]:
                imgPaths.append(
                    [
                        os.path.join(
                            origin.mediaPlaybacks["shots"]["basePath"],
                            origin.mediaPlaybacks["shots"]["seq"][0],
                        ),
                        origin.mediaPlaybacks["shots"]["curImg"],
                    ]
                )
            else:
                imgPaths.append(
                    [
                        os.path.join(
                            origin.mediaPlaybacks["shots"]["basePath"],
                            origin.mediaPlaybacks["shots"]["seq"][
                                origin.mediaPlaybacks["shots"]["curImg"]
                            ],
                        ),
                        0,
                    ]
                )
        else:
            for i in origin.mediaPlaybacks["shots"]["seq"]:
                imgPaths.append(
                    [os.path.join(origin.mediaPlaybacks["shots"]["basePath"], i), 0]
                )

        if "pstart" in origin.mediaPlaybacks["shots"]:
            sf = origin.mediaPlaybacks["shots"]["pstart"]
        else:
            sf = 0

        aqp = AquariumPublish.aqPublish(
            core=self.core,
            origin=self,
            ptype=pType,
            shotName=shotName,
            task=taskName,
            version=versionName,
            sources=imgPaths,
            startFrame=sf,
        )
        # if not hasattr(aqp, "sgPrjId") or not hasattr(aqp, "sgUserId"):
        #     return

        self.core.parentWindow(aqp)
        aqp.exec_()

        curTab = origin.tbw_browser.currentWidget().property("tabType")
        curData = [
            curTab,
            origin.cursShots,
            origin.curRTask,
            origin.curRVersion,
            origin.curRLayer,
        ]
        origin.showRender(curData[0], curData[1], curData[2], curData[3], curData[4])

    @err_catcher(name=__name__)
    def openprjman(self, shotName=None, eType="Shot", assetPath=None):
        self.messageInfo(message='Not available yet')
        return
        aq, aqProject, aqUser = self.connectToAquarium()
        if (shotName or assetPath):
            params = "apps/{appName}?itemKeys={itemKey}&mode=editor".format(
                appName= 'shoteditor' if eType == "Shot" else 'asseteditor',
                itemKey= ''
            )
        elif (aqProject):
            params = '{projectKey}?app=Home'.format(
                projectKey = aqProject._key
            )

        prjmanSite = "https://aquarium.fatfish.app/#/{params}".format(
            params=params,
        )

        import webbrowser

        webbrowser.open(prjmanSite)

    @err_catcher(name=__name__)
    def onProjectBrowserClose(self, origin):
        pass

    @err_catcher(name=__name__)
    def onSetProjectStartup(self, origin):
        pass
