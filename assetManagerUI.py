import logging
import os

from Qt import QtWidgets, QtCore, QtGui
from Qt import _loadUi
from guiUtil import prompt
from guiUtil.template import getTextDialog

import asset


MODULE_PATH = os.path.dirname(__file__)
UI_FILE = os.path.join(MODULE_PATH, 'assetManager.ui')

ICON_SIZE = 220


class AssetManagerUI(QtWidgets.QMainWindow):

    def __init__(self, directory=asset.ASSET_PATH):
        super(AssetManagerUI, self).__init__()
        _loadUi(UI_FILE, self)

        self._dir = directory
        self._props = None

        self.force_refresh()

        # set gui properties
        self.ui_info_widget.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))

        # connect signals and slots
        self.ui_list_widget.itemClicked.connect(self.display_detail)
        self.ui_open_btn.clicked.connect(self.open)
        self.ui_import_btn.clicked.connect(self.load)
        self.ui_delete_btn.clicked.connect(self.delete_entry)
        self.ui_create_scene_action.triggered.connect(self.create_entry)
        self.ui_set_dir_action.triggered.connect(self.set_dir)

    def set_dir(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            "Set base directory",
            MODULE_PATH
        )

        self._dir = directory
        self.force_refresh()

    def get_props(self):
        self._props = asset.Asset.get_from_dir(self._dir)

    def populate(self):
        self.ui_list_widget.clear()

        for prop in self._props:
            item = QtWidgets.QListWidgetItem(prop.name)
            item.setData(QtCore.Qt.UserRole, prop)
            self.ui_list_widget.addItem(item)

    def force_refresh(self):
        self.get_props()
        self.populate()
        self.ui_info_widget.clear()

    def display_detail(self):
        self.ui_info_widget.clear()

        item = self.ui_list_widget.currentItem()
        prop = item.data(QtCore.Qt.UserRole)

        if prop.thumbnail:
            thumbnail = QtWidgets.QListWidgetItem()
            thumbnail.setIcon(QtGui.QIcon(prop.thumbnail))
            self.ui_info_widget.addItem(thumbnail)

        if prop.name:
            name = QtWidgets.QListWidgetItem('Name: {}'.format(prop.name))
            self.ui_info_widget.addItem(name)

        if prop.size:
            size = QtWidgets.QListWidgetItem('Size: {}'.format(prop.size))
            self.ui_info_widget.addItem(size)

        if prop.mtime:
            last_edit = QtWidgets.QListWidgetItem('Last Edit: {}'.format(prop.mtime))
            self.ui_info_widget.addItem(last_edit)

    def get_current_item(self):
        item = self.ui_list_widget.currentItem()
        if not item:
            raise ValueError("No item selected for action")
        return item.data(QtCore.Qt.UserRole)

    def open(self, item=None):
        if not item:
            item = self.get_current_item()
        item.fopen()

    def load(self, item=None):
        if not item:
            item = self.get_current_item()
        item.fimport()

    def create_entry(self):
        dialog = getTextDialog.GetTextDialog()
        if dialog.exec_():
            name = dialog.get_text()
            item = asset.Asset.fsave(os.path.join(self._dir, name))

        self.force_refresh()
        prompt.message_log("Creation Success", ltype='info')

    def delete_entry(self):
        item = self.get_current_item()

        user_choice = prompt.message_yesno(
            "Delete the entry: {}?".format(item.name))
        if user_choice == QtWidgets.QMessageBox.No:
            return

        # delete the prop entry
        try:
            item.fdelete()
        except Exception as e:
            logging.error("deletion interrupted: %s", e)

        self.force_refresh()


def show():
    global window
    window = AssetManagerUI()
    window.show()
    return window


if __name__ == "__main__":
    window = show()
