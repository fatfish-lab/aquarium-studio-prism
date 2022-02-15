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

from Prism_Aquarium_Variables import Prism_Aquarium_Variables
from Prism_Aquarium_Functions import Prism_Aquarium_Functions

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

logger = logging.getLogger(__name__)

modulePath = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "external_modules")
sys.path.append(modulePath)

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
    def connectToAquarium(self, email=None, password=None, token=None):
        import aquarium

        connected = False
        aqSite = self.core.getConfig(
            "aquarium", "site", configPath=self.core.prismIni
        )

        if (not token): token = self.core.getConfig("aquarium", "token")

        if (not aqSite):
            logger.warning("Not all required information for the authentification are configured.\nPlease check the following Aquarium Studio settings :\n{aqSite}".format(
                aqSite='' if aqSite else '- Site url (in project settings)\n')
            )
            return False

        if (self.aq == None): self.aq = aquarium.Aquarium(api_url=aqSite, token=token)

        if (token == None or len(token) == 0) or password != None or (password != None and len(password) > 0):
            try:
                if (email and password):
                    self.aq.connect(email=email, password=password)
                else:
                    logger.warning("Not all required information for the authentification are configured.\nPlease check the following Aquarium Studio settings :\n{aqSite}{aqUserEmail}{aqUserPassword}".format(
                        aqSite='' if aqSite else '- Site url (in project settings)\n',
                        aqUserEmail='' if email else '- User email (in user settings)\n',
                        aqUserPassword='' if password else '- User password (in user settings)\n'))
                    connected = False
            except Exception as e:
                self.aq.logout()
                logger.warning("Could not connect to Aquarium Studio:\n\n%s" % e)
                connected = False

        connected = self.getAqCurrentUser()

        self.aqProject = self.getAqProject()
        
        return connected

    @err_catcher(name=__name__)
    def getAqCurrentUser(self): 
        try:
            me = self.aq.get_current_user()
            self.aqUser = me
            return True
        except Exception as e:
            logger.warning("Could not get user profile:\n\n%s" % e)
            return False

    @err_catcher(name=__name__)
    def getAqProject(self, projectKey = None):
        aqProject = None
        if (not projectKey): projectKey = self.core.getConfig(
                "aquarium", "projectkey", configPath=self.core.prismIni
            )
        if (projectKey):
            try:
                if (self.aqProject and self.aqProject._key == projectKey):
                    return self.aqProject
                else:
                    aqProject = self.aq.item(projectKey).get()
                    aqProject.prism = dict(
                        properties=None,
                        assetsLocation=None,
                        shotsLocation=None,
                        timelogsLocation=None
                    )

                    queryProperties = '# -($Child)> 0,1 $Properties AND item.data.prism != null VIEW item.data.prism'
                    prismProperties = aqProject.traverse(meshql=queryProperties)
                    if (prismProperties and len(prismProperties) > 0): aqProject.prism['properties'] = prismProperties[0]
                    
                    queryLocations = '# -()> * AND edge.type IN ["PrismAssetsLocation", "PrismShotsLocation", "PrismTimelogsLocation"]'
                    locations = aqProject.traverse(meshql=queryLocations)
                    for l in locations:
                        location = self.aq.element(l)
                        if location.edge.type == 'PrismAssetsLocation': aqProject.prism['assetsLocation'] = location.item._key
                        elif location.edge.type == 'PrismShotsLocation': aqProject.prism['shotsLocation'] = location.item._key
                        elif location.edge.type == 'PrismTimelogsLocation': aqProject.prism['timelogsLocation'] = location.item._key

            except Exception as e:
                logger.warning("Could not access to project:\n\n%s" % e)

        return aqProject

    @err_catcher(name=__name__)
    def getAqProjects(self):
        aliases = {
            'view': {
                'name': 'item.data.name',
                '_key': 'item._key' 
            }
        }

        projects = self.aq.query(
            meshql="# ($Project AND (item.data.completion >= 0 OR item.data.completion == null) AND NOT <($Trash)- *) SORT item.updatedAt DESC VIEW $view",
            aliases=aliases
        )
        return projects

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
    def getTimelogsLocation (self, project = None):
        if (project == None): project = self.aqProject

        location = project.prism['timelogsLocation']
        if not location: location = project._key
        return location

    @err_catcher(name=__name__)
    def getAqProjectAssets(self, project = None):
        if (project == None): project = self.aqProject

        startpoint = self.getAssetsLocation(project = project)
        query = "# -($Child, 3)> $Asset AND path.edges[*].data.hidden != true VIEW $view"
        aliases = {
            "view": {
                "item": "item",
                "parent": "path.vertices[-2]",
                "parents": "path.vertices",
                "tasks": "# -($Child, 2)> $Task SORT edge.data.weight VIEW item"
            }
        }
        assets = self.aq.item(startpoint).traverse(meshql=query, aliases=aliases)

        for asset in assets:
            parents = list(map(lambda parent: parent['data']['name'],asset['parents']))[1:-1]
            prismId = os.path.join(*(parents + [asset['item']['data']['name']]))
            asset['prismId'] = prismId
        
        return assets

    @err_catcher(name=__name__)
    def getAqProjectShots(self, project = None):
        if (project == None): project = self.aqProject

        startpoint = self.getShotsLocation(project = project)
        query = "# -($Child, 3)> $Shot AND path.edges[*].data.hidden != true VIEW $view"
        aliases = {
            "view": {
                "item": "item",
                "parent": "path.vertices[-2]",
                "tasks": "# -($Child, 2)> $Task SORT edge.data.weight VIEW item"
            }
        }
        shots = self.aq.item(startpoint).traverse(meshql=query, aliases=aliases)
        
        for shot in shots:
            prismId = None
            if (shot['parent']['_key'] == startpoint):
                prismId = "{separator}{shotName}".format(
                    separator = self.core.sequenceSeparator,
                    shotName = shot['item']['data']['name']
                )
            else:
                prismId = "{parentName}{separator}{shotName}".format(
                    parentName = shot['parent']['data']['name'],
                    separator = self.core.sequenceSeparator,
                    shotName = shot['item']['data']['name']
                )
            shot['prismId'] = prismId

        return shots