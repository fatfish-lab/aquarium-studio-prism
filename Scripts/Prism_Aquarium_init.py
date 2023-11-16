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

class Prism_Aquarium(Prism_Aquarium_Variables, Prism_Aquarium_Functions):
    def __init__(self, core):
        self.aqAssets = []
        self.aqShots = []
        self.aqProjectLocations = []

        self.aq = None
        self.aqUser = None
        self.aqProject = None

        Prism_Aquarium_Variables.__init__(self, core, self)
        Prism_Aquarium_Functions.__init__(self, core, self)

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

            except Exception as e:
                logger.warning("Could not access to project:\n\n%s" % e)

        return aqProject

    # @err_catcher(name=__name__)
    # def getAqProjects(self):
    #     aliases = {
    #         'view': {
    #             'name': 'item.data.name',
    #             '_key': 'item._key'
    #         }
    #     }

    #     projectsfun = self.aq.query(
    #         meshql="# ($Project AND (item.data.completion >= 0 OR item.data.completion == null) AND NOT (<($Trash)- *)) SORT item.updatedAt DESC VIEW $view",
    #         aliases=aliases
    #     )
    #     return projects

    @err_catcher(name=__name__)
    def getShotsLocation (self, project = None):
        if (project == None): project = self.aqProject

        location = project.prism['shotsLocation']
        if not location: location = project._key
        return location

    @err_catcher(name=__name__)
    def getAssetsLocation (self, project = None):
        if (project == None): project = self.aqProject

        location = project.prism['assetsLocation']
        if not location: location = project._key
        return location

    @err_catcher(name=__name__)
    def getAqProjectAssets(self, project = None):
        if (project == None): project = self.aqProject

        separator = '_'
        usePrismNamingConvention = False
        if ('usePrismNamingConvention' in project.prism['properties']) :
            usePrismNamingConvention = project.prism['properties']['usePrismNamingConvention']

        startpoint = self.getAssetsLocation(project = project)
        query = "# -($Child, 3)> 0,500 $Asset AND path.edges[*].data.hidden != true VIEW $view"
        aliases = {
            "view": {
                "item": "item",
                "name": "item.data.name",
                "parent": "path.vertices[-2]",
                "parentName": "path.vertices[-2].data.name",
                "parentsName": "path.vertices[*].data.name",
                "tasks": "# -($Child, 2)> $Task SORT edge.data.weight VIEW item"
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
    def getAqProjectShots(self, project = None):
        if (project == None): project = self.aqProject

        usePrismNamingConvention = False
        if ('usePrismNamingConvention' in project.prism['properties']) :
            usePrismNamingConvention = project.prism['properties']['usePrismNamingConvention']

        separator = '_'
        startpoint = self.getShotsLocation(project = project)
        query = "# -($Child, 3)> 0,500 $Shot AND path.edges[*].data.hidden != true VIEW $view"
        aliases = {
            "view": {
                "item": "item",
                "name": "item.data.name",
                "parent": "path.vertices[-2]",
                "parentName": "path.vertices[-2].data.name",
                "tasks": "# -($Child, 2)> $Task SORT edge.data.weight VIEW item"
            }
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
            shot['sequence'] = sequence

        return shots

    @err_catcher(name=__name__)
    def getAqProjectStatuses (self, project = None):
        if (project == None): project = self.aqProject
        if (self.aqProject == None):
            return []

        query = '# -($Child)> $Properties AND item.data.tasks_status != null VIEW item.data.tasks_status'

        statuses = []

        aqStatuses = self.aqProject.traverse(meshql=query)
        for aqStatus in aqStatuses:
            if aqStatus:
                exist = [status for status in statuses if status['status'] == aqStatus['status']]
                if len(exist) == 0:
                    statuses.append(aqStatus)

        if len(statuses) == 0:
            statuses = list(self._aq_api.DEFAULT_STATUSES.values())

        return statuses

    @err_catcher(name=__name__)
    def getAqStatusFromName (self, statusName):
        status = None
        aqStatuses = self.getAqProjectStatuses()

        aqStatus = [aqStatus for aqStatus in aqStatuses if aqStatus['status'] == statusName]
        if len(aqStatus) > 0:
            status = aqStatus[0]

        return status