import os

class SimpleDB:
    def __init__(self, filename):
        self.filename = filename
        if not os.path.exists(filename):
            open(filename, 'w+b').close()
        self.file = open(filename, 'r+b')
        self.page_size = 4096
        self.page_cache = {}

    def close(self):
        self.file.close()

    def read_page(self, page_number):
        if page_number in self.page_cache:
            return self.page_cache[page_number]
        self.file.seek(page_number * self.page_size)
        data = self.file.read(self.page_size)
        if not data:
            data = b'\x00' * self.page_size
        self.page_cache[page_number] = data
        return data

    def write_page(self, page_number, data):
        assert len(data) == self.page_size
        self.page_cache[page_number] = data
        self.file.seek(page_number * self.page_size)
        self.file.write(data)
        self.file.flush()

    def allocate_page(self):
        self.file.seek(0, os.SEEK_END)
        page_number = self.file.tell() // self.page_size + 1
        self.write_page(page_number, b'\x00' * self.page_size)
        return page_number

    def free_page(self, page_number):
        self.write_page(page_number, b'\x00' * self.page_size)

class Table:
    def __init__(self, name, columns):
        self.name = name
        self.columns = columns
        self.page_number = None
        self.rows = []

class Database:
    def __init__(self, filename):
        self.db = SimpleDB(filename)
        self.tables = {}
        self._load_metadata()

    def create_table(self, name, columns):
        if name in self.tables:
            print(f"Table '{name}' already exists.")
            return
        table = Table(name, columns)
        table.page_number = self.db.allocate_page()
        self.tables[name] = table
        self._save_metadata()

    def insert_into_table(self, table_name, values):
        if table_name not in self.tables:
            print(f"Table '{table_name}' does not exist.")
            return
        table = self.tables[table_name]
        if len(values) != len(table.columns):
            print(f"Error: Expected {len(table.columns)} values, got {len(values)}")
            return
        self._read_table(table)
        table.rows.append(values)
        self._write_table(table)

    def select_from_table(self, table_name):
        if table_name not in self.tables:
            print(f"Table '{table_name}' does not exist.")
            return []
        table = self.tables[table_name]
        self._read_table(table)
        return table.rows

    def _write_table(self, table):
        data = '\n'.join([','.join(map(str, row)) for row in table.rows]).encode().ljust(self.db.page_size, b'\x00')
        self.db.write_page(table.page_number, data)

    def _read_table(self, table):
        data = self.db.read_page(table.page_number).rstrip(b'\x00').decode()
        if data:
            table.rows = [line.split(',') for line in data.split('\n')]

    def select_row_from_table(self, table_name, column_name, value):
        if table_name not in self.tables:
            print(f"Table '{table_name}' does not exist.")
            return None
        table = self.tables[table_name]
        self._read_table(table)
        column_index = table.columns.index(column_name)
        for row in table.rows:
            if row[column_index] == value:
                return row
        return None

    def delete_from_table(self, table_name, column_name, value):
        if table_name not in self.tables:
            print(f"Table '{table_name}' does not exist.")
            return
        table = self.tables[table_name]
        self._read_table(table)
        column_index = table.columns.index(column_name)
        original_row_count = len(table.rows)
        table.rows = [row for row in table.rows if row[column_index] != value]
        if len(table.rows) != original_row_count:
            self._write_table(table)
            print(f"Row where {column_name} is {value} deleted from table '{table_name}'.")
        else:
            print(f"No row found where {column_name} is {value} in table '{table_name}'.")

    def edit_row(self, table_name, column_name, value, new_values):
        if table_name not in self.tables:
            print(f"Table '{table_name}' does not exist.")
            return
        table = self.tables[table_name]
        self._read_table(table)
        column_index = table.columns.index(column_name)
        row_updated = False
        for row in table.rows:
            if row[column_index] == value:
                for i, new_value in enumerate(new_values):
                    row[i] = new_value
                row_updated = True
                break
        if row_updated:
            self._write_table(table)
            print(f"Row where {column_name} is {value} updated in table '{table_name}'.")
        else:
            print(f"No row found where {column_name} is {value} in table '{table_name}'.")

    def delete_table(self, table_name):
        if table_name not in self.tables:
            print(f"Table '{table_name}' does not exist.")
            return
        table = self.tables.pop(table_name)
        self.db.free_page(table.page_number)
        self._save_metadata()
        self._reallocate_pages()
        print(f"Table '{table_name}' and its page deleted.")

    def _reallocate_pages(self):
        pages = sorted(table.page_number for table in self.tables.values())
        new_page_map = {}
        current_page = 1
        for old_page in pages:
            if old_page != current_page:
                new_page_map[old_page] = current_page
                data = self.db.read_page(old_page)
                self.db.write_page(current_page, data)
                self.db.free_page(old_page)
            current_page += 1
        for table in self.tables.values():
            if table.page_number in new_page_map:
                table.page_number = new_page_map[table.page_number]
        self._save_metadata()

    def _save_metadata(self):
        metadata = []
        for table in self.tables.values():
            metadata.append(f'{table.name}:{",".join(table.columns)}:{table.page_number}')
        data = '\n'.join(metadata).encode().ljust(self.db.page_size, b'\x00')
        self.db.write_page(0, data)

    def _load_metadata(self):
        data = self.db.read_page(0).rstrip(b'\x00').decode()
        if data:
            for line in data.split('\n'):
                if line:
                    parts = line.split(':')
                    if len(parts) != 3:
                        continue
                    name, columns, page_number = parts
                    columns = columns.split(',')
                    page_number = int(page_number)
                    table = Table(name, columns)
                    table.page_number = page_number
                    self.tables[name] = table

# --------------EXEMPLO DE USO----------------
database = Database('test.db')

database.create_table('users', ['id', 'name', 'age'])
database.insert_into_table('users', [1, 'Alice', 24])
database.insert_into_table('users', [2, 'Bob', 19])

print(database.select_from_table('users'))

database.db.close()
