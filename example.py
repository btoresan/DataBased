from dataEngine import Database

# Example usage
db = Database('example.db')

# Create a table
db.create_table('employees', ['id', 'name', 'age'])

# Insert rows into the table
db.insert_into_table('employees', [1, 'John Doe', 30])
#make sure no primary key duplicates
db.insert_into_table('employees', [1, 'Cooler John Doe ', 25])

db.insert_into_table('employees', [2, 'Jane Smith', 25])
db.insert_into_table('employees', [3, 'Bob Johnson', 35])
db.insert_into_table('employees', [4, 'Alice Brown', 28])
db.insert_into_table('employees', [5, 'Charlie Davis', 40])
db.insert_into_table('employees', [6, 'Diana Evans', 22])
db.insert_into_table('employees', [7, 'Ethan Foster', 33])
db.insert_into_table('employees', [8, 'Fiona Green', 29])
db.insert_into_table('employees', [9, 'George Harris', 45])
db.insert_into_table('employees', [10, 'Hannah Irving', 31])
db.insert_into_table('employees', [11, 'Ian Johnson', 27])
db.insert_into_table('employees', [12, 'Jackie King', 36])
db.insert_into_table('employees', [13, 'Kevin Lee', 38])
db.insert_into_table('employees', [14, 'Laura Martinez', 26])
db.insert_into_table('employees', [15, 'Michael Nelson', 32])

print(db.peek_table('employees', 'age'))

# Visualize the table as a B-tree
db.visualize_table('employees')

# Print all rows in the table
print(db.peek_table('employees', 'id'))

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

