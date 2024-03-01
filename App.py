import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from tkcalendar import Calendar
from datetime import datetime
import pandas as pd

class Node:
    def __init__(self, name, appointment_time, phone, blood_type):
        self.name = name
        self.appointment_time = appointment_time
        self.phone = phone
        self.blood_type = blood_type
        self.next = None

class DonorDeque:
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_donor(self, name, appointment_time, phone, blood_type):
        new_node = Node(name, appointment_time, phone, blood_type)
        if not self.head:
            self.head = self.tail = new_node
            return

        new_time = datetime.strptime(appointment_time, '%d-%m-%Y %H:%M')

        current = self.head
        previous = None
        while current:
            current_time = datetime.strptime(current.appointment_time, '%d-%m-%Y %H:%M')
            if current_time > new_time:
                break
            elif current_time == new_time:
                previous = current
                current = current.next
                continue
            else:
                previous = current
                current = current.next

        if not previous:
            new_node.next = self.head
            self.head = new_node
        else:
            new_node.next = current
            previous.next = new_node
            if new_node.next is None:
                self.tail = new_node

    def remove_donor(self):
        if self.head:
            removed_donor = self.head
            self.head = self.head.next
            if self.head is None:
                self.tail = None
            return removed_donor
        else:
            return None

    def insert_urgent_donor(self, name, appointment_time, phone, blood_type):
        new_node = Node(name, appointment_time, phone, blood_type)
        new_node.next = self.head
        self.head = new_node
        if not self.tail:
            self.tail = new_node

    def search_appointment_time(self, name):
        current = self.head
        appointments = []
        while current:
            if current.name == name:
                appointments.append(current.appointment_time)
            current = current.next
        return appointments

    def remove_donor_by_name(self, name):
        current = self.head
        previous = None
        while current:
            if current.name == name:
                if previous:
                    previous.next = current.next
                    if current.next is None:
                        self.tail = previous
                else:
                    self.head = current.next
                    if self.head is None:
                        self.tail = None
                return True
            previous = current
            current = current.next
        return False

    def search_by_phone(self, phone):
        current = self.head
        while current:
            if current.phone == phone:
                return True, current.name, current.appointment_time, current.blood_type
            current = current.next
        return False, None, None, None

class DonorQueueUI:
    def __init__(self, master):
        self.master = master
        self.donor_queue = DonorDeque()
        self.setup_ui()
        
        master = tk.Tk()  # Define the "master" variable
        master.title("Blood Donor Management System")
        style = ttk.Style()
        style.theme_use('clam')  

        # Main frame for better organization
        self.frame = ttk.Frame(master, padding="10 10 10 10")
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.label = ttk.Label(self.frame, text="Blood Donors:")
        self.label.grid(row=0, column=0, sticky="W", pady=5)

        # Setup for Treeview
        self.donor_treeview = ttk.Treeview(self.frame, columns=("Number", "Name", "Date", "Phone", "Blood"), show="headings", height=100)
        self.donor_treeview.grid(row=1, column=0, columnspan=4, pady=5, sticky=(tk.W, tk.E))
        
        # Define the headings and column configuration
        self.donor_treeview.heading("Number", text="Number")
        self.donor_treeview.heading("Name", text="Name")
        self.donor_treeview.heading("Date", text="Date")
        self.donor_treeview.heading("Phone", text="Phone")
        self.donor_treeview.heading("Blood", text="Blood Type")

        # Set the column width and anchor for each column
        self.donor_treeview.column("Number", width=50, anchor="center")
        self.donor_treeview.column("Name", width=100, anchor="center")
        self.donor_treeview.column("Date", width=100, anchor="center")
        self.donor_treeview.column("Phone", width=100, anchor="center")
        self.donor_treeview.column("Blood", width=80, anchor="center")

        # Adjust the scrollbar for the Treeview
        self.donor_list_box_scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.donor_treeview.yview)
        self.donor_list_box_scrollbar.grid(row=1, column=4, sticky='ns', pady=5)
        self.donor_treeview.config(yscrollcommand=self.donor_list_box_scrollbar.set)
        
        # Name Entry with Placeholder Text
        self.name_label = ttk.Label(self.frame, text="Name:")
        self.name_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(self.frame, width=20)  # Adjust width as needed
        self.name_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Combined Date and Time Picker - Enhanced
        self.datetime_label = ttk.Label(self.frame, text="Appointment Date and Time:")
        self.datetime_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        self.datetime_entry = ttk.Entry(self.frame, width=20)  # Adjust width as needed
        self.datetime_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        self.pick_datetime_button = ttk.Button(self.frame, text="Pick Date and Time", command=self.pick_datetime)
        self.pick_datetime_button.grid(row=3, column=2, sticky=tk.W, padx=5, pady=5)

        # Add Donor Button
        self.add_button = ttk.Button(self.frame, text="Add Donor", command=self.add_donor)
        self.add_button.grid(row=8, column=0, pady=5, sticky=tk.W)
        
        # Add Urgent Donor Button
        self.add_urgent_button = ttk.Button(self.frame, text="Add Urgent Donor", command=self.add_urgent_donor)
        self.add_urgent_button.grid(row=8, column=1, pady=5, sticky=tk.W)
        
        # Remove Donor Button
        self.remove_button = ttk.Button(self.frame, text="Remove Donor", command=self.remove_donor)
        self.remove_button.grid(row=5, column=2, pady=5, sticky=tk.W)

        # Search Appointment
        self.search_button = ttk.Button(self.frame, text="Search Appointment", command=self.search_appointment)
        self.search_button.grid(row=6, column=0, pady=5, sticky=tk.W)
        self.search_entry = ttk.Entry(self.frame, width=20)  # Adjust width as needed
        self.search_entry.grid(row=6, column=1, pady=5, sticky=(tk.W, tk.E))

        # Configure the grid to be more responsive
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(1, weight=1)
        
        # Phone Entry with Placeholder Text
        self.phone_label = ttk.Label(self.frame, text="Phone Number:")
        self.phone_label.grid(row=4, column=0, sticky=tk.W, pady=5)  # Điều chỉnh hàng/cột theo cấu trúc của bạn
        self.phone_entry = ttk.Entry(self.frame, width=20)  # Adjust width as needed
        self.phone_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)  # Điều chỉnh hàng/cột theo cấu trúc của bạn
        
        # Import and Export Buttons
        self.import_button = ttk.Button(self.frame, text="Import from Excel", command=self.import_from_excel)
        self.import_button.grid(row=0, column=1, pady=5, sticky=tk.W)
        
        # Export to Excel Button
        self.export_button = ttk.Button(self.frame, text="Export to Excel", command=self.export_to_excel)
        self.export_button.grid(row=0, column=2, pady=5, sticky=tk.W)
        
        # Blood Type Combobox
        self.blood_type_label = ttk.Label(self.frame, text="Blood Type:")
        self.blood_type_label.grid(row=5, column=0, sticky=tk.W, pady=1)  # Adjust grid positioning as needed
        self.blood_type_combobox = ttk.Combobox(self.frame, 
                                                values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        self.blood_type_combobox.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
                
        # Search by Phone
        self.search_phone_entry = ttk.Entry(self.frame, width=20)
        self.search_phone_entry.grid(row=7, column=1, pady=5, sticky=(tk.W, tk.E))
        self.search_phone_button = ttk.Button(self.frame, text="Search Phone", command=self.search_by_phone)
        self.search_phone_button.grid(row=7, column=0, pady=5, sticky=tk.W)
        
        # Filter by Blood Type
        self.donor_treeview.heading("Blood", text="Blood Type", command=lambda: self.ask_blood_type_filter())
             
    def ask_blood_type_filter(self):
        top = tk.Toplevel(self.master)
        top.title("Filter by Blood Type")

        tk.Label(top, text="Select a Blood Type:").pack(pady=10)

        # Create a Combobox with blood types
        blood_type_var = tk.StringVar()
        blood_type_combobox = ttk.Combobox(top, textvariable=blood_type_var, 
                                       values=["All", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        blood_type_combobox.pack(pady=5)
        blood_type_combobox.current(0)  # Default to 'All'

        # Button to apply the filter
        apply_button = ttk.Button(top, text="Apply Filter", command=lambda: self.apply_blood_type_filter(blood_type_var.get(), top))
        apply_button.pack(pady=10)
        
    def apply_blood_type_filter(self, filtered_blood_type, top=None):
        for item in self.donor_treeview.get_children():
            self.donor_treeview.delete(item)
    
        current = self.donor_queue.head
        count = 1  # Initialize counter for numbering
        while current:
            if filtered_blood_type == "All" or current.blood_type == filtered_blood_type:
                self.donor_treeview.insert("", tk.END, values=(count, current.name, current.appointment_time, current.phone, current.blood_type))
            current = current.next
            count += 1

        if top:  # Close the pop-up window if it's open
            top.destroy()

    def pick_datetime(self):
        def set_datetime():
            selected_date = cal.selection_get().strftime('%d-%m-%Y')
            selected_time = f"{hour_var.get()}:{minute_var.get()}"
            self.datetime_entry.delete(0, tk.END)
            self.datetime_entry.insert(0, f"{selected_date} {selected_time}")
            top.destroy()

        top = tk.Toplevel(self.master)
        cal = Calendar(top, selectmode='day', date_pattern='dd-mm-y')
        cal.pack(pady=10)

        # Time selection
        hour_var = tk.StringVar()
        minute_var = tk.StringVar()
        hour_cb = ttk.Combobox(top, textvariable=hour_var, values=[f"{i:02d}" for i in range(24)], width=5)
        minute_cb = ttk.Combobox(top, textvariable=minute_var, values=[f"{i:02d}" for i in range(60)], width=5)
        hour_cb.pack()
        minute_cb.pack()

        ok_button = tk.Button(top, text="OK", command=set_datetime)
        ok_button.pack()

    def validate_datetime(self, datetime_str):
        """Validate the datetime format '%Y-%m-%d %H:%M'."""
        try:
            datetime.strptime(datetime_str, '%d-%m-%Y %H:%M')
            return True
        except ValueError:
            return False

    def add_donor(self):
        name = self.name_entry.get()
        datetime_str = self.datetime_entry.get() 
        phone = self.phone_entry.get()
        blood_type = self.blood_type_combobox.get()
        if self.validate_datetime(datetime_str) and blood_type:
            self.donor_queue.insert_donor(name, datetime_str, phone, blood_type)
            self.refresh_list()
        else:
            messagebox.showerror("Please enter all entry", "Please ensure the datetime is in the format DD-MM-YYYY HH:MM.")
 
    def refresh_list(self, filtered_blood_type="All"):
        for item in self.donor_treeview.get_children():
            self.donor_treeview.delete(item)
    
        current = self.donor_queue.head
        count = 1  # Initialize counter for numbering
        while current:
            if filtered_blood_type == "All" or current.blood_type == filtered_blood_type:
                self.donor_treeview.insert("", tk.END, values=(count, current.name, current.appointment_time, current.phone, current.blood_type))
            current = current.next
            count += 1

    def add_urgent_donor(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        blood_type = self.blood_type_combobox.get()
        # Use the current datetime for the urgent donor
        now = datetime.now()
        datetime_str = now.strftime('%d-%m-%Y %H:%M')  # Format the datetime string

        # No need to validate datetime since we're generating it programmatically
        self.donor_queue.insert_urgent_donor(name, datetime_str, phone, blood_type)
        self.refresh_list()

    def remove_donor(self):
        selected_items = self.donor_treeview.selection()
        if selected_items:
            # If any items are selected, remove those specific donors by name
            for selected_item in selected_items:
                item_data = self.donor_treeview.item(selected_item, 'values')
                selected_name = item_data[1]  # Name is the second value
                self.donor_queue.remove_donor_by_name(selected_name)
        else:
            # If no items are selected, remove the top donor
            self.donor_queue.remove_donor()
        self.refresh_list()
  
    def search_appointment(self):
        name = self.search_entry.get()
        appointments = self.donor_queue.search_appointment_time(name)
        if appointments:
            appointments_str = "\n".join(appointments)
            messagebox.showinfo("Search Result", f"{name}'s Appointment Times:\n{appointments_str}")
        else:
            messagebox.showinfo("Search Result", "No appointments found for this name.")
    
    def import_from_excel(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if filename:
            try:
                df = pd.read_excel(filename)
                for index, row in df.iterrows():
                    self.donor_queue.insert_donor(row['Name'], row['Appointment Time'], row['Phone'], row['Blood Type'])
                self.refresh_list()
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import from Excel.\nError: {e}")

    def export_to_excel(self):
        filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if filename:
            try:
                data = []
                current = self.donor_queue.head
                while current:
                    data.append([current.name, current.appointment_time, current.phone, current.blood_type])
                    current = current.next
                df = pd.DataFrame(data, columns=['Name', 'Appointment Time', 'Phone', 'Blood Type'])
                df.to_excel(filename, index=False)
                messagebox.showinfo("Export Successful", "Data exported to Excel file successfully.")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export to Excel.\nError: {e}")
                
    def search_by_phone(self):
        phone = self.search_phone_entry.get()
        found, name, appointment_time, blood_type = self.donor_queue.search_by_phone(phone)
        if found:
            messagebox.showinfo("Search Result", f"Name: {name}\nAppointment Time: {appointment_time}\nBlood Type: {blood_type}")
        else:
            messagebox.showinfo("Search Result", "No donor found with this phone number.")
  
# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = DonorQueueUI(root)
    root.mainloop()
