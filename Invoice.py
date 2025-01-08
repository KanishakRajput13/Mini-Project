import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from fpdf import FPDF
import googlemaps

# Load item list from JSON file
with open('item_list.json', 'r') as file:
    item_list = json.load(file)

# Initialize the main window
root = tk.Tk()
root.title("Invoice Generator")

# Google Maps API Key
API_KEY = 'AIzaSyDEEAzIeGC9L7Rchjiy8qjdZq_9U-HIn_w'
gmaps = googlemaps.Client(key=API_KEY)

# Order ID
order_id_label = tk.Label(root, text="Order ID:")
order_id_label.pack(pady=5)
order_id_entry = tk.Entry(root, width=50)
order_id_entry.pack(pady=5)

# Purchase Date
purchase_date_label = tk.Label(root, text="Purchase Date:")
purchase_date_label.pack(pady=5)
purchase_date_entry = DateEntry(root, width=47, background='darkblue', foreground='white', borderwidth=2)
purchase_date_entry.pack(pady=5)

# Shipping Address
shipping_address_label = tk.Label(root, text="Shipping Address:")
shipping_address_label.pack(pady=5)
shipping_address_entry = tk.Entry(root, width=50)
shipping_address_entry.pack(pady=5)

# Autocomplete Listbox for Address
autocomplete_listbox = tk.Listbox(root, width=50, height=5)
autocomplete_listbox.place_forget()

def autocomplete_address(event):
    address = shipping_address_entry.get()
    if address:
        results = gmaps.places_autocomplete(address)
        if results:
            autocomplete_listbox.delete(0, tk.END)
            for result in results:
                autocomplete_listbox.insert(tk.END, result['description'])
            x = shipping_address_entry.winfo_x()
            y = shipping_address_entry.winfo_y() + shipping_address_entry.winfo_height()
            autocomplete_listbox.place(x=x, y=y)
            autocomplete_listbox.tkraise()  # Raise the listbox to the top of the stacking order
        else:
            autocomplete_listbox.place_forget()
    else:
        autocomplete_listbox.place_forget()

def select_address(event=None):
    selected_address = autocomplete_listbox.get(tk.ACTIVE)
    shipping_address_entry.delete(0, tk.END)
    shipping_address_entry.insert(0, selected_address)
    autocomplete_listbox.place_forget()
    purchase_date_entry.focus_set()

shipping_address_entry.bind('<KeyRelease>', autocomplete_address)
shipping_address_entry.bind('<Down>', lambda event: autocomplete_listbox.focus_set())
autocomplete_listbox.bind('<Return>', select_address)
autocomplete_listbox.bind('<Double-1>', select_address)
autocomplete_listbox.bind('<Escape>', lambda event: autocomplete_listbox.place_forget())

# Items Section
items_frame = tk.Frame(root)
items_frame.pack(pady=10)

item_name_label = tk.Label(items_frame, text="Item Name:")
item_name_label.grid(row=0, column=0, padx=5, pady=5)
item_name_entry = tk.Entry(items_frame, width=30)
item_name_entry.grid(row=0, column=1, padx=5)

# Autocomplete Listbox for Item Name
item_autocomplete_listbox = tk.Listbox(items_frame, width=30, height=5)
item_autocomplete_listbox.grid(row=1, column=1, padx=5, pady=5)
item_autocomplete_listbox.place_forget()

def autocomplete_item_name(event):
    item_name = item_name_entry.get()
    if item_name:
        matching_items = [item['item'] for item in item_list if item_name.lower() in item['item'].lower()]
        if matching_items:
            item_autocomplete_listbox.delete(0, tk.END)
            for item in matching_items:
                item_autocomplete_listbox.insert(tk.END, item)
            x = item_name_entry.winfo_x()
            y = item_name_entry.winfo_y() + item_name_entry.winfo_height()
            item_autocomplete_listbox.place(x=x, y=y)
            item_autocomplete_listbox.tkraise()  # Raise the listbox to the top of the stacking order
        else:
            item_autocomplete_listbox.place_forget()
    else:
        item_autocomplete_listbox.place_forget()

def select_item_name(event=None):
    selected_item_name = item_autocomplete_listbox.get(tk.ACTIVE)
    item_name_entry.delete(0, tk.END)
    item_name_entry.insert(0, selected_item_name)
    item_autocomplete_listbox.place_forget()
    quantity_entry.focus_set()

item_name_entry.bind('<KeyRelease>', autocomplete_item_name)
item_name_entry.bind('<Down>', lambda event: item_autocomplete_listbox.focus_set())
item_autocomplete_listbox.bind('<Return>', select_item_name)
item_autocomplete_listbox.bind('<Double-1>', select_item_name)
item_autocomplete_listbox.bind('<Escape>', lambda event: item_autocomplete_listbox.place_forget())

quantity_label = tk.Label(items_frame, text="Quantity:")
quantity_label.grid(row=2, column=0, padx=5, pady=5)
quantity_entry = tk.Entry(items_frame, width=30)
quantity_entry.grid(row=2, column=1, padx=5)

add_item_button = ttk.Button(items_frame, text="Add Item")
add_item_button.grid(row=3, column=0, columnspan=2, pady=10)

# Items List
items_list_label = tk.Label(root, text="Items:")
items_list_label.pack(pady=5)
items_listbox = tk.Listbox(root, width=50, height=10)
items_listbox.pack(pady=5)

# Total Cost
total_cost_label = tk.Label(root, text="Total Cost: Rs:0.00")
total_cost_label.pack(pady=5)

# Functions
items = []
total_cost = 0.0

def add_item():
    global total_cost
    item_name = item_name_entry.get().strip()
    quantity = quantity_entry.get().strip()
    if not item_name or not quantity:
        messagebox.showwarning("Input Error", "Please enter both item name and quantity.")
        return
    try:
        quantity = int(quantity)
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number for quantity.")
        return
    
    # Find the item in the item list
    item = next((item for item in item_list if item['item'].lower() == item_name.lower()), None)
    if not item:
        messagebox.showerror("Input Error", "Item not found in the database.")
        return
    
    cost = item['cost'] * quantity
    items.append((item_name, quantity, cost))
    items_listbox.insert(tk.END, f"{item_name} - Quantity: {quantity} - Cost: Rs:{cost:.2f}")
    total_cost += cost
    total_cost_label.config(text=f"Total Cost: Rs:{total_cost:.2f}")
    item_name_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)
    item_name_entry.focus_set()

add_item_button.config(command=add_item)

def wrap_text(text, width):
    words = text.split()
    lines = []
    for i in range(0, len(words), width):
        lines.append(' '.join(words[i:i+width]))
    return '\n'.join(lines)

def generate_pdf():
    order_id = order_id_entry.get().strip()
    purchase_date = purchase_date_entry.get().strip()
    shipping_address = shipping_address_entry.get().strip()
    
    if not order_id or not purchase_date or not shipping_address:
        messagebox.showwarning("Input Error", "Please fill in all the order details.")
        return
    
    # Create invoices directory if it doesn't exist
    if not os.path.exists("invoices"):
        os.makedirs("invoices")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Invoice", ln=True, align='C')
    
    # Order ID
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Order ID: {order_id}", ln=True)
    
    # Purchase Date
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Purchase Date: {purchase_date}", ln=True)
    
    # Shipping Address
    pdf.set_font("Arial", 'B', 12)
    wrapped_address = wrap_text(shipping_address, 4)
    pdf.multi_cell(200, 10, txt=f"Shipping Address: {wrapped_address}")
    pdf.cell(200, 10, txt="", ln=True)  # Empty line
    
    # Items Table Header
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(200, 200, 200)  # Set fill color to a shade of gray
    pdf.cell(80, 10, txt="Item Name", border=1, fill=True)
    pdf.cell(40, 10, txt="Quantity", border=1, fill=True)
    pdf.cell(40, 10, txt="Cost", border=1, ln=True, fill=True)
    
    # Items
    pdf.set_font("Arial", size=12)
    for item_name, quantity, cost in items:
        pdf.cell(80, 10, txt=item_name, border=1)
        pdf.cell(40, 10, txt=str(quantity), border=1)
        pdf.cell(40, 10, txt=f"Rs:{cost:.2f}", border=1, ln=True)
    
    pdf.cell(160, 10, txt="", ln=True)  # Empty line
    
    # Total Cost
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(80, 10, txt="Total Cost", border=1)
    pdf.cell(40, 10, txt="", border=1)
    pdf.cell(40, 10, txt=f"Rs:{total_cost:.2f}", border=1, ln=True)
    
    # Save the PDF with the order ID as the filename
    pdf_filename = f"invoices/invoice_{order_id}.pdf"
    pdf.output(pdf_filename)
    messagebox.showinfo("Success", f"Invoice PDF generated successfully and saved as {pdf_filename}!")

# Generate PDF Button
generate_pdf_button = ttk.Button(root, text="Generate PDF", command=generate_pdf)
generate_pdf_button.pack(pady=10)

# Bind Enter key to navigate to the next field
order_id_entry.bind('<Return>', lambda event: purchase_date_entry.focus_set())
purchase_date_entry.bind('<Return>', lambda event: shipping_address_entry.focus_set())
shipping_address_entry.bind('<Return>', lambda event: item_name_entry.focus_set())
item_name_entry.bind('<Return>', lambda event: quantity_entry.focus_set())
quantity_entry.bind('<Return>', lambda event: add_item_button.focus_set())
add_item_button.bind('<Return>', lambda event: item_name_entry.focus_set())

# Run the application
root.mainloop()