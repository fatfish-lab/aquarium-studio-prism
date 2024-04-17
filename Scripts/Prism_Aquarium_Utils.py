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

import urllib.parse

def baseUrl(base, url):
    if url: return urllib.parse.urljoin(base, url)
    else: return None

def hexToRgb(hex):
    rgb = None
    if (hex and type(hex) == str):
        [hashtag, color] = hex.split('#')
        if (color): rgb = list(int(color[i:i+2], 16) for i in (0, 2, 4))
    return rgb

def flatten(listToFlatten):
    return [item for sublist in listToFlatten for item in sublist]
