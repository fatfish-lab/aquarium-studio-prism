# -*- coding: utf-8 -*-

import os
import sys
import logging

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
    import AquariumSync_ui
else:
    import AquariumSync_ui_ps2 as AquariumSync_ui

logger = logging.getLogger(__name__)

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

class TableModel(QAbstractTableModel):
    def __init__(self, data, origin):
        super(TableModel, self).__init__()
        self._data = data
        self.origin = origin

    def headerData(self, index, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return {
                    0: lambda: 'SELECT',
                    1: lambda: 'ACTION',
                    2: lambda: 'ITEM NAME',
                    3: lambda: 'FOLDER',
                    4: lambda: 'CATEGORIES',
                    5: lambda: 'UPDATES',
                    6: lambda: 'SYNCED STATUS',
                }[index]()
            else:
                return index + 1

    def data(self, index, role):
        value = self._data[index.row()][index.column()]
        if role == Qt.DisplayRole:
            return {
                0: lambda value: '',
                1: lambda value: value,
                2: lambda value: self.origin.getItem(value)['item'].data.name if self.origin.getItem(value) is not None else value,
                3: lambda value: self.origin.getItem(value)['parent'].data.name if self.origin.getItem(value) is not None else value,
                4: lambda value: ','.join(map(lambda val: '({step}) {category}'.format(step=val[0], category=val[1]), value)) if isinstance(value, list) else value,
                5: lambda value: value,
                6: lambda value: 'Synced' if value == True else 'Not synced' if value == False else value,
            }[index.column()](value)
        elif role == Qt.TextAlignmentRole:
            return {
                0: lambda value: Qt.AlignCenter,
                1: lambda value: Qt.AlignCenter,
                2: lambda value: Qt.AlignCenter,
                3: lambda value: Qt.AlignCenter,
                4: lambda value: Qt.AlignCenter,
                5: lambda value: Qt.AlignCenter,
                6: lambda value: Qt.AlignCenter
            }[index.column()](value)
        elif role == Qt.ForegroundRole:
            return {
                0: lambda value: '',
                1: lambda value: QColor('#37b24d') if value == 'create' else QColor('#f76707'),
                2: lambda value: '',
                3: lambda value: '',
                4: lambda value: '',
                5: lambda value: '',
                6: lambda value: QColor('#37b24d') if value == True else QColor('#f03e3e')
            }[index.column()](value)
        elif role == Qt.CheckStateRole:
            return {
                0: lambda value: Qt.Checked if value == True else Qt.Unchecked,
                1: lambda value: None,
                2: lambda value: None,
                3: lambda value: None,
                4: lambda value: None,
                5: lambda value: None,
                6: lambda value: None
            }[index.column()](value)
        else:
            return None

    def flags(self, index):
        if not index.isValid(): return None
        elif index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
        else:
            if self._data[index.row()][0] == True:
                return Qt.ItemIsEnabled
            else:
                return Qt.NoItemFlags

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        if role == Qt.CheckStateRole and index.column() == 0:
            if value == Qt.Checked:
                self._data[index.row()][index.column()] = True
            else:
                self._data[index.row()][index.column()] = False
        return True

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        if (len(self._data) > 0):
            return len(self._data[0])
        else:
            return 0

class aqSync(QDialog, AquariumSync_ui.Ui_dlg_aqSync):
    def __init__(
        self, core, origin, ptype = 'Asset', target = 'aquarium'
    ):
        QDialog.__init__(self)
        self.setupUi(self)

        self.core = core
        self.origin = origin
        self.ptype = ptype
        self.target = target

        self.aqItems = {}
        self.tableData = []
        self.model = None
        
        self.cb_target.addItem('Sync to Aquarium Studio', 'aquarium')
        self.cb_target.addItem('Sync to Prism', 'prism')

        idx = self.cb_target.findData(target)
        if idx != -1:
            self.cb_target.setCurrentIndex(idx)
        else:
            self.cb_target.clear()
            self.cb_target.addItem('No valid target !', None)

        connected = self.origin.connectToAquarium()
        if connected == False:
            self.origin.messageWarning(
                message="You are not connected to Aquarium Studio. Please check your settings.",
                title="Aquarium studio publish"
            )
            return

        if ptype == "Asset":
            self.rb_asset.setChecked(True)
        else:
            self.rb_shot.setChecked(True)

        self.connectEvents()
        self.refresh()
    
    @err_catcher(name=__name__)
    def connectEvents(self):
        self.cb_target.activated.connect(
            lambda: self.refresh()
        )
        self.rb_asset.toggled.connect(
            lambda: self.refresh()
        )
        self.rb_shot.toggled.connect(
            lambda: self.refresh()
        )
        self.b_refresh.pressed.connect(self.refresh)
        self.b_sync.clicked.connect(self.sync)

    @err_catcher(name=__name__)
    def refresh(self):
        if self.cb_target.currentData() == 'aquarium':
            self.target = 'aquarium'
            self.b_sync.setText('Synchronize Prism to Aquarium Studio')
        elif self.cb_target.currentData() == 'prism':
            self.target = 'prism'
            self.b_sync.setText('Synchronize Aquarium Studio to Prism')
        else:
            self.target = None

        if self.rb_asset.isChecked():
            self.ptype = 'Asset'
        elif self.rb_shot.isChecked():
            self.ptype = 'Shot'
        else:
            self.ptype = None

        self.l_syncInfo.setText('Select the {type}s you want to create or update on {target} :'.format(
            type = self.ptype.lower(),
            target = self.target.capitalize()
        ))

        self.analyze()

    @err_catcher(name=__name__)
    def analyze (self):
        if self.ptype == 'Asset':
            self.aqItems = {
                asset['prismId']: {
                    'item': self.origin.aq.cast(asset['item']),
                    'parent': self.origin.aq.cast(asset['parent']),
                    'tasks': [self.origin.aq.cast(task) for task in asset['tasks']],
                    'prismId': asset['prismId']  
            } for asset in self.origin.getAqProjectAssets()}
        elif self.ptype == 'Shot':
            self.aqItems =  {
                shot['prismId']: {
                    'item': self.origin.aq.cast(shot['item']),
                    'parent': self.origin.aq.cast(shot['parent']),
                    'tasks': [self.origin.aq.cast(task) for task in shot['tasks']],
                    'prismId': shot['prismId'] 
            } for shot in self.origin.getAqProjectShots()}
        else:
            self.origin.messageWarning(
                message='No valid type is selected',
                title='Aquarium Studio sync'
            )
            return

        if self.target == 'aquarium':
            if self.ptype == 'Asset':
                self.tableData = self.prismAssetsToAq()
            else:
                self.tableData = self.prismShotsToAq()
        elif self.target == 'prism':
            if self.ptype == 'Asset':
                self.tableData = self.aqAssetsToPrism()
            else:
                self.tableData = self.aqShotsToPrism()
        else:
            self.origin.messageWarning(
                message="No valid target to sync data",
                title="Aquarium Studio sync"
            )

        self.model = TableModel(self.tableData, self)
        self.t_items.setModel(self.model)
        self.t_items.resizeColumnsToContents()

        if (len(self.tableData) > 0):
            self.b_sync.setEnabled(True)
            self.t_items.setEnabled(True)
            self.l_synced.setText('')
        else:
            self.b_sync.setEnabled(False)
            self.t_items.setEnabled(False)
            self.l_synced.setText('No {type} need to be synced.'.format(
                type=self.ptype.lower()
            ))

    @err_catcher(name=__name__)
    def getItem(self, key):
        entity = None
        for itemKey in self.aqItems:
            item = self.aqItems[itemKey]
            if item == key: entity = item
            elif item['item'] and item['item']._key == key: entity = item
        
        return entity

    @err_catcher(name=__name__)
    def prismAssetsToAq(self):
        assetsToCreate = []
        assets = self.core.entities.getAssetPaths()
        aBasePath = self.core.getAssetPath()
        prismAssets = [[os.path.basename(path), path.replace(aBasePath, "").replace(os.path.basename(path), "")[1:-1], path.replace(aBasePath, "")[1:]] for path in assets]

        self.core.entities.refreshOmittedEntities()
        location = self.origin.getAssetsLocation()
        steps = dict(self.origin.core.getConfig("globals", "pipeline_steps", configPath=self.origin.core.prismIni))

        for assetName, folderName, prismAssetName in prismAssets:
            if prismAssetName not in self.core.entities.omittedEntities["asset"]:
                isAssetExist = prismAssetName in self.aqItems
                if isAssetExist:
                    parent = self.aqItems[prismAssetName]['parent']
                    isAssetStoredInFolder = parent.data.name == folderName or parent._key == location
                    if isAssetStoredInFolder:
                        categories = []
                        tasksName = list(map(lambda task: task.data.name, self.aqItems[prismAssetName]['tasks']))
                        shotPrismSteps = self.core.entities.getSteps(asset=prismAssetName)

                        for step in shotPrismSteps:
                            if step in steps.keys():
                                shotPrismCategories = self.core.entities.getCategories(asset=prismAssetName, step=step)
                                for category in shotPrismCategories:
                                    if category not in tasksName:
                                        categories.append([step, category])

                        if len(categories) > 0:
                            parentName = parent.data.name if parent._key != location else 'Root location'
                            assetsToCreate.append([False, 'update', self.aqItems[prismAssetName]['item']._key, parentName, categories, None, False])
                    else:
                        assetsToCreate.append([False, 'move', self.aqItems[prismAssetName]['item']._key, prismFolderName, 'Do not change categories', None, False])
                        pass
                else:
                    assetsToCreate.append([True, 'create', assetName, prismFolderName, 'Categorie from Aquarium template', None, False])

        return assetsToCreate

    @err_catcher(name=__name__)
    def prismShotsToAq(self):
        shotsToCreate = []
        for i in os.walk(self.core.getShotPath()):
            foldercont = i
            break

        self.core.entities.refreshOmittedEntities()
        steps = dict(self.origin.core.getConfig("globals", "pipeline_steps", configPath=self.origin.core.prismIni))
        localShots = []
        for prismShotName in foldercont[1]:
            if not prismShotName.startswith("_") and prismShotName not in self.core.entities.omittedEntities["shot"]:
                shotName, seqName = self.core.entities.splitShotname(prismShotName)
                if seqName == "no sequence" or len(seqName) == 0:
                    seqName = None

                if len(shotName) > 0: localShots.append([shotName, seqName, prismShotName])

        location = self.origin.getShotsLocation()
        for shotName, seqName, prismShotName in localShots:
            isShotExist = prismShotName in self.aqItems
            if isShotExist:
                parent = self.aqItems[prismShotName]['parent']
                isShotStoredInFolder = parent.data.name == seqName or parent._key == location
                if isShotStoredInFolder:
                    categories = []
                    tasksName = list(map(lambda task: task.data.name, self.aqItems[prismShotName]['tasks']))
                    shotPrismSteps = self.core.entities.getSteps(shot=prismShotName)
                    item = self.aqItems[prismShotName]['item']

                    for step in shotPrismSteps:
                        if step in steps.keys():
                            shotPrismCategories = self.core.entities.getCategories(shot=prismShotName, step=step)
                            for category in shotPrismCategories:
                                if category not in tasksName:
                                    categories.append([step, category])

                        parentName = parent.data.name if parent._key != location else 'Root location'
                    if len(categories) > 0:
                        shotsToCreate.append([False, 'update', item._key, parentName, categories, False])
                else:
                        frameIn, frameOut = self.core.entities.getShotRange(prismShotName)
                        newFrameRange = []
                        if frameIn != item.data.frameIn: newFrameRange.append('frameIn : {frameIn}'.format(frameIn=frameIn))
                        if frameOut != item.data.frameOut: newFrameRange.append('frameOut : {frameOut}'.format(frameOut=frameOut))
                        if len(newFrameRange) > 0:
                            shotsToCreate.append([False, 'update frame range', item._key, parentName, categories, ' - '.join(newFrameRange), False])

            else:
                    shotsToCreate.append([False, 'move', self.aqItems[prismShotName]['item']._key, seqName, 'Do not change categories', None, False])
            else:
                shotsToCreate.append([True, 'create', shotName, seqName, 'Categorie from Aquarium template', None, False])
        return shotsToCreate

    @err_catcher(name=__name__)
    def aqAssetsToPrism(self): 
        assetsToCreate = []
        
        steps = dict(self.origin.core.getConfig("globals", "pipeline_steps", configPath=self.origin.core.prismIni))
        for asset in self.aqItems:
            item = self.aqItems[asset]['item']
            parent = self.aqItems[asset]['parent']
            tasks = self.aqItems[asset]['tasks']
            prismId = self.aqItems[asset]['prismId']

            prismAssetPath = os.path.join(self.core.getAssetPath(), prismId)
            action = None
            if not os.path.exists(prismAssetPath):
                action = 'create'
            
            categories = []
            for task in tasks:
                taskSteps = (step for step, categories in steps.items() if task.data.name in categories)
                taskStep = next(taskSteps, None)
                if taskStep:
                    if action is None:
                        catPath = self.core.getEntityPath(asset=prismId, step=taskStep, category=task.data.name)
                        if not os.path.exists(catPath):
                            categories.append([taskStep, task.data.name])
                    elif action == 'create':
                        categories.append([taskStep, task.data.name])

            if len(categories) > 0 and action is None:
                action = 'update'
            elif len(categories) == 0 and action is 'create':
                categories = 'No categories detected'

            if action:
                assetsToCreate.append([True, action, item._key, item._key, categories, None, False])

        return assetsToCreate

    @err_catcher(name=__name__)
    def aqShotsToPrism(self):    
        shotsToCreate = []

        steps = dict(self.origin.core.getConfig("globals", "pipeline_steps", dft={}, configPath=self.origin.core.prismIni))
        for shot in self.aqItems:
            item = self.aqItems[shot]['item']
            parent = self.aqItems[shot]['parent']
            tasks = self.aqItems[shot]['tasks']
            prismId = self.aqItems[shot]['prismId']

            prismShotPath = os.path.join(self.core.getShotPath(), prismId)
            action = None
            if not os.path.exists(prismShotPath):
                action = 'create'
            
            categories = []
            for task in tasks:
                taskSteps = (step for step, categories in steps.items() if task.data.name in categories)
                taskStep = next(taskSteps, None)
                if taskStep:
                    if action is None:
                        catPath = self.core.getEntityPath(shot=prismId, step=taskStep, category=task.data.name)
                        if not os.path.exists(catPath):
                            categories.append([taskStep, task.data.name])
                    elif action == 'create':
                        categories.append([taskStep, task.data.name])

            if len(categories) > 0 and action is None:
                action = 'update'
            elif len(categories) == 0 and action is 'create':
                categories = 'No categories detected'
            elif action is None:
                frameIn, frameOut = self.core.entities.getShotRange(prismId)
                newFrameRange = []
                if frameIn != item.data.frameIn: newFrameRange.append('frameIn : {frameIn}'.format(frameIn=item.data.frameIn))
                if frameOut != item.data.frameOut: newFrameRange.append('frameOut : {frameOut}'.format(frameOut=item.data.frameOut))
                if len(newFrameRange) > 0:
                    shotsToCreate.append([False, 'update frame range', item._key, item._key, categories, ' - '.join(newFrameRange), False])

            if action:
                shotsToCreate.append([True, action, item._key, item._key, categories, None, False])

        return shotsToCreate

    @err_catcher(name=__name__)
    def sync (self):
        selectedData = list(filter(lambda data: data[0] == True, self.model._data))
        if len(selectedData) > 0:
            confirmed = self.origin.messageConfirm(
                message="{itemNumber} {type}(s) will be sync in {target}. Do you want to continue ?".format(
                    itemNumber=len(selectedData),
                    type=self.ptype,
                    target=self.target
                )
            )
            if confirmed:
                location = None
                if self.ptype == 'Asset': location = self.origin.getAssetsLocation()
                elif self.ptype == 'Shot': location = self.origin.getShotsLocation()
                else:
                    self.origin.messageWarning(
                        message='No valid type is selected. Sync cancelled.',
                        title='Aquarium Studio sync'
                    )
                    return
                folders = [self.origin.aq.cast(group) for group in self.origin.aq.item(location).traverse(meshql='# -($Child)> $Group VIEW item')]
                
                for data in selectedData:
                    action = data[1]

                    itemName = data[2]
                    item = None
                    if self.getItem(data[2]): 
                        item = self.getItem(data[2])['item']
                        itemName = item.data.name
                    
                    parentName = data[3]
                    parent = None
                    if self.getItem(data[3]): 
                        parent = self.getItem(data[3])['parent']
                        parentName = parent.data.name
                    
                    categories = data[4]

                    if self.target == 'aquarium':
                        itemLocation = location
                        folderNames = (folder for folder in folders if folder.data.name == parentName)
                        folder = next(folderNames, None)
                        if folder:
                            itemLocation = folder._key
                        elif parentName is not None and len(parentName) > 0:
                            group = self.origin.aq.item(itemLocation).append(type='Group', data={'name': parentName}, apply_template=True)
                            if group:
                                folders.append(group.item)
                                itemLocation = group.item._key
                        if action == 'create':
                            try:
                                itemData = {
                                    'name': itemName
                                }
                                if (self.ptype == 'Shot'):
                                    frameIn, frameOut = self.core.entities.getShotRange(self.getItem(data[2])['prismId'])
                                    itemData['frameIn'] = frameIn
                                    itemData['frameOut'] = frameOut
                                
                                self.origin.aq.item(itemLocation).append(type=self.ptype, data=itemData, apply_template=True)
                                data[-1] = True
                            except Exception as e:
                                data[-1] = e
                        elif action == 'update':
                            if item:
                                try:
                                    for step, category in categories:
                                        item.append(type='Task', data={'name': category}, apply_template=True)
                                    data[-1] = True
                                except Exception as e:
                                    data[-1] = e
                            else:
                                data[-1] = "Can't find the item to append the new tasks"
                        elif action == 'update frame range':
                            if item:
                                try:
                                    frameIn, frameOut = self.core.entities.getShotRange(self.getItem(data[2])['prismId'])
                                    item.update_data(data={
                                        frameIn: frameIn,
                                        frameOut: frameOut
                                    })
                                    data[-1] = True
                                except Exception as e:
                                    data[-1] = e
                            else:
                                data[-1] = "Can't find the item to update frame range"
                        elif action == 'move':
                            try:
                                if item and parent and itemLocation:
                                    data[-1] = 'Move is not yet implemented.'
                                    # item.move(
                                    #     old_parent_key=parent._key,
                                    #     new_parent_key=itemLocation
                                    # )
                                else:
                                    data[-1] = "Can't find the item to move it under parent"
                            except Exception as e:
                                data[-1] = e

                    elif self.target == 'prism':
                        prismItemNames = (key for key in self.aqItems if key == self.getItem(data[2])['prismId'])
                        prismItemName = next(prismItemNames, None)

                        if action == 'create':
                            try:
                                if prismItemName:
                                    self.core.entities.createEntity(self.ptype.lower(), prismItemName)
                                    if item and self.ptype == 'Shot':
                                        self.core.entities.setShotRange(self, prismItemName, item.data.frameIn, item.data.frameOut)
                                
                                    for step, category in categories:
                                        if step and category:
                                            self.core.entities.createCategory(self.ptype.lower(), prismItemName, step, category)
                                    data[-1] = True
                                else:
                                    data[-1] = "Can't detect prism item name. Not synced"
                            except Exception as e:
                                data[-1] = e
                        elif action == 'update':
                            try:
                                if prismItemName:                               
                                    for step, category in categories:
                                        if step and category:
                                            self.core.entities.createCategory(self.ptype.lower(), prismItemName, step, category)
                                    data[-1] = True
                                else:
                                    data[-1] = "Can't detect prism item name. Not synced"
                            except Exception as e:
                                data[-1] = e
                        elif action == 'update frame range':
                            try:
                                if prismItemName and item:                               
                                    self.core.entities.setShotRange(self, prismItemName, item.data.frameIn, item.data.frameOut)
                                    data[-1] = True
                                else:
                                    data[-1] = "Can't detect prism item name. Not synced"
                            except Exception as e:
                                data[-1] = e
                            
                    else:
                        return
                
                if self.target == 'prism':
                    self.core.pb.refreshAHierarchy()
                
                self.b_sync.setEnabled(False)
                self.l_synced.setText('Sync done. Refresh before re-sync again.')
            else:
                self.origin.messageWarning(
                    message="Synchronisation cancelled",
                    title="Aquarium Studio sync"
                )
        else:
            self.origin.messageInfo(
                message="No {type} is selected. Nothing to synchronize.".format(
                    type=self.ptype.lower()
                ),
                title="Aquarium Studio sync"
            )
