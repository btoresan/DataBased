import tkinter as tk
from tkinter import filedialog, messagebox
import dataEngine as de

class DataBasedApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Linux Games Database Search")
        self.root.geometry("600x400")
        
        # Initialize database as None
        self.db = None
        
        # Start with the first page
        self.start_page()

        self.root.mainloop()

    def start_page(self):
        # Clear the window if it's not the first page
        for widget in self.root.winfo_children():
            widget.destroy()

        # Title for the start page
        title_label = tk.Label(self.root, text="DataBased", font=("Helvetica", 64))
        title_label.pack(pady=20)

        # Create the start page with the Open Database button
        open_button = tk.Button(self.root, text="Open Database", command=self.open_db, width=20, height=3, font=("Helvetica", 16))
        open_button.pack(expand=True)
    
    def search_page(self):
        # Clear the window for the search page
        for widget in self.root.winfo_children():
            widget.destroy()

        # Title for search page
        search_title = tk.Label(self.root, text="Search DataBased", font=("Helvetica", 42))
        search_title.pack(pady=20)

        # Create a frame to hold the radiobuttons
        mode_frame = tk.Frame(self.root)
        mode_frame.pack(pady=(10, 5), expand=True)  # Adjust top and bottom padding

        # Variable to hold the search mode
        self.search_mode = tk.StringVar(value="Name")  # Default to Name

        # Create radiobuttons for selecting search mode
        rb_name = tk.Radiobutton(mode_frame, text="Search by Name", variable=self.search_mode, value="Name", font=("Helvetica", 12))
        rb_name.pack(side=tk.LEFT, padx=5)

        rb_appid = tk.Radiobutton(mode_frame, text="Search by AppID", variable=self.search_mode, value="AppID", font=("Helvetica", 12))
        rb_appid.pack(side=tk.LEFT, padx=5)

        # Create a frame to hold the search entry and button
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=(5, 30), expand=True)  # Adjust top and bottom padding

        # Create the search entry widget
        self.search_entry = tk.Entry(search_frame, font=("Helvetica", 16), width=50)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))

        # Bind Enter key to search button click
        self.search_entry.bind("<Return>", lambda event: self.results_page())

        # Create the search button widget
        search_button = tk.Button(search_frame, text="Search", command=self.results_page, font=("Helvetica", 12))
        search_button.pack(side=tk.LEFT)

        # Center the frames in the window
        self.root.update_idletasks()  # Update the window to get accurate dimensions
        frame_width = search_frame.winfo_reqwidth()
        frame_height = search_frame.winfo_reqheight() + mode_frame.winfo_reqheight()  # Include both frames
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        x = (window_width - frame_width) // 2
        y = ((window_height - frame_height) // 2)  # Adjust vertical position to be higher
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def results_page(self):
        query = self.search_entry.get()
        search_mode = self.search_mode.get() # "AppID" or "Name"

        if not query:
            messagebox.showwarning("Empty Query", "Please enter a search term.")
            return
        
        # Clear the window for the results page
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Makes the search
        if search_mode == "Title":
            query = self.db.select_row_from_table('Index', 'Title', query)[1]
        results = self.db.select_row_from_table('Games', "AppID", query)
        
        if len(results) == 0:
            messagebox.showwarning("No Results", "No results found.")
            self.search_page()
            return
        if len(results) > 1:
            messagebox.showwarning("Multiple Results", "Multiple results found. Try searching by AppID.")
            self.search_page()
            return

        results = results[0]
        score = results[4]

        if score > 900:
            color, quality = "green", "Very Positive"
        elif score > 600:
            color, quality = "yellow", "Positive"
        elif score > 300:
            color, quality = "orange", "Mixed"
        else:
            color, quality = "red", "Negative"
        
        # Title for results page
        results_title = tk.Label(self.root, text=results[1], font=("Helvetica", 32))
        results_title.pack(pady=20)

        # Create a frame for the quality box
        quality_frame = tk.Frame(self.root, padx=10, pady=5)
        quality_frame.pack(pady=10)

        # Create the quality box
        quality_box = tk.Label(quality_frame, text=quality, font=("Helvetica", 16), padx=10, pady=5, bg=color)
        quality_box.pack(side=tk.LEFT)

        # Go back to search button
        back_button = tk.Button(self.root, text="Back to Search", command=self.search_page, font=("Helvetica", 12))
        back_button.pack(pady=10)

        comments = self.db.select_row_from_table('Comments', 'AppId', results[0])

        # Get the first 50 comments
        first_50_comments = comments[:50]

        comments_frame = tk.Frame(self.root)
        comments_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Create a label and button for each comment
        for i, comment in enumerate(first_50_comments):
            text = tk.Label(comments_frame, text=f"{comment[2]}: {comment[9]}", wraplength=500, justify=tk.LEFT)
            text.grid(row=i, column=0, padx=5, pady=5, sticky='w')
            
            button = tk.Button(comments_frame, text=f"Button")
            button.grid(row=i, column=1, padx=5, pady=5)

    def show_results_page(self):
        # Retrieve the query from the search entry
        query = self.search_entry.get()
        search_mode = self.search_mode.get() # "AppID" or "Name"

        if not query:
            messagebox.showwarning("Empty Query", "Please enter a search term.")
            return
        
        # Clear the window for the results page
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Title for results page
        results_title = tk.Label(self.root, text=f"Results for '{query}'", font=("Helvetica", 16))
        results_title.pack(pady=20)

        # Create frame for search results
        results_frame = tk.Frame(self.root)
        results_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, height=15)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Go back to search button
        back_button = tk.Button(self.root, text="Back to Search", command=self.search_page, font=("Helvetica", 12))
        back_button.pack(pady=10)

        # Simulate search operation (Replace this with actual search logic)
        results = self.db.select_row_from_table('Games', 'Title', query)
        self.results_text.delete(1.0, tk.END)
        if results:
            for result in results:
                self.results_text.insert(tk.END, f"{result}\n")
        else:
            self.results_text.insert(tk.END, "No results found.")
    
    def open_db(self):
        db_path = filedialog.askopenfilename(
            title="Open Database",
            filetypes=(("Database Files", "*.db"), ("All Files", "*.*"))
        )
        if db_path:
            try:
                self.db = de.Database(db_path)
                self.search_page()  # Move to the search page
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    app = DataBasedApp()
