import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
import uuid

class InsuranceSystemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Insurance System Management")
        self.root.geometry("1200x800")
        
        # Database connection
        self.connection_string = (
           "Driver={ODBC Driver 17 for SQL Server};"  # Використовуємо новіший драйвер
    "Server=localhost;"                       # Або IP-адреса сервера
    "Database=Helsi;"
    "UID=sa;"
    "PWD=1234;"
    "Encrypt=yes;"                           # Шифрування увімкнено
    "TrustServerCertificate=yes;"            # Довіряємо самопідписаним сертифікатам
    "Connection Timeout=30;"
        )
        self.conn = None
        self.cursor = None
        
        self.connect_to_db()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_client_tab()
        self.create_employee_tab()
        self.create_vehicle_tab()
        self.create_policy_tab()
        self.create_claim_tab()
        self.create_payment_tab()
        self.create_reports_tab()
        
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
    
    # Similar methods for other tabs (Employee, Vehicle, Policy, Claim, Payment)
    # I'll show the structure for one more tab and then you can implement the rest similarly
    
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
    
    def create_vehicle_tab(self):
        # Similar structure to client and employee tabs
        pass
    
    def create_policy_tab(self):
        # Similar structure to client and employee tabs
        pass
    
    def create_claim_tab(self):
        # Similar structure to client and employee tabs
        pass
    
    def create_payment_tab(self):
        # Similar structure to client and employee tabs
        pass
    
    def create_reports_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Reports")
        
        report_frame = ttk.LabelFrame(tab, text="Generate Reports")
        report_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Button(report_frame, text="Active Policies Report", command=self.generate_active_policies_report).pack(pady=5)
        ttk.Button(report_frame, text="Claims by Month Report", command=self.generate_claims_by_month_report).pack(pady=5)
        ttk.Button(report_frame, text="Payments Summary Report", command=self.generate_payments_summary_report).pack(pady=5)
        
        self.report_text = tk.Text(report_frame, height=20, wrap=tk.WORD)
        self.report_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(report_frame, orient="vertical", command=self.report_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_text.configure(yscrollcommand=scrollbar.set)
    
    def generate_active_policies_report(self):
        result = self.execute_sp("sp_GetActivePoliciesReport")
        if result:
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, "Active Policies Report\n\n")
            for row in result:
                self.report_text.insert(tk.END, f"Policy: {row[0]}, Client: {row[1]}, Vehicle: {row[2]}, Premium: {row[3]}\n")
    
    def generate_claims_by_month_report(self):
        result = self.execute_sp("sp_GetClaimsByMonthReport")
        if result:
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, "Claims by Month Report\n\n")
            for row in result:
                self.report_text.insert(tk.END, f"Month: {row[0]}, Claims Count: {row[1]}, Total Damage: {row[2]}\n")
    
    def generate_payments_summary_report(self):
        result = self.execute_sp("sp_GetPaymentsSummaryReport")
        if result:
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, "Payments Summary Report\n\n")
            for row in result:
                self.report_text.insert(tk.END, f"Claim ID: {row[0]}, Payment Date: {row[1]}, Amount: {row[2]}, Method: {row[3]}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = InsuranceSystemApp(root)
    root.mainloop()