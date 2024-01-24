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
# Copyright (C) 2016-2023 Richard Frangenberg
# Copyright (C) 2023 Prism Software GmbH
#
# Licensed under proprietary license. See license file in the directory of this plugin for details.
#
# This file is part of Prism-Plugin-Aquarium.
# It's created by Yann Moriaud, from Fatfish Lab
# Contact support@fatfi.sh for any issue related to this plugin
#
# Prism-Plugin-Aquarium is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.


import os
import sys
import importlib
import logging
import traceback
from datetime import datetime
import time

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

from Prism_Aquarium_Utils import baseUrl
from Prism_Aquarium_Utils import hexToRgb

logger = logging.getLogger(__name__)


class Prism_Aquarium_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin
        if self.isActive():
            extModPath = os.path.join(self.pluginDirectory, "ExternalModules")

            if extModPath not in sys.path:
                sys.path.append(extModPath)

            self.name = "Aquarium"

            self.dbCache = {}
            self.requestInProgress = False

            self.requiresLogin = True
            self.hasRemoteDatabase = True
            self.hasNotes = True
            self.hasTaskAssignment = True
            self.publishVersionNameFromFilename = False
            self.episodeSeparator = "__"
            self.register()

    # if returns true, the plugin will be loaded by Prism
    @err_catcher(name=__name__)
    def isActive(self):
        return True

    @property
    def aq_api(self):
        if not hasattr(self, "_aq_api"):
            self._aq_api = importlib.import_module("aquarium")

        return self._aq_api

    @err_catcher(name=__name__)
    def register(self):
        self.prjMng = self.core.getPlugin("ProjectManagement")
        if not self.prjMng:
            self.core.registerCallback("pluginLoaded", self.onPluginLoaded, plugin=self.plugin)
            return

        self.prjMng.registerManager(self)
        self.core.registerCallback("onProjectCreationSettingsReloaded", self.onProjectCreationSettingsReloaded, plugin=self.plugin)

    @err_catcher(name=__name__)
    def unregister(self):
        if getattr(self, "prjMng"):
            self.prjMng.unregisterManager(self.name)

    @err_catcher(name=__name__)
    def onPluginLoaded(self, plugin):
        if plugin.pluginName == "ProjectManagement":
            self.register()

    @err_catcher(name=__name__)
    def onProjectCreationSettingsReloaded(self, settings):
        # QUESTION: What's the goal of the function ?
        if "prjManagement" not in settings:
            return

        if "aquarium_projectKey" not in settings["prjManagement"]:
            return

        del settings["prjManagement"]["aquarium_projectKey"]

    @err_catcher(name=__name__)
    def getRequiredAuthorization(self):
        # QUESTION: How to prompt to the user email + password but store a token
        data = [
            {"name": "aquarium_token", "label": "Token", "isSecret": True, "type": "QLineEdit"},
            # {"name": "aquarium_email", "label": "Username", "isSecret": False, "type": "QLineEdit"},
            # {"name": "aquarium_password", "label": "Password", "isSecret": True, "type": "QLineEdit"},
        ]
        return data

    @err_catcher(name=__name__)
    def getIcon(self):
        path = os.path.join(self.pluginDirectory, "Resources", "aquarium.png")
        return QPixmap(path)

    @err_catcher(name=__name__)
    def getLoginName(self):
        # QUESTION: What's the goal of that function
        data = self.prjMng.getAuthorization() or {}
        return data.get("aquarium_email")

    @err_catcher(name=__name__)
    def getAllUsernames(self):
        # TODO: Make it compatible with Aquarium
        return
        # prjId = self.getCurrentProjectId()
        # if prjId is None:
        #     return

        # filters = [["projects", "is", {"type": "Project", "id": prjId}]]
        # fields = ["name"]
        # text = "Querying usernames - please wait..."
        # popup = self.core.waitPopup(self.core, text, hidden=True)
        # with popup:
        #     users = self.makeDbRequest("find", ["HumanUser", filters, fields], popup=popup)

        # users = [user["name"] for user in users]
        # loginName = self.getUsername()
        # if loginName not in users:
        #     users.insert(0, loginName)

        # return users

    @err_catcher(name=__name__)
    def getDefaultStatus(self):
        # TODO: Improve products, media and tasks statuses
        # FIXME: Set status not working
        statuses = []

        if (self.aqStatuses == None):
            self.aqStatuses = self.getAqProjectStatuses()

        for aqStatus in self.aqStatuses:
            status = {
                "name": aqStatus['status'],
                "abbreviation": aqStatus['status'],
                "color": hexToRgb(aqStatus['color']),
                "products": True,
                "media": True,
                "tasks": True,
            }
            statuses.append(status)

        return statuses

    @err_catcher(name=__name__)
    def getProjectSettings(self):
        # dftStatus = self.getDefaultStatus()
        data = [
            {"name": "aquarium_setup", "label": "Setup...", "tooltip": "Opens a setup window to guide you through the process of connecting your Aquarium project to your Prism project.", "type": "QPushButton", "callback": self.prjMng.openSetupDlg},
            {"name": "aquarium_url", "label": "Url", "type": "QLineEdit"},
            # QUESTION: How to have a combo box with projects in it ?
            {"name": "aquarium_projectKey", "label": "Project key", "type": "QLineEdit"},
            # {"name": "aquarium_versionPubStatus", "label": "Status of published versions", "type": "QLineEdit", "default": "rev"},
            {"name": "aquarium_showTaskStatus", "label": "Show Task Status", "type": "QCheckBox", "default": True},
            # {"name": "aquarium_showProductStatus", "label": "Show Product Status", "type": "QCheckBox", "default": True},
            # {"name": "aquarium_showMediaStatus", "label": "Show Media Status", "type": "QCheckBox", "default": True},
            {"name": "aquarium_allowNonExistentTaskPublishes", "label": "Allow publishes from non-existent tasks", "type": "QCheckBox", "default": True},
            {"name": "aquarium_allowLocalTasks", "label": "Allow local tasks", "type": "QCheckBox", "default": False},
            {"name": "aquarium_useUsername", "label": "Use Aquarium usernames", "type": "QCheckBox", "default": True},
            # {"name": "aquarium_syncDepartments", "label": "Auto Sync Departments", "type": "QCheckBox", "default": False},
            # {"name": "aquarium_syncEntityConnections", "label": "Auto Sync Asset-Shot connections", "type": "QCheckBox", "default": False},
            # {"name": "aquarium_shortDeps", "label": "Use short department names", "type": "QCheckBox", "default": False},
            # {"name": "aquarium_syncDepsNow", "label": "Sync Departments", "tooltip": "Queries the existing departments in Aquarium and creates the same departments in the Prism project.", "type": "QPushButton", "callback": self.prjMng.syncDepartments},
            # {"name": "aquarium_cacheInvalidation", "label": "Cache invalidation (sec)", "type": "QSpinBox", "default": -1, "tooltip": "The amount of seconds after which a cached request to the remote database gets invalidated. The next identical request will be send to the database instead of using a cached value.\n-1 means there will be no cache invalidation.\n0 means no cache will be used."},
            # {"name": "aquarium_status", "label": "Available Status", "type": "status", "default": dftStatus},
        ]
        return data

    @err_catcher(name=__name__)
    def getRemoteUrl(self):
        url = self.core.getConfig("prjManagement", "aquarium_url", config="project") or ""
        return url

    @err_catcher(name=__name__)
    def getExampleUrl(self):
        return "https://company.aquarium.app"

    @err_catcher(name=__name__)
    def getCurrentUrl(self):
        return self.aq.api_url

    @err_catcher(name=__name__)
    def openInBrowser(self, entityType, entity):
        aqSite = self.aq.api_url
        itemKey = entity['id']
        url = aqSite + "/#/open/%s" % (itemKey)
        self.core.openWebsite(url)

    @err_catcher(name=__name__)
    def showTaskStatus(self):
        # TODO: Handle that option
        return self.core.getConfig("prjManagement", "aquarium_showTaskStatus", config="project", dft=True)

    @err_catcher(name=__name__)
    def showProductStatus(self):
        # TODO: Handle that option
        return self.core.getConfig("prjManagement", "aquarium_showProductStatus", config="project", dft=True)

    @err_catcher(name=__name__)
    def showMediaStatus(self):
        # TODO: By default Aquarium doesn't have any status
        return self.core.getConfig("prjManagement", "aquarium_showMediaStatus", config="project", dft=True)

    @err_catcher(name=__name__)
    def getAllowNonExistentTaskPublishes(self):
        # TODO: Handle that option
        return self.core.getConfig("prjManagement", "aquarium_allowNonExistentTaskPublishes", config="project", dft=True)

    @err_catcher(name=__name__)
    def getAllowLocalTasks(self):
        # TODO: Handle that option
        return self.core.getConfig("prjManagement", "aquarium_allowLocalTasks", config="project", dft=False)

    @err_catcher(name=__name__)
    def getUseAqUsername(self):
        # QUESTION: What's the goal of that function ?
        return self.core.getConfig("prjManagement", "aquarium_useUsername", config="project", dft=True)

    @err_catcher(name=__name__)
    def getSyncDepartments(self):
        # TODO: Handle that option
        return self.core.getConfig("prjManagement", "aquarium_syncDepartments", config="project", dft=False)

    @err_catcher(name=__name__)
    def getSyncEntityConnections(self):
        # QUESTION: Can I delete that function ?
        return self.core.getConfig("prjManagement", "aquarium_syncEntityConnections", config="project", dft=False)

    @err_catcher(name=__name__)
    def getUseShortDepartmentNames(self):
        # QUESTION: Can I delete that function ?
        return self.core.getConfig("prjManagement", "aquarium_shortDeps", config="project", dft=False)

    @err_catcher(name=__name__)
    def makeDbRequest(self, method, args=None, popup=None, allowCache=True):
        # FIXME: Improve function based on Aquarium requirements
        if not isinstance(args, list):
            if args:
                args = [args]
            else:
                args = []

        if method not in self.dbCache:
            self.dbCache[method] = []

        if allowCache:
            for request in self.dbCache[method]:
                if request["args"] == args:
                    return request["result"]
        else:
            self.dbCache[method] = [r for r in self.dbCache[method] if r["args"] != args]

        if self.requestInProgress:
            while self.requestInProgress:
                time.sleep(0.1)

            return self.makeDbRequest(method, args=args, popup=popup, allowCache=allowCache)

        self.requestInProgress = True
        logger.debug("make request: %s, %s" % (method, args))
        if popup and not popup.msg:
            popup.show()

        try:
            result = getattr(self.aq, method)(*args)
        except Exception as e:
            self.requestInProgress = False
            # traceback.print_stack()
            logger.debug(method)
            logger.debug(args)
            msg = "Could not request Aquarium data:\n\n%s" % e
            self.core.popup(msg)
            return

        data = {"args": args, "result": result}
        self.dbCache[method].append(data)
        self.requestInProgress = False
        return result

    @err_catcher(name=__name__)
    def clearDbCache(self):
        # QUESTION: When changing projects, does this function is called ?
        self.dbCache = {}
        # self.aqProject = None
        self.aqShots = None
        self.aqAssets = None
        # self.aqStatuses = None

    @err_catcher(name=__name__)
    def isLoggedIn(self):
        if not self.aq:
            return False

        try:
            if self.aqUser is None and self.aq.token is not None:
                self.aqUser = self.aq.me()
        except Exception:
            pass

        return bool(self.aqUser)

    @err_catcher(name=__name__)
    def login(self, auth=None, quiet=False):
        if auth is None:
            auth = self.prjMng.getAuthorization()

        url = auth.get("url")
        token = auth.get("aquarium_token")
        self.core.users.setUserReadOnly(False)

        if not url:
            if not quiet:
                msg = "No Aquarium Url is set in the project settings. Cannot connect to Aquarium."
                result = self.core.popupQuestion(msg, buttons=["Setup Aquarium...", "Close"], icon=QMessageBox.Warning)
                if result == "Setup Aquarium...":
                    self.prjMng.openSetupDlg()

            return

        if not token:
            if not quiet:
                msg = "Your are not connected to Aquarium. Please go to you user settings > Project management and enter your credentials."
                self.core.popup(msg)

            return

        url = url.strip("\\/")
        try:
            self.aq = self.aq_api.Aquarium(api_url=url, token=token)
            self.aqProject = self.getCurrentProject()
        except Exception as e:
            logger.warning(traceback.format_exc())
            if not quiet:
                msg = "Failed to login into Aquarium:\n\n%s" % e
                self.core.popup(msg)
                return

        if self.isLoggedIn():
            logger.debug("logged in into Aquarium")
            self.clearDbCache()
            if self.getUseAqUsername():
                self.prjMng.setLocalUsername()

    @err_catcher(name=__name__)
    def getUsername(self):
        username = None
        if self.aq:
            try:
                user = self.aq.me()
                if not user:
                    return
                username = user.data.name
            except:
                return

        return username

    @err_catcher(name=__name__)
    def getProjects(self, parent=None):
        # TODO: Move that Aquarium function
        text = "Querying projects - please wait..."
        popup = self.core.waitPopup(self.core, text, parent=parent, hidden=True)
        with popup:
            # QUESTION: How to ensure project management is logged in ?
            if not self.prjMng.ensureLoggedIn():
                return

            meshql = "# $Project AND (item.data.completion >= 0 OR item.data.completion == null) VIEW $view"
            aliases = {
                'view': {
                    '_key': 'item._key',
                    'name': 'item.data.name',
                    "status": 'item.data.status',
                    "start_date": "item.data.startDate",
                    "end_date": "item.data.endDate",
                    "thumbnail": "item.data.thumbnail",
                }
            }

            aqProjects = self.makeDbRequest("query", [meshql, aliases], popup=popup) or []
            projects = []
            for project in aqProjects:
                thumbnail_url = None
                # FIXME: Prism is not using Aquarium session to download images (request to download image is not authenticated)
                # if project["thumbnail"]:
                #     thumbnail_url = urllib.parse.urljoin(self.getCurrentUrl(), project["thumbnail"])
                project["thumbnail_url"] = thumbnail_url
                projects.append(project)

            return projects

    @err_catcher(name=__name__)
    def getCurrentProject(self, parent=None):
        text = "Querying current project - please wait..."
        popup = self.core.waitPopup(self.core, text, parent=parent, hidden=True)
        with popup:
            if not self.prjMng.ensureLoggedIn():
                return

            projectKey = self.getCurrentProjectId()
            if (projectKey):
                if self.aqProject and self.aqProject._key == projectKey: return self.aqProject
                else:
                    return self.getAqProject(projectKey)
            else:
                return None

    @err_catcher(name=__name__)
    def getCurrentProjectId(self):
        if not self.prjMng.ensureLoggedIn(quiet=True):
            return

        projectKey = self.core.getConfig("prjManagement", "aquarium_projectKey", config="project")
        if not projectKey:
            msg = "No Aquarium project is specified in the project settings."
            logger.warning(msg)
            return

        return projectKey

    @err_catcher(name=__name__)
    def getProjectIdByName(self, name):
        # REVIEW: Do I need that function ?
        if not self.prjMng.ensureLoggedIn():
            return

        projectKey = self.core.getConfig("prjManagement", "aquarium_projectKey", config="project")
        if projectKey is None:
            return

        return projectKey

    @err_catcher(name=__name__)
    def getAssetDepartments(self, allowCache=True):
        text = "Querying asset departments - please wait..."
        popup = self.core.waitPopup(self.core, text, hidden=True)
        with popup:
            departments = []
            if self.aqProject:
                aqDepartments = self.aqProject.prism['properties'].get('departments').get('asset')
                if aqDepartments and len(aqDepartments) > 0:
                    for department in aqDepartments:
                        departments.append({
                            "name": department.get('name'),
                            "abbreviation": department.get('name'),
                            "defaultTasks": department.get('tasks')
                        })

            return departments

    @err_catcher(name=__name__)
    def getShotDepartments(self, allowCache=True):
        text = "Querying shot departments - please wait..."
        popup = self.core.waitPopup(self.core, text, hidden=True)
        with popup:
            departments = []
            if self.aqProject:
                aqDepartments = self.aqProject.prism['properties'].get('departments').get('shot')
                if aqDepartments and len(aqDepartments) > 0:
                    for department in aqDepartments:
                        departments.append({
                            "name": department.get('name'),
                            "abbreviation": department.get('name'),
                            "defaultTasks": department.get('tasks')
                        })

            return departments

    @err_catcher(name=__name__)
    def getConnectedEntities(self, entity):
        # QUESTION: What's a connected entity ?
        centities = []
        return centities

    @err_catcher(name=__name__)
    def setConnectedEntities(self, entities, connectedEntities, add=False, remove=False, setReverse=True):
        # QUESTION: What's a connected entity ?
        msg = "Entity connection cannot get set in Prism, if your project in connected to Aquarium.\n\nPlease set the entity connection in Aquarium."
        result = self.core.popupQuestion(msg, buttons=["Open Aquarium", "Close"], icon=QMessageBox.Warning)
        if result == "Open Aquarium":
            self.openInBrowser(entities[0]["type"], entities[0])

        return False

    @err_catcher(name=__name__)
    def getAssetFolders(self, path=None, parent=None):
        assetFolders = []
        if path:
            path = path.replace('\\', "/")

        assets = self.getAssets(path=path) or []
        for asset in assets:
            cat = os.path.dirname(asset["asset_path"])
            if cat and cat not in assetFolders:
                assetFolders.append(cat)

        return assetFolders

    @err_catcher(name=__name__)
    def getAssets(self, path=None, parent=None):
        # FIXME: Add Prism cache management
        text = "Querying assets - please wait..."
        popup = self.core.waitPopup(self.core, text, parent=parent, hidden=True)

        with popup:
            if not self.prjMng.ensureLoggedIn():
                return

            assets = []
            if path:
                path = path.replace("\\", "/")

            aqAssets = self.aqAssets
            if (aqAssets is None):
                aqAssets = self.getAqProjectAssets()

            for aqAsset in aqAssets:
                if path and not aqAsset['prismPath'].startswith(path):
                    continue

                assetData = {
                    "type": "asset",
                    "id": aqAsset['item']['_key'],
                    "asset_path": aqAsset['prismPath'],
                    "description": aqAsset['item']['data'].get('description'),
                    "thumbnail_url": None,
                    # "thumbnail_url": baseUrl(self.getCurrentUrl(), aqAsset['item']['data'].get('thumbnail')),
                }
                assets.append(assetData)

            if not path:
                self.aqAssets = aqAssets

            return assets

    @err_catcher(name=__name__)
    def getAssetId(self, entity, prjId=None):
        # QUESTION: What's the goal of that function ?
        return

    @err_catcher(name=__name__)
    def getShots(self, parent=None):
        text = "Querying shots - please wait..."
        popup = self.core.waitPopup(self.core, text, parent=parent, hidden=True)
        with popup:
            if not self.prjMng.ensureLoggedIn():
                return

            shots = []

            aqShots = self.aqShots
            if (aqShots is None):
                aqShots = self.getAqProjectShots()
                self.aqShots = aqShots

            for aqShot in aqShots:
                shotData = {
                    "type": "shot",
                    "id": aqShot['item']['_key'],
                    "shot": aqShot['item']['data'].get('name', ''),
                    "sequence": aqShot['sequence'],
                    "start": aqShot['item']['data'].get('frameIn'),
                    "end": aqShot['item']['data'].get('frameOut'),
                    "description": aqShot['item']['data'].get('description'),
                    "thumbnail_url": None,
                    # "thumbnail_url": baseUrl(self.getCurrentUrl(), aqShot['item']['data'].get('thumbnail')),
                }
                shots.append(shotData)

            return shots

    @err_catcher(name=__name__)
    def getShotByEntity(self, entity):
        shots = self.getShots()
        if shots is None:
            return

        for shot in shots:
            if shot["sequence"] == entity["sequence"] and shot["shot"] == entity["shot"]:
                return shot

        msg = 'Could not find shot "%s" in Aquarium.' % self.core.entities.getShotName(entity)
        self.core.popup(msg)

    @err_catcher(name=__name__)
    def getShotId(self, entity, prjId=None):
        # QUESTION: What's the goal of that function ?
        return

    @err_catcher(name=__name__)
    def getTask(self, entity, dep, task, parent=None):
        tasks = self.getTasksFromEntity(entity)
        for t in tasks:
            if dep and t["department"] != dep:
                continue

            if t["task"] != task:
                continue

            return t

    @err_catcher(name=__name__)
    def getDepartmentFromAssetTaskName(self, taskName):
        department = None
        departements = [department for department in self.getAssetDepartments() if taskName in department['defaultTasks']]
        if (len(departements) > 0):
            department = departements[0]
        return department

    @err_catcher(name=__name__)
    def getDepartmentFromShotTaskName(self, taskName):
        department = None
        departements = [department for department in self.getShotDepartments() if taskName in department['defaultTasks']]
        if (len(departements) > 0):
            department = departements[0]
        return department

    @err_catcher(name=__name__)
    def getTasksFromEntity(self, entity, parent=None, allowCache=True):
        text = "Querying tasks - please wait..."
        popup = self.core.waitPopup(self.core, text, parent=parent, hidden=True)
        with popup:
            tasks = []
            if (entity["type"] == 'asset'):
                aqEntities = [aqAsset for aqAsset in self.aqAssets if aqAsset['prismPath'] == entity.get("asset_path", "").replace("\\", "/")]
                if len(aqEntities) > 0:
                    aqTasks = aqEntities[0]['tasks']
                    for aqTask in aqTasks:
                        department = self.getDepartmentFromAssetTaskName(aqTask["data"]["name"])
                        if department:
                            data = {
                                "department": department['name'],
                                "task": aqTask["data"]["name"],
                                "status": aqTask['data'].get('status', ''),
                                "id": aqTask["_key"],
                            }
                            tasks.append(data)
            elif (entity["type"] == 'shot'):
                aqEntities = [aqShot for aqShot in self.aqShots if aqShot['sequence'] == entity.get("sequence", "") and aqShot['name'] == entity.get("shot", "")]
                if len(aqEntities) > 0:
                    aqTasks = aqEntities[0]['tasks']
                    for aqTask in aqTasks:
                        department = self.getDepartmentFromShotTaskName(aqTask["data"]["name"])
                        if department:
                            data = {
                                "department": department['name'],
                                "task": aqTask["data"]["name"],
                                "status": aqTask['data'].get('status', ''),
                                "id": aqTask["_key"],
                            }
                            tasks.append(data)
            return tasks

    @err_catcher(name=__name__)
    def getTaskId(self, entity, prjId, taskname):
        # QUESTION: What's the goal of that function ?
        return

    @err_catcher(name=__name__)
    def setTaskStatus(self, entity, department, task, status, parent=None):
        text = "Setting status - please wait..."
        popup = self.core.waitPopup(self.core, text, parent=parent, hidden=True)
        with popup:
            if not self.prjMng.ensureLoggedIn():
                return

            taskKey = entity['id']
            if taskKey:
                aqStatus = self.getAqStatusFromName(status)
                if (aqStatus):
                    self.aq.task(taskKey).update_data(data=aqStatus)
                    self.getTasksFromEntity(entity, parent=parent, allowCache=False)
                    self.getAssignedTasks(allowCache=False)
                    return True
                else:
                    msg = "Couldn't find matching status in Aquarium. Failed to set status."
                    self.core.popup(msg)
                    return False
            else:
                msg = "Couldn't find matching task in Aquarium. Failed to set status."
                self.core.popup(msg)
                return False

    @err_catcher(name=__name__)
    def getStatusList(self, allowCache=True):
        text = "Querying status list - please wait..."
        popup = self.core.waitPopup(self.core, text, hidden=True)
        with popup:
            statuses = []
            if self.aqStatuses is None:
                self.aqStatuses = self.getAqProjectStatuses()

            for aqStatus in self.aqStatuses:
                status = {
                    "name": aqStatus['status'],
                    "abbreviation": aqStatus['status'],
                    "color": hexToRgb(aqStatus['color']),
                    "products": True,
                    "media": True,
                    "tasks": True,
                }
                statuses.append(status)

            return statuses


    @err_catcher(name=__name__)
    def getProductVersions(self, entity, parent=None, allowCache=True):
        # TODO: getProductVersions
        return []

    @err_catcher(name=__name__)
    def getProductVersion(self, entity, product, versionName):
        # TODO: getProductVersion
        return []

    @err_catcher(name=__name__)
    def getProductVersionStatus(self, entity, product, versionName):
        # TODO: getProductVersionStatus
        return []

    @err_catcher(name=__name__)
    def setProductVersionStatus(self, entity, product, versionName, status, parent=None):
        # TODO: setProductVersionStatus
        return False

    @err_catcher(name=__name__)
    def publishProduct(self, path, entity, task, version, description="", parent=None, origTask=None):
        # TODO: publishProduct
        return

    @err_catcher(name=__name__)
    def getMediaVersions(self, entity, parent=None, allowCache=True):
        # TODO: getMediaVersions
        return

    @err_catcher(name=__name__)
    def getMediaVersion(self, entity, identifierData, versionName):
        # TODO: getMediaVersion
        return []

    @err_catcher(name=__name__)
    def getMediaVersionStatus(self, entity, identifierData, versionName):
        # TODO: getMediaVersionStatus
        return

    @err_catcher(name=__name__)
    def setMediaVersionStatus(self, entity, identifierData, versionName, status, parent=None):
        # TODO: setMediaVersionStatus
        return

    @err_catcher(name=__name__)
    def publishMedia(self, paths, entity, task, version, description="", uploadPreview=True, parent=None, origTask=None):
        # TODO: publishMedia
        return

    @err_catcher(name=__name__)
    def getNotes(self, entityType, entity, allowCache=True):
        print(entityType, entity)
        # TODO: getNotes
        return

    @err_catcher(name=__name__)
    def createNote(self, entityType, entity, note, origin):
        # TODO: createNote
        return

    @err_catcher(name=__name__)
    def createReply(self, entityType, entity, parentNote, note, origin):
        # TODO: createReply
        return

    @err_catcher(name=__name__)
    def getAssignedTasks(self, user=None, allowCache=True):
        # TODO: getAssignedTasks
        return []