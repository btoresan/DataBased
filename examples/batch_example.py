from dataEngine import Database

# Example usage
db = Database('example_batch.db')

db.create_table('employees', ['id', 'name', 'age'])

values = [
    [1, 'John Doe', 30],
    [2, 'Jane Smith', 25],
    [3, 'Bob Johnson', 35],
    [4, 'Alice Brown', 28],
    [5, 'Charlie Davis', 40],
    [6, 'Diana Evans', 22],
    [7, 'Ethan Foster', 33],
    [8, 'Fiona Green', 29],
    [9, 'George Harris', 45],
    [10, 'Hannah Irving', 31],
    [11, 'Ian Johnson', 27],
    [12, 'Jackie King', 36],
    [13, 'Kevin Lee', 38],
    [14, 'Laura Martinez', 26],
    [15, 'Michael Nelson', 32]
]

db.insert_into_table_batch('employees', values)

print(db.peek_table('employees', 'id'))