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

from Prism_Aquarium_Variables import Prism_Aquarium_Variables
from Prism_Aquarium_Functions import Prism_Aquarium_Functions

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

import logging
logger = logging.getLogger(__name__)

class Prism_Aquarium(Prism_Aquarium_Variables, Prism_Aquarium_Functions):
    def __init__(self, core):
        self.aq = None
        self.aqUser = None

        self.aqUsers = None
        self.aqShots = None
        self.aqAssets = None
        self.aqPlaylists = None
        self.aqProject = None
        self.aqTaskStatuses = None
        self.aqVersionStatuses = None
        self.aqProjectLocations = []

        Prism_Aquarium_Variables.__init__(self, core, self)
        Prism_Aquarium_Functions.__init__(self, core, self)
    @err_catcher(name=__name__)
    def getAqProjects(self):
        meshql = "# $Project AND (item.data.completion >= 0 OR item.data.completion == null) VIEW $view"
        aliases = {
            'view': {
                'id': "item._key",
                '_key': 'item._key',
                'name': 'item.data.name',
                "status": 'item.data.status',
                "start_date": "item.data.startDate",
                "end_date": "item.data.endDate",
                "thumbnail_url": "item.data.thumbnail",
                "thumbnail": "item.data.thumbnail",
            }
        }

        return self.aq.query(meshql=meshql, aliases=aliases)


    @err_catcher(name=__name__)
    def getAqProject(self, projectKey = None):
        aqProject = None
        if (not projectKey): projectKey = self.core.getConfig("prjManagement", "aquarium_projectKey", config="project")
        if (projectKey):
            try:
                aqProject = self.aq.item(projectKey).get()
                aqProject.prism = dict(
                    properties=None,
                    assetsLocation=None,
                    shotsLocation=None
                )

                queryProperties = '# -($Child)> 0,1 $Properties AND item.data.prism != null AND item.data.prism.version >= "2.0.0" VIEW item.data.prism'
                prismProperties = aqProject.traverse(meshql=queryProperties)
                if (prismProperties and len(prismProperties) > 0): aqProject.prism['properties'] = prismProperties[0]

                queryLocations = '# -()> * AND edge.type IN ["PrismAssetsLocation", "PrismShotsLocation"]'
                locations = aqProject.traverse(meshql=queryLocations)
                for l in locations:
                    location = self.aq.element(l)
                    if location.edge.type == 'PrismAssetsLocation': aqProject.prism['assetsLocation'] = location.item._key
                    elif location.edge.type == 'PrismShotsLocation': aqProject.prism['shotsLocation'] = location.item._key

                if (aqProject.prism["properties"] == None):
                    logger.warning("Project %s does not have Prism properties. Please go to project settings in Aquarium > Connector and enable Prism." % aqProject.data.name)

            except Exception as e:
                logger.warning("Could not access to project:\n\n%s" % e)

        return aqProject

    @err_catcher(name=__name__)
    def getShotsLocation (self, project = None):
        if (project == None): project = self.aqProject

        location = None
        if project:
            location = project.prism['shotsLocation']
            if not location: location = project._key

        return location

    @err_catcher(name=__name__)
    def getAssetsLocation (self, project = None):
        if (project == None): project = self.aqProject

        location = None
        if project:
            location = project.prism['assetsLocation']
            if not location: location = project._key

        return location

    @err_catcher(name=__name__)
    def getAqProjectAssets(self, project = None):
        if (project == None): project = self.aqProject

        if project == None:
            return []

        separator = '_'
        usePrismNamingConvention = False

        if (project.prism and 'properties' in project.prism and isinstance(project.prism["properties"], dict)):
            if ('usePrismNamingConvention' in project.prism['properties']) :
                usePrismNamingConvention = project.prism['properties']['usePrismNamingConvention']

        startpoint = self.getAssetsLocation(project = project)
        query = "# -($Child, 3)> 0,500 $Asset AND path.edges[*].data.hidden != true VIEW $view"
        aliases = {
            "view": {
                "item": "item",
                "_key": "item._key",
                "name": "item.data.name",
                "thumbnail": "item.data.thumbnail",
                "parent": "path.vertices[-2]",
                "parentName": "path.vertices[-2].data.name",
                "parentsName": "path.vertices[*].data.name",
                "tasks": "# -($Child, 2)> $Task SORT edge.data.weight VIEW $taskView"
            },
            "taskView": {
                "_key": "item._key",
                "data": "item.data",
                "users": "# -($Assigned)> $User VIEW item",
            }
        }

        if (usePrismNamingConvention) :
            aliases['view']['name'] = "SUBSTITUTE(item.data.name, [ '_',' ','-' ], '{separator}' )".format(
                separator=separator
            )
            aliases['view']['parentName'] = "SUBSTITUTE(path.vertices[-2].data.name, [ '_',' ','-' ], '{separator}' )".format(
                separator=separator
            )
            aliases['view']['parentsName'] = "JSON_PARSE(SUBSTITUTE(path.vertices[*].data.name, [ '_',' ','-' ], '{separator}' ))".format(
                separator=separator
            )

        assets = self.aq.item(startpoint).traverse(meshql=query, aliases=aliases)

        for asset in assets:
            prismPath = '/'.join(asset['parentsName'][1:-1] + [asset['name']])
            asset['prismPath'] = prismPath

        return assets

    @err_catcher(name=__name__)
    def getAqProjectShots(self, project = None, withEpisodes = False):
        if (project == None): project = self.aqProject

        if project == None:
            return []

        usePrismNamingConvention = False
        if (project.prism and 'properties' in project.prism and isinstance(project.prism["properties"], dict)):
            if ('usePrismNamingConvention' in project.prism['properties']) :
                usePrismNamingConvention = project.prism['properties']['usePrismNamingConvention']

        separator = '_'
        startpoint = self.getShotsLocation(project = project)
        query = "# -($Child, 3)> 0,500 $Shot AND path.edges[*].data.hidden != true VIEW $view"
        aliases = {
            "view": {
                "item": "item",
                "_key": "item._key",
                "name": "item.data.name",
                "thumbnail": "item.data.thumbnail",
                "parent": "path.vertices[-2]",
                "parentName": "path.vertices[-2].data.name",
                "tasks": "# -($Child, 2)> $Task SORT edge.data.weight VIEW $taskView"
            },
            "taskView": {
                "_key": "item._key",
                "data": "item.data",
                "users": "# -($Assigned)> $User VIEW item",
            }
        }

        aliases["view"]["sequence"] = "FIRST(# <($Child)- 0,1 $Sequence SORT null VIEW $sequenceView)"
        aliases["sequenceView"] = {
            "item": "item",
            "tasks": "# -($Child, 2)> $Task AND path.vertices[-2].type IN ['Sequence','Task'] SORT edge.data.weight VIEW $taskView"
        }

        if withEpisodes:
            aliases["view"]["episode"] = "FIRST(# <($Child, 3)- 0,1 $Episode SORT null VIEW $episodeView)"
            aliases["episodeView"] = {
                "item": "item",
                "tasks": "# -($Child, 2)> $Task AND path.vertices[-2].type IN ['Episode','Task'] SORT edge.data.weight VIEW $taskView"
            }

        if (usePrismNamingConvention):
            aliases["view"]["name"] = "SUBSTITUTE(item.data.name, [ '_',' ','-' ], '{separator}' )".format(
                separator=separator
            )
            aliases["view"]["parentName"] = "SUBSTITUTE(path.vertices[-2].data.name, [ '_','-','.',' ' ], '{separator}' )".format(
                separator='.'
            )

        shots = self.aq.item(startpoint).traverse(meshql=query, aliases=aliases)

        for shot in shots:
            prismId = None
            sequence = None
            if (shot['parent']['_key'] == startpoint):
                prismId = "{separator}{shotName}".format(
                    separator = separator,
                    shotName = shot['name']
                )
            else:
                prismId = "{parentName}{separator}{shotName}".format(
                    parentName = shot['parentName'],
                    separator = separator,
                    shotName = shot['name']
                )
                sequence = shot['parentName']
            shot['prismId'] = prismId
            shot['sequenceName'] = sequence
            if withEpisodes:
                shot['episodeName'] = shot.get('episode', {}).get('item', {}).get('data', {}).get('name', '')

        return shots

    @err_catcher(name=__name__)
    def getAqProjectStatuses (self, property = "tasks_status"):
        if self.aqProject == None:
            return []

        query = '# -($Child)> $Properties AND item.data.{property} != null VIEW item.data.{property}'.format(property=property)

        statuses = []

        aqStatuses = self.aqProject.traverse(meshql=query)
        for aqStatus in aqStatuses:
            if aqStatus:
                exist = [status for status in statuses if status['status'] == aqStatus['status']]
                if len(exist) == 0:
                    statuses.append(aqStatus)

        if len(statuses) == 0:
            if property == "versions_status":
                statuses = list(self._aq_api.DEFAULT_VERSION_STATUSES.values())
            else:
                statuses = list(self._aq_api.DEFAULT_STATUSES.values())

        return statuses

    @err_catcher(name=__name__)
    def getAqStatusFromName (self, statusName):
        status = None
        aqTaskStatuses = self.getAqProjectStatuses()

        aqStatus = [aqStatus for aqStatus in aqTaskStatuses if aqStatus['status'] == statusName]
        if len(aqStatus) > 0:
            status = aqStatus[0]

        return status


    @err_catcher(name=__name__)
    def getAqProjectPlaylists(self, project = None):
        if (project == None): project = self.aqProject

        if project == None:
            return []

        query = "# -($Child, 2)> 0,500 $Playlist VIEW $view"
        aliases = {
            "view": {
                "item": "item",
                "_key": "item._key",
                "name": "item.data.name",
                "thumbnail": "item.data.thumbnail",
                "parent": "path.vertices[-2]",
                "medias": "# -()> 0,500 edge.type IN ['Child', 'Playlist'] AND $Media SORT edge.createdAt ASC VIEW $mediaView"
            },
            "mediaView": {
                "_key": "item._key",
                "data": "item.data",
                "origin": "FIRST(# <($Origin)- 0,1 * VIEW $originView)",
                "parent": "$originView",
                "comments": "# -($Child)> 0,500 $Comment SORT edge.createdAt ASC VIEW populate(item)"
            },
            "originView": {
                "_key": "item._key",
                "item": "item",
                "parents": "FIRST(# <($Child, 3)- 0,1 item.type IN ['Asset', 'Shot'] SORT null VIEW REVERSE(path.vertices))",
            }
        }

        playlists = self.aq.item(project._key).traverse(meshql=query, aliases=aliases)
        return playlists

    @err_catcher(name=__name__)
    def findPlaylistByName(self, playlistName):
        playlists = self.aqPlaylists
        if playlists is None:
            playlists = self.getAqProjectPlaylists()

        for playlist in playlists:
            if playlist["name"] == playlistName:
                return playlist

        return None

    def findAssetByPath(self, path):
        find = lambda asset: asset.get('prismPath', '') == path.replace('\\', "/")
        return next(filter(find, self.aqAssets), None)

    def findShotBySequenceAndName(self, sequence, name):
        find = lambda shot: shot.get('sequenceName', '') == sequence and shot.get('name', '') == name
        return next(filter(find, self.aqShots), None)

    def findUserByName(self, name):
        find = lambda user: user.data.name == name
        return next(filter(find, self.aqUsers), None)

    @err_catcher(name=__name__)
    def resolveAqEntity(self, entity):
        if entity.get("type") == "asset":
            return self.findAssetByPath(entity.get("asset_path", ""))
        if entity.get("type") == "shot":
            return self.findShotBySequenceAndName(entity.get("sequence", ""), entity.get("shot", ""))
        return None

    @err_catcher(name=__name__)
    def getEntityDisplayName(self, entity):
        if entity.get("type") == "asset":
            return entity.get("asset_path", "").replace("\\", "/")
        if entity.get("type") == "shot":
            return self.core.entities.getShotName(entity)
        return ""

    @err_catcher(name=__name__)
    def getAqTaskVersions(self, entityKey, prismType=None):
        query = "# -($Child, 2)> $Task VIEW $taskView"
        aliases = {
            "taskView": {
                "taskKey": "item._key",
                "taskName": "item.data.name",
                "versions": "# -($Child)> $Version SORT edge.createdAt ASC VIEW $versionView",
            },
            "versionView": {
                "versionKey": "item._key",
                "versionName": "item.data.name",
                "medias": "# -($Child)> $Media SORT edge.createdAt DESC VIEW $mediaView",
            },
            "mediaView": {
                "mediaKey": "item._key",
                "data": "item.data",
            },
        }

        tasks = self.aq.item(entityKey).traverse(meshql=query, aliases=aliases) or []
        versions = []

        for task in tasks:
            for version in task.get("versions") or []:
                for media in version.get("medias") or []:
                    mediaData = media.get("data") or {}
                    mediaPrismType = mediaData.get("prism", {}).get("type", "media")
                    if prismType and mediaPrismType != prismType:
                        continue

                    versions.append({
                        "taskKey": task.get("taskKey"),
                        "taskName": task.get("taskName"),
                        "versionKey": version.get("versionKey"),
                        "versionName": version.get("versionName"),
                        "mediaKey": media.get("mediaKey"),
                        "data": mediaData,
                        "prismType": mediaPrismType,
                    })

        return versions

    @err_catcher(name=__name__)
    def buildPrismVersionLabel(self, entity, task, version, origTask=None):
        taskLabel = origTask or task
        return "%s_%s_%s" % (
            self.getEntityDisplayName(entity),
            taskLabel,
            version,
        )