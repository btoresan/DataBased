import os
from graphviz import Digraph
import pickle

class BTreeNode:
    def __init__(self, t, leaf=False):
        self.t = t  # Minimum degree (defines the range for number of keys)
        self.leaf = leaf  # True if leaf node, else False
        self.keys = []  # List of keys in the node
        self.children = []  # List of child nodes

    def insert_non_full(self, key):
        i = len(self.keys) - 1
        if self.leaf:
            # Insert the new key into the node
            self.keys.append(None)
            while i >= 0 and self.keys[i] > key:
                self.keys[i + 1] = self.keys[i]
                i -= 1
            self.keys[i + 1] = key
        else:
            # Find the child which is going to have the new key
            while i >= 0 and self.keys[i] > key:
                i -= 1
            i += 1
            if len(self.children[i].keys) == 2 * self.t - 1:
                self.split_child(i, self.children[i])
                if self.keys[i] < key:
                    i += 1
            self.children[i].insert_non_full(key)

    def split_child(self, i, y):
        t = self.t
        z = BTreeNode(t, y.leaf)
        self.children.insert(i + 1, z)
        self.keys.insert(i, y.keys[t - 1])
        z.keys = y.keys[t:(2 * t - 1)]
        y.keys = y.keys[0:(t - 1)]
        if not y.leaf:
            z.children = y.children[t:(2 * t)]
            y.children = y.children[0:t]

    def delete(self, key):
        t = self.t
        i = 0
        while i < len(self.keys) and key > self.keys[i]:
            i += 1

        if i < len(self.keys) and self.keys[i] == key:
            if self.leaf:
                self.keys.pop(i)
            else:
                self.delete_internal_node(key, i)
        else:
            if self.leaf:
                return  # The key is not in the tree
            flag = i == len(self.keys)
            if len(self.children[i].keys) < t:
                self.fill(i)
            if flag and i > len(self.keys):
                self.children[i - 1].delete(key)
            else:
                self.children[i].delete(key)

    def delete_internal_node(self, key, i):
        t = self.t
        if len(self.children[i].keys) >= t:
            pred = self.get_predecessor(i)
            self.keys[i] = pred
            self.children[i].delete(pred)
        elif len(self.children[i + 1].keys) >= t:
            succ = self.get_successor(i)
            self.keys[i] = succ
            self.children[i + 1].delete(succ)
        else:
            self.merge(i)
            self.children[i].delete(key)

    def get_predecessor(self, i):
        current = self.children[i]
        while not current.leaf:
            current = current.children[len(current.children) - 1]
        return current.keys[len(current.keys) - 1]

    def get_successor(self, i):
        current = self.children[i + 1]
        while not current.leaf:
            current = current.children[0]
        return current.keys[0]

    def fill(self, i):
        t = self.t
        if i != 0 and len(self.children[i - 1].keys) >= t:
            self.borrow_from_prev(i)
        elif i != len(self.keys) and len(self.children[i + 1].keys) >= t:
            self.borrow_from_next(i)
        else:
            if i != len(self.keys):
                self.merge(i)
            else:
                self.merge(i - 1)

    def borrow_from_prev(self, i):
        child = self.children[i]
        sibling = self.children[i - 1]
        for j in range(len(child.keys) - 1, -1, -1):
            child.keys[j + 1] = child.keys[j]
        if not child.leaf:
            for j in range(len(child.children) - 1, -1, -1):
                child.children[j + 1] = child.children[j]
        child.keys[0] = self.keys[i - 1]
        if not self.leaf:
            child.children[0] = sibling.children[len(sibling.children) - 1]
        self.keys[i - 1] = sibling.keys[len(sibling.keys) - 1]
        sibling.keys.pop()
        if not sibling.leaf:
            sibling.children.pop()

    def borrow_from_next(self, i):
        child = self.children[i]
        sibling = self.children[i + 1]
        child.keys.append(self.keys[i])
        if not child.leaf:
            child.children.append(sibling.children[0])
        self.keys[i] = sibling.keys[0]
        sibling.keys.pop(0)
        if not sibling.leaf:
            sibling.children.pop(0)

    def merge(self, i):
        child = self.children[i]
        sibling = self.children[i + 1]
        child.keys.append(self.keys[i])
        for j in range(len(sibling.keys)):
            child.keys.append(sibling.keys[j])
        if not child.leaf:
            for j in range(len(sibling.children)):
                child.children.append(sibling.children[j])
        self.keys.pop(i)
        self.children.pop(i + 1)

class BTree:
    def __init__(self, t):
        self.t = t  # Minimum degree
        self.root = BTreeNode(t, True)

    def search(self, k, x=None):
        if x is None:
            x = self.root
        i = 0
        while i < len(x.keys) and k > x.keys[i]:
            i += 1
        if i < len(x.keys) and k == x.keys[i]:
            return (x, i)
        elif x.leaf:
            return None
        else:
            return self.search(k, x.children[i])
        
    def search_first_element(self, k, x=None, results=None):
        if results is None:
            results = []
        if x is None:
            x = self.root

        i = 0
        # Traverse keys and search in appropriate children
        while i < len(x.keys):
            if x.keys[i][0] == k:
                results.append(x.keys[i])
            if k < x.keys[i][0]:
                if not x.leaf:
                    self.search_first_element(k, x.children[i], results)
                break
            i += 1

        # If not found in the current level, go to the rightmost child
        if not x.leaf and (i == len(x.keys) or k > x.keys[-1][0]):
            self.search_first_element(k, x.children[i], results)

        return results

    def insert(self, k):
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            s = BTreeNode(self.t, False)
            self.root = s
            s.children.insert(0, root)
            s.split_child(0, root)
            s.insert_non_full(k)
        else:
            root.insert_non_full(k)

    def delete(self, key):
        if not self.root:
            return
        self.root.delete(key)
        if len(self.root.keys) == 0:
            if not self.root.leaf:
                self.root = self.root.children[0]
            else:
                self.root = None

    def in_order_traversal(self, node=None, result=None):
        if result is None:
            result = []
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys):
            if not node.leaf:
                self.in_order_traversal(node.children[i], result)
            result.append(node.keys[i])
            i += 1
        if not node.leaf:
            self.in_order_traversal(node.children[i], result)
        return result

    def reverse_order_traversal(self, node=None, result=None):
        if result is None:
            result = []
        if node is None:
            node = self.root
        i = len(node.keys) - 1
        while i >= 0:
            if not node.leaf:
                self.reverse_order_traversal(node.children[i + 1], result)
            result.append(node.keys[i])
            i -= 1
        if not node.leaf:
            self.reverse_order_traversal(node.children[0], result)
        return result

    def visualize(self, filename="btree"):
        def add_nodes_edges(node, dot=None):
            if dot is None:
                dot = Digraph()
                dot.node(name=str(id(node)), label="|".join(map(str, node.keys)))
            else:
                dot.node(name=str(id(node)), label="|".join(map(str, node.keys)))

            for i, child in enumerate(node.children):
                dot.edge(str(id(node)), str(id(child)))
                add_nodes_edges(child, dot)

            return dot

        dot = add_nodes_edges(self.root)
        dot.render(filename, format='png', cleanup=True)

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
    def __init__(self, name, columns, degree=3):
        self.name = name
        self.columns = columns
        self.page_number = None
        self.rows = []
        self.btree = BTree(degree)

class Database:
    def __init__(self, filename):
        self.db = SimpleDB(filename)
        self.tables = {}
        self._load_metadata()

    def create_table(self, name, columns, degree=3):
        if name in self.tables:
            print(f"Table '{name}' already exists.")
            return
        table = Table(name, columns, degree)
        table.page_number = self.db.allocate_page()
        self.tables[name] = table
        self._save_metadata()

    def insert_into_table(self, table_name, values):
        if table_name not in self.tables:
            print(f"Table '{table_name}' does not exist.")
            return
        table = self.tables[table_name]
        if len(values) != len(table.columns):
            print(f"Expected {len(table.columns)} values, got {len(values)}.")
            return
        self._read_table(table)
        table.btree.insert(values)
        self._write_table(table)

    def load_table(self, table_name):
        if table_name not in self.tables:
            print(f"Table '{table_name}' does not exist.")
            return
        table = self.tables[table_name]
        self._read_table(table)
        return table
    
    def peek_table(self, table_name, reverse=False):
        if table_name not in self.tables:
            print(f"Table '{table_name}' does not exist.")
            return
        table = self.tables[table_name]
        self._read_table(table)
        if reverse:
            return table.btree.reverse_order_traversal()
        return table.btree.in_order_traversal()

    def _write_table(self, table):
        data = pickle.dumps(table.btree)
        data = data.ljust(self.db.page_size, b'\x00')
        self.db.write_page(table.page_number, data)

    def _read_table(self, table):
        data = self.db.read_page(table.page_number).rstrip(b'\x00')
        if data:
            table.btree = pickle.loads(data)

    def select_row_from_table(self, table_name, column_name, value):
        if table_name not in self.tables:
            print(f"Table '{table_name}' does not exist.")
            return
        
        table = self.tables[table_name]
        self._read_table(table)
        #Busca rapida pela chave primaria
        if column_name == table.columns[0]:
            return table.btree.search_first_element(value)
        #Por favor pesquise pela chave primaria
        else:
            results = []
            for row in table.btree.in_order_traversal():
                if value in row:
                    results.append(row)
            return results

    def delete_row_from_table(self, table_name, value):
        if table_name not in self.tables:
            print(f"Table '{table_name}' does not exist.")
            return
        table = self.tables[table_name]
        self._read_table(table)
        table.btree.delete(value)
        self._write_table(table)
        return

    def edit_row_from_table(self, table_name, column_name, value, new_values):
        if table_name not in self.tables:
            print(f"Table '{table_name}' does not exist.")
            return
        table = self.tables[table_name]
        self._read_table(table)
        if len(new_values) != len(table.columns):
            print(f"Expected {len(table.columns)} values, got {len(new_values)}.")
        current_values = self.select_row_from_table(table_name, column_name, value)
        if not current_values:
            print(f"Row with {column_name} = {value} not found.")
            return
        if len(current_values) > 1:
            current_values = current_values[0]
        self.delete_row_from_table(table_name, current_values[0])
        self.insert_into_table(table_name, new_values)

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

    def visualize_table(self, table_name):
        if table_name not in self.tables:
            print(f"Table '{table_name}' does not exist.")
            return
        table = self.tables[table_name]
        self._read_table(table)
        table.btree.visualize(table_name)

    def close(self):
        self.db.close()

# --------------EXEMPLO DE USO----------------

# Example usage
db = Database('test.db')

# Create a table
db.create_table('employees', ['id', 'name', 'age'])

# Insert rows into the table
db.insert_into_table('employees', [1, 'John Doe', 30])
db.insert_into_table('employees', [2, 'Jane Smith', 25])
db.insert_into_table('employees', [3, 'Bob Johnson', 35])

# Visualize the table as a B-tree
db.visualize_table('employees')

# Print all rows in the table
print(db.peek_table('employees'))

# Search for a specific row by column value
result = db.select_row_from_table('employees', 'name', 'John Doe')
print(result)

# Edit a row in the table
db.edit_row_from_table('employees', 'id', 2, [2, 'Jane Brown', 26])

# Delete a row from the table
db.delete_row_from_table('employees', [3, 'Bob Johnson', 35])

# Delete the table
db.delete_table('employees')

# Close the database
db.close()
