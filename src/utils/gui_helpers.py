import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pandas as pd
from app_state import AppState

class DataLoaderGUI:
    def __init__(self, state: AppState):
        self.app_state = state
        self.root = tk.Tk()
        self.root.title("SCADA Dataset Loader")
        self.root.geometry("480x420")

        self.path_to_data_folder = tk.StringVar()
        tk.Label(self.root, text="Path to dataset folder:").pack(pady=4)
        tk.Entry(self.root, textvariable=self.path_to_data_folder, width=55).pack()
        tk.Button(self.root, text="Select folder", command=self.select_folder).pack(pady=5)

        tk.Label(self.root, text="Dataset type:").pack(pady=4)
        self.dataset_type = tk.StringVar(value="Kelmarsh")
        ttk.Combobox(self.root, textvariable=self.dataset_type,
                     values=["Kelmarsh", "Penmanshiel", "CareToCompare"]).pack()

        tk.Label(self.root, text="Columns to load (optional):").pack(pady=4)
        self.columns_text = tk.Text(self.root, height=4, width=50)
        # self.columns_text.insert("1.0", "timestamp, wind_speed")
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
            self.app_state.load_dataset(dataset_type, folder_path, columns_to_keep)
            dataset = self.app_state.get_dataset()
            data_frame = dataset.get_dataframe()
            self.output_label.config(text=f"Loaded dataset of: {len(data_frame)} records, {len(data_frame.columns)} columns")
            messagebox.showinfo("Success", f"Successfully loaded dataset ({len(data_frame)} records).")

            self.preview_dataframe(data_frame)
            
            DataAnalysisGUI(self.app_state)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def preview_dataframe(self, data_frame: pd.DataFrame, limit=10):
        if data_frame is None or data_frame.empty:
            messagebox.showwarning("No data loaded", "No data to preview.")
            return

        preview_df = data_frame.head(limit)
        cols = list(preview_df.columns)
        data = preview_df.values.tolist()

        preview = tk.Toplevel(self.root)
        preview.title("Data preview")
        preview.geometry("1000x350")

        container = ttk.Frame(preview)
        container.pack(fill=tk.BOTH, expand=True)

        horizontal_scroll = ttk.Scrollbar(container, orient="horizontal")
        vertical_scroll = ttk.Scrollbar(container, orient="vertical")

        tree = ttk.Treeview(
            container,
            columns=cols,
            show="headings",
            xscrollcommand=horizontal_scroll.set,
            yscrollcommand=vertical_scroll.set
        )

        horizontal_scroll.config(command=tree.xview)
        vertical_scroll.config(command=tree.yview)

        tree.grid(row=0, column=0, sticky="nsew")
        vertical_scroll.grid(row=0, column=1, sticky="ns")
        horizontal_scroll.grid(row=1, column=0, sticky="ew")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=140, anchor="center")

        for row in data:
            row_str = ["" if pd.isna(v) else str(v) for v in row]
            tree.insert("", "end", values=row_str)

        info = ttk.Label(preview, text=f"Preview of {len(preview_df)}/{len(data_frame)} records.")
        info.pack(side=tk.BOTTOM, pady=5)



class DataAnalysisGUI:
    def __init__(self, app_state):
        self.app_state = app_state
        self.root = tk.Toplevel()
        self.root.title("Wind Farm Data Analysis")
        self.root.geometry("1000x600")

        ttk.Label(self.root, text="Data Analysis Overview", font=("Segoe UI", 13, "bold")).pack(pady=10)

        ttk.Button(self.root, text="Run Analysis", command=self.run_analysis).pack(pady=5)

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def run_analysis(self):
        dataset = self.app_state.get_dataset()
        if not dataset:
            messagebox.showwarning("No dataset", "Load a dataset first.")
            return

        try:
            results = dataset.analyze_overview()

            for name, df in results.items():
                frame = ttk.Frame(self.tabs)
                self.tabs.add(frame, text=name.replace("_", " ").title())

                self.display_dataframe(df, frame)

        except Exception as e:
            messagebox.showerror("Analysis error", str(e))

    def display_dataframe(self, df: pd.DataFrame, parent):
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True)

        horizontal_scroll = ttk.Scrollbar(container, orient="horizontal")
        vertical_scroll = ttk.Scrollbar(container, orient="vertical")

        tree = ttk.Treeview(
            container,
            columns=list(df.columns),
            show="headings",
            xscrollcommand=horizontal_scroll.set,
            yscrollcommand=vertical_scroll.set
        )

        horizontal_scroll.config(command=tree.xview)
        vertical_scroll.config(command=tree.yview)

        tree.grid(row=0, column=0, sticky="nsew")
        vertical_scroll.grid(row=0, column=1, sticky="ns")
        horizontal_scroll.grid(row=1, column=0, sticky="ew")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=160, anchor="center")

        for _, row in df.iterrows():
            values = [str(value) for value in row.values]
            tree.insert("", "end", values=values)
