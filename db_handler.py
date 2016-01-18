from enum import Enum

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
            print(len(content))
            print(line_num)
            handle = self.handle_line(content[line_num])
            if(handle == Handle.table):
                line_num = self.parse_table(content[line_num:])

    def parse_table(self, content):
        keywords = [
            "PK",
            "FK"
        ]
        line_num = 0
        creation_tokens = content[line_num].split()
        new_table = Table(creation_tokens[2])
        line_num = line_num + 1
        while(line_num < len(content)):
            current_line = content[line_num]
            column_info = self.parse_table_line(current_line)
            if(column_info['type'] not in keywords and column_info['name']):
                new_table.add_column(column_info['name'], column_info['type'])
            elif (column_info['type'] == "PK"):
                print("memes")
                new_table.add_primary_key(column_info['name'])
            else:
                pass
            line_num = line_num + 1
            if(column_info['end']):
                break
        self.tables.append(new_table)
        return line_num

    def parse_table_line(self, line):
        tokens = line.split()
        name = None
        type = None
        table_end = True if (");" in tokens) else False
        handle = self.handle_line(line)
        if(len(tokens) > 1):
            if (handle == Handle.primary_key):
                if(tokens[2] == "("):
                    name = tokens[3]
                else:
                    #strips parentheses (string from pos 1 to pos length-1)
                    name = tokens[2][1:-1]
                type = "PK"
            elif(handle == Handle.foreign_key):
                pass
            else:
                name = tokens[0]
                if("(" in tokens[1]):
                    type = tokens[1] + tokens[2] + tokens[3]
                else:
                    type = tokens[1]
        return {"name": name, "type": type, "end": table_end}

    def keyword_handler(self, tokens):
        if (tokens[0].lower() == "create"):
            return Handle.table
        if (tokens[0].lower() == "primary"):
            return Handle.primary_key
        if (tokens[0].lower() == "foreign"):
            return Handle.foreign_key


    # Parses 1 line of code. Expects one string.
    def handle_line(self, line):
        current_token = 0
        tokens = line.split()
        if (tokens[current_token].lower() in self.keywords):
            return self.keyword_handler(tokens)
        return Handle.none

    def import_file(self, import_file):
        file = open(import_file)
        content = file.read()
        content_lines = content.split("\n")
        content_lines = [line for line in content_lines if line.strip()]
        self.parse(content_lines)

    def export_database(self):
        pass

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
        self.primary_key = ""

    def add_column(self, name, type):
        self.columns.append((name, type))

    def add_primary_key(self, name):
        self.primary_key = name

if __name__ == "__main__":
    database = Database()
    database.import_file("test.sql")
    print(database.tables[0].columns)
    print(database.tables[0].primary_key)

