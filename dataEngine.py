import os


#Classe para armazenar uma Database usando paginas de forma simples
class SimpleDB:
    #Inicializa o SimpleDB com um nome de arquivo dado
    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, 'w+b')
        self.page_size = 4096
        self.page_cache = {}

    #Fecha o arquivo do banco de dados
    def close(self):
        self.file.close()

    #Le uma pagina do arquivo do banco de dados priorizando a busca na "cache"
    def read_page(self, page_number):
        #testa primeiro a cache
        if page_number in self.page_cache:
            return self.page_cache[page_number]

        #se nao estiver na cache, le do arquivo
        self.file.seek(page_number * self.page_size)
        data = self.file.read(self.page_size)
        if not data:
            data = b'\x00' * self.page_size
        self.page_cache[page_number] = data
        return data

    #Escreve uma pagina no arquivo do banco de dados
    #O Arquivo é divido em páginas de 4KB (pode ser variado) para evitar carregar algo muito grande de uma vez
    #Ele verifica se o tamanho da pagina é o mesmo que o tamanho da pagina do banco de dados
    #Armazena na cache o dado recém escrito para evitar leituras desnecessárias
    def write_page(self, page_number, data):
        assert len(data) == self.page_size
        self.page_cache[page_number] = data
        self.file.seek(page_number * self.page_size)
        self.file.write(data)
        self.file.flush()

    #Aloca uma nova pagina no final do arquivo do banco de dados
    #O início da página é marcado com 0x00
    #Ele retorna o número de página
    def allocate_page(self):
        self.file.seek(0, os.SEEK_END)
        page_number = self.file.tell() // self.page_size
        self.write_page(page_number, b'\x00' * self.page_size)
        return page_number

#Classe que utilizaremos para armazenar tabelas e seus dados no banco de dados
class Table:
    def __init__(self, name, columns):
        self.name = name
        self.columns = columns
        self.page_number = None
        self.rows = []

#Aplicação da SimpleDB usando a classe Table para uma melhor organização de dados
class Database:
    #Inicializa o Database com um nome de arquivo dado
    def __init__(self, filename):
        self.db = SimpleDB(filename)
        self.tables = {}

    #Cria uma página com a tabela e suas colunas
    def create_table(self, name, columns):
        table = Table(name, columns)
        table.page_number = self.db.allocate_page()
        self.tables[name] = table

    #Insere uma linha na tabela especificada no fim da tabela
    def insert_into_table(self, table_name, values):
        table = self.tables[table_name]
        self._read_table(table) 
        table.rows.append(values)
        self._write_table(table)

    #Seleciona e retorna todas as linhas da tabela especificada
    def select_from_table(self, table_name):
        table = self.tables[table_name]
        self._read_table(table)
        return table.rows

    #Serializa as linhas da tabela e as escreve na página da tabela no banco de dados
    def _write_table(self, table):
        data = '\n'.join([','.join(map(str, row)) for row in table.rows]).encode().ljust(self.db.page_size, b'\x00')
        self.db.write_page(table.page_number, data)

    #Lê os dados da tabela de sua página no banco de dados e os deserializa em linhas
    def _read_table(self, table):
        data = self.db.read_page(table.page_number).rstrip(b'\x00').decode()
        if data:
            table.rows = [line.split(',') for line in data.split('\n')]

    #Seleciona e retorna uma linha específica da tabela especificada onde a coluna dada tem o valor especificado
    def select_row_from_table(self, table_name, column_name, value):
        table = self.tables[table_name]
        self._read_table(table)
        column_index = table.columns.index(column_name)
        for row in table.rows:
            if row[column_index] == value:
                return row
        return None

# --------------EXEMPLO DE USO----------------
database = Database('test.db')

# Cria uma tabela
database.create_table('mytable', ['id', 'data'])

# Insere dados
database.insert_into_table('mytable', [1, 'Hello World'])
database.insert_into_table('mytable', [2, 'Goodbye World'])

# Seleção de dados
print(database.select_from_table('mytable')) #Devolve todo o conteudo da tabela
print(database.select_row_from_table('mytable', 'id', '2')) #Devolve a linha onde o id é 2

# Fecha 
database.db.close()