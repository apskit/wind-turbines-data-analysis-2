import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pandas as pd
from app_state import AppState
from data_processing.anomaly_detection import AnomalyDetector
from plots import plot_correlation_matrix, plot_data_uptime, plot_variable_boxplot, plot_variable_histogram, plot_variable_timeline, plot_variable_timeseries
from wind_farm_data import WindFarmDataset

class DataLoaderGUI:
    def __init__(self, state: AppState):
        self.app_state = state
        self.root = tk.Tk()
        self.root.title("Wind Farm Dataset Loader")
        self.root.geometry("480x420")

        ttk.Label(self.root, text="Dataset Loader", font=("Segoe UI", 13, "bold")).pack(pady=10)

        self.path_to_data_folder = tk.StringVar()
        ttk.Label(self.root, text="Path to dataset folder:").pack(pady=4)
        ttk.Entry(self.root, textvariable=self.path_to_data_folder, width=55).pack()
        ttk.Button(self.root, text="Select folder", command=self.select_folder).pack(pady=5)

        ttk.Label(self.root, text="Dataset type:").pack(pady=4)
        self.dataset_type = tk.StringVar(value="Kelmarsh")
        ttk.Combobox(self.root, textvariable=self.dataset_type,
                     values=["Kelmarsh", "Penmanshiel", "CareToCompare"]).pack()

        ttk.Label(self.root, text="Columns to load (optional):").pack(pady=4)
        self.columns_text = tk.Text(self.root, height=4, width=50)
        # self.columns_text.insert("1.0", "timestamp, wind_speed")
        self.columns_text.pack()

        self.show_preview = tk.BooleanVar()
        checkbox = tk.Checkbutton(self.root, text="Show data preview", variable=self.show_preview)
        checkbox.pack(pady=10)

        ttk.Button(self.root, text="Load dataset", command=self.load_data).pack(pady=15)

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
            # messagebox.showinfo("Success", f"Successfully loaded dataset ({len(data_frame)} records).")

            if self.show_preview.get():
                self.preview_dataframe(data_frame)
            
            DataAnalysisGUI(self.app_state, dataset)
            AnomalyDetectionGUI(self.app_state, dataset)

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
    def __init__(self, app_state: AppState, dataset: WindFarmDataset):
        self.app_state = app_state
        self.dataset = dataset
        self.df = dataset.get_dataframe()
        self.selected_parameter = None

        self.analysis_frames = {}
        self.root = tk.Toplevel()
        self.root.title("Wind Farm Data Analysis")
        self.root.geometry("1000x600")

        ttk.Label(self.root, text="Data Analysis Overview", font=("Segoe UI", 13, "bold")).pack(pady=10)

        options_frame = ttk.Frame(self.root)
        options_frame.pack(pady=5)

        tk.Label(options_frame, text="Turbines:").pack(side=tk.LEFT, pady=6)
        self.selected_turbine = tk.StringVar(value="all")
        turbines_list = dataset.get_turbines_list()
        turbines = ["all"] + sorted(turbines_list)
        ttk.Combobox(options_frame, textvariable=self.selected_turbine, values=turbines).pack(side=tk.LEFT, pady=6)


        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=5)

        ttk.Button(
            button_frame, 
            text="Availability Analysis", 
            command=lambda: self.run_analysis(type="availability")
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame, 
            text="Variable Ranges Analysis", 
            command=lambda: self.run_analysis(type="variable", turbine_id=self.selected_turbine.get())
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame, 
            text="Plot Data Availability", 
            command=lambda: plot_data_uptime(self.df, turbine_id=self.selected_turbine.get())
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame, 
            text="Plot Variable Availability", 
            command=self.on_plot_timeline
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Plot Variable Ranges Boxplot",
            command=self.on_plot_boxplot
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Plot Variable Ranges Histogram",
            command=self.on_plot_histogram
        ).pack(side=tk.LEFT, padx=5)


        normalization_frame = ttk.Frame(self.root)
        normalization_frame.pack(pady=5)

        ttk.Button(
            normalization_frame, 
            text="Plot Correlation Matrix", 
            command=lambda: [dataset.set_correlation_matrix(), plot_correlation_matrix(dataset.get_correlation_matrix())]
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            normalization_frame, 
            text="Correlation Analysis", 
            command=lambda: self.run_correlation_analysis(preview=True)
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            normalization_frame, 
            text="Remove Correlated Signals", 
            command=lambda: self.run_correlation_analysis(preview=False)
        ).pack(side=tk.LEFT, padx=5)
        tk.Label(normalization_frame, text="  |  ").pack(side=tk.LEFT, pady=6)

        tk.Label(normalization_frame, text="Dataset for plotting:").pack(side=tk.LEFT, pady=6)
        self.selected_dataset = tk.StringVar(value="preprocessed")
        datasets_list = ["preprocessed", "z-score normalization", "min-max normalization", "robust scaling"]
        ttk.Combobox(normalization_frame, textvariable=self.selected_dataset, values=datasets_list).pack(side=tk.LEFT, pady=6)

        ttk.Button(
            normalization_frame, 
            text="Change", 
            command=lambda: self.change_dataset(dataset, type=self.selected_dataset.get())
        ).pack(side=tk.LEFT, padx=5)

        self.dataset_change_label = tk.Label(normalization_frame, text="", fg="green")
        self.dataset_change_label.pack()

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def run_analysis(self, type: str | None = None, turbine_id: str | None = None):
        dataset = self.app_state.get_dataset()
        if not dataset:
            messagebox.showwarning("Dataset not found", "Load a dataset first.")
            return

        try:
            if type:
                if type == "availability":
                    analysis_key = f"availability_and_time_ranges"
                    result_df = dataset.analyze_availability()
                elif type == "variable":
                    analysis_key = f"variable_ranges_{'T' + turbine_id if turbine_id.isdigit() else 'all'}"
                    result_df = dataset.analyze_variable_ranges(turbine_id)             
            
                if analysis_key in self.analysis_frames:
                    self.tabs.forget(self.analysis_frames[analysis_key])
                    del self.analysis_frames[analysis_key]

                frame = ttk.Frame(self.tabs)
                self.analysis_frames[analysis_key] = frame
                self.tabs.add(frame, text=analysis_key.replace("_", " ").title())
            
            else:
                result_df = dataset.analyze_overview(turbine_id)

                for name, result_df in result_df.items():
                    frame = ttk.Frame(self.tabs)
                    self.tabs.add(frame, text=name.replace("_", " ").title())

            self.display_dataframe(result_df, frame)
            self.tabs.select(frame)

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

        tree.bind("<<TreeviewSelect>>", lambda e: self.on_parameter_select(e, tree))

    def on_parameter_select(self, event, tree):
        selected_item = tree.focus()
        values = tree.item(selected_item, "values")
        if not values:
            return
        self.selected_parameter = values[0]
      
    def on_plot_boxplot(self):
        if not self.selected_parameter:
            messagebox.showwarning("No parameter selected", "Select signal from Variable Analysis tab first.")
            return
        turbine = self.selected_turbine.get()
        plot_variable_boxplot(self.df, self.selected_parameter, turbine)

    def on_plot_histogram(self):
        if not self.selected_parameter:
            messagebox.showwarning("No parameter selected", "Select signal from Variable Analysis tab first.")
            return
        turbine = self.selected_turbine.get()
        plot_variable_histogram(self.df, self.selected_parameter, turbine)

    def on_plot_timeline(self):
        if not self.selected_parameter:
            messagebox.showwarning("No parameter selected", "Select signal from Variable Ranges tab first.")
            return
        turbine = self.selected_turbine.get()
        plot_variable_timeline(self.df, self.selected_parameter, turbine)

    def change_dataset(self, dataset: WindFarmDataset, type: str):
        if type == "preprocessed":
            self.df = dataset.get_dataframe()

        else:
            normalization_type = type.split()[0].lower().replace('-', '_')
            dataset.normalize_data(normalization_type)
            
            self.df = dataset.get_dataframe_normalized() 
        
        self.dataset_change_label.config(text=f"Loaded {type} dataset")


    def run_correlation_analysis(self, preview: bool = True):
        try:
            correlation_analysis = self.dataset.remove_correlated_signals(threshold=0.95, preview=preview)

            if preview:
                analysis_key = f"correlation_preview"
                if analysis_key in self.analysis_frames:
                    self.tabs.forget(self.analysis_frames[analysis_key])
                    del self.analysis_frames[analysis_key]

                frame = ttk.Frame(self.tabs)
                self.analysis_frames[analysis_key] = frame
                self.tabs.add(frame, text="Correlation Removal Preview")

                results_for_df = []
                for rep, removed_list in correlation_analysis["representatives_map"].items():
                    results_for_df.append({
                        "Representatives": rep,
                        "To remove": ", ".join(removed_list)
                    })
                
                df_result = pd.DataFrame(results_for_df)
                self.display_dataframe(df_result, frame)
                self.tabs.select(frame)

            else:
                self.df = self.dataset.get_dataframe()
                messagebox.showinfo("Correlation Removal Completed",
                    f"Removed {len(correlation_analysis['to_remove'])} correlated signals."
                )

        except Exception as e:
            messagebox.showerror("Correlation analysis error", str(e))



class AnomalyDetectionGUI:
    def __init__(self, app_state: AppState, dataset: WindFarmDataset):
        self.app_state = app_state
        self.dataset = dataset
        self.df = dataset.get_dataframe()
        self.detector = AnomalyDetector(self.dataset)

        self.selected_parameter = None
        self.analysis_frames = {}

        self.root = tk.Toplevel()
        self.root.title("Wind Farm Anomaly Detection")
        self.root.geometry("1000x600")

        ttk.Label(self.root, text="Anomaly Detection Overview", font=("Segoe UI", 13, "bold")).pack(pady=10)

        detection_frame = ttk.Frame(self.root)
        detection_frame.pack(pady=5)

        tk.Label(detection_frame, text="Method:").pack(side=tk.LEFT, pady=6)
        self.selected_method = tk.StringVar(value="IQR")
        datasets_list = ["IQR", "Isolation Forest", "DBSCAN"]
        ttk.Combobox(detection_frame, textvariable=self.selected_method, values=datasets_list).pack(side=tk.LEFT, pady=6)

        ttk.Label(detection_frame, text=" Contamination (IF):").pack(side=tk.LEFT, pady=6)
        self.contamination_var = tk.StringVar(value="0.01")
        self.entry = ttk.Entry(detection_frame, textvariable=self.contamination_var, width=5).pack(side=tk.LEFT, pady=6)

        ttk.Button(
            detection_frame, 
            text="Detect Anomalies", 
            command=lambda: self.run_anomaly_detection(method=self.selected_method.get())
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            detection_frame, 
            text="Remove Anomalies", 
            command=lambda: self.run_anomaly_removal(method=self.selected_method.get())
        ).pack(side=tk.LEFT, padx=5)


        testing_frame = ttk.Frame(self.root)
        testing_frame.pack(pady=5)

        tk.Label(testing_frame, text="Turbines:").pack(side=tk.LEFT, pady=6)
        turbines_list = dataset.get_turbines_list()
        turbines = sorted(turbines_list)
        self.selected_turbine = tk.StringVar(value=turbines_list[0])
        ttk.Combobox(testing_frame, textvariable=self.selected_turbine, values=turbines).pack(side=tk.LEFT, pady=6)

        ttk.Button(
            testing_frame, 
            text="Plot Variable Timeseries", 
            command=self.on_plot_timeseries
        ).pack(side=tk.LEFT, padx=5)

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


    def run_anomaly_detection(self, method: str = "irq"):
        try:
            if method == "IQR":
                row_mask, cell_mask = self.detector.detect_outliers_iqr()
                analysis_key = "iqr_anomalies"
                tab_name = "IQR Anomalies"

            elif method == "Isolation Forest":
                contamination = float(self.contamination_var.get())
                row_mask, cell_mask = self.detector.detect_isolation_forest(contamination)
                analysis_key = "isolation_forest"
                tab_name = "Isolation Forest Anomalies"

            elif method == "DBSCAN":
                row_mask, cell_mask = self.detector.detect_dbscan()
                analysis_key = "dbscan"
                tab_name = "DBSCAN Anomalies"

            result_df = self.prepare_results_table(row_mask, cell_mask)
            self.cell_mask = cell_mask

            if analysis_key in self.analysis_frames:
                self.tabs.forget(self.analysis_frames[analysis_key])
                del self.analysis_frames[analysis_key]

            frame = ttk.Frame(self.tabs)
            self.analysis_frames[analysis_key] = frame
            self.tabs.add(frame, text=tab_name)

            self.display_dataframe(result_df, frame)
            self.tabs.select(frame)

        except Exception as e:
            messagebox.showerror("Anomaly Detection Error", str(e))

    def prepare_results_table(self, row_mask: pd.Series, cell_mask: pd.DataFrame) -> pd.DataFrame:
        total_rows = len(row_mask)

        summary = []
        for col in cell_mask.columns:
            col_anomalies = cell_mask[col].sum()
            percentage = (col_anomalies / total_rows * 100) if total_rows > 0 else 0

            summary.append({
                "Signal": col,
                "Anomalies number": int(col_anomalies),
                "Anomalies percentage in data [%]": round(percentage, 2)
            })

        result_df = pd.DataFrame(summary)
        return result_df
    

    def run_anomaly_removal(self, method: str):
        try:
            mask_map = {
                "IQR": "iqr_cell",
                "Isolation Forest": "iforest_cell",
                "DBSCAN": "dbscan_cell"
            }

            if method not in mask_map:
                messagebox.showerror("Unknown method", f"No mask defined for: {method}")
                return

            mask_name = mask_map[method]

            removed = self.detector.apply_mask(mask_name)

            messagebox.showinfo(
                "Anomaly removal complete",
                f"{removed} values marked as NaN"
            )

        except ValueError as e:
            messagebox.showerror("Mask error", str(e))


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
        tree.bind("<<TreeviewSelect>>", lambda e: self.on_parameter_select(e, tree))

    def on_parameter_select(self, event, tree):
        selected_item = tree.focus()
        values = tree.item(selected_item, "values")
        if not values:
            return
        self.selected_parameter = values[0]


    def on_plot_timeseries(self):
        if not self.selected_parameter:
            messagebox.showwarning("No parameter selected", "Select signal from Anomalies tab first.")
            return
        turbine = self.selected_turbine.get()
        plot_variable_timeseries(self.df, self.selected_parameter, self.cell_mask, turbine)
