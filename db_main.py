import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QMenu,
    QInputDialog,
    QMessageBox
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from db_ui import Ui_main_window
from db_normalizer import Table, Database


class UIHandlers(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()

        self.database = Database()
        self.ui = Ui_main_window()
        self.ui.setupUi(self)
        import_button = self.ui.action_import
        import_button.triggered.connect(self.get_file_for_import)
        save_button = self.ui.action_save
        save_button.triggered.connect(self.save_file)
        saveas_button = self.ui.action_save_as
        saveas_button.triggered.connect(self.save_file_as)
        normalize_button = self.ui.normalize_button
        normalize_button.clicked.connect(self.normalize_database)
        self.ui.database_info_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.database_info_tree.customContextMenuRequested.connect(
            self.database_info_tree_menu
        )
        self.model = QStandardItemModel()
        self.ui.database_info_tree.setModel(self.model)
        self.filename_without_path = ""
        self.show()

    def generate_column_data(self, columns):
        column_data = []
        for column in columns:
            this_column_tuple = (column["name"],)
            this_column_data = [(column["type"], [])]
            for flag in column["flags"]:
                this_column_data.append((flag, []))
            this_column_tuple += (this_column_data,)
            column_data.append(this_column_tuple)
        return column_data

    def generate_foreign_key_data(self, fks):
        fk_data = []
        for fk in fks:
            this_fk_tuple = (fk["name"],)
            this_fk_data = []
            this_fk_table = ("Table Reference",)
            this_fk_table_data = [(fk["table"],[])]
            this_fk_table += (this_fk_table_data,)
            this_fk_data.append(this_fk_table)
            this_fk_column = ("Column Reference",)
            this_fk_column_data = [(fk["column"],[])]
            this_fk_column += (this_fk_column_data,)
            this_fk_data.append(this_fk_column)
            this_fk_tuple += (this_fk_data,)
            fk_data.append(this_fk_tuple)
        return fk_data

    def generate_primary_key_data(self, pks):
        pk_data = []
        for pk in pks:
            this_pk_tuple = (pk, [])
            pk_data.append(this_pk_tuple)
        return pk_data

    def generate_functional_dependency_data(self, fds):
        fd_data = []
        for child, parent in fds.items():
            this_fd_tuple = (child,)
            this_fd_tuple += ([(parent[0],[])],)
            fd_data.append(this_fd_tuple)
        return fd_data

    def update_tree_view(self):
        tree_data = self.generate_tree_data
        self.model.clear()
        self.set_model_header_name()
        self.add_items(self.model, self.generate_tree_data())

    def generate_tree_data(self):
        tables = self.database.tables
        tree_data = []
        for table in tables:
            tuple = (table.table_name,)
            table_data = [
                ("Columns",),
                ("Primary Keys",),
                ("Foreign Keys",),
                ("Functional Dependencies",)
            ]
            column_data = self.generate_column_data(table.columns)
            pk_data = self.generate_primary_key_data(
                table.primary_keys
            )
            fk_data = self.generate_foreign_key_data(
                table.foreign_keys
            )
            fd_data = self.generate_functional_dependency_data(
                table.functional_dependencies
            )
            table_data[0] += (column_data,)
            table_data[1] += (pk_data,)
            table_data[2] += (fk_data,)
            table_data[3] += (fd_data,)
            tuple += (table_data,)
            tree_data.append(tuple)
        return tree_data

    def add_items(self, parent, elements):
        for text, children in elements:
            item = QStandardItem(text)
            parent.appendRow(item)
            if children:
                self.add_items(item, children)

    def set_model_header_name(self):
        if(self.filename_without_path):
            self.model.setHorizontalHeaderLabels([self.filename_without_path])
        else:
            self.model.setHorizontalHeaderLabels(["New File"])

    def update_sql_code(self, text):
        self.ui.export_SQL_code.setText(text)

    def save_file(self):
        save_file = open(self.filename, 'w')
        save_file.truncate()
        save_file.write(self.database.export_database())

    def save_file_as(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            'Save file',
            '~/',
            self.tr("SQL Files (*.sql)")
        )
        new_file = open(filename, 'w')
        new_file.write(self.database.export_database())
        new_file.close()

    def get_file_for_import(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            'Choose file',
            '~/',
            self.tr("SQL Files (*.sql)")
        )
        self.database = Database()
        self.database.import_file(filename)
        self.update_sql_code(self.database.export_database())
        self.filename = filename
        self.filename_without_path = filename.split("/")[-1]
        self.update_tree_view()
        self.set_model_header_name()
        return filename

    def normalize_database(self):
        self.database.handle_functional_dependencies()
        self.update_sql_code(self.database.export_database())
        self.update_tree_view()

    def add_column(self, table):
        def add_column_closure():
            this_table = self.database.get_table(table)
            name, ok_column = QInputDialog.getText(
                self,
                'Add Column',
                'Column Name',
            )
            if(ok_column):
                datatype, ok_data = QInputDialog.getText(
                    self,
                    'Add Column',
                    'Column Data Type',
                )
            if(ok_data):
                ok_flag = True
                flags = []
                flag_names = [
                    "NOT NULL",
                    "UNIQUE INDEX",
                    "BINARY",
                    "UNSIGNED",
                    "ZEROFILL",
                    "AUTO_INCREMENT",
                ]
                while(ok_flag):
                    flag, ok_flag = QInputDialog.getItem(
                        self,
                        'Add Column',
                        'Flag',
                        flag_names,
                        0,
                        False
                    )
                    if(flag and ok_flag):
                        flag_names = list(set(flag_names) - set([flag]))
                        flags.append(flag)
                if(flags):
                    this_table.add_column(
                        name,
                        datatype,
                        flags
                    )
                self.update_tree_view()
                self.update_sql_code(self.database.export_database())
        return add_column_closure

    def create_table(self):
        def create_table_closure():
            table_name, ok_table = QInputDialog.getText(
                self,
                'Create New Table',
                'New Table Name'
            )
            if(ok_table):
                self.database.create_table(table_name)
                self.update_tree_view()
                self.update_sql_code(self.database.export_database())
        return create_table_closure

    def add_primary_key(self, table):
        def add_primary_key_closure():
            this_table = self.database.get_table(table)
            columns = this_table.columns
            primary_keys = this_table.primary_keys
            column_names = list(
                map(
                    lambda column: column["name"],
                    columns
                )
            )
            column_names = list(set(column_names) - set(primary_keys))
            primary_key, ok_primary_key = QInputDialog.getItem(
                self,
                'Add Primary Key',
                'Primary Key',
                column_names,
                0,
                False
            )
            if(ok_primary_key):
                this_table.add_primary_key(primary_key)
                self.update_tree_view()
                self.update_sql_code(self.database.export_database())
        return add_primary_key_closure


    def add_functional_dependency(self, table):
        def add_functional_dependency_closure():
            this_table = self.database.get_table(table)
            columns = this_table.columns
            column_names = list(
                map(
                    lambda column: column["name"],
                    columns
                )
            )
            child, ok_child = QInputDialog.getItem(
                self,
                'Add Functional Dependency',
                'Child',
                column_names,
                0,
                False
            )
            if(child):
                column_names = list(set(column_names) - set([child]))
            if(ok_child):
                ok_parent = True
                parents = []
                while(ok_parent):
                    parent, ok_parent = QInputDialog.getItem(
                        self,
                        'Add Functional Dependency',
                        'Parent',
                        column_names,
                        0,
                        False
                    )
                    if(parent and ok_parent):
                        column_names = list(set(column_names) - set([parent]))
                        parents.append(parent)
                if(parents):
                    this_table.add_functional_dependency(
                        child,
                        parents
                    )
                    self.update_tree_view()
        return add_functional_dependency_closure

    def delete_column(self, table, column):
        def delete_column_closure():
            this_table = self.database.get_table(table)
            message = 'Are you sure you want to delete '
            message += column + ' from ' + table + '?'
            ok_delete = QMessageBox.question(
                self,
                'Delete Column',
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if(ok_delete):
                this_table.remove_column(column)
                self.update_tree_view()
                self.update_sql_code(self.database.export_database())
        return delete_column_closure

    def delete_primary_key(self, table, primary_key):
        def delete_primary_key_closure():
            this_table = self.database.get_table(table)
            message = 'Are you sure you want to delete the primary key for '
            message += primary_key + ' from ' + table +'?'
            ok_delete = QMessageBox.question(
                self,
                'Delete Primary Key',
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if(ok_delete):
                this_table.remove_primary_key(primary_key)
                self.update_tree_view()
                self.update_sql_code(self.database.export_database())
        return delete_primary_key_closure


    def delete_foreign_key(self, table, foreign_key):
        def delete_foreign_key_closure():
            this_table = self.database.get_table(table)
            message = 'Are you sure you want to delete the foreign key for '
            message += foreign_key + ' from ' + table +'?'
            ok_delete = QMessageBox.question(
                self,
                'Delete Foreign Key',
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if(ok_delete):
                this_table.remove_foreign_key(foreign_key)
                self.update_tree_view()
                self.update_sql_code(self.database.export_database())
        return delete_foreign_key_closure

    def delete_functional_dependency(self, table, functional_dependency):
        def delete_functional_dependency_closure():
            this_table = self.database.get_table(table)
            message = 'Are you sure you want to '
            message += 'delete the functional dependency for '
            message += functional_dependency + ' from ' + table +'?'
            ok_delete = QMessageBox.question(
                self,
                'Delete Functional Dependency',
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if(ok_delete):
                this_table.remove_functional_dependency(functional_dependency)
                self.update_tree_view()
                self.update_sql_code(self.database.export_database())
        return delete_functional_dependency_closure


    def get_node_level(self, index):
        level = 0
        while(index.parent().isValid()):
            index = index.parent()
            level += 1
        return level

    def database_info_tree_menu_l1(self, menu, index):
        if(index.data() == "Columns"):
            menu.addAction(
                self.tr("Add Column"),
                self.add_column(index.parent().data()),
                0
            )
        elif(index.data() == "Primary Keys"):
            menu.addAction(
                self.tr("Add Primary Key"),
                self.add_primary_key(index.parent().data()),
                0
            )
        elif(index.data() == "Foreign Keys"):
            menu.addAction(self.tr("Add Foreign Key"))
        else:
            menu.addAction(
                self.tr("Add Functional Dependency"),
                self.add_functional_dependency(index.parent().data()),
                0
            )
        return menu

    def database_info_tree_menu_l2(self, menu, index):
        index_parent = index.parent()
        table = index_parent.parent().data()
        if(index_parent.data() == "Columns"):
            menu.addAction(
                self.tr("Delete Column"),
                self.delete_column(table, index.data()),
                0
            )
        elif(index_parent.data() == "Primary Keys"):
            menu.addAction(
                self.tr("Delete Primary Key"),
                self.delete_primary_key(table, index.data()),
                0
            )
        elif(index_parent.data() == "Foreign Keys"):
            menu.addAction(
                self.tr("Delete Foreign Key"),
                self.delete_foreign_key(table, index.data()),
                0
            )
        else:
            menu.addAction(
                self.tr("Delete Functional Dependency"),
                self.delete_functional_dependency(table, index.data()),
                0
            )
        return menu

    def database_info_tree_menu_l3(self, menu, index):
        index_l1 = index.parent().parent()
        if(index_l1.data() == "Columns"):
            menu.addAction("Edit Column Data")
            menu.addAction("Delete Flag")
        return menu

    def database_info_tree_menu(self, position):
        indexes = self.ui.database_info_tree.selectedIndexes()
        if(len(indexes) > 0):
            level = self.get_node_level(indexes[0])
            index = indexes[0]
        else:
            level = -1
        tree_menu = QMenu()
        if(level == -1):
            tree_menu.addAction(
                self.tr("Create Table"),
                self.create_table(),
                0
            )
        elif(level == 0):
            tree_menu.addAction(self.tr("Delete Table"))
        elif(level == 1):
            tree_menu = self.database_info_tree_menu_l1(tree_menu, index)
        elif(level == 2):
            tree_menu = self.database_info_tree_menu_l2(tree_menu, index)
        elif(level == 3):
            tree_menu = self.database_info_tree_menu_l3(tree_menu, index)
        tree_menu.exec_(
            self.ui.database_info_tree.viewport().mapToGlobal(position)
        )


app = QApplication(sys.argv)
window = UIHandlers()
sys.exit(app.exec_())

