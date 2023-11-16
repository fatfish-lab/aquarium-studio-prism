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


class Prism_Aquarium_Variables(object):
    def __init__(self, core, plugin):
        self.version = "v2.0.0-beta.3"
        self.pluginName = "Aquarium"
        self.pluginType = "Custom"
        self.platforms = ["Windows"]
        self.pluginDirectory = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
