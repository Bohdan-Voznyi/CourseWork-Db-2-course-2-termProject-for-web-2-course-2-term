import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
import uuid
from datetime import datetime
from fpdf import FPDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Insurance System - Login")
        self.root.geometry("400x200")
        
        # Database connection
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
        self.connect_to_db()
        
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
        
        # Focus on username field
        self.username_entry.focus_set()
        
    def connect_to_db(self):
        try:
            self.conn = pyodbc.connect(self.connection_string)
            self.cursor = self.conn.cursor()
        except Exception as e:
            messagebox.showerror("Database Connection Error", f"Failed to connect to database:\n{str(e)}")
            self.root.destroy()
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Validation Error", "Please enter both username and password")
            return
        
        try:
            # Check credentials in database
            query = "SELECT Roleuser FROM Users WHERE Username = ?"
            self.cursor.execute(query, (username,))
            result = self.cursor.fetchone()
            
            if result:
                role = result[0]
                # In a real application, you would verify the password properly (hashed, etc.)
                # For this example, we'll just check if the password is not empty
                if password:  # Replace with proper password verification
                    self.root.destroy()
                    root = tk.Tk()
                    app = InsuranceSystemApp(root, role)
                    root.mainloop()
                else:
                    messagebox.showerror("Login Failed", "Invalid password")
            else:
                messagebox.showerror("Login Failed", "Invalid username")
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Error during login:\n{str(e)}")


class InsuranceSystemApp:
    def __init__(self, root, user_role):
        self.root = root
        self.user_role = user_role
        self.root.title(f"Insurance System Management - {user_role}")
        self.root.geometry("1200x800")
        
        # Database connection
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
        
        self.connect_to_db()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs based on user role
        if self.user_role == "Admin":
            self.create_client_tab()
            self.create_employee_tab()
            self.create_vehicle_tab()
            self.create_policy_tab()
            self.create_claim_tab()
            self.create_payment_tab()
        self.create_reports_tab()
        
        # Add logout button
        logout_button = ttk.Button(root, text="Logout", command=self.logout)
        logout_button.pack(side=tk.BOTTOM, pady=10)
    
    def logout(self):
        self.root.destroy()
        root = tk.Tk()
        LoginWindow(root)
        root.mainloop()
    
    def connect_to_db(self):
        try:
            self.conn = pyodbc.connect(self.connection_string)
            self.cursor = self.conn.cursor()
        except Exception as e:
            messagebox.showerror("Database Connection Error", f"Failed to connect to database:\n{str(e)}")
    
    def execute_sp(self, sp_name, params=None):
        try:
            if params:
                placeholders = ", ".join(["?"] * len(params))
                query = f"EXEC {sp_name} {placeholders}"
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(f"EXEC {sp_name}")
            
            if self.cursor.description:  # If there are results to fetch
                return self.cursor.fetchall()
            else:
                self.conn.commit()
                return None
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Database Error", f"Error executing stored procedure {sp_name}:\n{str(e)}")
            return None
    
    # Client Tab Methods
    def create_client_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Clients")
        
        # Client List
        client_list_frame = ttk.LabelFrame(tab, text="Client List")
        client_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.client_tree = ttk.Treeview(client_list_frame, columns=("ID", "Full Name", "Address", "Phone", "Email", "Passport"), show="headings")
        self.client_tree.heading("ID", text="ID")
        self.client_tree.heading("Full Name", text="Full Name")
        self.client_tree.heading("Address", text="Address")
        self.client_tree.heading("Phone", text="Phone")
        self.client_tree.heading("Email", text="Email")
        self.client_tree.heading("Passport", text="Passport Number")
        
        for col in self.client_tree["columns"]:
            self.client_tree.column(col, width=120)
        
        self.client_tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(client_list_frame, orient="vertical", command=self.client_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.client_tree.configure(yscrollcommand=scrollbar.set)
        
        # Client Form
        client_form_frame = ttk.LabelFrame(tab, text="Client Form")
        client_form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(client_form_frame, text="Full Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.client_name_entry = ttk.Entry(client_form_frame, width=40)
        self.client_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(client_form_frame, text="Address:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.client_address_entry = ttk.Entry(client_form_frame, width=40)
        self.client_address_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(client_form_frame, text="Phone:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.client_phone_entry = ttk.Entry(client_form_frame, width=40)
        self.client_phone_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(client_form_frame, text="Email:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.client_email_entry = ttk.Entry(client_form_frame, width=40)
        self.client_email_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(client_form_frame, text="Passport Number:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.client_passport_entry = ttk.Entry(client_form_frame, width=40)
        self.client_passport_entry.grid(row=4, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Add Client", command=self.add_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Client", command=self.update_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Client", command=self.delete_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_clients).pack(side=tk.LEFT, padx=5)
        
        # Bind treeview selection
        self.client_tree.bind("<<TreeviewSelect>>", self.on_client_select)
        
        # Load initial data
        self.refresh_clients()
    
    def add_client(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can add clients")
            return
            
        name = self.client_name_entry.get()
        address = self.client_address_entry.get()
        phone = self.client_phone_entry.get()
        email = self.client_email_entry.get()
        passport = self.client_passport_entry.get()
        
        if not all([name, address, phone, email, passport]):
            messagebox.showwarning("Validation Error", "All fields are required")
            return
        
        client_id = str(uuid.uuid4())
        params = (client_id, name, address, phone, email, passport)
        self.execute_sp("sp_AddClient", params)
        self.refresh_clients()
        self.clear_client_form()
    
    def update_client(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can update clients")
            return
            
        selected = self.client_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a client to update")
            return
        
        client_id = self.client_tree.item(selected[0], "values")[0]
        name = self.client_name_entry.get()
        address = self.client_address_entry.get()
        phone = self.client_phone_entry.get()
        email = self.client_email_entry.get()
        passport = self.client_passport_entry.get()
        
        if not all([name, address, phone, email, passport]):
            messagebox.showwarning("Validation Error", "All fields are required")
            return
        
        params = (client_id, name, address, phone, email, passport)
        self.execute_sp("sp_UpdateClient", params)
        self.refresh_clients()
    
    def delete_client(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can delete clients")
            return
            
        selected = self.client_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a client to delete")
            return
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this client?"):
            return
        
        client_id = self.client_tree.item(selected[0], "values")[0]
        self.execute_sp("sp_DeleteClient", (client_id,))
        self.refresh_clients()
        self.clear_client_form()
    
    def refresh_clients(self):
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)
        
        clients = self.execute_sp("sp_GetAllClients")
        if clients:
            for client in clients:
                self.client_tree.insert("", tk.END, values=client)
    
    def on_client_select(self, event):
        selected = self.client_tree.selection()
        if not selected:
            return
        
        values = self.client_tree.item(selected[0], "values")
        self.client_name_entry.delete(0, tk.END)
        self.client_name_entry.insert(0, values[1])
        self.client_address_entry.delete(0, tk.END)
        self.client_address_entry.insert(0, values[2])
        self.client_phone_entry.delete(0, tk.END)
        self.client_phone_entry.insert(0, values[3])
        self.client_email_entry.delete(0, tk.END)
        self.client_email_entry.insert(0, values[4])
        self.client_passport_entry.delete(0, tk.END)
        self.client_passport_entry.insert(0, values[5])
    
    def clear_client_form(self):
        self.client_name_entry.delete(0, tk.END)
        self.client_address_entry.delete(0, tk.END)
        self.client_phone_entry.delete(0, tk.END)
        self.client_email_entry.delete(0, tk.END)
        self.client_passport_entry.delete(0, tk.END)
    
    # Employee Tab Methods
    def create_employee_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Employees")
        
        # Employee List
        employee_list_frame = ttk.LabelFrame(tab, text="Employee List")
        employee_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.employee_tree = ttk.Treeview(employee_list_frame, columns=("ID", "Full Name", "Position", "Phone", "Email"), show="headings")
        self.employee_tree.heading("ID", text="ID")
        self.employee_tree.heading("Full Name", text="Full Name")
        self.employee_tree.heading("Position", text="Position")
        self.employee_tree.heading("Phone", text="Phone")
        self.employee_tree.heading("Email", text="Email")
        
        for col in self.employee_tree["columns"]:
            self.employee_tree.column(col, width=120)
        
        self.employee_tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(employee_list_frame, orient="vertical", command=self.employee_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.employee_tree.configure(yscrollcommand=scrollbar.set)
        
        # Employee Form
        employee_form_frame = ttk.LabelFrame(tab, text="Employee Form")
        employee_form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(employee_form_frame, text="Full Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.employee_name_entry = ttk.Entry(employee_form_frame, width=40)
        self.employee_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(employee_form_frame, text="Position:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.employee_position_entry = ttk.Entry(employee_form_frame, width=40)
        self.employee_position_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(employee_form_frame, text="Phone:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.employee_phone_entry = ttk.Entry(employee_form_frame, width=40)
        self.employee_phone_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(employee_form_frame, text="Email:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.employee_email_entry = ttk.Entry(employee_form_frame, width=40)
        self.employee_email_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Add Employee", command=self.add_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Employee", command=self.update_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Employee", command=self.delete_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_employees).pack(side=tk.LEFT, padx=5)
        
        # Bind treeview selection
        self.employee_tree.bind("<<TreeviewSelect>>", self.on_employee_select)
        
        # Load initial data
        self.refresh_employees()
    
    def add_employee(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can add employees")
            return
            
        name = self.employee_name_entry.get()
        position = self.employee_position_entry.get()
        phone = self.employee_phone_entry.get()
        email = self.employee_email_entry.get()
        
        if not all([name, position, phone, email]):
            messagebox.showwarning("Validation Error", "All fields are required")
            return
        
        employee_id = str(uuid.uuid4())
        params = (employee_id, name, position, phone, email)
        self.execute_sp("sp_AddEmployee", params)
        self.refresh_employees()
        self.clear_employee_form()
    
    def update_employee(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can update employees")
            return
            
        selected = self.employee_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select an employee to update")
            return
        
        employee_id = self.employee_tree.item(selected[0], "values")[0]
        name = self.employee_name_entry.get()
        position = self.employee_position_entry.get()
        phone = self.employee_phone_entry.get()
        email = self.employee_email_entry.get()
        
        if not all([name, position, phone, email]):
            messagebox.showwarning("Validation Error", "All fields are required")
            return
        
        params = (employee_id, name, position, phone, email)
        self.execute_sp("sp_UpdateEmployee", params)
        self.refresh_employees()
    
    def delete_employee(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can delete employees")
            return
            
        selected = self.employee_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select an employee to delete")
            return
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this employee?"):
            return
        
        employee_id = self.employee_tree.item(selected[0], "values")[0]
        self.execute_sp("sp_DeleteEmployee", (employee_id,))
        self.refresh_employees()
        self.clear_employee_form()
    
    def refresh_employees(self):
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)
        
        employees = self.execute_sp("sp_GetAllEmployees")
        if employees:
            for employee in employees:
                self.employee_tree.insert("", tk.END, values=employee)
    
    def on_employee_select(self, event):
        selected = self.employee_tree.selection()
        if not selected:
            return
        
        values = self.employee_tree.item(selected[0], "values")
        self.employee_name_entry.delete(0, tk.END)
        self.employee_name_entry.insert(0, values[1])
        self.employee_position_entry.delete(0, tk.END)
        self.employee_position_entry.insert(0, values[2])
        self.employee_phone_entry.delete(0, tk.END)
        self.employee_phone_entry.insert(0, values[3])
        self.employee_email_entry.delete(0, tk.END)
        self.employee_email_entry.insert(0, values[4])
    
    def clear_employee_form(self):
        self.employee_name_entry.delete(0, tk.END)
        self.employee_position_entry.delete(0, tk.END)
        self.employee_phone_entry.delete(0, tk.END)
        self.employee_email_entry.delete(0, tk.END)
    
    # Vehicle Tab Methods
    def create_vehicle_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Vehicles")
        
        # Vehicle List
        vehicle_list_frame = ttk.LabelFrame(tab, text="Vehicle List")
        vehicle_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.vehicle_tree = ttk.Treeview(vehicle_list_frame, columns=("ID", "Owner", "Make", "Model", "Year", "License Plate", "VIN"), show="headings")
        self.vehicle_tree.heading("ID", text="ID")
        self.vehicle_tree.heading("Owner", text="Owner")
        self.vehicle_tree.heading("Make", text="Make")
        self.vehicle_tree.heading("Model", text="Model")
        self.vehicle_tree.heading("Year", text="Year")
        self.vehicle_tree.heading("License Plate", text="License Plate")
        self.vehicle_tree.heading("VIN", text="VIN")
        
        for col in self.vehicle_tree["columns"]:
            self.vehicle_tree.column(col, width=120)
        
        self.vehicle_tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(vehicle_list_frame, orient="vertical", command=self.vehicle_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.vehicle_tree.configure(yscrollcommand=scrollbar.set)
        
        # Vehicle Form
        vehicle_form_frame = ttk.LabelFrame(tab, text="Vehicle Form")
        vehicle_form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(vehicle_form_frame, text="Owner:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.owner_combobox = ttk.Combobox(vehicle_form_frame, width=37)
        self.owner_combobox.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(vehicle_form_frame, text="Make:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.vehicle_make_entry = ttk.Entry(vehicle_form_frame, width=40)
        self.vehicle_make_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(vehicle_form_frame, text="Model:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.vehicle_model_entry = ttk.Entry(vehicle_form_frame, width=40)
        self.vehicle_model_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(vehicle_form_frame, text="Year:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.vehicle_year_entry = ttk.Entry(vehicle_form_frame, width=40)
        self.vehicle_year_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(vehicle_form_frame, text="License Plate:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.vehicle_plate_entry = ttk.Entry(vehicle_form_frame, width=40)
        self.vehicle_plate_entry.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(vehicle_form_frame, text="VIN:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        self.vehicle_vin_entry = ttk.Entry(vehicle_form_frame, width=40)
        self.vehicle_vin_entry.grid(row=5, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Add Vehicle", command=self.add_vehicle).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Vehicle", command=self.update_vehicle).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Vehicle", command=self.delete_vehicle).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_vehicles).pack(side=tk.LEFT, padx=5)
        
        # Bind treeview selection
        self.vehicle_tree.bind("<<TreeviewSelect>>", self.on_vehicle_select)
        
        # Load initial data
        self.refresh_vehicles()
        self.load_client_combobox()
    
    def load_client_combobox(self):
        clients = self.execute_sp("sp_GetAllClients")
        if clients:
            client_names = [f"{client[1]} ({client[0]})" for client in clients]
            self.owner_combobox['values'] = client_names
    
    def add_vehicle(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can add vehicles")
            return
            
        owner = self.owner_combobox.get()
        make = self.vehicle_make_entry.get()
        model = self.vehicle_model_entry.get()
        year = self.vehicle_year_entry.get()
        plate = self.vehicle_plate_entry.get()
        vin = self.vehicle_vin_entry.get()
        
        if not all([owner, make, model, year, plate, vin]):
            messagebox.showwarning("Validation Error", "All fields are required")
            return
        
        try:
            year = int(year)
        except ValueError:
            messagebox.showwarning("Validation Error", "Year must be a number")
            return
        
        # Extract owner ID from combobox value (format: "Name (ID)")
        owner_id = owner.split("(")[-1].rstrip(")")
        
        vehicle_id = str(uuid.uuid4())
        params = (vehicle_id, owner_id, make, model, year, plate, vin)
        self.execute_sp("sp_AddVehicle", params)
        self.refresh_vehicles()
        self.clear_vehicle_form()
    
    def update_vehicle(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can update vehicles")
            return
            
        selected = self.vehicle_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a vehicle to update")
            return
        
        vehicle_id = self.vehicle_tree.item(selected[0], "values")[0]
        owner = self.owner_combobox.get()
        make = self.vehicle_make_entry.get()
        model = self.vehicle_model_entry.get()
        year = self.vehicle_year_entry.get()
        plate = self.vehicle_plate_entry.get()
        vin = self.vehicle_vin_entry.get()
        
        if not all([owner, make, model, year, plate, vin]):
            messagebox.showwarning("Validation Error", "All fields are required")
            return
        
        try:
            year = int(year)
        except ValueError:
            messagebox.showwarning("Validation Error", "Year must be a number")
            return
        
        # Extract owner ID from combobox value (format: "Name (ID)")
        owner_id = owner.split("(")[-1].rstrip(")")
        
        params = (vehicle_id, owner_id, make, model, year, plate, vin)
        self.execute_sp("sp_UpdateVehicle", params)
        self.refresh_vehicles()
    
    def delete_vehicle(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can delete vehicles")
            return
            
        selected = self.vehicle_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a vehicle to delete")
            return
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this vehicle?"):
            return
        
        vehicle_id = self.vehicle_tree.item(selected[0], "values")[0]
        self.execute_sp("sp_DeleteVehicle", (vehicle_id,))
        self.refresh_vehicles()
        self.clear_vehicle_form()
    
    def refresh_vehicles(self):
        for item in self.vehicle_tree.get_children():
            self.vehicle_tree.delete(item)
        
        vehicles = self.execute_sp("sp_GetAllVehicles")
        if vehicles:
            for vehicle in vehicles:
                self.vehicle_tree.insert("", tk.END, values=vehicle)
    
    def on_vehicle_select(self, event):
        selected = self.vehicle_tree.selection()
        if not selected:
            return
        
        values = self.vehicle_tree.item(selected[0], "values")
        self.owner_combobox.set(f"{values[1]} ({values[0]})")
        self.vehicle_make_entry.delete(0, tk.END)
        self.vehicle_make_entry.insert(0, values[2])
        self.vehicle_model_entry.delete(0, tk.END)
        self.vehicle_model_entry.insert(0, values[3])
        self.vehicle_year_entry.delete(0, tk.END)
        self.vehicle_year_entry.insert(0, values[4])
        self.vehicle_plate_entry.delete(0, tk.END)
        self.vehicle_plate_entry.insert(0, values[5])
        self.vehicle_vin_entry.delete(0, tk.END)
        self.vehicle_vin_entry.insert(0, values[6])
    
    def clear_vehicle_form(self):
        self.owner_combobox.set('')
        self.vehicle_make_entry.delete(0, tk.END)
        self.vehicle_model_entry.delete(0, tk.END)
        self.vehicle_year_entry.delete(0, tk.END)
        self.vehicle_plate_entry.delete(0, tk.END)
        self.vehicle_vin_entry.delete(0, tk.END)
    
    # Policy Tab Methods
    def create_policy_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Policies")
        
        # Policy List
        policy_list_frame = ttk.LabelFrame(tab, text="Policy List")
        policy_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.policy_tree = ttk.Treeview(policy_list_frame, columns=(
            "ID", "Policy Number", "Client", "Vehicle", "Employee", 
            "Start Date", "End Date", "Type", "Premium", "Status"
        ), show="headings")
        
        self.policy_tree.heading("ID", text="ID")
        self.policy_tree.heading("Policy Number", text="Policy Number")
        self.policy_tree.heading("Client", text="Client")
        self.policy_tree.heading("Vehicle", text="Vehicle")
        self.policy_tree.heading("Employee", text="Employee")
        self.policy_tree.heading("Start Date", text="Start Date")
        self.policy_tree.heading("End Date", text="End Date")
        self.policy_tree.heading("Type", text="Type")
        self.policy_tree.heading("Premium", text="Premium")
        self.policy_tree.heading("Status", text="Status")
        
        for col in self.policy_tree["columns"]:
            self.policy_tree.column(col, width=120)
        
        self.policy_tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(policy_list_frame, orient="vertical", command=self.policy_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.policy_tree.configure(yscrollcommand=scrollbar.set)
        
        # Policy Form
        policy_form_frame = ttk.LabelFrame(tab, text="Policy Form")
        policy_form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(policy_form_frame, text="Policy Number:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.policy_number_entry = ttk.Entry(policy_form_frame, width=40)
        self.policy_number_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(policy_form_frame, text="Client:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.policy_client_combobox = ttk.Combobox(policy_form_frame, width=37)
        self.policy_client_combobox.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(policy_form_frame, text="Vehicle:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.policy_vehicle_combobox = ttk.Combobox(policy_form_frame, width=37)
        self.policy_vehicle_combobox.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(policy_form_frame, text="Employee:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.policy_employee_combobox = ttk.Combobox(policy_form_frame, width=37)
        self.policy_employee_combobox.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(policy_form_frame, text="Start Date (YYYY-MM-DD):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.policy_start_entry = ttk.Entry(policy_form_frame, width=40)
        self.policy_start_entry.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(policy_form_frame, text="End Date (YYYY-MM-DD):").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        self.policy_end_entry = ttk.Entry(policy_form_frame, width=40)
        self.policy_end_entry.grid(row=5, column=1, padx=5, pady=5)
        
        ttk.Label(policy_form_frame, text="Insurance Type:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        self.policy_type_combobox = ttk.Combobox(policy_form_frame, values=["Comprehensive", "Third Party", "Theft", "Fire"], width=37)
        self.policy_type_combobox.grid(row=6, column=1, padx=5, pady=5)
        
        ttk.Label(policy_form_frame, text="Premium Amount:").grid(row=7, column=0, padx=5, pady=5, sticky=tk.W)
        self.policy_premium_entry = ttk.Entry(policy_form_frame, width=40)
        self.policy_premium_entry.grid(row=7, column=1, padx=5, pady=5)
        
        ttk.Label(policy_form_frame, text="Status:").grid(row=8, column=0, padx=5, pady=5, sticky=tk.W)
        self.policy_status_combobox = ttk.Combobox(policy_form_frame, values=["Active", "Expired", "Cancelled"], width=37)
        self.policy_status_combobox.grid(row=8, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Add Policy", command=self.add_policy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Policy", command=self.update_policy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Policy", command=self.delete_policy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_policies).pack(side=tk.LEFT, padx=5)
        
        # Bind treeview selection
        self.policy_tree.bind("<<TreeviewSelect>>", self.on_policy_select)
        
        # Load initial data
        self.refresh_policies()
        self.load_policy_comboboxes()
    
    def load_policy_comboboxes(self):
        # Load clients
        clients = self.execute_sp("sp_GetAllClients")
        if clients:
            client_names = [f"{client[1]} ({client[0]})" for client in clients]
            self.policy_client_combobox['values'] = client_names
        
        # Load vehicles
        vehicles = self.execute_sp("sp_GetAllVehicles")
        if vehicles:
            vehicle_names = [f"{vehicle[2]} {vehicle[3]} ({vehicle[0]})" for vehicle in vehicles]
            self.policy_vehicle_combobox['values'] = vehicle_names
        
        # Load employees
        employees = self.execute_sp("sp_GetAllEmployees")
        if employees:
            employee_names = [f"{employee[1]} ({employee[0]})" for employee in employees]
            self.policy_employee_combobox['values'] = employee_names
    
    def add_policy(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can add policies")
            return
            
        policy_number = self.policy_number_entry.get()
        client = self.policy_client_combobox.get()
        vehicle = self.policy_vehicle_combobox.get()
        employee = self.policy_employee_combobox.get()
        start_date = self.policy_start_entry.get()
        end_date = self.policy_end_entry.get()
        insurance_type = self.policy_type_combobox.get()
        premium = self.policy_premium_entry.get()
        status = self.policy_status_combobox.get()
        
        if not all([policy_number, client, vehicle, employee, start_date, end_date, insurance_type, premium, status]):
            messagebox.showwarning("Validation Error", "All fields are required")
            return
        
        try:
            premium = float(premium)
        except ValueError:
            messagebox.showwarning("Validation Error", "Premium must be a number")
            return
        
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Validation Error", "Dates must be in YYYY-MM-DD format")
            return
        
        # Extract IDs from combobox values
        client_id = client.split("(")[-1].rstrip(")")
        vehicle_id = vehicle.split("(")[-1].rstrip(")")
        employee_id = employee.split("(")[-1].rstrip(")")
        
        policy_id = str(uuid.uuid4())
        params = (
            policy_id, policy_number, client_id, vehicle_id, employee_id, 
            start_date, end_date, insurance_type, premium, status
        )
        self.execute_sp("sp_AddPolicy", params)
        self.refresh_policies()
        self.clear_policy_form()
    
    def update_policy(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can update policies")
            return
            
        selected = self.policy_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a policy to update")
            return
        
        policy_id = self.policy_tree.item(selected[0], "values")[0]
        policy_number = self.policy_number_entry.get()
        client = self.policy_client_combobox.get()
        vehicle = self.policy_vehicle_combobox.get()
        employee = self.policy_employee_combobox.get()
        start_date = self.policy_start_entry.get()
        end_date = self.policy_end_entry.get()
        insurance_type = self.policy_type_combobox.get()
        premium = self.policy_premium_entry.get()
        status = self.policy_status_combobox.get()
        
        if not all([policy_number, client, vehicle, employee, start_date, end_date, insurance_type, premium, status]):
            messagebox.showwarning("Validation Error", "All fields are required")
            return
        
        try:
            premium = float(premium)
        except ValueError:
            messagebox.showwarning("Validation Error", "Premium must be a number")
            return
        
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Validation Error", "Dates must be in YYYY-MM-DD format")
            return
        
        # Extract IDs from combobox values
        client_id = client.split("(")[-1].rstrip(")")
        vehicle_id = vehicle.split("(")[-1].rstrip(")")
        employee_id = employee.split("(")[-1].rstrip(")")
        
        params = (
            policy_id, policy_number, client_id, vehicle_id, employee_id, 
            start_date, end_date, insurance_type, premium, status
        )
        self.execute_sp("sp_UpdatePolicy", params)
        self.refresh_policies()
    
    def delete_policy(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can delete policies")
            return
            
        selected = self.policy_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a policy to delete")
            return
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this policy?"):
            return
        
        policy_id = self.policy_tree.item(selected[0], "values")[0]
        self.execute_sp("sp_DeletePolicy", (policy_id,))
        self.refresh_policies()
        self.clear_policy_form()
    
    def refresh_policies(self):
        for item in self.policy_tree.get_children():
            self.policy_tree.delete(item)
        
        policies = self.execute_sp("sp_GetAllPolicies")
        if policies:
            for policy in policies:
                self.policy_tree.insert("", tk.END, values=policy)
    
    def on_policy_select(self, event):
        selected = self.policy_tree.selection()
        if not selected:
            return
        
        values = self.policy_tree.item(selected[0], "values")
        self.policy_number_entry.delete(0, tk.END)
        self.policy_number_entry.insert(0, values[1])
        self.policy_client_combobox.set(f"{values[2]} ({values[0]})")
        self.policy_vehicle_combobox.set(f"{values[3]} ({values[0]})")
        self.policy_employee_combobox.set(f"{values[4]} ({values[0]})")
        self.policy_start_entry.delete(0, tk.END)
        self.policy_start_entry.insert(0, values[5])
        self.policy_end_entry.delete(0, tk.END)
        self.policy_end_entry.insert(0, values[6])
        self.policy_type_combobox.set(values[7])
        self.policy_premium_entry.delete(0, tk.END)
        self.policy_premium_entry.insert(0, values[8])
        self.policy_status_combobox.set(values[9])
    
    def clear_policy_form(self):
        self.policy_number_entry.delete(0, tk.END)
        self.policy_client_combobox.set('')
        self.policy_vehicle_combobox.set('')
        self.policy_employee_combobox.set('')
        self.policy_start_entry.delete(0, tk.END)
        self.policy_end_entry.delete(0, tk.END)
        self.policy_type_combobox.set('')
        self.policy_premium_entry.delete(0, tk.END)
        self.policy_status_combobox.set('')
    
    # Claim Tab Methods
    def create_claim_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Claims")
        
        # Claim List
        claim_list_frame = ttk.LabelFrame(tab, text="Claim List")
        claim_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.claim_tree = ttk.Treeview(claim_list_frame, columns=(
            "ID", "Policy", "Claim Date", "Description", "Damage Amount", "Approved"
        ), show="headings")
        
        self.claim_tree.heading("ID", text="ID")
        self.claim_tree.heading("Policy", text="Policy")
        self.claim_tree.heading("Claim Date", text="Claim Date")
        self.claim_tree.heading("Description", text="Description")
        self.claim_tree.heading("Damage Amount", text="Damage Amount")
        self.claim_tree.heading("Approved", text="Approved")
        
        for col in self.claim_tree["columns"]:
            self.claim_tree.column(col, width=120)
        
        self.claim_tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(claim_list_frame, orient="vertical", command=self.claim_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.claim_tree.configure(yscrollcommand=scrollbar.set)
        
        # Claim Form
        claim_form_frame = ttk.LabelFrame(tab, text="Claim Form")
        claim_form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(claim_form_frame, text="Policy:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.claim_policy_combobox = ttk.Combobox(claim_form_frame, width=37)
        self.claim_policy_combobox.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(claim_form_frame, text="Claim Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.claim_date_entry = ttk.Entry(claim_form_frame, width=40)
        self.claim_date_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(claim_form_frame, text="Description:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.claim_desc_entry = ttk.Entry(claim_form_frame, width=40)
        self.claim_desc_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(claim_form_frame, text="Damage Amount:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.claim_amount_entry = ttk.Entry(claim_form_frame, width=40)
        self.claim_amount_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(claim_form_frame, text="Approved:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.claim_approved_combobox = ttk.Combobox(claim_form_frame, values=["Yes", "No"], width=37)
        self.claim_approved_combobox.grid(row=4, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Add Claim", command=self.add_claim).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Claim", command=self.update_claim).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Claim", command=self.delete_claim).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_claims).pack(side=tk.LEFT, padx=5)
        
        # Bind treeview selection
        self.claim_tree.bind("<<TreeviewSelect>>", self.on_claim_select)
        
        # Load initial data
        self.refresh_claims()
        self.load_claim_comboboxes()
    
    def load_claim_comboboxes(self):
        # Load policies
        policies = self.execute_sp("sp_GetAllPolicies")
        if policies:
            policy_numbers = [f"{policy[1]} ({policy[0]})" for policy in policies]
            self.claim_policy_combobox['values'] = policy_numbers
    
    def add_claim(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can add claims")
            return
            
        policy = self.claim_policy_combobox.get()
        claim_date = self.claim_date_entry.get()
        description = self.claim_desc_entry.get()
        damage_amount = self.claim_amount_entry.get()
        approved = self.claim_approved_combobox.get()
        
        if not all([policy, claim_date, description, damage_amount, approved]):
            messagebox.showwarning("Validation Error", "All fields are required")
            return
        
        try:
            damage_amount = float(damage_amount)
        except ValueError:
            messagebox.showwarning("Validation Error", "Damage amount must be a number")
            return
        
        try:
            datetime.strptime(claim_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Validation Error", "Date must be in YYYY-MM-DD format")
            return
        
        # Extract policy ID from combobox value
        policy_id = policy.split("(")[-1].rstrip(")")
        is_approved = 1 if approved == "Yes" else 0
        
        claim_id = str(uuid.uuid4())
        params = (claim_id, policy_id, claim_date, description, damage_amount, is_approved)
        self.execute_sp("sp_AddClaim", params)
        self.refresh_claims()
        self.clear_claim_form()
    
    def update_claim(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can update claims")
            return
            
        selected = self.claim_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a claim to update")
            return
        
        claim_id = self.claim_tree.item(selected[0], "values")[0]
        policy = self.claim_policy_combobox.get()
        claim_date = self.claim_date_entry.get()
        description = self.claim_desc_entry.get()
        damage_amount = self.claim_amount_entry.get()
        approved = self.claim_approved_combobox.get()
        
        if not all([policy, claim_date, description, damage_amount, approved]):
            messagebox.showwarning("Validation Error", "All fields are required")
            return
        
        try:
            damage_amount = float(damage_amount)
        except ValueError:
            messagebox.showwarning("Validation Error", "Damage amount must be a number")
            return
        
        try:
            datetime.strptime(claim_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Validation Error", "Date must be in YYYY-MM-DD format")
            return
        
        # Extract policy ID from combobox value
        policy_id = policy.split("(")[-1].rstrip(")")
        is_approved = 1 if approved == "Yes" else 0
        
        params = (claim_id, policy_id, claim_date, description, damage_amount, is_approved)
        self.execute_sp("sp_UpdateClaim", params)
        self.refresh_claims()
    
    def delete_claim(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can delete claims")
            return
            
        selected = self.claim_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a claim to delete")
            return
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this claim?"):
            return
        
        claim_id = self.claim_tree.item(selected[0], "values")[0]
        self.execute_sp("sp_DeleteClaim", (claim_id,))
        self.refresh_claims()
        self.clear_claim_form()
    
    def refresh_claims(self):
        for item in self.claim_tree.get_children():
            self.claim_tree.delete(item)
        
        claims = self.execute_sp("sp_GetAllClaims")
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
        self.claim_policy_combobox.set(f"{values[1]} ({values[0]})")
        self.claim_date_entry.delete(0, tk.END)
        self.claim_date_entry.insert(0, values[2])
        self.claim_desc_entry.delete(0, tk.END)
        self.claim_desc_entry.insert(0, values[3])
        self.claim_amount_entry.delete(0, tk.END)
        self.claim_amount_entry.insert(0, values[4])
        self.claim_approved_combobox.set(values[5])
    
    def clear_claim_form(self):
        self.claim_policy_combobox.set('')
        self.claim_date_entry.delete(0, tk.END)
        self.claim_desc_entry.delete(0, tk.END)
        self.claim_amount_entry.delete(0, tk.END)
        self.claim_approved_combobox.set('')
    
    # Payment Tab Methods
    def create_payment_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Payments")
        
        # Payment List
        payment_list_frame = ttk.LabelFrame(tab, text="Payment List")
        payment_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.payment_tree = ttk.Treeview(payment_list_frame, columns=(
            "ID", "Claim", "Payment Date", "Amount", "Method"
        ), show="headings")
        
        self.payment_tree.heading("ID", text="ID")
        self.payment_tree.heading("Claim", text="Claim")
        self.payment_tree.heading("Payment Date", text="Payment Date")
        self.payment_tree.heading("Amount", text="Amount")
        self.payment_tree.heading("Method", text="Method")
        
        for col in self.payment_tree["columns"]:
            self.payment_tree.column(col, width=120)
        
        self.payment_tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(payment_list_frame, orient="vertical", command=self.payment_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.payment_tree.configure(yscrollcommand=scrollbar.set)
        
        # Payment Form
        payment_form_frame = ttk.LabelFrame(tab, text="Payment Form")
        payment_form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(payment_form_frame, text="Claim:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.payment_claim_combobox = ttk.Combobox(payment_form_frame, width=37)
        self.payment_claim_combobox.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(payment_form_frame, text="Payment Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.payment_date_entry = ttk.Entry(payment_form_frame, width=40)
        self.payment_date_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(payment_form_frame, text="Amount:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.payment_amount_entry = ttk.Entry(payment_form_frame, width=40)
        self.payment_amount_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(payment_form_frame, text="Method:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.payment_method_combobox = ttk.Combobox(payment_form_frame, values=["Bank Transfer", "Cash", "Check", "Credit Card"], width=37)
        self.payment_method_combobox.grid(row=3, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Add Payment", command=self.add_payment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Payment", command=self.update_payment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Payment", command=self.delete_payment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_payments).pack(side=tk.LEFT, padx=5)
        
        # Bind treeview selection
        self.payment_tree.bind("<<TreeviewSelect>>", self.on_payment_select)
        
        # Load initial data
        self.refresh_payments()
        self.load_payment_comboboxes()
    
    def load_payment_comboboxes(self):
        # Load claims
        claims = self.execute_sp("sp_GetAllClaims")
        if claims:
            claim_descriptions = [f"{claim[3]} ({claim[0]})" for claim in claims]
            self.payment_claim_combobox['values'] = claim_descriptions
    
    def add_payment(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can add payments")
            return
            
        claim = self.payment_claim_combobox.get()
        payment_date = self.payment_date_entry.get()
        amount = self.payment_amount_entry.get()
        method = self.payment_method_combobox.get()
        
        if not all([claim, payment_date, amount, method]):
            messagebox.showwarning("Validation Error", "All fields are required")
            return
        
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showwarning("Validation Error", "Amount must be a number")
            return
        
        try:
            datetime.strptime(payment_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Validation Error", "Date must be in YYYY-MM-DD format")
            return
        
        # Extract claim ID from combobox value
        claim_id = claim.split("(")[-1].rstrip(")")
        
        payment_id = str(uuid.uuid4())
        params = (payment_id, claim_id, payment_date, amount, method)
        self.execute_sp("sp_AddPayment", params)
        self.refresh_payments()
        self.clear_payment_form()
    
    def update_payment(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can update payments")
            return
            
        selected = self.payment_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a payment to update")
            return
        
        payment_id = self.payment_tree.item(selected[0], "values")[0]
        claim = self.payment_claim_combobox.get()
        payment_date = self.payment_date_entry.get()
        amount = self.payment_amount_entry.get()
        method = self.payment_method_combobox.get()
        
        if not all([claim, payment_date, amount, method]):
            messagebox.showwarning("Validation Error", "All fields are required")
            return
        
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showwarning("Validation Error", "Amount must be a number")
            return
        
        try:
            datetime.strptime(payment_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Validation Error", "Date must be in YYYY-MM-DD format")
            return
        
        # Extract claim ID from combobox value
        claim_id = claim.split("(")[-1].rstrip(")")
        
        params = (payment_id, claim_id, payment_date, amount, method)
        self.execute_sp("sp_UpdatePayment", params)
        self.refresh_payments()
    
    def delete_payment(self):
        if self.user_role != "Admin":
            messagebox.showwarning("Permission Denied", "Only Admin can delete payments")
            return
            
        selected = self.payment_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a payment to delete")
            return
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this payment?"):
            return
        
        payment_id = self.payment_tree.item(selected[0], "values")[0]
        self.execute_sp("sp_DeletePayment", (payment_id,))
        self.refresh_payments()
        self.clear_payment_form()
    
    def refresh_payments(self):
        for item in self.payment_tree.get_children():
            self.payment_tree.delete(item)
        
        payments = self.execute_sp("sp_GetAllPayments")
        if payments:
            for payment in payments:
                self.payment_tree.insert("", tk.END, values=payment)
    
    def on_payment_select(self, event):
        selected = self.payment_tree.selection()
        if not selected:
            return
        
        values = self.payment_tree.item(selected[0], "values")
        self.payment_claim_combobox.set(f"{values[1]} ({values[0]})")
        self.payment_date_entry.delete(0, tk.END)
        self.payment_date_entry.insert(0, values[2])
        self.payment_amount_entry.delete(0, tk.END)
        self.payment_amount_entry.insert(0, values[3])
        self.payment_method_combobox.set(values[4])
    
    def clear_payment_form(self):
        self.payment_claim_combobox.set('')
        self.payment_date_entry.delete(0, tk.END)
        self.payment_amount_entry.delete(0, tk.END)
        self.payment_method_combobox.set('')
    
    # Reports Tab Methods
    def create_reports_tab(self):
        # Створення вкладки
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📊 Звіти")
        
        # Основний фрейм для звітів
        report_frame = ttk.LabelFrame(tab, text="📋 Генерування звітів", padding=(20, 10))
        report_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Фрейм для кнопок звітів
        buttons_frame = ttk.Frame(report_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Кнопки для звітів
        reports = [
            ("📑 Активні поліси", self.generate_active_policies_report),
            ("📈 Претензії по місяцях", self.generate_claims_by_month_report),
            ("💰 Платежі", self.generate_payments_summary_report),
            ("🖨️ Експорт в PDF", self.export_to_pdf)
        ]
        
        for text, cmd in reports:
            btn = ttk.Button(
                buttons_frame, 
                text=text, 
                command=cmd,
                style="Accent.TButton"
            )
            btn.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
        
        # Treeview для табличного відображення даних
        self.report_tree = ttk.Treeview(
            report_frame,
            selectmode="extended",
            show="headings"
        )
        
        # Додаємо смуги прокрутки
        vsb = ttk.Scrollbar(report_frame, orient="vertical", command=self.report_tree.yview)
        hsb = ttk.Scrollbar(report_frame, orient="horizontal", command=self.report_tree.xview)
        self.report_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Розміщення елементів
        self.report_tree.pack(fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Контекстне меню для копіювання даних
        self.treeview_menu = tk.Menu(self.report_tree, tearoff=0)
        self.treeview_menu.add_command(label="Копіювати", command=self.copy_from_treeview)
        self.report_tree.bind("<Button-3>", self.show_treeview_menu)

    def generate_active_policies_report(self):
        self.clear_report_tree()
        """Генерація звіту по активним полісам"""
        # Очищаємо попередні дані
        self.clear_report_tree()
        
        # Встановлюємо колонки
        self.report_tree["columns"] = ("ID", "Клієнт", "Тип", "Сума", "Дата початку", "Дата закінчення", "Статус")
        
        # Налаштування колонок
        for col in self.report_tree["columns"]:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=100, anchor=tk.CENTER)
        
        # Додаємо тестові дані (замініть на реальні дані з БД)
        sample_data = [
            ("1001", "Іванов І.І.", "Авто", "5000", "2023-01-15", "2024-01-15", "Активний"),
            ("1002", "Петров П.П.", "ОСАГО", "2500", "2023-03-20", "2024-03-20", "Активний"),
            ("1003", "Сидорова С.С.", "Життя", "15000", "2022-11-10", "2023-11-10", "Неактивний")
        ]
        
        for item in sample_data:
            self.report_tree.insert("", tk.END, values=item)

    def export_to_pdf(self):
        if not self.report_tree.get_children():
            messagebox.showwarning("Увага", "Немає даних для експорту")
            return

        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 2*cm, "Звіт")
        c.setFont("Helvetica", 10)
        c.drawCentredString(width / 2, height - 2.7*cm, f"Згенеровано: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Початкові координати таблиці
        x_offset = 2*cm
        y_offset = height - 4*cm
        row_height = 1*cm

        columns = self.report_tree["columns"]
        headers = [self.report_tree.heading(col)["text"] for col in columns]

        col_width = (width - 4*cm) / len(columns)

        # Малюємо заголовки таблиці
        c.setFont("Helvetica-Bold", 10)
        for i, header in enumerate(headers):
            c.drawString(x_offset + i * col_width + 2, y_offset, str(header))
        y_offset -= row_height

        # Малюємо дані
        c.setFont("Helvetica", 10)
        for child in self.report_tree.get_children():
            values = self.report_tree.item(child)["values"]
            for i, item in enumerate(values):
                c.drawString(x_offset + i * col_width + 2, y_offset, str(item))
            y_offset -= row_height
            if y_offset < 2*cm:  # Якщо до кінця сторінки, додати нову сторінку
                c.showPage()
                c.setFont("Helvetica", 10)
                y_offset = height - 2*cm

        c.save()
        messagebox.showinfo("Успіх", f"Звіт збережено у файлі: {filename}")

    def clear_report_tree(self):
        """Очищення Treeview"""
        self.report_tree.delete(*self.report_tree.get_children())
        for col in self.report_tree["columns"]:
            self.report_tree.heading(col, text="")
            self.report_tree.column(col, width=0)

    def copy_from_treeview(self):
        """Копіювання виділених даних з Treeview"""
        selected_items = self.report_tree.selection()
        if not selected_items:
            return
        
        # Формуємо текст для копіювання
        copy_text = ""
        
        # Заголовки
        columns = self.report_tree["columns"]
        headers = [self.report_tree.heading(col)["text"] for col in columns]
        copy_text += "\t".join(headers) + "\n"
        
        # Дані
        for item in selected_items:
            values = self.report_tree.item(item)["values"]
            copy_text += "\t".join(str(v) for v in values) + "\n"
        
        # Копіюємо в буфер обміну
        self.root.clipboard_clear()
        self.root.clipboard_append(copy_text.strip())

    def show_treeview_menu(self, event):
        """Показ контекстного меню для Treeview"""
        item = self.report_tree.identify_row(event.y)
        if item:
            self.report_tree.selection_set(item)
            self.treeview_menu.post(event.x_root, event.y_root)

    def generate_active_policies_report(self):
        self.clear_report_tree()
        
        # Встановлення колонок
        self.report_tree["columns"] = ("Policy ID", "Client", "Vehicle", "Premium", "Start Date", "End Date", "Status")
        
        for col in self.report_tree["columns"]:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=120, anchor=tk.CENTER)
        
        # Отримання даних із збереженої процедури
        result = self.execute_sp("sp_GetActivePoliciesReport")
        
        if result:
            for row in result:
                self.report_tree.insert("", tk.END, values=row)

        
    def generate_claims_by_month_report(self):
        self.clear_report_tree()
        
        self.report_tree["columns"] = ("Month", "Claims Count", "Total Damage")
        
        for col in self.report_tree["columns"]:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=150, anchor=tk.CENTER)
        
        result = self.execute_sp("sp_GetClaimsByMonthReport")
        
        if result:
            for row in result:
                self.report_tree.insert("", tk.END, values=row)

    def generate_payments_summary_report(self):
        self.clear_report_tree()
        
        self.report_tree["columns"] = ("Claim ID", "Payment Date", "Amount", "Method")
        
        for col in self.report_tree["columns"]:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=150, anchor=tk.CENTER)
        
        result = self.execute_sp("sp_GetPaymentsSummaryReport")
        
        if result:
            for row in result:
                self.report_tree.insert("", tk.END, values=row)


if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
    style = ttk.Style()
    style.configure("Accent.TButton", font=('Segoe UI', 9, 'bold'), foreground='#fff', background='#007bff')
    style.map("Accent.TButton", background=[('active', '#0069d9')])