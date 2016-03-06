# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_design.ui'
#
# Created: Sun Mar  6 23:32:09 2016
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_main_window(object):
    def setupUi(self, main_window):
        main_window.setObjectName("main_window")
        main_window.resize(793, 600)
        self.central_widget = QtWidgets.QWidget(main_window)
        self.central_widget.setObjectName("central_widget")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.central_widget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(-1, 0, 791, 551))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontal_layout_main = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontal_layout_main.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout_main.setObjectName("horizontal_layout_main")
        self.verti_layout_A = QtWidgets.QVBoxLayout()
        self.verti_layout_A.setObjectName("verti_layout_A")
        self.export_layout = QtWidgets.QVBoxLayout()
        self.export_layout.setObjectName("export_layout")
        self.export_label = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.export_label.setFrameShape(QtWidgets.QFrame.Box)
        self.export_label.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.export_label.setAlignment(QtCore.Qt.AlignCenter)
        self.export_label.setObjectName("export_label")
        self.export_layout.addWidget(self.export_label)
        self.export_SQL_code = QtWidgets.QTextEdit(self.horizontalLayoutWidget)
        self.export_SQL_code.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.export_SQL_code.setObjectName("export_SQL_code")
        self.export_layout.addWidget(self.export_SQL_code)
        self.verti_layout_A.addLayout(self.export_layout)
        self.horizontal_layout_main.addLayout(self.verti_layout_A)
        self.vert_layout_B = QtWidgets.QVBoxLayout()
        self.vert_layout_B.setObjectName("vert_layout_B")
        self.database_info_label = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.database_info_label.setFrameShape(QtWidgets.QFrame.Box)
        self.database_info_label.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.database_info_label.setAlignment(QtCore.Qt.AlignCenter)
        self.database_info_label.setObjectName("database_info_label")
        self.vert_layout_B.addWidget(self.database_info_label)
        self.database_info_tree = QtWidgets.QTreeView(self.horizontalLayoutWidget)
        self.database_info_tree.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.database_info_tree.setObjectName("database_info_tree")
        self.vert_layout_B.addWidget(self.database_info_tree)
        self.database_layout = QtWidgets.QVBoxLayout()
        self.database_layout.setObjectName("database_layout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.database_layout.addItem(spacerItem)
        self.normalize_button = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.normalize_button.setObjectName("normalize_button")
        self.database_layout.addWidget(self.normalize_button)
        self.vert_layout_B.addLayout(self.database_layout)
        self.horizontal_layout_main.addLayout(self.vert_layout_B)
        main_window.setCentralWidget(self.central_widget)
        self.menu_bar = QtWidgets.QMenuBar(main_window)
        self.menu_bar.setGeometry(QtCore.QRect(0, 0, 793, 25))
        self.menu_bar.setObjectName("menu_bar")
        self.menu_file = QtWidgets.QMenu(self.menu_bar)
        self.menu_file.setObjectName("menu_file")
        main_window.setMenuBar(self.menu_bar)
        self.status_bar = QtWidgets.QStatusBar(main_window)
        self.status_bar.setObjectName("status_bar")
        main_window.setStatusBar(self.status_bar)
        self.action_import = QtWidgets.QAction(main_window)
        self.action_import.setObjectName("action_import")
        self.action_export = QtWidgets.QAction(main_window)
        self.action_export.setObjectName("action_export")
        self.action_quit = QtWidgets.QAction(main_window)
        self.action_quit.setObjectName("action_quit")
        self.menu_file.addAction(self.action_import)
        self.menu_file.addAction(self.action_export)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_quit)
        self.menu_bar.addAction(self.menu_file.menuAction())

        self.retranslateUi(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "SQL Normalizer"))
        self.export_label.setToolTip(_translate("main_window", "This holds the SQL code that will be exported out on completion."))
        self.export_label.setText(_translate("main_window", "SQL To Export"))
        self.database_info_label.setToolTip(_translate("main_window", "This holds the tables currently in this database. Use this to add new columns and functional dependencies."))
        self.database_info_label.setText(_translate("main_window", "Database Information"))
        self.normalize_button.setText(_translate("main_window", "Normalize"))
        self.menu_file.setTitle(_translate("main_window", "File"))
        self.action_import.setText(_translate("main_window", "Import"))
        self.action_import.setShortcut(_translate("main_window", "Ctrl+I"))
        self.action_export.setText(_translate("main_window", "Export"))
        self.action_export.setShortcut(_translate("main_window", "Ctrl+E"))
        self.action_quit.setText(_translate("main_window", "Quit"))
        self.action_quit.setShortcut(_translate("main_window", "Ctrl+Q"))

