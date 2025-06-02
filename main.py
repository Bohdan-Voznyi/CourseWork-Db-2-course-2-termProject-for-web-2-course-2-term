import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
import uuid
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

class DatabaseManager:
    def __init__(self):
        self.connection_string = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=localhost;"
            "Database=insuranceSystem;"
            "UID=sa;"
            "PWD=1234;"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
            "Connection Timeout=30;"
        )
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.conn = pyodbc.connect(self.connection_string)
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            messagebox.showerror("Database Error", f"Connection failed: {str(e)}")
            return False

    def execute_sp(self, sp_name, params=None):
        try:
            if not self.conn:
                if not self.connect():
                    return None

            if params:
                placeholders = ", ".join(["?"] * len(params))
                query = f"EXEC {sp_name} {placeholders}"
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(f"EXEC {sp_name}")

            if self.cursor.description:
                result = self.cursor.fetchall()
                self.conn.commit()
                return result
            else:
                self.conn.commit()
                return True
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Database Error", f"Error in {sp_name}: {str(e)}")
            return None

    def close(self):
        if self.conn:
            self.conn.close()

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Insurance System - Login")
        self.root.geometry("400x200")
        
        self.db = DatabaseManager()
        
        # Login Form
        login_frame = ttk.Frame(self.root, padding="20")
        login_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.username_entry = ttk.Entry(login_frame, width=30)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.password_entry = ttk.Entry(login_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        button_frame = ttk.Frame(login_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Login", command=self.login).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.root.destroy).pack(side=tk.LEFT, padx=5)
        
        self.username_entry.focus_set()
        
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Validation Error", "Please enter both username and password")
            return
        
        try:
            result = self.db.execute_sp("sp_AuthenticateUser", (username, password))
            if result:
                role = result[0][2]
                self.root.destroy()
                root = tk.Tk()
                app = InsuranceSystemApp(root, role, self.db)
                root.mainloop()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")
        except Exception as e:
            messagebox.showerror("Database Error", f"Login error: {str(e)}")

class InsuranceSystemApp:
    def __init__(self, root, user_role, db):
        self.root = root
        self.user_role = user_role
        self.db = db
        self.root.title(f"Insurance System - {user_role}")
        self.root.geometry("1200x800")
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        if self.user_role == "Admin":
            self.create_client_tab()
            self.create_employee_tab()
            self.create_vehicle_tab()
            self.create_policy_tab()
            self.create_claim_tab()
            self.create_payment_tab()
        
        self.create_reports_tab()
        
        logout_button = ttk.Button(root, text="Logout", command=self.logout)
        logout_button.pack(side=tk.BOTTOM, pady=10)

    def logout(self):
        self.db.close()
        self.root.destroy()
        root = tk.Tk()
        LoginWindow(root)
        root.mainloop()

    # Client Tab
    def create_client_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Clients")
        
        # Client List
        client_list_frame = ttk.LabelFrame(tab, text="Client List")
        client_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.client_tree = ttk.Treeview(client_list_frame, columns=("ID", "Full Name", "Address", "Phone", "Email", "Passport"), show="headings")
        for col in self.client_tree["columns"]:
            self.client_tree.heading(col, text=col)
            self.client_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(client_list_frame, orient="vertical", command=self.client_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.client_tree.configure(yscrollcommand=scrollbar.set)
        self.client_tree.pack(fill=tk.BOTH, expand=True)
        
        # Client Form
        client_form_frame = ttk.LabelFrame(tab, text="Client Form")
        client_form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        labels = ["Full Name:", "Address:", "Phone:", "Email:", "Passport Number:"]
        self.client_entries = {}
        
        for i, text in enumerate(labels):
            ttk.Label(client_form_frame, text=text).grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            entry = ttk.Entry(client_form_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.client_entries[text.split(":")[0].lower().replace(" ", "_")] = entry
        
        # Buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Add", command=self.add_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update", command=self.update_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_client_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_clients).pack(side=tk.LEFT, padx=5)
        
        self.client_tree.bind("<<TreeviewSelect>>", self.on_client_select)
        self.refresh_clients()

    def add_client(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can add clients")
            return
            
        data = {k: v.get() for k, v in self.client_entries.items()}
        if not all(data.values()):
            messagebox.showwarning("Validation Error", "All fields are required")
            return
        
        client_id = str(uuid.uuid4())
        params = (client_id, data['full_name'], data['address'], data['phone'], data['email'], data['passport_number'])
        
        if self.db.execute_sp("sp_AddClient", params):
            self.refresh_clients()
            self.clear_client_form()

    def update_client(self):
        selected = self.client_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a client")
            return
            
        client_id = self.client_tree.item(selected[0], "values")[0]
        data = {k: v.get() for k, v in self.client_entries.items()}
        
        if not all(data.values()):
            messagebox.showwarning("Validation Error", "All fields are required")
            return
        
        params = (client_id, data['full_name'], data['address'], data['phone'], data['email'], data['passport_number'])
        
        if self.db.execute_sp("sp_UpdateClient", params):
            self.refresh_clients()

    def delete_client(self):
        selected = self.client_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a client")
            return
            
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this client?"):
            return
            
        client_id = self.client_tree.item(selected[0], "values")[0]
        
        if self.db.execute_sp("sp_DeleteClient", (client_id,)):
            self.refresh_clients()
            self.clear_client_form()

    def refresh_clients(self):
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)
        
        clients = self.db.execute_sp("sp_GetAllClients")
        if clients:
            for client in clients:
                self.client_tree.insert("", tk.END, values=client)

    def on_client_select(self, event):
        selected = self.client_tree.selection()
        if not selected:
            return
            
        values = self.client_tree.item(selected[0], "values")
        fields = ['full_name', 'address', 'phone', 'email', 'passport_number']
        
        for i, field in enumerate(fields, start=1):
            self.client_entries[field].delete(0, tk.END)
            self.client_entries[field].insert(0, values[i])

    def clear_client_form(self):
        for entry in self.client_entries.values():
            entry.delete(0, tk.END)

    # Employee Tab (similar structure to Client Tab)
    def create_employee_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Employees")
        
        # Employee List
        employee_list_frame = ttk.LabelFrame(tab, text="Employee List")
        employee_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.employee_tree = ttk.Treeview(employee_list_frame, columns=("ID", "Full Name", "Position", "Phone", "Email"), show="headings")
        for col in self.employee_tree["columns"]:
            self.employee_tree.heading(col, text=col)
            self.employee_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(employee_list_frame, orient="vertical", command=self.employee_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.employee_tree.configure(yscrollcommand=scrollbar.set)
        self.employee_tree.pack(fill=tk.BOTH, expand=True)
        
        # Employee Form
        employee_form_frame = ttk.LabelFrame(tab, text="Employee Form")
        employee_form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        labels = ["Full Name:", "Position:", "Phone:", "Email:"]
        self.employee_entries = {}
        
        for i, text in enumerate(labels):
            ttk.Label(employee_form_frame, text=text).grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            entry = ttk.Entry(employee_form_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.employee_entries[text.split(":")[0].lower()] = entry
        
        # Buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Add", command=self.add_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update", command=self.update_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_employee_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_employees).pack(side=tk.LEFT, padx=5)
        
        self.employee_tree.bind("<<TreeviewSelect>>", self.on_employee_select)
        self.refresh_employees()

    def add_employee(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can add employees")
            return
            
        data = {k: v.get() for k, v in self.employee_entries.items()}
        if not all(data.values()):
            messagebox.showwarning("Validation Error", "All fields are required")
            return
        
        employee_id = str(uuid.uuid4())
        params = (employee_id, data['full name'], data['position'], data['phone'], data['email'])
        
        if self.db.execute_sp("sp_AddEmployee", params):
            self.refresh_employees()
            self.clear_employee_form()

    def update_employee(self):
        selected = self.employee_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select an employee")
            return
            
        employee_id = self.employee_tree.item(selected[0], "values")[0]
        data = {k: v.get() for k, v in self.employee_entries.items()}
        
        if not all(data.values()):
            messagebox.showwarning("Validation Error", "All fields are required")
            return
        
        params = (employee_id, data['full name'], data['position'], data['phone'], data['email'])
        
        if self.db.execute_sp("sp_UpdateEmployee", params):
            self.refresh_employees()

    def delete_employee(self):
        selected = self.employee_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select an employee")
            return
            
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this employee?"):
            return
            
        employee_id = self.employee_tree.item(selected[0], "values")[0]
        
        if self.db.execute_sp("sp_DeleteEmployee", (employee_id,)):
            self.refresh_employees()
            self.clear_employee_form()

    def refresh_employees(self):
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)
        
        employees = self.db.execute_sp("sp_GetAllEmployees")
        if employees:
            for employee in employees:
                self.employee_tree.insert("", tk.END, values=employee)

    def on_employee_select(self, event):
        selected = self.employee_tree.selection()
        if not selected:
            return
            
        values = self.employee_tree.item(selected[0], "values")
        fields = ['full name', 'position', 'phone', 'email']
        
        for i, field in enumerate(fields, start=1):
            self.employee_entries[field].delete(0, tk.END)
            self.employee_entries[field].insert(0, values[i])

    def clear_employee_form(self):
        for entry in self.employee_entries.values():
            entry.delete(0, tk.END)

    # Vehicle Tab (similar structure with combobox for owner)
    def create_vehicle_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Vehicles")
        
        # Vehicle List
        vehicle_list_frame = ttk.LabelFrame(tab, text="Vehicle List")
        vehicle_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.vehicle_tree = ttk.Treeview(vehicle_list_frame, columns=("ID", "Owner", "Make", "Model", "Year", "License Plate", "VIN"), show="headings")
        for col in self.vehicle_tree["columns"]:
            self.vehicle_tree.heading(col, text=col)
            self.vehicle_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(vehicle_list_frame, orient="vertical", command=self.vehicle_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.vehicle_tree.configure(yscrollcommand=scrollbar.set)
        self.vehicle_tree.pack(fill=tk.BOTH, expand=True)
        
        # Vehicle Form
        vehicle_form_frame = ttk.LabelFrame(tab, text="Vehicle Form")
        vehicle_form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Owner Combobox
        ttk.Label(vehicle_form_frame, text="Owner:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.owner_combobox = ttk.Combobox(vehicle_form_frame, width=37)
        self.owner_combobox.grid(row=0, column=1, padx=5, pady=5)
        
        # Other fields
        labels = ["Make:", "Model:", "Year:", "License Plate:", "VIN:"]
        self.vehicle_entries = {}
        
        for i, text in enumerate(labels, start=1):
            ttk.Label(vehicle_form_frame, text=text).grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            entry = ttk.Entry(vehicle_form_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.vehicle_entries[text.split(":")[0].lower().replace(" ", "_")] = entry
        
        # Buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Add", command=self.add_vehicle).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update", command=self.update_vehicle).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_vehicle).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_vehicle_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_vehicles).pack(side=tk.LEFT, padx=5)
        
        self.vehicle_tree.bind("<<TreeviewSelect>>", self.on_vehicle_select)
        self.load_client_combobox()
        self.refresh_vehicles()

    def load_client_combobox(self):
        clients = self.db.execute_sp("sp_GetAllClients")
        if clients:
            client_names = [f"{client[1]} ({client[0]})" for client in clients]
            self.owner_combobox['values'] = client_names

    def add_vehicle(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can add vehicles")
            return
            
        owner = self.owner_combobox.get()
        if not owner:
            messagebox.showwarning("Validation Error", "Owner is required")
            return
            
        data = {k: v.get() for k, v in self.vehicle_entries.items()}
        if not all(data.values()):
            messagebox.showwarning("Validation Error", "All fields are required")
            return
        
        try:
            year = int(data['year'])
        except ValueError:
            messagebox.showwarning("Validation Error", "Year must be a number")
            return
        
        # Extract owner ID from combobox value
        owner_id = owner.split("(")[-1].rstrip(")")
        
        vehicle_id = str(uuid.uuid4())
        params = (vehicle_id, owner_id, data['make'], data['model'], year, data['license_plate'], data['vin'])
        
        if self.db.execute_sp("sp_AddVehicle", params):
            self.refresh_vehicles()
            self.clear_vehicle_form()

    def update_vehicle(self):
        selected = self.vehicle_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a vehicle")
            return
            
        vehicle_id = self.vehicle_tree.item(selected[0], "values")[0]
        owner = self.owner_combobox.get()
        
        if not owner:
            messagebox.showwarning("Validation Error", "Owner is required")
            return
            
        data = {k: v.get() for k, v in self.vehicle_entries.items()}
        if not all(data.values()):
            messagebox.showwarning("Validation Error", "All fields are required")
            return
        
        try:
            year = int(data['year'])
        except ValueError:
            messagebox.showwarning("Validation Error", "Year must be a number")
            return
        
        # Extract owner ID from combobox value
        owner_id = owner.split("(")[-1].rstrip(")")
        
        params = (vehicle_id, owner_id, data['make'], data['model'], year, data['license_plate'], data['vin'])
        
        if self.db.execute_sp("sp_UpdateVehicle", params):
            self.refresh_vehicles()

    def delete_vehicle(self):
        selected = self.vehicle_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a vehicle")
            return
            
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this vehicle?"):
            return
            
        vehicle_id = self.vehicle_tree.item(selected[0], "values")[0]
        
        if self.db.execute_sp("sp_DeleteVehicle", (vehicle_id,)):
            self.refresh_vehicles()
            self.clear_vehicle_form()

    def refresh_vehicles(self):
        for item in self.vehicle_tree.get_children():
            self.vehicle_tree.delete(item)
        
        vehicles = self.db.execute_sp("sp_GetAllVehicles")
        if vehicles:
            for vehicle in vehicles:
                self.vehicle_tree.insert("", tk.END, values=vehicle)

    def on_vehicle_select(self, event):
        selected = self.vehicle_tree.selection()
        if not selected:
            return
            
        values = self.vehicle_tree.item(selected[0], "values")
        self.owner_combobox.set(f"{values[1]} ({values[0]})")
        
        fields = ['make', 'model', 'year', 'license_plate', 'vin']
        for i, field in enumerate(fields, start=2):
            self.vehicle_entries[field].delete(0, tk.END)
            self.vehicle_entries[field].insert(0, values[i])

    def clear_vehicle_form(self):
        self.owner_combobox.set('')
        for entry in self.vehicle_entries.values():
            entry.delete(0, tk.END)

    # Policy Tab (similar structure with comboboxes for client, vehicle, employee)
    def create_policy_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Policies")
        
        # Policy List
        policy_list_frame = ttk.LabelFrame(tab, text="Policy List")
        policy_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("ID", "Policy Number", "Client", "Vehicle", "Employee", 
                  "Start Date", "End Date", "Type", "Premium", "Status")
        
        self.policy_tree = ttk.Treeview(policy_list_frame, columns=columns, show="headings")
        for col in columns:
            self.policy_tree.heading(col, text=col)
            self.policy_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(policy_list_frame, orient="vertical", command=self.policy_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.policy_tree.configure(yscrollcommand=scrollbar.set)
        self.policy_tree.pack(fill=tk.BOTH, expand=True)
        
        # Policy Form
        policy_form_frame = ttk.LabelFrame(tab, text="Policy Form")
        policy_form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Comboboxes
        combobox_labels = ["Client:", "Vehicle:", "Employee:"]
        self.policy_comboboxes = {}
        
        for i, text in enumerate(combobox_labels):
            ttk.Label(policy_form_frame, text=text).grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            combobox = ttk.Combobox(policy_form_frame, width=37)
            combobox.grid(row=i, column=1, padx=5, pady=5)
            self.policy_comboboxes[text.split(":")[0].lower()] = combobox
        
        # Other fields
        labels = ["Policy Number:", "Start Date (YYYY-MM-DD):", "End Date (YYYY-MM-DD):", 
                 "Insurance Type:", "Premium Amount:", "Status:"]
        self.policy_entries = {}
        
        for i, text in enumerate(labels, start=len(combobox_labels)):
            ttk.Label(policy_form_frame, text=text).grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            
            if text.startswith("Insurance Type") or text.startswith("Status"):
                values = ["Comprehensive", "Third Party", "Theft", "Fire"] if text.startswith("Insurance Type") else ["Active", "Expired", "Cancelled"]
                combobox = ttk.Combobox(policy_form_frame, values=values, width=37)
                combobox.grid(row=i, column=1, padx=5, pady=5)
                self.policy_entries[text.split(":")[0].lower().split(" ")[0]] = combobox
            else:
                entry = ttk.Entry(policy_form_frame, width=40)
                entry.grid(row=i, column=1, padx=5, pady=5)
                self.policy_entries[text.split(":")[0].lower().split(" ")[0]] = entry
        
        # Buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Add", command=self.add_policy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update", command=self.update_policy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_policy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_policy_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_policies).pack(side=tk.LEFT, padx=5)
        
        self.policy_tree.bind("<<TreeviewSelect>>", self.on_policy_select)
        self.load_policy_comboboxes()
        self.refresh_policies()

    def load_policy_comboboxes(self):
        # Load clients
        clients = self.db.execute_sp("sp_GetAllClients")
        if clients:
            client_names = [f"{client[1]} ({client[0]})" for client in clients]
            self.policy_comboboxes['client']['values'] = client_names
        
        # Load vehicles
        vehicles = self.db.execute_sp("sp_GetAllVehicles")
        if vehicles:
            vehicle_names = [f"{vehicle[2]} {vehicle[3]} ({vehicle[0]})" for vehicle in vehicles]
            self.policy_comboboxes['vehicle']['values'] = vehicle_names
        
        # Load employees
        employees = self.db.execute_sp("sp_GetAllEmployees")
        if employees:
            employee_names = [f"{employee[1]} ({employee[0]})" for employee in employees]
            self.policy_comboboxes['employee']['values'] = employee_names

    def add_policy(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can add policies")
            return
            
        # Validate comboboxes
        combobox_values = {}
        for name, combobox in self.policy_comboboxes.items():
            value = combobox.get()
            if not value:
                messagebox.showwarning("Validation Error", f"{name.capitalize()} is required")
                return
            combobox_values[name] = value
        
        # Validate other fields
        data = {}
        for name, entry in self.policy_entries.items():
            value = entry.get() if isinstance(entry, ttk.Entry) else entry.get()
            if not value:
                messagebox.showwarning("Validation Error", f"{name.capitalize()} is required")
                return
            data[name] = value
        
        try:
            premium = float(data['premium'])
        except ValueError:
            messagebox.showwarning("Validation Error", "Premium must be a number")
            return
        
        try:
            datetime.strptime(data['start'], "%Y-%m-%d")
            datetime.strptime(data['end'], "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Validation Error", "Dates must be in YYYY-MM-DD format")
            return
        
        # Extract IDs from combobox values
        client_id = combobox_values['client'].split("(")[-1].rstrip(")")
        vehicle_id = combobox_values['vehicle'].split("(")[-1].rstrip(")")
        employee_id = combobox_values['employee'].split("(")[-1].rstrip(")")
        
        policy_id = str(uuid.uuid4())
        params = (
            policy_id, data['policy_number'], client_id, vehicle_id, employee_id,
            data['start'], data['end'], data['insurance'], premium, data['status']
        )
        
        if self.db.execute_sp("sp_AddPolicy", params):
            self.refresh_policies()
            self.clear_policy_form()

    def update_policy(self):
        selected = self.policy_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a policy")
            return
            
        policy_id = self.policy_tree.item(selected[0], "values")[0]
        
        # Validate comboboxes
        combobox_values = {}
        for name, combobox in self.policy_comboboxes.items():
            value = combobox.get()
            if not value:
                messagebox.showwarning("Validation Error", f"{name.capitalize()} is required")
                return
            combobox_values[name] = value
        
        # Validate other fields
        data = {}
        for name, entry in self.policy_entries.items():
            value = entry.get() if isinstance(entry, ttk.Entry) else entry.get()
            if not value:
                messagebox.showwarning("Validation Error", f"{name.capitalize()} is required")
                return
            data[name] = value
        
        try:
            premium = float(data['premium'])
        except ValueError:
            messagebox.showwarning("Validation Error", "Premium must be a number")
            return
        
        try:
            datetime.strptime(data['start'], "%Y-%m-%d")
            datetime.strptime(data['end'], "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Validation Error", "Dates must be in YYYY-MM-DD format")
            return
        
        # Extract IDs from combobox values
        client_id = combobox_values['client'].split("(")[-1].rstrip(")")
        vehicle_id = combobox_values['vehicle'].split("(")[-1].rstrip(")")
        employee_id = combobox_values['employee'].split("(")[-1].rstrip(")")
        
        params = (
            policy_id, data['policy_number'], client_id, vehicle_id, employee_id,
            data['start'], data['end'], data['insurance'], premium, data['status']
        )
        
        if self.db.execute_sp("sp_UpdatePolicy", params):
            self.refresh_policies()

    def delete_policy(self):
        selected = self.policy_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a policy")
            return
            
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this policy?"):
            return
            
        policy_id = self.policy_tree.item(selected[0], "values")[0]
        
        if self.db.execute_sp("sp_DeletePolicy", (policy_id,)):
            self.refresh_policies()
            self.clear_policy_form()

    def refresh_policies(self):
        for item in self.policy_tree.get_children():
            self.policy_tree.delete(item)
        
        policies = self.db.execute_sp("sp_GetAllPolicies")
        if policies:
            for policy in policies:
                self.policy_tree.insert("", tk.END, values=policy)

    def on_policy_select(self, event):
        selected = self.policy_tree.selection()
        if not selected:
            return
            
        values = self.policy_tree.item(selected[0], "values")
        
        # Set comboboxes
        self.policy_comboboxes['client'].set(f"{values[2]} ({values[0]})")
        self.policy_comboboxes['vehicle'].set(f"{values[3]} ({values[0]})")
        self.policy_comboboxes['employee'].set(f"{values[4]} ({values[0]})")
        
        # Set other fields
        fields = ['policy_number', 'start', 'end', 'insurance', 'premium', 'status']
        for i, field in enumerate(fields, start=1):
            if field in self.policy_entries:
                if isinstance(self.policy_entries[field], ttk.Entry):
                    self.policy_entries[field].delete(0, tk.END)
                    self.policy_entries[field].insert(0, values[i+4])  # +4 because first 5 values are ID and combobox values
                else:
                    self.policy_entries[field].set(values[i+4])

    def clear_policy_form(self):
        for combobox in self.policy_comboboxes.values():
            combobox.set('')
        for entry in self.policy_entries.values():
            if isinstance(entry, ttk.Entry):
                entry.delete(0, tk.END)
            else:
                entry.set('')

    # Claim Tab (similar structure with combobox for policy)
    def create_claim_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Claims")
        
        # Claim List
        claim_list_frame = ttk.LabelFrame(tab, text="Claim List")
        claim_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("ID", "Policy", "Claim Date", "Description", "Damage Amount", "Approved")
        
        self.claim_tree = ttk.Treeview(claim_list_frame, columns=columns, show="headings")
        for col in columns:
            self.claim_tree.heading(col, text=col)
            self.claim_tree

    def create_claim_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Claims")
        
        # Claim List
        claim_list_frame = ttk.LabelFrame(tab, text="Claim List")
        claim_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("ID", "Policy", "Claim Date", "Description", "Damage Amount", "Approved")
        
        self.claim_tree = ttk.Treeview(claim_list_frame, columns=columns, show="headings")
        for col in columns:
            self.claim_tree.heading(col, text=col)
            self.claim_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(claim_list_frame, orient="vertical", command=self.claim_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.claim_tree.configure(yscrollcommand=scrollbar.set)
        self.claim_tree.pack(fill=tk.BOTH, expand=True)
        
        # Claim Form
        claim_form_frame = ttk.LabelFrame(tab, text="Claim Form")
        claim_form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Policy Combobox
        ttk.Label(claim_form_frame, text="Policy:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.policy_combobox = ttk.Combobox(claim_form_frame, width=37)
        self.policy_combobox.grid(row=0, column=1, padx=5, pady=5)
        
        # Other fields
        labels = ["Claim Date (YYYY-MM-DD):", "Description:", "Damage Amount:", "Approved:"]
        self.claim_entries = {}
        
        for i, text in enumerate(labels, start=1):
            ttk.Label(claim_form_frame, text=text).grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            
            if text.startswith("Approved"):
                combobox = ttk.Combobox(claim_form_frame, values=["Yes", "No"], width=37)
                combobox.grid(row=i, column=1, padx=5, pady=5)
                self.claim_entries[text.split(":")[0].lower().split(" ")[0]] = combobox
            else:
                entry = ttk.Entry(claim_form_frame, width=40)
                entry.grid(row=i, column=1, padx=5, pady=5)
                self.claim_entries[text.split(":")[0].lower().split(" ")[0]] = entry
        
        # Buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Add", command=self.add_claim).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update", command=self.update_claim).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_claim).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_claim_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_claims).pack(side=tk.LEFT, padx=5)
        
        self.claim_tree.bind("<<TreeviewSelect>>", self.on_claim_select)
        self.load_policy_combobox()
        self.refresh_claims()

    def load_policy_combobox(self):
        policies = self.db.execute_sp("sp_GetAllPolicies")
        if policies:
            policy_numbers = [f"{policy[1]} ({policy[0]})" for policy in policies]
            self.policy_combobox['values'] = policy_numbers

    def add_claim(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can add claims")
            return
            
        policy = self.policy_combobox.get()
        if not policy:
            messagebox.showwarning("Validation Error", "Policy is required")
            return
            
        data = {}
        for name, entry in self.claim_entries.items():
            value = entry.get() if isinstance(entry, ttk.Entry) else entry.get()
            if not value:
                messagebox.showwarning("Validation Error", f"{name.capitalize()} is required")
                return
            data[name] = value
        
        try:
            damage_amount = float(data['damage'])
        except ValueError:
            messagebox.showwarning("Validation Error", "Damage amount must be a number")
            return
        
        try:
            datetime.strptime(data['claim'], "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Validation Error", "Date must be in YYYY-MM-DD format")
            return
        
        # Extract policy ID from combobox value
        policy_id = policy.split("(")[-1].rstrip(")")
        is_approved = 1 if data['approved'] == "Yes" else 0
        
        claim_id = str(uuid.uuid4())
        params = (claim_id, policy_id, data['claim'], data['description'], damage_amount, is_approved)
        
        if self.db.execute_sp("sp_AddClaim", params):
            self.refresh_claims()
            self.clear_claim_form()

    def update_claim(self):
        selected = self.claim_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a claim")
            return
            
        claim_id = self.claim_tree.item(selected[0], "values")[0]
        
        policy = self.policy_combobox.get()
        if not policy:
            messagebox.showwarning("Validation Error", "Policy is required")
            return
            
        data = {}
        for name, entry in self.claim_entries.items():
            value = entry.get() if isinstance(entry, ttk.Entry) else entry.get()
            if not value:
                messagebox.showwarning("Validation Error", f"{name.capitalize()} is required")
                return
            data[name] = value
        
        try:
            damage_amount = float(data['damage'])
        except ValueError:
            messagebox.showwarning("Validation Error", "Damage amount must be a number")
            return
        
        try:
            datetime.strptime(data['claim'], "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Validation Error", "Date must be in YYYY-MM-DD format")
            return
        
        # Extract policy ID from combobox value
        policy_id = policy.split("(")[-1].rstrip(")")
        is_approved = 1 if data['approved'] == "Yes" else 0
        
        params = (claim_id, policy_id, data['claim'], data['description'], damage_amount, is_approved)
        
        if self.db.execute_sp("sp_UpdateClaim", params):
            self.refresh_claims()

    def delete_claim(self):
        selected = self.claim_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a claim")
            return
            
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this claim?"):
            return
            
        claim_id = self.claim_tree.item(selected[0], "values")[0]
        
        if self.db.execute_sp("sp_DeleteClaim", (claim_id,)):
            self.refresh_claims()
            self.clear_claim_form()

    def refresh_claims(self):
        for item in self.claim_tree.get_children():
            self.claim_tree.delete(item)
        
        claims = self.db.execute_sp("sp_GetAllClaims")
        if claims:
            for claim in claims:
                # Convert approved status to Yes/No
                claim_values = list(claim)
                claim_values[-1] = "Yes" if claim_values[-1] else "No"
                self.claim_tree.insert("", tk.END, values=claim_values)

    def on_claim_select(self, event):
        selected = self.claim_tree.selection()
        if not selected:
            return
            
        values = self.claim_tree.item(selected[0], "values")
        self.policy_combobox.set(f"{values[1]} ({values[0]})")
        
        fields = ['claim', 'description', 'damage', 'approved']
        for i, field in enumerate(fields, start=2):
            if field in self.claim_entries:
                if isinstance(self.claim_entries[field], ttk.Entry):
                    self.claim_entries[field].delete(0, tk.END)
                    self.claim_entries[field].insert(0, values[i])
                else:
                    self.claim_entries[field].set(values[i])

    def clear_claim_form(self):
        self.policy_combobox.set('')
        for entry in self.claim_entries.values():
            if isinstance(entry, ttk.Entry):
                entry.delete(0, tk.END)
            else:
                entry.set('')

    # Payment Tab
    def create_payment_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Payments")
        
        # Payment List
        payment_list_frame = ttk.LabelFrame(tab, text="Payment List")
        payment_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("ID", "Claim", "Payment Date", "Amount", "Method")
        
        self.payment_tree = ttk.Treeview(payment_list_frame, columns=columns, show="headings")
        for col in columns:
            self.payment_tree.heading(col, text=col)
            self.payment_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(payment_list_frame, orient="vertical", command=self.payment_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.payment_tree.configure(yscrollcommand=scrollbar.set)
        self.payment_tree.pack(fill=tk.BOTH, expand=True)
        
        # Payment Form
        payment_form_frame = ttk.LabelFrame(tab, text="Payment Form")
        payment_form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Claim Combobox
        ttk.Label(payment_form_frame, text="Claim:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.claim_combobox = ttk.Combobox(payment_form_frame, width=37)
        self.claim_combobox.grid(row=0, column=1, padx=5, pady=5)
        
        # Other fields
        labels = ["Payment Date (YYYY-MM-DD):", "Amount:", "Method:"]
        self.payment_entries = {}
        
        for i, text in enumerate(labels, start=1):
            ttk.Label(payment_form_frame, text=text).grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            
            if text.startswith("Method"):
                combobox = ttk.Combobox(payment_form_frame, values=["Bank Transfer", "Cash", "Check", "Credit Card"], width=37)
                combobox.grid(row=i, column=1, padx=5, pady=5)
                self.payment_entries[text.split(":")[0].lower().split(" ")[0]] = combobox
            else:
                entry = ttk.Entry(payment_form_frame, width=40)
                entry.grid(row=i, column=1, padx=5, pady=5)
                self.payment_entries[text.split(":")[0].lower().split(" ")[0]] = entry
        
        # Buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Add", command=self.add_payment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update", command=self.update_payment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_payment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_payment_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_payments).pack(side=tk.LEFT, padx=5)
        
        self.payment_tree.bind("<<TreeviewSelect>>", self.on_payment_select)
        self.load_claim_combobox()
        self.refresh_payments()

    def load_claim_combobox(self):
        claims = self.db.execute_sp("sp_GetAllClaims")
        if claims:
            claim_descriptions = [f"{claim[3]} ({claim[0]})" for claim in claims]
            self.claim_combobox['values'] = claim_descriptions

    def add_payment(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can add payments")
            return
            
        claim = self.claim_combobox.get()
        if not claim:
            messagebox.showwarning("Validation Error", "Claim is required")
            return
            
        data = {}
        for name, entry in self.payment_entries.items():
            value = entry.get() if isinstance(entry, ttk.Entry) else entry.get()
            if not value:
                messagebox.showwarning("Validation Error", f"{name.capitalize()} is required")
                return
            data[name] = value
        
        try:
            amount = float(data['amount'])
        except ValueError:
            messagebox.showwarning("Validation Error", "Amount must be a number")
            return
        
        try:
            datetime.strptime(data['payment'], "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Validation Error", "Date must be in YYYY-MM-DD format")
            return
        
        # Extract claim ID from combobox value
        claim_id = claim.split("(")[-1].rstrip(")")
        
        payment_id = str(uuid.uuid4())
        params = (payment_id, claim_id, data['payment'], amount, data['method'])
        
        if self.db.execute_sp("sp_AddPayment", params):
            self.refresh_payments()
            self.clear_payment_form()

    def update_payment(self):
        selected = self.payment_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a payment")
            return
            
        payment_id = self.payment_tree.item(selected[0], "values")[0]
        
        claim = self.claim_combobox.get()
        if not claim:
            messagebox.showwarning("Validation Error", "Claim is required")
            return
            
        data = {}
        for name, entry in self.payment_entries.items():
            value = entry.get() if isinstance(entry, ttk.Entry) else entry.get()
            if not value:
                messagebox.showwarning("Validation Error", f"{name.capitalize()} is required")
                return
            data[name] = value
        
        try:
            amount = float(data['amount'])
        except ValueError:
            messagebox.showwarning("Validation Error", "Amount must be a number")
            return
        
        try:
            datetime.strptime(data['payment'], "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Validation Error", "Date must be in YYYY-MM-DD format")
            return
        
        # Extract claim ID from combobox value
        claim_id = claim.split("(")[-1].rstrip(")")
        
        params = (payment_id, claim_id, data['payment'], amount, data['method'])
        
        if self.db.execute_sp("sp_UpdatePayment", params):
            self.refresh_payments()

    def delete_payment(self):
        selected = self.payment_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a payment")
            return
            
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this payment?"):
            return
            
        payment_id = self.payment_tree.item(selected[0], "values")[0]
        
        if self.db.execute_sp("sp_DeletePayment", (payment_id,)):
            self.refresh_payments()
            self.clear_payment_form()

    def refresh_payments(self):
        for item in self.payment_tree.get_children():
            self.payment_tree.delete(item)
        
        payments = self.db.execute_sp("sp_GetAllPayments")
        if payments:
            for payment in payments:
                self.payment_tree.insert("", tk.END, values=payment)

    def on_payment_select(self, event):
        selected = self.payment_tree.selection()
        if not selected:
            return
            
        values = self.payment_tree.item(selected[0], "values")
        self.claim_combobox.set(f"{values[1]} ({values[0]})")
        
        fields = ['payment', 'amount', 'method']
        for i, field in enumerate(fields, start=2):
            if field in self.payment_entries:
                if isinstance(self.payment_entries[field], ttk.Entry):
                    self.payment_entries[field].delete(0, tk.END)
                    self.payment_entries[field].insert(0, values[i])
                else:
                    self.payment_entries[field].set(values[i])

    def clear_payment_form(self):
        self.claim_combobox.set('')
        for entry in self.payment_entries.values():
            if isinstance(entry, ttk.Entry):
                entry.delete(0, tk.END)
            else:
                entry.set('')

    # Reports Tab
    def create_reports_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Reports")
        
        # Report Frame
        report_frame = ttk.LabelFrame(tab, text="Generate Reports", padding=(20, 10))
        report_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Buttons Frame
        buttons_frame = ttk.Frame(report_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Report Buttons
        reports = [
            ("Active Policies", self.generate_active_policies_report),
            ("Claims by Month", self.generate_claims_by_month_report),
            ("Payments Summary", self.generate_payments_summary_report),
            ("Export to PDF", self.export_to_pdf)
        ]
        
        for text, cmd in reports:
            btn = ttk.Button(buttons_frame, text=text, command=cmd)
            btn.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
        
        # Report Treeview
        self.report_tree = ttk.Treeview(report_frame, selectmode="extended", show="headings")
        
        # Scrollbars
        vsb = ttk.Scrollbar(report_frame, orient="vertical", command=self.report_tree.yview)
        hsb = ttk.Scrollbar(report_frame, orient="horizontal", command=self.report_tree.xview)
        self.report_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Layout
        self.report_tree.pack(fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Context Menu
        self.treeview_menu = tk.Menu(self.report_tree, tearoff=0)
        self.treeview_menu.add_command(label="Copy", command=self.copy_from_treeview)
        self.report_tree.bind("<Button-3>", self.show_treeview_menu)

    def generate_active_policies_report(self):
        self.clear_report_tree()
        
        result = self.db.execute_sp("sp_GetActivePoliciesReport")
        if not result:
            return
        
        # Set columns based on result
        columns = result[0].cursor_description
        self.report_tree["columns"] = [col[0] for col in columns]
        
        for col in self.report_tree["columns"]:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=120, anchor=tk.CENTER)
        
        for row in result:
            self.report_tree.insert("", tk.END, values=row)

    def generate_claims_by_month_report(self):
        self.clear_report_tree()
        
        result = self.db.execute_sp("sp_GetClaimsByMonthReport")
        if not result:
            return
        
        # Set columns based on result
        columns = result[0].cursor_description
        self.report_tree["columns"] = [col[0] for col in columns]
        
        for col in self.report_tree["columns"]:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=120, anchor=tk.CENTER)
        
        for row in result:
            self.report_tree.insert("", tk.END, values=row)

    def generate_payments_summary_report(self):
        self.clear_report_tree()
        
        result = self.db.execute_sp("sp_GetPaymentsSummaryReport")
        if not result:
            return
        
        # Set columns based on result
        columns = result[0].cursor_description
        self.report_tree["columns"] = [col[0] for col in columns]
        
        for col in self.report_tree["columns"]:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=120, anchor=tk.CENTER)
        
        for row in result:
            self.report_tree.insert("", tk.END, values=row)

    def export_to_pdf(self):
        if not self.report_tree.get_children():
            messagebox.showwarning("Warning", "No data to export")
            return

        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 2*cm, "Insurance System Report")
        c.setFont("Helvetica", 10)
        c.drawCentredString(width / 2, height - 2.7*cm, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Table headers
        x_offset = 2*cm
        y_offset = height - 4*cm
        row_height = 0.7*cm

        columns = self.report_tree["columns"]
        col_width = (width - 4*cm) / len(columns)

        c.setFont("Helvetica-Bold", 10)
        for i, col in enumerate(columns):
            c.drawString(x_offset + i * col_width + 2, y_offset, col)
        y_offset -= row_height

        # Table data
        c.setFont("Helvetica", 10)
        for child in self.report_tree.get_children():
            values = self.report_tree.item(child)["values"]
            for i, value in enumerate(values):
                c.drawString(x_offset + i * col_width + 2, y_offset, str(value))
            y_offset -= row_height
            
            if y_offset < 2*cm:  # New page if needed
                c.showPage()
                c.setFont("Helvetica", 10)
                y_offset = height - 2*cm

        c.save()
        messagebox.showinfo("Success", f"Report saved to: {filename}")

    def clear_report_tree(self):
        self.report_tree.delete(*self.report_tree.get_children())
        for col in self.report_tree["columns"]:
            self.report_tree.heading(col, text="")
            self.report_tree.column(col, width=0)

    def copy_from_treeview(self):
        selected_items = self.report_tree.selection()
        if not selected_items:
            return
        
        copy_text = ""
        
        # Headers
        columns = self.report_tree["columns"]
        headers = [self.report_tree.heading(col)["text"] for col in columns]
        copy_text += "\t".join(headers) + "\n"
        
        # Data
        for item in selected_items:
            values = self.report_tree.item(item)["values"]
            copy_text += "\t".join(str(v) for v in values) + "\n"
        
        self.root.clipboard_clear()
        self.root.clipboard_append(copy_text.strip())

    def show_treeview_menu(self, event):
        item = self.report_tree.identify_row(event.y)
        if item:
            self.report_tree.selection_set(item)
            self.treeview_menu.post(event.x_root, event.y_root)

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.configure("TButton", padding=6)
    style.configure("TLabel", padding=5)
    style.configure("TEntry", padding=5)
    LoginWindow(root)
    root.mainloop()