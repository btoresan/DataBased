import tkinter as tk
from tkinter import filedialog, messagebox, font
import dataEngine as de

class DataBasedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Linux Games Database Search")
        self.root.geometry("600x400")
        
        # Initialize database as None
        self.db = None

        # Start with the first page
        self.start_page()

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
            color, quality = "blue", "Positive"
        elif score > 300:
            color, quality = "orange", "Mixed"
        else:
            color, quality = "red", "Negative"
        
        # Title for results page
        self.results_title = tk.Label(self.root, text=results[1], font=("Helvetica", 32))
        self.results_title.pack(pady=20)

        # Create a frame for the quality box
        self.quality_frame = tk.Frame(self.root, padx=10, pady=5)
        self.quality_frame.pack(pady=10)

        # Create the quality box
        self.quality_box = tk.Label(self.quality_frame, text=quality, font=("Helvetica", 16), padx=10, pady=5, bg=color)
        self.quality_box.pack(side=tk.LEFT)

        self.review_label = tk.Label(self.root, text=f"Positive: {results[-3]} | Negative: {results[-2]} | Score: {results[-1]}", font=("Helvetica", 16))
        self.review_label.pack(pady=10)

        # Go back to search button
        self.back_button = tk.Button(self.root, text="Back to Search", command=self.search_page, font=("Helvetica", 12))
        self.back_button.pack(pady=10)

        #A partir da qui os comentarios da pagina vvvvv

        self.all_comments = self.db.select_row_from_table('Comments', 'AppId', results[0])
        self.comments = self.all_comments

        self.button_frame = tk.Frame(self.root, pady=10, padx=10)
        self.button_frame.pack()

        # Create three buttons side by side
        self.tinker_button = tk.Button(self.button_frame, text="Show Only Tinker", command=self.tinker_only)
        self.tinker_button.pack(padx=5, side="left")

        self.works_button = tk.Button(self.button_frame, text="Show Only Works", command=self.works_only)
        self.works_button.pack(padx=5, side="left")

        self.order_button = tk.Button(self.button_frame, text="Order by Duration", command=self.order_by_duration)
        self.order_button.pack(padx=5, side="left")

        self.system_button = tk.Button(self.button_frame, text="Coments with SysInfo", command=self.only_sysinfo)
        self.system_button.pack(padx=5, side="left")

        self.reset_button = tk.Button(self.button_frame, text="Reset", command=self.reset_results)
        self.reset_button.pack(padx=5, side="left")

        self.stats = tk.Label(self.root, text=f"Found {len(self.comments)} comments", font=("Helvetica", 20))
        self.stats.pack(pady=20)

        self.canvas = tk.Canvas(self.root)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.frame = tk.Frame(self.canvas)

        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)      

        self.canvas.pack(side="left",fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.frame.bind("<Configure>", self._on_frame_configure)

        for comment in self.comments:
            self.comment_frame = tk.Frame(self.frame)
            self.label = tk.Label(self.comment_frame, text=f"Works : {comment[-2]} | SignificantBugs : {comment[3]} | Duration : {comment[4]} | Tinker : {comment[-3]}", font=("Helvetica", 16))
            self.button = tk.Button(self.comment_frame, text="View", command=lambda c=comment: self.view_comment(c), font=("Helvetica", 12))

            self.label.pack(side="left", padx=5)
            self.button.pack(side="right", padx=5)

            self.comment_frame.pack(fill="x", pady=2)

    def only_sysinfo(self):
        self.comments = [comment for comment in self.comments if comment[10] != {}]

        self.stats = tk.Label(self.root, text=f"Filtered by System Info ({len(self.comments)} comments)", font=("Helvetica", 20))
        self.stats.pack(pady=20)

        # Destroy all comment widgets
        for widget in self.frame.winfo_children():
            widget.destroy()

        for comment in self.comments:
            self.comment_frame = tk.Frame(self.frame)
            self.label = tk.Label(self.comment_frame, text=f"Works : {comment[-2]} | SignificantBugs : {comment[3]} | Duration : {comment[4]} | Tinker : {comment[-3]}", font=("Helvetica", 16))
            self.button = tk.Button(self.comment_frame, text="View", command=lambda c=comment: self.view_comment(c), font=("Helvetica", 12))

            self.label.pack(side="left", padx=5)
            self.button.pack(side="right", padx=5)

            self.comment_frame.pack(fill="x", pady=2)

    def tinker_only(self):
        self.comments = [comment for comment in self.comments if comment[-3] == True]

        self.stats = tk.Label(self.root, text=f"Filtered by Tinker ({len(self.comments)} comments)", font=("Helvetica", 20))
        self.stats.pack(pady=20)

        # Destroy all comment widgets
        for widget in self.frame.winfo_children():
            widget.destroy()

        for comment in self.comments:
            self.comment_frame = tk.Frame(self.frame)
            self.label = tk.Label(self.comment_frame, text=f"Works : {comment[-2]} | SignificantBugs : {comment[3]} | Duration : {comment[4]} | Tinker : {comment[-3]}", font=("Helvetica", 16))
            self.button = tk.Button(self.comment_frame, text="View", command=lambda c=comment: self.view_comment(c), font=("Helvetica", 12))

            self.label.pack(side="left", padx=5)
            self.button.pack(side="right", padx=5)

            self.comment_frame.pack(fill="x", pady=2)

    def works_only(self):
        self.comments = [comment for comment in self.comments if comment[-2] == True]

        self.stats = tk.Label(self.root, text=f"Filtered by Works ({len(self.comments)} comments)", font=("Helvetica", 20))
        self.stats.pack(pady=20)

        # Destroy all comment widgets
        for widget in self.frame.winfo_children():
            widget.destroy()

        for comment in self.comments:
            self.comment_frame = tk.Frame(self.frame)
            self.label = tk.Label(self.comment_frame, text=f"Works : {comment[-2]} | SignificantBugs : {comment[3]} | Duration : {comment[4]} | Tinker : {comment[-3]}", font=("Helvetica", 16))
            self.button = tk.Button(self.comment_frame, text="View", command=lambda c=comment: self.view_comment(c), font=("Helvetica", 12))

            self.label.pack(side="left", padx=5)
            self.button.pack(side="right", padx=5)

            self.comment_frame.pack(fill="x", pady=2)

    def order_by_duration(self):

        self.comments = [comment for comment in self.comments if comment[4] != ""]
        self.comments = sorted(self.comments, key=lambda x: x[4])

        self.stats = tk.Label(self.root, text=f"Ordered by Duration ({len(self.comments)} comments)", font=("Helvetica", 20))
        self.stats.pack(pady=20)

        # Destroy all comment widgets
        for widget in self.frame.winfo_children():
            widget.destroy()

        for comment in self.comments:
            self.comment_frame = tk.Frame(self.frame)
            self.label = tk.Label(self.comment_frame, text=f"Works : {comment[-2]} | SignificantBugs : {comment[3]} | Duration : {comment[4]} | Tinker : {comment[-3]}", font=("Helvetica", 16))
            self.button = tk.Button(self.comment_frame, text="View", command=lambda c=comment: self.view_comment(c), font=("Helvetica", 12))

            self.label.pack(side="left", padx=5)
            self.button.pack(side="right", padx=5)

            self.comment_frame.pack(fill="x", pady=2)

    def reset_results(self):

        self.comments = self.all_comments

        # Destroy all comment widgets
        for widget in self.frame.winfo_children():
            widget.destroy()

        self.stats = tk.Label(self.root, text=f"Reset ({len(self.comments)} comments)", font=("Helvetica", 20))
        self.stats.pack(pady=20)

        for comment in self.comments:
            self.comment_frame = tk.Frame(self.frame)
            self.label = tk.Label(self.comment_frame, text=f"Works : {comment[-2]} | SignificantBugs : {comment[3]} | Duration : {comment[4]} | Tinker : {comment[-3]}", font=("Helvetica", 16))
            self.button = tk.Button(self.comment_frame, text="View", command=lambda c=comment: self.view_comment(c), font=("Helvetica", 12))

            self.label.pack(side="left", padx=5)
            self.button.pack(side="right", padx=5)

            self.comment_frame.pack(fill="x", pady=2)

    def view_comment(self, comment):
        self.root.title("Comment Details")

        for widget in self.root.winfo_children():
            widget.destroy()

        self.back_button = tk.Button(self.root, text="Back to Search", command=self.search_page, font=("Helvetica", 12))
        self.back_button.pack(pady=10)

        comment_id_label = tk.Label(self.root, text=f"Comment ID: {comment[0]}", font=("Helvetica", 16), fg="white")
        comment_id_label.pack(pady=5, anchor="w")

        app_id_label = tk.Label(self.root, text=f"App ID: {comment[1]}", font=("Helvetica", 16), fg="white")
        app_id_label.pack(pady=5, anchor="w")

        time_label = tk.Label(self.root, text=f"Time: {comment[2]}", font=("Helvetica", 16), fg="white")
        time_label.pack(pady=5, anchor="w")

        significant_bugs_label = tk.Label(self.root, text=f"Significant Bugs: {comment[3]}", font=("Helvetica", 16), fg="white")
        significant_bugs_label.pack(pady=5, anchor="w")

        duration_label = tk.Label(self.root, text=f"Duration: {comment[4]}", font=("Helvetica", 16), fg="white")
        duration_label.pack(pady=5, anchor="w")

        installs_label = tk.Label(self.root, text=f"Installs: {comment[5]}", font=("Helvetica", 16), fg="white")
        installs_label.pack(pady=5, anchor="w")

        opens_label = tk.Label(self.root, text=f"Opens: {comment[6]}", font=("Helvetica", 16), fg="white")
        opens_label.pack(pady=5, anchor="w")

        performance_faults_label = tk.Label(self.root, text=f"Performance Faults: {comment[7]}", font=("Helvetica", 16), fg="white")
        performance_faults_label.pack(pady=5, anchor="w")

        tinker_label = tk.Label(self.root, text=f"Tinker: {comment[8]}", font=("Helvetica", 16), fg="white")
        tinker_label.pack(pady=5, anchor="w")

        verdict_label = tk.Label(self.root, text=f"Verdict: {comment[9]}", font=("Helvetica", 16), fg="white")
        verdict_label.pack(pady=5, anchor="w")

        if comment[10] != {}:
            sysinfo_label = tk.Label(self.root, text="System Info:", font=("Helvetica", 16), fg="white")
            for key in comment[10].keys():
                sysinfo_label = tk.Label(self.root, text=f"     {key}: {comment[10][key]}", font=("Helvetica", 16), fg="white")
                sysinfo_label.pack(pady=5, anchor="w")
        

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))  
        
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
    root = tk.Tk()
    app = DataBasedApp(root)
    root.mainloop()
