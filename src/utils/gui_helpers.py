import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pandas as pd
from data_loading.loader_factory import get_loader

class DataLoaderGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SCADA Dataset Loader")
        self.root.geometry("480x420")

        self.path_to_data_folder = tk.StringVar()
        tk.Label(self.root, text="Path to dataset folder:").pack(pady=4)
        tk.Entry(self.root, textvariable=self.path_to_data_folder, width=55).pack()
        tk.Button(self.root, text="Select folder", command=self.select_folder).pack(pady=5)

        tk.Label(self.root, text="Dataset type:").pack(pady=4)
        self.dataset_type = tk.StringVar(value="kelmarsh")
        ttk.Combobox(self.root, textvariable=self.dataset_type,
                     values=["kelmarsh", "caretocompare_a", "caretocompare_b", "caretocompare_c", "penmanshiel"]).pack()

        tk.Label(self.root, text="Columns to load (optional):").pack(pady=4)
        self.columns_text = tk.Text(self.root, height=4, width=50)
        self.columns_text.insert("1.0", "timestamp, wind_speed")
        self.columns_text.pack()

        tk.Button(self.root, text="Load dataset", command=self.load_data).pack(pady=15)

        self.output_label = tk.Label(self.root, text="", fg="green")
        self.output_label.pack()

        self.root.mainloop()

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_to_data_folder.set(folder)

    def load_data(self):
        folder_path = self.path_to_data_folder.get()
        dataset_type = self.dataset_type.get()
        cols = self.columns_text.get("1.0", "end").strip()
        columns_to_keep = [col.strip() for col in cols.split(",")] if cols else None

        try:
            loader = get_loader(dataset_type, folder_path, columns_to_keep)
            data_frame = loader.load_all()
            self.output_label.config(text=f"Loaded dataset of: {len(data_frame)} records, {len(data_frame.columns)} columns")
            messagebox.showinfo("Success", f"Successfully loaded dataset ({len(data_frame)} records).")

            self.preview_dataframe(data_frame)

        except Exception as e:
            messagebox.showerror("Error", str(e))


    def preview_dataframe(self, data_frame: pd.DataFrame, limit=20):
        if data_frame is None or data_frame.empty:
            messagebox.showwarning("No data loaded", "No data to preview.")
            return

        preview_df = data_frame.head(limit)
        cols = list(preview_df.columns)
        data = preview_df.values.tolist()

        preview = tk.Toplevel(self.root)
        preview.title("Data preview")
        preview.geometry("1000x600")

        frame = ttk.Frame(preview)
        frame.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(frame, columns=cols, show="headings")
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=140, anchor="center")

        for row in data:
            row_str = ["" if pd.isna(v) else str(v) for v in row]
            tree.insert("", "end", values=row_str)

        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=y_scroll.set)

        info = ttk.Label(preview, text=f"Preview of {len(preview_df)}/{len(data_frame)} records.")
        info.pack(side=tk.BOTTOM, pady=5)
