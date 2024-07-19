import os

# Classe para armazenar uma Database usando paginas de forma simples
class SimpleDB:
    # Inicializa o SimpleDB com um nome de arquivo dado
    def __init__(self, filename):
        self.filename = filename
        if not os.path.exists(filename):
            open(filename, 'w+b').close()
        self.file = open(filename, 'r+b')
        self.page_size = 4096
        self.page_cache = {}

    # Fecha o arquivo do banco de dados
    def close(self):
        self.file.close()

    # Le uma pagina do arquivo do banco de dados priorizando a busca na "cache"
    def read_page(self, page_number):
        # testa primeiro a cache
        if page_number in self.page_cache:
            return self.page_cache[page_number]

        # se nao estiver na cache, le do arquivo
        self.file.seek(page_number * self.page_size)
        data = self.file.read(self.page_size)
        if not data:
            data = b'\x00' * self.page_size
        self.page_cache[page_number] = data
        return data

    # Escreve uma pagina no arquivo do banco de dados
    def write_page(self, page_number, data):
        assert len(data) == self.page_size
        self.page_cache[page_number] = data
        self.file.seek(page_number * self.page_size)
        self.file.write(data)
        self.file.flush()

    # Aloca uma nova pagina no final do arquivo do banco de dados
    def allocate_page(self):
        self.file.seek(0, os.SEEK_END)
        page_number = (self.file.tell() // self.page_size) + 1
        self.write_page(page_number, b'\x00' * self.page_size)
        return page_number

# Classe que utilizaremos para armazenar tabelas e seus dados no banco de dados
class Table:
    def __init__(self, name, columns):
        self.name = name
        self.columns = columns
        self.page_number = None
        self.rows = []

# Aplicação da SimpleDB usando a classe Table para uma melhor organização de dados
class Database:
    # Inicializa o Database com um nome de arquivo dado
    def __init__(self, filename):
        self.db = SimpleDB(filename)
        self.tables = {}
        self._load_metadata()  # Carrega a metadata ao iniciar o banco de dados

    # Cria uma página com a tabela e suas colunas
    def create_table(self, name, columns):
        if name in self.tables:
            print(f"Table '{name}' already exists.")
            return
        table = Table(name, columns)
        table.page_number = self.db.allocate_page()
        self.tables[name] = table
        self._save_metadata()  # Salva a metadata após criar a tabela

    # Insere uma linha na tabela especificada no fim da tabela
    def insert_into_table(self, table_name, values):
        table = self.tables[table_name]
        self._read_table(table)
        table.rows.append(values)
        self._write_table(table)

    # Seleciona e retorna todas as linhas da tabela especificada
    def select_from_table(self, table_name):
        if table_name not in self.tables:
            print(f"Table '{table_name}' does not exist.")
            return []
        table = self.tables[table_name]
        self._read_table(table)
        return table.rows

    # Serializa as linhas da tabela e as escreve na página da tabela no banco de dados
    def _write_table(self, table):
        data = '\n'.join([','.join(map(str, row)) for row in table.rows]).encode().ljust(self.db.page_size, b'\x00')
        self.db.write_page(table.page_number, data)

    # Lê os dados da tabela de sua página no banco de dados e os deserializa em linhas
    def _read_table(self, table):
        data = self.db.read_page(table.page_number).rstrip(b'\x00').decode()
        if data:
            table.rows = [line.split(',') for line in data.split('\n')]

    # Seleciona e retorna uma linha específica da tabela especificada onde a coluna dada tem o valor especificado
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

    # Salva os metadados de todas as tabelas na primeira página do arquivo de banco de dados
    def _save_metadata(self):
        metadata = []
        for table in self.tables.values():
            metadata.append(f'{table.name}:{",".join(table.columns)}:{table.page_number}')
        data = '\n'.join(metadata).encode().ljust(self.db.page_size, b'\x00')
        self.db.write_page(0, data)

    # Carrega os metadados de todas as tabelas da primeira página do arquivo de banco de dados
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

database.create_table('products', ['id', 'name', 'price'])
database.insert_into_table('products', [1, 'Apple', 1.2])
database.insert_into_table('products', [2, 'Banana', 0.8])

print(database.select_from_table('users'))
print(database.select_from_table('products'))

database.db.close()