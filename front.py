import tkinter as tk
from tkinter import filedialog
import dataEngine as de

class DataBasedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DataBased")
        self.database_path = None

        # Main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        self.db = None

        # Create the initial menu
        self.create_initial_menu()

    def create_initial_menu(self):
        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Reset the window title
        self.root.title("DataBased")

        # Create and pack the initial menu label
        label = tk.Label(self.main_frame, text="DataBased", font=("Arial", 24))
        label.pack(pady=20)

        # Create the open button
        open_button = tk.Button(self.main_frame, text="Open Database", command=self.open_database)
        open_button.pack(pady=5)

    def open_database(self):
        self.database_path = filedialog.askopenfilename(
            title="Select Any File",
            filetypes=(("All files", "*.*"),)
        )
        if self.database_path:
            try:    
                self.db = de.Database(self.database_path)
                self.create_main_menu()
            except Exception as e:
                print(e)
                self.database_path = None
                self.error_message("Invalid Database File")

    def create_main_menu(self):
        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Reset the window title
        self.root.title("DataBased")

        # Create and pack the main menu label
        label = tk.Label(self.main_frame, text="DataBased", font=("Arial", 24))
        label.pack(pady=20)

        # Operation names
        operations = ["PEEK", "SELECT", "INSERT", "EDIT", "REMOVE"]

        # Create navigation buttons
        for operation in operations:
            button = tk.Button(self.main_frame, text=operation, command=lambda operation=operation: self.show_page(operation))
            button.pack(pady=5)

        # Create the close button
        close_button = tk.Button(self.main_frame, text="Close Database", command=self.close_database)
        close_button.pack(pady=5)

    def close_database(self):
        self.database_path = None
        self.create_initial_menu()

    def show_page(self, operation):
        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Set the window title to the operation
        self.root.title(f"{operation}")

        # Call the appropriate function for the selected operation
        if operation == "PEEK":
            self.show_peek_page()
        elif operation == "SELECT":
            self.show_select_page()
        elif operation == "INSERT":
            self.show_insert_page()
        elif operation == "EDIT":
            self.show_edit_page()
        elif operation == "REMOVE":
            self.show_remove_page()

    def error_message(self, message):
        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Create and pack the error message label
        label = tk.Label(self.main_frame, text=message, font=("Arial", 24))
        label.pack(pady=20)

        # Create the back button
        back_button = tk.Button(self.main_frame, text="Back", command=self.create_initial_menu)
        back_button.pack(pady=5)

    def show_peek_page(self):
        label = tk.Label(self.main_frame, text="PEEK Page", font=("Arial", 24))
        label.pack(pady=20)

        tables = list(self.db.tables.keys())
        table = tables[0]

        data = list(self.db.peek_table(table, 'id'))

        # Create a text widget to display the data
        text_widget = tk.Text(self.main_frame, height=10, width=50)
        text_widget.pack(pady=10)

        # Get the data from the database
        data = self.db.peek_table(table, 'id')

        # Display the data in the text widget
        for row in data:
            text_widget.insert(tk.END, f"{row}\n")

        # Create the back button
        back_button = tk.Button(self.main_frame, text="Close", command=self.create_main_menu)
        back_button.pack(pady=5)

    def show_select_page(self):
        label = tk.Label(self.main_frame, text="SELECT Page", font=("Arial", 24))
        label.pack(pady=20)

        # Here you can add the SELECT-specific code

        back_button = tk.Button(self.main_frame, text="Close", command=self.create_main_menu)
        back_button.pack(pady=5)

    def show_insert_page(self):
        label = tk.Label(self.main_frame, text="INSERT Page", font=("Arial", 24))
        label.pack(pady=20)

        # Todo add the INSERT-specific code

        back_button = tk.Button(self.main_frame, text="Close", command=self.create_main_menu)
        back_button.pack(pady=5)

    def show_edit_page(self):
        label = tk.Label(self.main_frame, text="EDIT Page", font=("Arial", 24))
        label.pack(pady=20)

        # Todo add the EDIT-specific code

        back_button = tk.Button(self.main_frame, text="Close", command=self.create_main_menu)
        back_button.pack(pady=5)

    def show_remove_page(self):
        label = tk.Label(self.main_frame, text="REMOVE Page", font=("Arial", 24))
        label.pack(pady=20)

        # Todo add the REMOVE-specific code

        back_button = tk.Button(self.main_frame, text="Close", command=self.create_main_menu)
        back_button.pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = DataBasedApp(root)
    root.geometry("400x300")  # Set the window size
    root.mainloop()
