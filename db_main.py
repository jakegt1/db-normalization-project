import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem
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
            this_fd_tuple = (child,)
            this_fd_tuple += ([(parent,[])],)
            fd_data.append(this_fd_tuple)
        return fd_data

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

    def get_file_for_import(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Choose file', '~/')
        self.database.import_file(filename)
        self.ui.export_SQL_code.setText(self.database.export_database())
        self.add_items(self.model, self.generate_tree_data())
        self.ui.database_info_tree.setModel(self.model)
        return filename

app = QApplication(sys.argv)
window = UIHandlers()
sys.exit(app.exec_())

