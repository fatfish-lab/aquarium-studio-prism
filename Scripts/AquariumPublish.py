# -*- coding: utf-8 -*-

import os
import sys
import traceback
import subprocess
import datetime
import platform
# import imp
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
    import AquariumPublish_ui
else:
    import AquariumPublish_ui_ps2 as AquariumPublish_ui

logger = logging.getLogger(__name__)
# try:
#     import CreateItem
# except:
#     modPath = imp.find_module("CreateItem")[1]
#     if modPath.endswith(".pyc") and os.path.exists(modPath[:-1]):
#         os.remove(modPath)
#     import CreateItem

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


class aqPublish(QDialog, AquariumPublish_ui.Ui_dlg_aqPublish):
    def __init__(
        self, core, origin, ptype, shotName, task, version, sources, startFrame
    ):
        QDialog.__init__(self)
        self.setupUi(self)

        self.core = core
        self.core.parentWindow(self)
        self.origin = origin
        self.ptype = ptype
        self.shotName = shotName
        self.taskVersion = version
        self.fileSources = sources
        self.startFrame = startFrame
        self.itemList = {}
        self.aqItems = []

        connected = self.origin.connectToAquarium()

        if connected == False:
            return

        # self.core.appPlugin.aquariumPublish_startup(self)

        # for i in range(7):
        #     self.cb_playlist.addItem(
        #         "DAILIES_%s" % (datetime.date.today() + datetime.timedelta(days=i))
        #     )

        if ptype == "Asset":
            self.rb_asset.setChecked(True)
        else:
            self.rb_shot.setChecked(True)

        self.updateItems()
        self.navigateToCurrent(shotName, task)

        # if self.core.appPlugin.pluginName == "Houdini" and hasattr(
        #     self.core.appPlugin, "fixStyleSheet"
        # ):
        #     self.core.appPlugin.fixStyleSheet(self.gb_playlist)

        self.connectEvents()

    @err_catcher(name=__name__)
    def connectEvents(self):
        self.rb_asset.pressed.connect(self.updateItems)
        self.rb_shot.pressed.connect(self.updateItems)
        # self.b_addTask.clicked.connect(self.createTask)
        self.b_addTask.setVisible(False)
        self.cb_shot.activated.connect(self.updateTasks)
        self.b_aqPublish.clicked.connect(self.publish)

    @err_catcher(name=__name__)
    def updateItems(self):
        if self.rb_asset.isChecked():
            self.aqItems = self.origin.getAqProjectAssets()
        elif self.rb_shot.isChecked():
            self.aqItems = self.origin.getAqProjectShots()

        self.cb_shot.clear()
        self.itemList = {}
        if (len(self.aqItems) == 0):
            self.cb_shot.addItem("No {itemType} found in the project".format(
                itemType=self.ptype
            ), None)
        for a in self.aqItems:
            item = self.origin.aq.cast(a['item'])
            parent = self.origin.aq.cast(a['parent'])
            tasks = [self.origin.aq.cast(task) for task in a['tasks']]

            if (self.ptype == 'Asset'):
                prismItemName = "{itemName}".format(
                    itemName=item.data.name
                )
            else:
                prismItemName = "{parentName}{separator}{itemName}".format(
                    parentName=parent.data.name,
                    separator=self.core.sequenceSeparator,
                    itemName=item.data.name
                )

            self.cb_shot.addItem(prismItemName, item._key)
            self.itemList[item._key] = {
                "item": item,
                "parent": parent,
                "tasks": tasks,
                "prismItemName": prismItemName
            }

        self.updateTasks()

    @err_catcher(name=__name__)
    def updateTasks(self, idx=None):
        self.cb_task.clear()
        itemKey = self.cb_shot.currentData()
        if itemKey == "" or itemKey is None:
            self.cb_task.addItem("No {itemType} is selected in the list".format(
                itemType=self.ptype
            ), None)
            return

        if (self.itemList[itemKey]):
            publishItem = self.itemList[itemKey]
            if (publishItem is None):
                return
            self.aqTasks = publishItem['tasks']

            taskPaths = [""]
            if self.ptype == "Asset":
                assetPath = self.core.getAssetPath()
                taskPaths.append(
                    os.path.join(
                        assetPath,
                        self.itemList[itemKey]['parent'].data.name,
                        self.itemList[itemKey]['item'].data.name,
                        "Rendering",
                        "3dRender",
                    )
                )
                taskPaths.append(
                    os.path.join(
                        assetPath,
                        self.itemList[itemKey]['parent'].data.name,
                        self.itemList[itemKey]['item'].data.name,
                        "Rendering",
                        "2dRender",
                    )
                )
                taskPaths.append(
                    os.path.join(
                        assetPath,
                        self.itemList[itemKey]['parent'].data.name,
                        self.itemList[itemKey]['item'].data.name,
                        "Rendering",
                        "external",
                    )
                )
                taskPaths.append(
                    os.path.join(
                        assetPath,
                        self.itemList[itemKey]['parent'].data.name,
                        self.itemList[itemKey]['item'].data.name,
                        "Playblasts",
                    )
                )
            elif self.ptype == "Shot":
                shotPath = self.core.getShotPath()
                taskPaths.append(
                    os.path.join(
                        shotPath,
                        self.itemList[itemKey]['prismItemName'],
                        "Rendering",
                        "3dRender"
                    )
                )
                taskPaths.append(
                    os.path.join(
                        shotPath,
                        self.itemList[itemKey]['prismItemName'],
                        "Rendering",
                        "2dRender"
                    )
                )
                taskPaths.append(
                    os.path.join(
                        shotPath,
                        self.itemList[itemKey]['prismItemName'],
                        "Rendering",
                        "external"
                    )
                )
                taskPaths.append(
                    os.path.join(shotPath,
                    self.itemList[itemKey]['prismItemName'],
                    "Playblasts")
                )

            taskNames = []
            for i in taskPaths:
                if os.path.exists(i):
                    taskNames += os.listdir(i)

            taskNames = list(set(taskNames))
            
            if (len(self.aqTasks) == 0):
                self.cb_task.addItem("The {itemType} {itemName} has no tasks".format(
                    itemType=self.itemList[itemKey]['item'].type,
                    itemName=self.itemList[itemKey]['item'].data.name
                ), None)

            for task in self.aqTasks:
                self.cb_task.addItem(task.data.name, task._key)
            
            if len(self.aqTasks) > 0 and len(taskNames) > 0:
                self.cb_task.insertSeparator(len(self.aqTasks))
            self.cb_task.addItems(taskNames)
        else:
            self.origin.messageInfo(
                message = "Can't find the %s in the list." % self.ptype,
                title = "Aquarium studio publish")
            return

    # 	@err_catcher(name=__name__)
    # 	def createTask(self):
    # 		self.newItem = CreateItem.CreateItem(core=self.core)
    #
    # 		self.newItem.setModal(True)
    # 		self.core.parentWindow(self.newItem)
    # 		self.newItem.e_item.setFocus()
    # 		self.newItem.setWindowTitle("Create " + self.ptype)
    # 		self.newItem.l_item.setText(self.ptype + " Name:")
    # 		res = self.newItem.exec_()
    #
    # 		if res == 1:
    # 			data = { 'project': {'type': 'Project','id': self.sgPrjId},
    # 				'content': self.newItem.e_item.text(),
    # 				'sg_status_list': 'ip',
    # 				'entity' : {'type': self.ptype, 'id': curShotId}
    # 			}
    # 			result = self.sg.create('Task', data)

    @err_catcher(name=__name__)
    def navigateToCurrent(self, shotName, task):
        idx = self.cb_shot.findText(shotName)
        if idx != -1:
            self.cb_shot.setCurrentIndex(idx)

        self.updateTasks()

        idx = self.cb_task.findText(task)
        if idx != -1:
            self.cb_task.setCurrentIndex(idx)

    @err_catcher(name=__name__)
    def enterEvent(self, event):
        QApplication.restoreOverrideCursor()

    @err_catcher(name=__name__)
    def publish(self):
        if self.cb_shot.currentData() == "" or self.cb_shot.currentData() is None:
            self.origin.messageWarning (
                message = "No %s selected in the list. Publish canceled" % self.ptype,
                title = "Aquarium studio publish"
            )
            return

        if self.cb_task.currentData() == "" or self.cb_task.currentData() is None:
            self.origin.messageWarning (
                message = "No task is selected in the list. Publish canceled.",
                title = "Aquarium studio publish"
            )
            return
        
        publishButtonText = self.b_aqPublish.text()
        self.enableWidgets(enable = False)

        self.thread = QThread()
        self.worker = UploadWorker()
        self.worker.origin = self
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.encode)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.encoding.connect(
            lambda: self.b_aqPublish.setText("Encoding...")
        )
        self.worker.started.connect(
            lambda: self.b_aqPublish.setText("Publishing...")
        )
        self.worker.uploading.connect(
            lambda: self.b_aqPublish.setText("Uploading...")
        )
        self.worker.uploaded.connect(
            lambda: self.b_aqPublish.setText("Publish completed !")
        )
        self.worker.finished.connect(
            lambda published: self.endPublish(published)
        )
        self.worker.error.connect(
            lambda: self.errorOnPublish(textButton = publishButtonText)
        )

        self.thread.start()

        # if len(curTaskId) > 0:
        #     curTaskId = curTaskId[0]
        # else:
        #     fields = ["code", "short_name", "entity_type"]
        #     # 	sgSteps = { x['short_name'] : x for x in self.sg.find("Step", [], fields) if x['entity_type'] is not None}
        #     data = {
        #         "project": {"type": "Project", "id": self.sgPrjId},
        #         "content": self.cb_task.currentText(),
        #         "sg_status_list": "ip",
        #         "entity": {"type": self.ptype, "id": curShotId}
        #         # 	'step' : {'type': 'Step', 'id': sgSteps["ren"]['id'] }
        #     }
        #     try:
        #         result = self.sg.create("Task", data)
        #     except Exception as e:
        #         if "Entity of type Task cannot be created by this user." in str(e):
        #             QMessageBox.warning(
        #                 self.core.messageParent,
        #                 "Warning",
        #                 "This aquarium account cannot create tasks.\n\nPublish canceled.",
        #             )
        #             return
        #         else:
        #             raise e
        #     curTaskId = result["id"]



            # sgSite = self.core.getConfig(
            #     "aquarium", "site", configPath=self.core.prismIni
            # )
            # sgSite += "/detail/Version/" + str(createdVersion["id"])

            # versionInfoPath = os.path.join(
            #     os.path.dirname(source[0]), "versionInfo.yml"
            # )
            # if not os.path.exists(versionInfoPath):
            #     versionInfoPath = os.path.join(
            #         os.path.dirname(os.path.dirname(source[0])), "versionInfo.yml"
            #     )

            # self.core.setConfig("information", "aquarium-url", sgSite, configPath=versionInfoPath)

    def errorOnPublish (self, textButton):
        self.b_aqPublish.setText(textButton)
        self.enableWidgets(enable = True)

    def enableWidgets (self, enable= True):
        self.b_aqPublish.setEnabled(enable)
        self.rb_asset.setEnabled(enable)
        self.rb_shot.setEnabled(enable)
        self.cb_shot.setEnabled(enable)
        self.cb_task.setEnabled(enable)
        self.te_description.setEnabled(enable)

    def endPublish (self, published):
        msgStr = "Successfully published:"
        for i in published:
            msgStr += "\n%s" % i

        msg = QMessageBox(
            QMessageBox.Information,
            "Aquarium studio publish",
            msgStr,
            parent=self.core.messageParent,
        )
        # msg.addButton("Open version in Aquarium", QMessageBox.YesRole)
        msg.addButton("Close", QMessageBox.YesRole)
        msg.setFocus()
        action = msg.exec_()

        # if action == 0:
        #     import webbrowser

        #     webbrowser.open(sgSite)

        self.enableWidgets(enable = True)
        self.accept()

class UploadWorker(QObject):
    encoding = Signal()
    started = Signal()
    uploading = Signal()
    uploaded = Signal()
    finished = Signal(list)
    error = Signal(str)

    origin = None
    published = []

    def encode(self):
        self.started.emit()
        self.encoding.emit()
        curShotId = self.origin.cb_shot.currentData()
        curTaskId = self.origin.cb_task.currentData()
        for source in self.origin.fileSources:
            versionName = "%s_%s_%s" % (
                self.origin.cb_shot.currentText(),
                self.origin.cb_task.currentText(),
                self.origin.taskVersion,
            )
            if len(self.origin.fileSources) > 1:
                versionName += "_%s" % os.path.splitext(os.path.basename(source[0]))[0]
            baseName, extension = os.path.splitext(source[0])

            videoInput = extension in [".mp4", ".mov"]
            if videoInput:
                sequenceName = source[0]
            else:
                try:
                    int(baseName[-4:])
                    sequenceName = baseName[:-4] + "####" + extension
                except:
                    sequenceName = source[0]

            tmpFiles = []

            ffmpegIsInstalled = False
            if platform.system() == "Windows":
                ffmpegPath = os.path.join(
                    self.origin.core.prismLibs, "Tools", "FFmpeg", "bin", "ffmpeg.exe"
                )
                if os.path.exists(ffmpegPath):
                    ffmpegIsInstalled = True
            elif platform.system() == "Linux":
                ffmpegPath = "ffmpeg"
                try:
                    subprocess.Popen([ffmpegPath], shell = True)
                    ffmpegIsInstalled = True
                except:
                    pass
            elif platform.system() == "Darwin":
                ffmpegPath = os.path.join(self.origin.core.prismLibs, "Tools", "ffmpeg")
                if os.path.exists(ffmpegPath):
                    ffmpegIsInstalled = True

            imgPath = source[0]
            if extension in [".exr", ".mp4", ".mov"]:
                inputpath = source[0].replace("\\", "/")
                outputpath = os.path.splitext(inputpath)[0] + ".jpg"
                if ffmpegIsInstalled:
                    if videoInput:
                        nProc = subprocess.Popen(
                            [
                                ffmpegPath,
                                "-apply_trc",
                                "iec61966_2_1",
                                "-i",
                                inputpath,
                                "-pix_fmt",
                                "yuv420p",
                                "-vf",
                                "select=gte(n\,%s)" % source[1],
                                "-frames",
                                "1",
                                outputpath,
                                "-y",
                            ],
                            shell = True
                        )
                    else:
                        nProc = subprocess.Popen(
                            [
                                ffmpegPath,
                                "-apply_trc",
                                "iec61966_2_1",
                                "-i",
                                inputpath,
                                "-pix_fmt",
                                "yuv420p",
                                outputpath,
                                "-y",
                            ],
                            shell = True
                        )

                    result = nProc.communicate()
                    imgPath = outputpath
                    tmpFiles.append(imgPath)


            # data = {
            #     "project": {"type": "Project", "id": self.origin.sgPrjId},
            #     "code": versionName,
            #     "description": self.origin.te_description.toPlainText(),
            #     "sg_path_to_frames": sequenceName,
            #     "sg_status_list": "rev",
            #     "entity": {"type": self.origin.ptype, "id": curShotId},
            #     "sg_task": {"type": "Task", "id": curTaskId},
            # }

            # if self.origin.sgUserId is not None:
            #     data["user"] = {"type": "HumanUser", "id": self.origin.sgUserId}

            # if os.path.exists(imgPath):
            #     data["image"] = imgPath

            # try:
            #     createdVersion = self.origin.sg.create("Version", data)
            # except Exception as e:
            #     exc_type, exc_obj, exc_tb = sys.exc_info()
            #     erStr = "ERROR:\n%s" % traceback.format_exc()
            #     QMessageBox.warning(self.origin.core.messageParent, "Aquarium studio publish", erStr)
            #     return

            if ffmpegIsInstalled:
                proxyPath = ""
                inputpath = source[0].replace("\\", "/")
                mp4File = (
                    os.path.join(
                        os.path.dirname(inputpath) + "(mp4)",
                        os.path.basename(inputpath),
                    )[:-9]
                    + ".mp4"
                )
                pwidth = 0
                pheight = 0
                if os.path.exists(mp4File):
                    proxyPath = mp4File
                else:
                    isSequence = False

                    if not videoInput:
                        try:
                            x = int(inputpath[-8:-4])
                            isSequence = True
                        except:
                            pass

                    if os.path.splitext(inputpath)[1] in [
                        ".jpg",
                        ".jpeg",
                        ".JPG",
                        ".png",
                        ".tif",
                        ".tiff",
                    ]:
                        size = QImage(inputpath).size()
                        pwidth = size.width()
                        pheight = size.height()
                    elif os.path.splitext(inputpath)[1] in [".exr"]:
                        oiio = self.origin.core.media.getOIIO()

                        if oiio:
                            imgSpecs = oiio.ImageBuf(str(inputpath)).spec()
                            pwidth = imgSpecs.full_width
                            pheight = imgSpecs.full_height

                    elif os.path.splitext(inputpath)[1] in [".mp4", ".mov"]:
                        try:
                            import imageio
                        except:
                            pass
                        vidReader = imageio.get_reader(inputpath, "ffmpeg")

                        pwidth = vidReader._meta["size"][0]
                        pheight = vidReader._meta["size"][1]

                    # if int(pwidth) % 2 == 1 or int(pheight) % 2 == 1:
                    #     QMessageBox.warning(
                    #         self.origin.core.messageParent,
                    #         "Media conversion",
                    #         "Media with odd resolution can't be converted to mp4. No proxy video could be generated.",
                    #     )
                    # else:
                        if isSequence or videoInput:
                            if isSequence:
                                inputpath = os.path.splitext(inputpath)[0][:-(self.origin.core.framePadding)] + "%04d".replace("4", str(self.origin.core.framePadding)) + os.path.splitext(inputpath)[1]
                                outputpath = os.path.splitext(inputpath)[0][:-(self.origin.core.framePadding+1)] + ".mp4"
                                nProc = subprocess.Popen(
                                    [
                                        ffmpegPath,
                                        "-start_number",
                                        str(self.origin.startFrame),
                                        "-framerate",
                                        "24",
                                        "-apply_trc",
                                        "iec61966_2_1",
                                        "-i",
                                        inputpath,
                                        "-pix_fmt",
                                        "yuv420p",
                                        "-start_number",
                                        str(self.origin.startFrame),
                                        outputpath,
                                        "-y",
                                    ],
                                shell = True)
                            else:
                                outputpath = os.path.splitext(inputpath)[0][:-(self.origin.core.framePadding+1)] + "(proxy).mp4"
                                nProc = subprocess.Popen(
                                    [
                                        ffmpegPath,
                                        "-apply_trc",
                                        "iec61966_2_1",
                                        "-i",
                                        inputpath,
                                        "-pix_fmt",
                                        "yuv420p",
                                        "-start_number",
                                        str(self.origin.startFrame),
                                        outputpath,
                                        "-y",
                                    ],
                                shell = True)
                            
                            mp4Result = nProc.communicate()
                            proxyPath = outputpath
                            tmpFiles.append(proxyPath)

                logger.debug('Publish data %s', {
                    "itemKey":curShotId,
                    "itemName":self.origin.itemList[curShotId]['item'].data.name,
                    "description": self.origin.te_description.toPlainText(),
                    "version": versionName,
                    "taskKey": curTaskId,
                    "taskName": self.origin.cb_task.currentText(),
                    "image": imgPath,
                    "proxy": proxyPath
                })

                if (proxyPath == '' and imgPath != ''):
                    proxyPath = imgPath
                
                if (
                    proxyPath != ""
                    and os.path.exists(proxyPath)
                    and os.stat(proxyPath).st_size != 0
                ):
                    try:
                        self.upload(
                            item = self.origin.itemList[curShotId]['item'],
                            taskName = self.origin.cb_task.currentText(),
                            filePath = proxyPath
                        )
                        self.uploaded.emit()

                    except Exception as e:
                        self.error.emit()
                        self.origin.origin.messageWarning(
                            message = "Uploading proxy video failed:\n\n%s" % str(e),
                            title = 'Aquarium Studio publish'
                        )

            # if self.origin.gb_playlist.isChecked():
            #     fields = ["id", "versions"]
            #     filters = [
            #         ["project", "is", {"type": "Project", "id": self.origin.sgPrjId}],
            #         ["code", "is", self.origin.cb_playlist.currentText()],
            #     ]
            #     sgPlaylists = self.origin.sg.find("Playlist", filters, fields)

            #     if len(sgPlaylists) > 0:
            #         vers = sgPlaylists[0]["versions"]
            #         vers.append(createdVersion)
            #         data = {"versions": vers}
            #         self.origin.sg.update("Playlist", sgPlaylists[0]["id"], data)
            #     else:
            #         data = {
            #             "project": {"type": "Project", "id": self.origin.sgPrjId},
            #             "code": self.origin.cb_playlist.currentText(),
            #             "description": "dailies_01",
            #             "sg_status": "opn",
            #             "versions": [createdVersion],
            #         }

            #         try:
            #             createdPlaylist = self.origin.sg.create("Playlist", data)
            #         except:
            #             data.pop("sg_status")
            #             createdPlaylist = self.origin.sg.create("Playlist", data)

            for i in tmpFiles:
                try:
                    os.remove(i)
                except:
                    pass

            self.published.append(versionName)
            self.finished.emit(self.published)

    def upload(self, item, taskName, filePath):
        self.uploading.emit()
        item.upload_on_task(task_name=taskName, path=filePath)