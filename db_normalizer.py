#!/usr/bin/python3
from enum import Enum
import re

class Database:

    def __init__(self):
        self.keywords = [
            "create",
            "primary",
            "foreign"
        ]
        self.tables = []

        # Parse function. Expects list of lines in an array.
    def parse(self, content):
        line_num = 0
        while(line_num < len(content)):
            handle = self.handle_line(content[line_num])
            if(handle == Handle.table):
                line_num = line_num + self.parse_table(content[line_num:])

    def parse_table(self, content):
        keywords = [
            "PK",
            "FK"
        ]
        line_num = 0
        creation_tokens = content[line_num].split()
        table_name = creation_tokens[2].replace("(","")
        new_table = Table(table_name)
        line_num = line_num + 1
        while(line_num < len(content)):
            current_line = content[line_num]
            column_info = self.parse_table_line(current_line)
            if(column_info['type'] not in keywords and column_info['name']):
                new_table.add_column(
                    column_info['name'],
                    column_info['type'],
                    column_info['flags']
                )
            elif (column_info['type'] == "PK"):
                for name in column_info['name']:
                    new_table.add_primary_key(name)
            elif (column_info['type'] == "FK"):
                new_table.add_foreign_key(
                    column_info['name'],
                    column_info['fk_table'],
                    column_info['fk_reference']
                )
                pass
            line_num = line_num + 1
            if(column_info['end']):
                break
        self.tables.append(new_table)
        return line_num

    def handle_foreign_key(self, line):
        table = None
        reference = None
        if(line[2] == "("):
            table = line[3]
            line = line[5:]
        else:
            table = line[2][1:-1]
            line = line[3:]
        variableList = re.findall("[a-zA-Z]+", line[1])
        if(len(variableList) > 1):
            table = variableList[0]
            reference = variableList[1]
        else:
            if(re.match("[a-zA-Z]+\(",variableList[0])):
                table = re.match.group()[0:-1]
                reference = line[2]
            else:
                table = variableList[0]
                reference = line[3]
        return {"table": table, "reference": reference}

    def parse_flags(self, line):
        flags = []
        while(line):
            popped = line.pop(0)
            if(popped.lower() == "not" or popped.lower() == "unique"):
                next_token = line.pop(0).replace(",","")
                flags.append(popped + " " + next_token)
            else:
                popped = popped.replace(",","")
                flags.append(popped)
        return flags

    def parse_primary_key_line(self, tokens):
        names = []
        if(tokens[2] == "("):
            if("," not in tokens[3]):
                names.append(tokens[3])
                tokens = tokens[4:]
                while(tokens):
                    name = tokens.pop()
                    if("," not in name and ")" not in name):
                        names.append(name)
            else:
                tokens = tokens[3:]
                while(tokens):
                    name = tokens.pop()
                    if("(" in name):
                        name = name[1:]
                    if(")" in name):
                        name = name[:-1]
                    for split in name.split(","):
                        if(split != ""):
                            names.append(split)
        elif("," in tokens[2]):
            tokens = tokens[2:]
            while(tokens):
                name = tokens.pop()
                if("(" in name):
                    name = name[1:]
                if(")" in name):
                    name = name[:-1]
                for split in name.split(","):
                    if(split != ""):
                        names.append(split)
        else:
            names.append(tokens[2][1:-1])
        return names

    def parse_table_line(self, line):
        tokens = line.split()
        name = None
        type = None
        flags = []
        reference = None
        table = None
        table_end = True if (");" in tokens) else False
        handle = self.handle_line(line)
        if(len(tokens) > 1):
            if (handle == Handle.primary_key):
                name = self.parse_primary_key_line(tokens)
                type = "PK"
            elif(handle == Handle.foreign_key):
                if(tokens[2] == "("):
                    name = tokens[3]
                else:
                    name = tokens[2][1:-1]
                foreign_key_variables = self.handle_foreign_key(tokens)
                reference = foreign_key_variables["reference"]
                table = foreign_key_variables["table"]
                type = "FK"
                pass
            else:
                name = tokens[0]
                if("(" in tokens[1]):
                    type = tokens[1] + tokens[2] + tokens[3]
                    tokens = tokens[4:]
                else:
                    type = tokens[1]
                    tokens = tokens[2:]
                flags = self.parse_flags(tokens)
        return {
            "name": name,
            "type": type,
            "end": table_end,
            "flags": flags,
            "fk_reference": reference,
            "fk_table": table
        }

    def keyword_handler(self, tokens):
        if (tokens[0].lower() == "create"):
            return Handle.table
        if (tokens[0].lower() == "primary"):
            return Handle.primary_key
        if (tokens[0].lower() == "foreign"):
            return Handle.foreign_key

    # Shows the handle for a line of code. Expects a string.
    def handle_line(self, line):
        current_token = 0
        tokens = line.split()
        if (tokens[current_token].lower() in self.keywords):
            return self.keyword_handler(tokens)
        return Handle.none

    def add_functional_dependency(self, table_name, child, parents):
        for table in self.tables:
            if (table.table_name == table_name):
                table.add_functional_dependency(child, parents)
                break

    def import_file(self, import_file):
        file = open(import_file)
        content = file.read()
        content_lines = content.split("\n")
        content_lines = [line for line in content_lines if line.strip()]
        self.parse(content_lines)

    def handle_functional_dependencies(self):
        fixables = {}
        for table in self.tables:
            table_name = table.table_name
            fixables[table_name] = {}
            for child, parents in table.functional_dependencies.items():
                if(parents != table.primary_keys):
                    if(not parents[0] in fixables[table_name]):
                        fixables[table_name][parents[0]] = []
                    fixables[table_name][parents[0]].append(child)
        for table, deps_to_fix in fixables.items():
            for parent, children in deps_to_fix.items():
                new_table = Table(table+"_"+parent)
                old_table = self.get_table(table)
                parent_column_info = old_table.get_column(parent)
                new_table.add_primary_key(parent)
                new_table.add_column(
                    parent_column_info["name"],
                    parent_column_info["type"],
                    parent_column_info["flags"]
                )
                for child in children:
                    child_info = old_table.get_column(child)
                    print(child_info)
                    new_table.add_column(
                        child_info["name"],
                        child_info["type"],
                        child_info["flags"]
                    )
                    self.get_table(table).remove_column(child_info["name"])
                    self.get_table(table).remove_functional_dependency(
                        child_info["name"]
                    )
                new_table.add_foreign_key(
                    parent,
                    old_table.table_name,
                    parent
                )
                self.tables.append(new_table)

    def get_table(self, table_name):
        tableFound = None
        for table in self.tables:
            if(table.table_name == table_name):
                tableFound = table
                break
        return tableFound

    def export_database(self):
        tables = self.tables
        returnString = "";
        for table in tables:
            returnString += "CREATE TABLE "+table.table_name+"(\n"
            for column in table.columns:
                returnString += "  "+column['name']+" "+column['type']
                for flag in column['flags']:
                    returnString+= " "+flag
                returnString += ",\n"
            for foreign_key in table.foreign_keys:
                returnString += "  FOREIGN KEY "+foreign_key['name']+" "
                returnString += "REFERENCES "+foreign_key['table']+"( "
                returnString += foreign_key['column']+" ),\n"
            returnString += "  PRIMARY KEY ( "+table.primary_keys[0]
            for primary_key in (table.primary_keys[1:]):
                returnString += ", "+primary_key
            returnString += " )\n"
            returnString += ");\n\n"
        return returnString

    def tables(self):
        return self.tables

class Handle(Enum):
    none = 100
    table = 200
    table_end = 201
    primary_key = 210
    foreign_key = 220

class Table:

    def __init__(self, table_name):
        self.table_name = table_name
        self.columns = []
        self.primary_keys = []
        self.foreign_keys = []
        self.functional_dependencies = {}

    def add_column(self, name, type, flags):
        if not (flags):
            self.columns.append({"name": name, "type": type, "flags": None})
        else:
            self.columns.append({"name": name, "type": type, "flags": flags})

    def get_column(self, name):
        columnFound = None
        for column in self.columns:
            if(column["name"] == name):
                columnFound = column
                break
        return columnFound

    def remove_column(self, name):
        self.columns[:] = (
            [column for column in self.columns if not (column["name"] == name)]
        )
        self.remove_primary_key(name)
        self.remove_foreign_key(name)
        self.remove_functional_dependency(name)

    def add_functional_dependency(self, child, parents):
        child_check = self.get_column(child)
        parent_check = True
        for parent in parents:
            parent_check = parent_check and self.get_column(parent)
        if(child_check and parent_check):
            self.functional_dependencies[child] = parents
        return (child_check and parent_check)

    def remove_primary_key(self, name):
        self.primary_keys[:] = (
            [
                primary_key
                for primary_key in self.primary_keys
                if not (primary_key == name)
            ]
        )

    def remove_foreign_key(self, name):
        self.foreign_keys[:] = (
            [
                foreign_key
                for foreign_key in self.foreign_keys
                if not (foreign_key["name"] == name)
            ]
        )

    def remove_functional_dependency(self, child):
        self.functional_dependencies.pop(child, None)

    def add_primary_key(self, name):
        self.primary_keys.append(name)

    def add_foreign_key(self, name, references_table, references_column):
        self.foreign_keys.append({
            "name": name,
            "table": references_table,
            "column": references_column
        })

    def primary_keys(self):
        return self.primary_keys

    def functional_dependencies(self):
        return self.functional_dependencies

    def columns(self):
        return self.columns

    def foreign_keys(self):
        return self.foreign_keys

    def table_name(self):
        return self.table_name

if __name__ == "__main__":
    database = Database()
    database.import_file("test_func.sql")
    print(database.export_database())
    database.add_functional_dependency("winners", "winnerdob", ["winner"])
    #for x in database.tables:
    #    print(x.primary_keys)
    database.handle_functional_dependencies()
    database.handle_functional_dependencies()
    print(database.export_database())

