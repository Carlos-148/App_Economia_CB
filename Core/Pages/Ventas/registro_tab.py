"""
Core.Pages.Ventas.registro_tab - Registro de ventas
"""

import tkinter as tk
import tkinter as tk
from tkinter import messagebox, END, ttk, messagebox

logger = __import__('Core.Common.logger', fromlist=['setup_logger']).setup_logger()


class RegistrarVentaTab(ttk.Frame):
    """Tab para registrar ventas"""
    
    def __init__(self, parent, backend):
        super().__init__(parent)
        self.backend = backend
        self.logger = logger
        
        self.product_map = {}
        self.client_name_to_id = {}
        self.item_rows = []
        self.next_item_id = 1
        self.selected_client_id = None
        self.selected_client_name = None
        
        self.setup_ui()
        self.load_products()
        self.load_clients()
    
    def setup_ui(self):
        """Configura la interfaz"""
        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        paned = ttk.Panedwindow(main, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left: Productos
        left = ttk.Frame(paned)
        paned.add(left, weight=3)
        
        header = ttk.Frame(left)
        header.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(header, text="➕ Registrar Venta", font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT)
        
        ttk.Button(header, text="➕ Agregar Producto", command=self.add_item_dialog).pack(side=tk.LEFT, padx=(0, 5))
        
        cols = ("Producto", "Cantidad", "Precio", "Subtotal")
        self.products_tree = ttk.Treeview(left, columns=cols, show="headings", height=12)
        
        for c in cols:
            self.products_tree.heading(c, text=c)
        
        self.products_tree.column("Producto", width=240)
        self.products_tree.column("Cantidad", width=80, anchor=tk.CENTER)
        self.products_tree.column("Precio", width=100, anchor=tk.E)
        self.products_tree.column("Subtotal", width=100, anchor=tk.E)
        
        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        
        self.products_tree.bind("<Double-1>", self.on_tree_double_click)
        
        # Right: Clientes
        right = ttk.Frame(paned, width=300)
        paned.add(right, weight=1)
        
        ttk.Label(right, text="👥 Seleccionar Cliente", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 8))
        
        client_cols = ("Nombre",)
        self.clients_tree = ttk.Treeview(right, columns=client_cols, show="headings", height=12)
        self.clients_tree.heading("Nombre", text="Nombre")
        self.clients_tree.column("Nombre", width=280)
        self.clients_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        client_scroll = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.clients_tree.yview)
        self.clients_tree.configure(yscroll=client_scroll.set)
        client_scroll.pack(side=tk.LEFT, fill=tk.Y)
        
        self.clients_tree.bind("<<TreeviewSelect>>", self.on_client_select)
        
        # Total
        total_frame = ttk.LabelFrame(main, text="💰 TOTAL A PAGAR")
        total_frame.pack(fill=tk.X, pady=(8, 0))
        
        self.total_label = ttk.Label(total_frame, text="$0.00", font=("Segoe UI", 18, "bold"))
        self.total_label.pack(anchor="w", pady=6)
        
        ttk.Button(total_frame, text="✅ Registrar Venta", command=self.submit_sale).pack(fill=tk.X, padx=6, pady=(0, 6))
    
    def load_products(self):
        """Carga productos"""
        try:
            prods = self.backend.get_productos_con_costo()
            self.product_map.clear()
            
            for p in prods:
                name = p.get("nombre", "")
                self.product_map[name] = p
            
            self.logger.info(f"Productos cargados: {len(self.product_map)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
    
    def load_clients(self):
        """Carga clientes"""
        try:
            for item in self.clients_tree.get_children():
                self.clients_tree.delete(item)
            
            rows = self.backend.get_clientes_activos()
            self.client_name_to_id = {r["nombre"]: r["id"] for r in rows}
            
            for client in rows:
                self.clients_tree.insert("", tk.END, iid=str(client["id"]), values=(client["nombre"],))
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
    
    def add_item_dialog(self):
        """Agrega un item a la venta"""
        if not self.product_map:
            messagebox.showwarning("Aviso", "No hay productos")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Agregar Producto")
        dialog.geometry("400x150")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Producto:").pack(anchor="w")
        product_combo = ttk.Combobox(frame, values=list(self.product_map.keys()), state="readonly", width=40)
        product_combo.pack(fill=tk.X, pady=(0, 8))
        
        if self.product_map:
            product_combo.set(list(self.product_map.keys())[0])
        
        ttk.Label(frame, text="Cantidad:").pack(anchor="w")
        qty_entry = ttk.Entry(frame)
        qty_entry.insert(0, "1")
        qty_entry.pack(fill=tk.X, pady=(0, 8))
        qty_entry.focus()
        
        def on_add():
            prod_name = product_combo.get().strip()
            prod = self.product_map.get(prod_name)
            
            if not prod:
                messagebox.showerror("Error", "Producto no encontrado")
                return
            
            try:
                qty = int(float(qty_entry.get().strip()))
            except ValueError:
                messagebox.showerror("Error", "Cantidad inválida")
                return
            
            if qty <= 0:
                messagebox.showwarning("Aviso", "Cantidad > 0")
                return
            
            item_id = self.next_item_id
            self.next_item_id += 1
            unit_price = float(prod.get("precio_venta", 0) or 0)
            subtotal = round(unit_price * qty, 2)
            
            self.products_tree.insert(
                "",
                tk.END,
                iid=str(item_id),
                values=(prod_name, qty, f"${unit_price:.2f}", f"${subtotal:.2f}")
            )
            
            self.item_rows.append({
                "item_id": item_id,
                "product_id": prod.get("id"),
                "product_name": prod_name,
                "quantity": qty,
                "unit_price": unit_price
            })
            
            self.update_total()
            dialog.destroy()
        
        ttk.Button(frame, text="✅ Agregar", command=on_add).pack(pady=(8, 0), fill=tk.X)
    
    def on_tree_double_click(self, event):
        """Edita cantidad en doble click"""
        item = self.products_tree.identify_row(event.y)
        
        if not item:
            return
        
        row = next((r for r in self.item_rows if str(r["item_id"]) == str(item)), None)
        
        if not row:
            return
        
        new_qty = tk.simpledialog.askinteger("Editar", f"Nueva cantidad:", initialvalue=row["quantity"])
        
        if new_qty and new_qty > 0:
            row["quantity"] = new_qty
            new_sub = round(row["unit_price"] * new_qty, 2)
            self.products_tree.item(
                str(row["item_id"]),
                values=(row["product_name"], new_qty, f"${row['unit_price']:.2f}", f"${new_sub:.2f}")
            )
            self.update_total()
    
    def on_client_select(self, event):
        """Selecciona cliente"""
        selection = self.clients_tree.selection()
        
        if not selection:
            self.selected_client_id = None
            return
        
        cid = int(selection[0])
        self.selected_client_id = cid
        
        for name, idv in self.client_name_to_id.items():
            if idv == cid:
                self.selected_client_name = name
                break
    
    def update_total(self):
        """Actualiza total"""
        subtotal = sum(r["unit_price"] * r["quantity"] for r in self.item_rows)
        self.total_label.config(text=f"${subtotal:.2f}")
    
    def submit_sale(self):
        """Registra la venta"""
        if not self.selected_client_id:
            messagebox.showwarning("Aviso", "Selecciona cliente")
            return
        
        if not self.item_rows:
            messagebox.showwarning("Aviso", "Agrega productos")
            return
        
        try:
            items = [
                {"product_id": r["product_id"], "quantity": r["quantity"], "unit_price": r["unit_price"]}
                for r in self.item_rows
            ]
            
            res = self.backend.crear_venta_multiple(self.selected_client_id, items)
            total = res.get("total", 0)
            
            messagebox.showinfo(
                "✅ Éxito",
                f"Venta registrada\nCliente: {self.selected_client_name}\nTotal: ${total:.2f}"
            )
            
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
    
    def clear_form(self):
        """Limpia el formulario"""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        self.item_rows.clear()
        self.next_item_id = 1
        self.clients_tree.selection_remove(self.clients_tree.selection())
        self.selected_client_id = None
        self.total_label.config(text="$0.00")