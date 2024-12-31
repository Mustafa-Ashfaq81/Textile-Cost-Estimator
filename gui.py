# gui.py

import tkinter as tk
from tkinter import ttk, messagebox
import database

# For PDF generation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from datetime import datetime


# Product categories & subcategories
PRODUCT_CATEGORIES = {
    "Labels": [
        "Satin Labels",
        "Taffeta Labels",
        "Tavik labels",
        "Twill Tape labels",
        "Canvas tape labels",
        "Woven labels"
    ],
    "Hang tags": [
        "Size tag",
        "Pocket Flasher"
    ],
    "Inserts": [],
    "Stickers": [
        "Thermal barcode sticker",
        "Label stickers"
    ],
    "Patches": [
        "PU Patches",
        "Leather Patches",
        "Embroidery Patches",
        "Woven Patches"
    ],
    "Office Stationery": [
        "Visiting Cards",
        "Letter Heads",
        "Envelope",
        "Office File"
    ],
    "Broachers": [],
    "Catalogues": [],
    "Dairies": [],
    "Calendars": [
        "Wall calendars",
        "Table Calendars"
    ],
    "Promotional items": [
        "Mugs",
        "T. Shirts"
    ]
}


class ScrollableFrame(ttk.Frame):
    """
    A reusable scrollable frame container.
    """
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # Update scroll region when the inner frame changes size
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")


class CostEstimatorApp(tk.Frame):
    """
    Main Cost Estimator interface, including:
      - Category/Subcategory
      - Quantity
      - Artwork cost
      - Dimensions & Material
      - Card & Board fields (shown only if "Card & Board" is selected)
      - Additional specs (printing, foil, etc.)
      - Generate PDF report
      - Save to DB
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Mosaic Vision Cost Estimator")
        self.master.geometry("950x650")

        # Initialize or migrate the DB
        database.init_db()

        # Wrap UI in a scrollable frame
        self.scroll_container = ScrollableFrame(self.master)
        self.scroll_container.pack(fill="both", expand=True)

        self.create_widgets_in_scrollable(self.scroll_container.scrollable_frame)
        self.apply_style()

    def create_widgets_in_scrollable(self, parent):
        """
        Creates all GUI widgets within the scrollable frame.
        """
        title_label = tk.Label(parent, text="Cost Estimator", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=10)

        row_idx = 1

        # 1) Client
        tk.Label(parent, text="Client:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.client_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=self.client_name_var, width=30).grid(row=row_idx, column=1, padx=5, pady=5)
        row_idx += 1

        # 2) Category
        tk.Label(parent, text="Category:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.category_var = tk.StringVar()
        cat_values = list(PRODUCT_CATEGORIES.keys())
        self.category_combo = ttk.Combobox(parent, textvariable=self.category_var, values=cat_values, state="readonly")
        self.category_combo.grid(row=row_idx, column=1, padx=5, pady=5)
        self.category_combo.bind("<<ComboboxSelected>>", self.update_subcats)
        row_idx += 1

        # 3) Subcategory
        tk.Label(parent, text="Subcategory:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.subcategory_var = tk.StringVar()
        self.subcategory_combo = ttk.Combobox(parent, textvariable=self.subcategory_var, values=[], state="readonly")
        self.subcategory_combo.grid(row=row_idx, column=1, padx=5, pady=5)
        row_idx += 1

        # 4) Qty (pieces)
        tk.Label(parent, text="Qty (pieces):", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.quantity_var = tk.StringVar()
        tk.Entry(parent, textvariable=self.quantity_var, width=15).grid(row=row_idx, column=1, padx=5, pady=5)
        row_idx += 1

        # 5) Artwork
        tk.Label(parent, text="Artwork Cost:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.artwork_cost_var = tk.StringVar()
        tk.Entry(parent, textvariable=self.artwork_cost_var, width=15).grid(row=row_idx, column=1, padx=5, pady=5)

        self.artwork_cost_type_var = tk.StringVar(value="per_order")
        ttk.Radiobutton(parent, text="Per Pc", variable=self.artwork_cost_type_var, value="per_piece").grid(row=row_idx, column=2, padx=5)
        ttk.Radiobutton(parent, text="Per Order", variable=self.artwork_cost_type_var, value="per_order").grid(row=row_idx, column=3, padx=5)
        row_idx += 1

        # 6) Basic size
        tk.Label(parent, text="Width(in):", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.width_var = tk.StringVar()
        tk.Entry(parent, textvariable=self.width_var, width=10).grid(row=row_idx, column=1, padx=5, pady=5)
        row_idx += 1

        tk.Label(parent, text="Length(in):", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.length_var = tk.StringVar()
        tk.Entry(parent, textvariable=self.length_var, width=10).grid(row=row_idx, column=1, padx=5, pady=5)
        row_idx += 1

        # 7) Material
        tk.Label(parent, text="Material:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.material_var = tk.StringVar()
        mat_opts = [
            "Paper", "Card & Board", "Sticker", "Transparent Sticker",
            "PVC Sticker", "Thermal Sticker", "Fleece", "PU",
            "Leather", "Satin Labels", "Taffeta Labels", "Fabric Labels",
            "Twill Tape"
        ]
        self.material_combo = ttk.Combobox(parent, textvariable=self.material_var, values=mat_opts, state="readonly")
        self.material_combo.grid(row=row_idx, column=1, padx=5, pady=5)
        self.material_combo.bind("<<ComboboxSelected>>", self.on_material_change)
        row_idx += 1

        # -------- Card & Board fields (shown only if 'Card & Board') --------
        # Sheet W-in
        tk.Label(parent, text="Sheet W-in:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.sheetW_var = tk.StringVar()
        self.sheetW_entry = tk.Entry(parent, textvariable=self.sheetW_var, width=10)
        self.sheetW_entry.grid(row=row_idx, column=1, padx=5, pady=5)
        row_idx += 1

        # Sheet L-in
        tk.Label(parent, text="Sheet L-in:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.sheetL_var = tk.StringVar()
        self.sheetL_entry = tk.Entry(parent, textvariable=self.sheetL_var, width=10)
        self.sheetL_entry.grid(row=row_idx, column=1, padx=5, pady=5)
        row_idx += 1

        # Gsm
        tk.Label(parent, text="Gsm:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.gsm_var = tk.StringVar()
        self.gsm_entry = tk.Entry(parent, textvariable=self.gsm_var, width=10)
        self.gsm_entry.grid(row=row_idx, column=1, padx=5, pady=5)
        row_idx += 1

        # Gen
        tk.Label(parent, text="Gen(user):", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.gen_var = tk.StringVar()
        self.gen_entry = tk.Entry(parent, textvariable=self.gen_var, width=10)
        self.gen_entry.grid(row=row_idx, column=1, padx=5, pady=5)
        row_idx += 1

        # Kg-Price
        tk.Label(parent, text="Kg-Price:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.kgPrice_var = tk.StringVar()
        self.kgPrice_entry = tk.Entry(parent, textvariable=self.kgPrice_var, width=10)
        self.kgPrice_entry.grid(row=row_idx, column=1, padx=5, pady=5)
        row_idx += 1

        # Freight
        tk.Label(parent, text="Freight:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.freight_var = tk.StringVar()
        self.freight_entry = tk.Entry(parent, textvariable=self.freight_var, width=10)
        self.freight_entry.grid(row=row_idx, column=1, padx=5, pady=5)
        row_idx += 1

        # Sheet/pkt
        tk.Label(parent, text="Sheet/pkt:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.sheetPkt_var = tk.StringVar()
        self.sheetPkt_entry = tk.Entry(parent, textvariable=self.sheetPkt_var, width=10)
        self.sheetPkt_entry.grid(row=row_idx, column=1, padx=5, pady=5)
        row_idx += 1

        # Product W-in
        tk.Label(parent, text="Prod W-in:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.prodW_var = tk.StringVar()
        self.prodW_entry = tk.Entry(parent, textvariable=self.prodW_var, width=10)
        self.prodW_entry.grid(row=row_idx, column=1, padx=5, pady=5)
        row_idx += 1

        # Product L-in
        tk.Label(parent, text="Prod L-in:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.prodL_var = tk.StringVar()
        self.prodL_entry = tk.Entry(parent, textvariable=self.prodL_var, width=10)
        self.prodL_entry.grid(row=row_idx, column=1, padx=5, pady=5)
        row_idx += 1

        # Card Order Qty
        tk.Label(parent, text="Card Order Qty:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.cardQty_var = tk.StringVar()
        self.cardQty_entry = tk.Entry(parent, textvariable=self.cardQty_var, width=10)
        self.cardQty_entry.grid(row=row_idx, column=1, padx=5, pady=5)
        row_idx += 1

        # Hide all Card & Board fields unless user picks "Card & Board"
        for w in (
            self.sheetW_entry, self.sheetL_entry, self.gsm_entry, self.gen_entry,
            self.kgPrice_entry, self.freight_entry, self.sheetPkt_entry,
            self.prodW_entry, self.prodL_entry, self.cardQty_entry
        ):
            w.grid_remove()

        # 8) Printing
        tk.Label(parent, text="Print Colors(Front):", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.printFront_var = tk.StringVar(value="0")
        tk.Entry(parent, textvariable=self.printFront_var, width=5).grid(row=row_idx, column=1, sticky="w", padx=5, pady=5)

        tk.Label(parent, text="(Back):", font=("Arial", 10, "bold")).grid(row=row_idx, column=2, sticky="e", padx=5, pady=5)
        self.printBack_var = tk.StringVar(value="0")
        tk.Entry(parent, textvariable=self.printBack_var, width=5).grid(row=row_idx, column=3, sticky="w", padx=5, pady=5)
        row_idx += 1

        tk.Label(parent, text="Print Color Cost:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.printColorCost_var = tk.StringVar(value="0")
        tk.Entry(parent, textvariable=self.printColorCost_var, width=10).grid(row=row_idx, column=1, padx=5, pady=5)

        self.printColorCost_type_var = tk.StringVar(value="per_piece")
        ttk.Radiobutton(parent, text="Per Pc", variable=self.printColorCost_type_var, value="per_piece").grid(row=row_idx, column=2, padx=5)
        ttk.Radiobutton(parent, text="Per Ord", variable=self.printColorCost_type_var, value="per_order").grid(row=row_idx, column=3, padx=5)
        row_idx += 1

        # 9) Foil
        tk.Label(parent, text="Foil Cost:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.foil_var = tk.StringVar(value="0")
        tk.Entry(parent, textvariable=self.foil_var, width=10).grid(row=row_idx, column=1, padx=5, pady=5)

        self.foil_type_var = tk.StringVar(value="per_piece")
        ttk.Radiobutton(parent, text="Per Pc", variable=self.foil_type_var, value="per_piece").grid(row=row_idx, column=2, padx=5)
        ttk.Radiobutton(parent, text="Per Ord", variable=self.foil_type_var, value="per_order").grid(row=row_idx, column=3, padx=5)
        row_idx += 1

        # 10) Screen
        tk.Label(parent, text="Screen Cost:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.screen_var = tk.StringVar(value="0")
        tk.Entry(parent, textvariable=self.screen_var, width=10).grid(row=row_idx, column=1, padx=5, pady=5)

        self.screen_type_var = tk.StringVar(value="per_piece")
        ttk.Radiobutton(parent, text="Per Pc", variable=self.screen_type_var, value="per_piece").grid(row=row_idx, column=2, padx=5)
        ttk.Radiobutton(parent, text="Per Ord", variable=self.screen_type_var, value="per_order").grid(row=row_idx, column=3, padx=5)
        row_idx += 1

        # 11) Heat
        tk.Label(parent, text="Heat Cost:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.heat_var = tk.StringVar(value="0")
        tk.Entry(parent, textvariable=self.heat_var, width=10).grid(row=row_idx, column=1, padx=5, pady=5)

        self.heat_type_var = tk.StringVar(value="per_piece")
        ttk.Radiobutton(parent, text="Per Pc", variable=self.heat_type_var, value="per_piece").grid(row=row_idx, column=2, padx=5)
        ttk.Radiobutton(parent, text="Per Ord", variable=self.heat_type_var, value="per_order").grid(row=row_idx, column=3, padx=5)
        row_idx += 1

        # 12) Emboss
        tk.Label(parent, text="Emboss Cost:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.emboss_var = tk.StringVar(value="0")
        tk.Entry(parent, textvariable=self.emboss_var, width=10).grid(row=row_idx, column=1, padx=5, pady=5)

        self.emboss_type_var = tk.StringVar(value="per_piece")
        ttk.Radiobutton(parent, text="Per Pc", variable=self.emboss_type_var, value="per_piece").grid(row=row_idx, column=2, padx=5)
        ttk.Radiobutton(parent, text="Per Ord", variable=self.emboss_type_var, value="per_order").grid(row=row_idx, column=3, padx=5)
        row_idx += 1

        # 13) Coating
        tk.Label(parent, text="Coating:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.coat_var = tk.StringVar(value="None")
        coat_opts = ["None", "UV Coating", "Lamination"]
        self.coat_combo = ttk.Combobox(parent, textvariable=self.coat_var, values=coat_opts, state="readonly")
        self.coat_combo.grid(row=row_idx, column=1, padx=5, pady=5)

        tk.Label(parent, text="Coat Cost:", font=("Arial", 10, "bold")).grid(row=row_idx, column=2, sticky="e", padx=5, pady=5)
        self.coatCost_var = tk.StringVar(value="0")
        tk.Entry(parent, textvariable=self.coatCost_var, width=10).grid(row=row_idx, column=3, padx=5, pady=5)
        row_idx += 1

        self.coat_type_var = tk.StringVar(value="per_piece")
        ttk.Radiobutton(parent, text="Coat Per Pc", variable=self.coat_type_var, value="per_piece").grid(row=row_idx, column=1, padx=5, sticky="w")
        ttk.Radiobutton(parent, text="Coat Per Ord", variable=self.coat_type_var, value="per_order").grid(row=row_idx, column=2, padx=5, sticky="w")
        row_idx += 1

        # 14) Cutting
        tk.Label(parent, text="Cutting Cost:", font=("Arial", 10, "bold")).grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
        self.cut_var = tk.StringVar(value="0")
        tk.Entry(parent, textvariable=self.cut_var, width=10).grid(row=row_idx, column=1, padx=5, pady=5)

        self.cut_type_var = tk.StringVar(value="per_piece")
        ttk.Radiobutton(parent, text="Cut Per Pc", variable=self.cut_type_var, value="per_piece").grid(row=row_idx, column=2, padx=5)
        ttk.Radiobutton(parent, text="Cut Per Ord", variable=self.cut_type_var, value="per_order").grid(row=row_idx, column=3, padx=5)
        row_idx += 1

        # Buttons: Calculate, Save, PDF
        calc_btn = ttk.Button(parent, text="Calculate Cost", command=self.calculate_cost)
        calc_btn.grid(row=row_idx, column=0, columnspan=1, pady=15)

        save_btn = ttk.Button(parent, text="Save to DB", command=self.save_record)
        save_btn.grid(row=row_idx, column=1, columnspan=1, pady=15)

        pdf_btn = ttk.Button(parent, text="Generate PDF", command=self.generate_pdf)
        pdf_btn.grid(row=row_idx, column=2, columnspan=2, pady=15)

        row_idx += 1

        # Result text area
        self.result_text = tk.Text(parent, width=110, height=12, state="disabled", wrap="word")
        self.result_text.grid(row=row_idx, column=0, columnspan=4, pady=5)

    def apply_style(self):
        """
        Apply some basic styling to the widgets.
        """
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Arial", 10, "bold"), padding=6)
        style.configure("TRadiobutton", font=("Arial", 9))

    def update_subcats(self, event=None):
        """
        When the user picks a category, update subcategories.
        """
        cat = self.category_var.get()
        subcats = PRODUCT_CATEGORIES.get(cat, [])
        self.subcategory_combo.config(values=subcats)
        self.subcategory_var.set("")

    def on_material_change(self, event=None):
        """
        Show/hide Card & Board fields based on the selected material.
        """
        mat = self.material_var.get()
        card_fields = (
            self.sheetW_entry, self.sheetL_entry, self.gsm_entry, self.gen_entry,
            self.kgPrice_entry, self.freight_entry, self.sheetPkt_entry,
            self.prodW_entry, self.prodL_entry, self.cardQty_entry
        )
        if mat == "Card & Board":
            for w in card_fields:
                w.grid()
        else:
            for w in card_fields:
                w.grid_remove()

    def calculate_cost(self):
        """
        1) If 'Card & Board', do the advanced snippet logic with user 'Gen' etc.
        2) Combine with the 'per piece/per order' items for a final cost.
        3) Display the breakdown in result_text.
        4) Keep the data in self.calculated_data for DB or PDF usage.
        """
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)

        # Basic info
        client_name = self.client_name_var.get().strip()
        category = self.category_var.get()
        subcat = self.subcategory_var.get()

        try:
            qty_pieces = int(self.quantity_var.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity of pieces.")
            return

        # Artwork
        try:
            aw_cost = float(self.artwork_cost_var.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid artwork cost.")
            return
        aw_type = self.artwork_cost_type_var.get()

        # Basic size
        try:
            w_val = float(self.width_var.get() or 0)
            l_val = float(self.length_var.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid Width/Length (in).")
            return

        mat = self.material_var.get()

        # Default
        card_calc_cost_per_piece = 0.0
        card_calc_details = ""

        if mat == "Card & Board":
            # Attempt to parse the new fields
            try:
                sW = float(self.sheetW_var.get() or 0)
                sL = float(self.sheetL_var.get() or 0)
                gsm_val = float(self.gsm_var.get() or 0)
                gen_val = float(self.gen_var.get() or 0)
                kg_price = float(self.kgPrice_var.get() or 0)
                freight_val = float(self.freight_var.get() or 0)
                sheet_pkt = float(self.sheetPkt_var.get() or 0)
                pW = float(self.prodW_var.get() or 0)
                pL = float(self.prodL_var.get() or 0)
                cQ = float(self.cardQty_var.get() or 0)
            except ValueError:
                messagebox.showerror("Error", "Check Card & Board fields; must be numeric.")
                return

            # total-inches = sW*sL
            total_inches = sW * sL
            # inches*gsm = total_inches*gsm_val
            inches_gsm = total_inches * gsm_val
            # weight/sheet = (inches_gsm)/gen_val
            if gen_val == 0:
                messagebox.showerror("Error", "Gen cannot be zero.")
                return
            w_sheet = inches_gsm / gen_val
            # price/pkt = (w_sheet*kg_price)+freight_val
            price_pkt = (w_sheet * kg_price) + freight_val
            # sheet/pkt => user input sheet_pkt
            if sheet_pkt == 0:
                messagebox.showerror("Error", "sheet/pkt cannot be zero.")
                return
            price_sheet = price_pkt / sheet_pkt

            # total product size = pW*pL
            tot_prod_sz = pW * pL
            # product qty/sheet = total_inches / tot_prod_sz
            pq_sheet = 0.0
            if tot_prod_sz != 0:
                pq_sheet = total_inches / tot_prod_sz

            # how many sheets = cQ / pq_sheet
            sheets_req = pq_sheet and cQ / pq_sheet or 0
            # packets req = sheets_req / sheet_pkt
            packets_req = sheet_pkt and sheets_req / sheet_pkt or 0
            # rate/piece = price_sheet / pq_sheet
            rate_piece = pq_sheet and price_sheet / pq_sheet or 0
            # rate/inch = price_sheet / total_inches
            rate_inch = total_inches and price_sheet / total_inches or 0

            card_calc_cost_per_piece = rate_piece

            # Build textual breakdown
            lines = []
            lines.append(f"SheetW-in={sW}, SheetL-in={sL}, Tot-in={total_inches}")
            lines.append(f"Gsm={gsm_val}, inches*gsm={inches_gsm}, Gen={gen_val}")
            lines.append(f"Weight/sheet={w_sheet:.3f}")
            lines.append(f"KgPrice={kg_price}, Freight={freight_val}, Price/pkt={price_pkt:.2f}")
            lines.append(f"sheet/pkt={sheet_pkt}, Price/sheet={price_sheet:.3f}")
            lines.append(f"Prod W-in={pW}, L-in={pL}, TotSz={tot_prod_sz:.3f}")
            lines.append(f"ProdQty/Sheet={pq_sheet:.3f}, OrderQty={cQ}, SheetsReq={sheets_req:.3f}")
            lines.append(f"PacketsReq={packets_req:.3f}, Rate/Pc={rate_piece:.4f}, Rate/inch={rate_inch:.4f}")
            card_calc_details = "\n".join(lines)

        # Additional specs
        try:
            fCols = int(self.printFront_var.get() or 0)
            bCols = int(self.printBack_var.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid printing colors.")
            return

        pColorC = float(self.printColorCost_var.get() or 0)
        pColorType = self.printColorCost_type_var.get()

        foilC = float(self.foil_var.get() or 0)
        foilT = self.foil_type_var.get()

        screenC = float(self.screen_var.get() or 0)
        screenT = self.screen_type_var.get()

        heatC = float(self.heat_var.get() or 0)
        heatT = self.heat_type_var.get()

        embossC = float(self.emboss_var.get() or 0)
        embossT = self.emboss_type_var.get()

        coat = self.coat_var.get()
        coatC = float(self.coatCost_var.get() or 0)
        coatT = self.coat_type_var.get()

        cutC = float(self.cut_var.get() or 0)
        cutT = self.cut_type_var.get()

        cost_per_piece = card_calc_cost_per_piece
        cost_order = 0.0

        # Artwork
        if aw_type == "per_piece":
            cost_per_piece += aw_cost
        else:
            cost_order += aw_cost

        # Printing color
        if pColorType == "per_piece":
            cost_per_piece += pColorC
        else:
            cost_order += pColorC

        # Foil
        if foilT == "per_piece":
            cost_per_piece += foilC
        else:
            cost_order += foilC

        # Screen
        if screenT == "per_piece":
            cost_per_piece += screenC
        else:
            cost_order += screenC

        # Heat
        if heatT == "per_piece":
            cost_per_piece += heatC
        else:
            cost_order += heatC

        # Emboss
        if embossT == "per_piece":
            cost_per_piece += embossC
        else:
            cost_order += embossC

        # Coating
        if coatT == "per_piece":
            cost_per_piece += coatC
        else:
            cost_order += coatC

        # Cutting
        if cutT == "per_piece":
            cost_per_piece += cutC
        else:
            cost_order += cutC

        total_cost_per_piece = cost_per_piece
        piece_total = total_cost_per_piece * qty_pieces
        grand_total = piece_total + cost_order

        # Show in GUI
        lines = []
        lines.append(f"Client: {client_name}")
        lines.append(f"{category} → {subcat}")
        lines.append(f"Qty(pcs): {qty_pieces}")
        lines.append("")
        if mat == "Card & Board":
            lines.append("---- Card & Board Breakdown ----")
            lines.append(card_calc_details)
            lines.append("--------------------------------")

        lines.append(f"Cost/pc: {total_cost_per_piece:.4f}")
        lines.append(f"Per-Order sum: {cost_order:.4f}")
        lines.append(f"Total (Cost/pc × {qty_pieces}): {piece_total:.4f}")
        lines.append(f"Grand Total: {grand_total:.4f}")

        self.result_text.config(state="normal")
        self.result_text.insert(tk.END, "\n".join(lines))
        self.result_text.config(state="disabled")

        # Store for DB or PDF
        self.calculated_data = {
            "client_name": client_name,
            "category": category,
            "subcategory": subcat,
            "quantity": qty_pieces,

            "artwork_cost": aw_cost,
            "artwork_cost_type": aw_type,
            "width": w_val,
            "length": l_val,
            "material": mat,
            "gsm": float(self.gsm_var.get() or 0) if mat == "Card & Board" else 0.0,
            "card_calc_cost_per_piece": card_calc_cost_per_piece,
            "card_calc_details": card_calc_details,

            "front_colors": fCols,
            "back_colors": bCols,
            "printing_color_cost": pColorC,
            "printing_color_cost_type": pColorType,

            "foil_cost": foilC,
            "foil_cost_type": foilT,
            "screen_cost": screenC,
            "screen_cost_type": screenT,
            "heat_cost": heatC,
            "heat_cost_type": heatT,
            "emboss_cost": embossC,
            "emboss_cost_type": embossT,

            "coating": coat,
            "coating_cost": coatC,
            "coating_cost_type": coatT,

            "cutting_cost": cutC,
            "cutting_cost_type": cutT,

            "total_cost_per_piece": total_cost_per_piece,
            "total_cost_order": grand_total
        }

        messagebox.showinfo("Calculated", f"Calculation done! Grand Total = {grand_total:.2f}")

    def save_record(self):
        """
        Save the current cost data to the database.
        """
        if not hasattr(self, 'calculated_data'):
            messagebox.showerror("Error", "No calculation found. Please 'Calculate Cost' first.")
            return

        row_id = database.save_cost_estimate(self.calculated_data)
        messagebox.showinfo("Saved", f"Record saved with ID={row_id}")

    def generate_pdf(self):
        """
        Generate a professional PDF with headings, spacing, and clarity:
         - Title: "Mosaic Vision Cost Estimation"
         - Sub-title: "Costing for Client: <client_name> (Product: cat -> subcat)"
         - Final cost summary
         - Card & Board details (if any)
         - Additional specs
        """
        if not hasattr(self, 'calculated_data'):
            messagebox.showerror("Error", "No calculation available. Please 'Calculate Cost' first.")
            return

        data = self.calculated_data
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"CostReport_{now_str}.pdf"

        c = canvas.Canvas(pdf_filename, pagesize=A4)
        width, height = A4

        # Title
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2, height - 1 * inch, "Mosaic Vision Cost Estimation")

        # Subtitle
        c.setFont("Helvetica", 12)
        subtitle = f"Costing for Client: {data['client_name']} (Product: {data['category']} → {data['subcategory']})"
        c.drawCentredString(width / 2, height - 1.4 * inch, subtitle)

        y = height - 2 * inch

        # Final Cost Summary
        c.setFont("Helvetica-Bold", 14)
        c.drawString(inch, y, "Final Cost Summary:")
        y -= 0.3 * inch

        c.setFont("Helvetica", 12)
        lines = [
            f"Quantity (pieces): {data['quantity']}",
            f"Cost Per Piece: {data['total_cost_per_piece']:.4f}",
            f"Grand Total: {data['total_cost_order']:.4f}",
        ]
        for line in lines:
            c.drawString(inch, y, line)
            y -= 0.25 * inch

        y -= 0.2 * inch

        # Card & Board details
        if data["material"] == "Card & Board" and data["card_calc_details"]:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(inch, y, "Card & Board Detailed Breakdown:")
            y -= 0.3 * inch

            c.setFont("Helvetica", 12)
            detail_lines = data["card_calc_details"].split("\n")
            for dl in detail_lines:
                c.drawString(inch + 0.2 * inch, y, dl)
                y -= 0.25 * inch

            y -= 0.2 * inch

        # Additional Specs
        c.setFont("Helvetica-Bold", 14)
        c.drawString(inch, y, "Additional Specifications:")
        y -= 0.3 * inch

        c.setFont("Helvetica", 12)
        specs_list = []

        # Artwork
        if data['artwork_cost'] != 0:
            specs_list.append(f"Artwork Cost: {data['artwork_cost']} ({data['artwork_cost_type']})")

        # Printing color
        if data['printing_color_cost'] != 0:
            specs_list.append(
                f"Printing Color Cost: {data['printing_color_cost']} "
                f"({data['printing_color_cost_type']})   "
                f"Colors(Front={data['front_colors']}, Back={data['back_colors']})"
            )

        if data['foil_cost'] != 0:
            specs_list.append(f"Foil Cost: {data['foil_cost']} ({data['foil_cost_type']})")

        if data['screen_cost'] != 0:
            specs_list.append(f"Screen Cost: {data['screen_cost']} ({data['screen_cost_type']})")

        if data['heat_cost'] != 0:
            specs_list.append(f"Heat Cost: {data['heat_cost']} ({data['heat_cost_type']})")

        if data['emboss_cost'] != 0:
            specs_list.append(f"Emboss Cost: {data['emboss_cost']} ({data['emboss_cost_type']})")

        if data['coating_cost'] != 0:
            specs_list.append(f"Coating: {data['coating']} @ {data['coating_cost']} "
                              f"({data['coating_cost_type']})")

        if data['cutting_cost'] != 0:
            specs_list.append(f"Cutting Cost: {data['cutting_cost']} ({data['cutting_cost_type']})")

        if not specs_list:
            specs_list.append("No Additional Specifications (all zero).")

        for spec_line in specs_list:
            c.drawString(inch + 0.2 * inch, y, spec_line)
            y -= 0.25 * inch

        y -= 0.3 * inch

        # If material != Card & Board, show basic dimension info
        if data['material'] != "Card & Board":
            c.setFont("Helvetica-Bold", 14)
            c.drawString(inch, y, "Basic Dimensions:")
            y -= 0.3 * inch
            c.setFont("Helvetica", 12)

            dim_info = [
                f"Width(in): {data['width']}",
                f"Length(in): {data['length']}",
                f"Material: {data['material']}"
            ]
            for di in dim_info:
                c.drawString(inch + 0.2 * inch, y, di)
                y -= 0.25 * inch

        c.showPage()
        c.save()

        messagebox.showinfo("PDF Generated", f"PDF saved as {pdf_filename}")

def run_app():
    root = tk.Tk()
    app = CostEstimatorApp(master=root)
    app.mainloop()