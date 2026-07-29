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
import tempfile
import os


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


def getPrismData(itemData):
    if not itemData:
        return {}

    if isinstance(itemData, dict):
        return itemData.get("prism", None)

    return getattr(itemData, "prism", None)


def getValidationStatus(prismData):
    if prismData and "validation_status" in prismData:
        return prismData.get("validation_status")

    return None


# def getPrismType(itemData):
#     prismData = getPrismData(itemData)
#     return prismData.get("type") or "media"


def getEntityFromPlaylistMedia(mediaData, aqAssets=None, aqShots=None, origin=None):
    prismData = getPrismData(mediaData)

    if prismData:
        path = (prismData.get("path") or "").replace("\\", "/")

        if aqAssets:
            for asset in aqAssets:
                if path and path.startswith(asset.get("prismPath", "")):
                    return prismifyAsset(asset)

        if aqShots:
            for shot in aqShots:
                shotName = shot.get("name") or shot.get("item", {}).get("data", {}).get("name", "")
                if path and shotName and shotName in path:
                    return prismifyShot(shot)

    originType = None
    originKey = None
    if isinstance(origin, dict) and origin.get("parents"):
        main_parent = origin.get("parents")[0]
        if main_parent is not None:
            originType = main_parent.get("type")
            originKey = main_parent.get("_key")

    if originType == "Shot" and aqShots:
        for shot in aqShots:
            if shot.get("_key") == originKey:
                return prismifyShot(shot)

    if originType == "Asset" and aqAssets:
        for asset in aqAssets:
            if asset.get("_key") == originKey:
                return prismifyAsset(asset)

    return None

def getFileFromAq(file_url, aq):
    if not file_url:
        return None

    temp_dir = tempfile.gettempdir()

    base_name = os.path.basename(file_url)
    name, extension = os.path.splitext(base_name)

    file_path = os.path.join(temp_dir, 'prism_aquarium', name + extension)

    if os.path.exists(file_path) == False:
        thumbnail = aq.do_request('GET', file_url, decoding=False)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(thumbnail.content)
            f.close()

    return file_path

def prismifyShot(aqShot):
    return {
        "type": "shot",
        "id": aqShot['item']['_key'],
        "shot": aqShot['item']['data'].get('name', ''),
        "sequence": aqShot['sequenceName'],
        "start": aqShot['item']['data'].get('frameIn'),
        "end": aqShot['item']['data'].get('frameOut'),
        "description": aqShot['item']['data'].get('description'),
        "thumbnail": aqShot['thumbnail'],
        "episode": aqShot.get('episodeName', '')
    }

def prismifyAsset(aqAsset):
    return {
        "type": "asset",
        "id": aqAsset['item']['_key'],
        "asset_path": aqAsset['prismPath'],
        "description": aqAsset['item']['data'].get('description'),
        "thumbnail": aqAsset['thumbnail']
    }