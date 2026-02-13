import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def get_plot_scope(turbine_id: str) -> str:
    return f"{'Turbine ' + turbine_id if turbine_id.isdigit() else 'all Turbines'}"


def plot_data_uptime(df: pd.DataFrame, turbine_id: str = "all", expected_interval: str = "10min"):
    plot_scope = get_plot_scope(turbine_id)

    if turbine_id.lower() != "all":
        selected_turbines = [int(turbine_id)]
    else:
        selected_turbines = df["turbine_id"].unique()

    fig_height = max(4, len(selected_turbines) * 0.8)
    fig, ax = plt.subplots(figsize=(10, fig_height), num=f"Data Uptime Plot for {plot_scope}") 
    y_gap = 2
    
    label_added = False
    for i, id in enumerate(selected_turbines):
        df_selected_turbine = df[df["turbine_id"] == id]

        start, end = df_selected_turbine.index.min(), df_selected_turbine.index.max()
        expected_timestamps = pd.date_range(start=start, end=end, freq=expected_interval)

        full_timestamps_series = df_selected_turbine.iloc[:, 0].reindex(expected_timestamps)
        available_mask = full_timestamps_series.notna() 
    
        available_indices = np.where(available_mask == 1)[0]
        missing_indices = np.where(available_mask == 0)[0]

        y_offset = i * y_gap

        ax.scatter(expected_timestamps[available_indices], 
                [y_offset] * len(available_indices), 
                c="tab:blue",
                edgecolor="tab:blue", 
                s=160,
                linewidth=1,
                label="Available" if not label_added else None) 
        
        ax.scatter(expected_timestamps[missing_indices], 
                [y_offset] * len(missing_indices), 
                c="red",
                marker='|', # s
                s=400,
                linewidth=2,
                label="Unavailable" if not label_added else None)
        
        label_added = True

    ax.set_yticks([i * y_gap for i in range(len(selected_turbines))])
    ax.set_yticklabels([f"T{t}" for t in selected_turbines])
    ax.set_xlabel("Time")
    ax.set_title(f"Data Availability Over Time for {plot_scope}")

    ax.legend(loc='best', bbox_to_anchor=(1, 1))

    plt.tight_layout()
    plt.show()


def plot_variable_boxplot(df: pd.DataFrame, parameter: str, turbine_id: str = "all"):
    if parameter not in df.columns:
        raise ValueError(f"Column '{parameter}' not found in dataset.")

    if turbine_id.lower() != "all":
        df = df[df["turbine_id"] == int(turbine_id)]

    plot_scope = get_plot_scope(turbine_id)    
    title = f"Distribution of {parameter} for {plot_scope}"

    fig, ax = plt.subplots(figsize=(10, 5), num=f"Distribution Boxplot of {parameter} for {plot_scope}")
    df.boxplot(column=parameter, by="turbine_id", ax=ax, grid=False)
    ax.set_title(title)
    ax.set_xlabel("Turbine ID")
    ax.set_ylabel(parameter)
    
    plt.suptitle("")
    plt.tight_layout()
    plt.show()


def plot_variable_histogram(df: pd.DataFrame, parameter: str, turbine_id: str = "all", bins: int = 30):
    if parameter not in df.columns:
        raise ValueError(f"Column '{parameter}' not found in dataset.")

    if turbine_id.lower() != "all":
        df = df[df["turbine_id"] == int(turbine_id)]

    plot_scope = get_plot_scope(turbine_id)    
    title = f"Distribution of {parameter} for {plot_scope}"

    data = df[parameter].dropna()

    fig, ax = plt.subplots(figsize=(10, 5), num=f"Histogram of {parameter} for {plot_scope}")
    n, bins_edges, patches = ax.hist(data, bins='auto', color="tab:blue", edgecolor="black", alpha=0.7)

    data_mean = np.mean(data)
    data_median = np.median(data)
    ax.axvline(data_mean, color="red", linestyle="--", linewidth=1.5, label=f"Mean = {data_mean:.2f}")
    ax.axvline(data_median, color="green", linestyle="--", linewidth=1.5, label=f"Median = {data_median:.2f}")

    ax.set_title(title)
    ax.set_xlabel(parameter)
    ax.set_ylabel("Frequency")
    ax.legend(loc="best")
    ax.grid(True, linestyle="--", alpha=0.3)

    plt.tight_layout()
    plt.show()
