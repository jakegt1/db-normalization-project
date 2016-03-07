import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QMenu,
    QInputDialog
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
        normalize_button = self.ui.normalize_button
        normalize_button.clicked.connect(self.normalize_database)
        self.ui.database_info_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.database_info_tree.customContextMenuRequested.connect(
            self.database_info_tree_menu
        )
        self.model = QStandardItemModel()
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
            print(child)
            print(parent)
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
        print(tree_data)
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

    def update_sql_code(self, text):
        self.ui.export_SQL_code.setText(text)

    def get_file_for_import(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Choose file', '~/')
        self.database = Database()
        self.database.import_file(filename)
        self.update_sql_code(self.database.export_database())
        self.add_items(self.model, self.generate_tree_data())
        self.ui.database_info_tree.setModel(self.model)
        self.filename_without_path = filename.split("/")[-1]
        self.set_model_header_name()
        return filename

    def normalize_database(self):
        self.database.handle_functional_dependencies()
        self.update_sql_code(self.database.export_database())
        self.update_tree_view()

    def add_functional_dependency(self, table):
        def add_functional_dependency_closure():
            columns = self.database.get_table(table).columns
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
                print(column_names)
                print(set([child]))
                column_names = list(set(column_names) - set([child]))
                print(column_names)
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
                    self.database.get_table(table).add_functional_dependency(
                        child,
                        parents
                    )
                    self.update_tree_view()
        return add_functional_dependency_closure

    def get_node_level(self, index):
        level = 0
        while(index.parent().isValid()):
            index = index.parent()
            level += 1
        return level

    def database_info_tree_menu_l1(self, menu, index):
        if(index.data() == "Columns"):
            menu.addAction(self.tr("Add Column"), )
        elif(index.data() == "Primary Keys"):
            menu.addAction(self.tr("Add Primary Key"))
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
        if(index_parent.data() == "Columns"):
            menu.addAction(self.tr("Delete Column"))
        elif(index_parent.data() == "Primary Keys"):
            menu.addAction(self.tr("Delete Primary Key"))
        elif(index_parent.data() == "Foreign Keys"):
            menu.addAction(self.tr("Delete Foreign Key"))
        else:
            menu.addAction(self.tr("Delete Functional Dependency"))
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
        tree_menu = QMenu()
        if(level == 0):
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

