import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve


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


def plot_variable_timeline(df: pd.DataFrame, signal: str, turbine_id: str = "all", expected_interval: str = "10min"):
    plot_scope = get_plot_scope(turbine_id)

    if turbine_id.lower() != "all":
        selected_turbines = [int(turbine_id)]
    else:
        selected_turbines = df["turbine_id"].unique()

    fig_height = max(4, len(selected_turbines) * 0.8)
    fig, ax = plt.subplots(figsize=(10, fig_height), num=f"Variable Availability Plot for {signal} of {plot_scope}") 
    y_gap = 2
    
    label_added = False
    for i, id in enumerate(selected_turbines):
        df_selected_turbine = df[df["turbine_id"] == id]

        start, end = df_selected_turbine.index.min(), df_selected_turbine.index.max()
        expected_timestamps = pd.date_range(start=start, end=end, freq=expected_interval)

        full_signal_series = df_selected_turbine[signal].reindex(expected_timestamps)
        available_mask = full_signal_series.notna() 
    
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
    ax.set_title(f"'{signal}' Availability Over Time for {plot_scope}")

    ax.legend(loc='best', bbox_to_anchor=(1, 1))

    plt.tight_layout()
    plt.show()


def plot_correlation_matrix(correlation_matrix: pd.DataFrame, plot_labels=True):
    fig, ax = plt.subplots(figsize=(9, 7))
    cax = ax.matshow(correlation_matrix)
    fig.colorbar(cax)

    if plot_labels:
        short_labels = [col[:14] for col in correlation_matrix.columns]

        ax.set_xticks(range(correlation_matrix.shape[1]))
        ax.set_xticklabels(short_labels, fontsize=7, rotation=85)

        ax.set_yticks(range(correlation_matrix.shape[0]))
        ax.set_yticklabels(short_labels, fontsize=7)

    plt.title('Correlation Matrix')
    plt.tight_layout()
    plt.show()


def plot_variable_timeseries(df: pd.DataFrame, parameter: str, mask: pd.DataFrame, turbine_id: str = "all"):
    if turbine_id.lower() != "all":
        turbine_filter = df["turbine_id"] == int(turbine_id)
        
        df = df[turbine_filter]
        mask = mask[turbine_filter]

    plot_scope = get_plot_scope(turbine_id)
    title = f"Time Series of {parameter} for {plot_scope}"

    values = df[parameter]
    timestamps = df.index

    if parameter in mask.columns:
        anomaly_points = mask[parameter].loc[df.index]
    else:
        anomaly_points = pd.Series(False, index=df.index)

    anomalies_x = timestamps[anomaly_points]
    anomalies_y = values[anomaly_points]

    fig, ax = plt.subplots(figsize=(12, 5), num=f"Time Series of {parameter} ({plot_scope})")

    ax.plot(timestamps, values, label=parameter, color="tab:blue")

    ax.scatter(
        anomalies_x,
        anomalies_y,
        color="red",
        s=25,
        label="Anomalies",
        zorder=5
    )

    ax.set_title(title)
    ax.set_xlabel("Time")
    ax.set_ylabel(parameter)
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.legend(loc="best")

    plt.tight_layout()
    plt.show()


def plot_anomaly_score_timeseries(df: pd.DataFrame, scores: pd.Series, row_mask: pd.Series, turbine_id: str, method: str):
    df = df[df["turbine_id"] == int(turbine_id)]
    
    scores = scores.loc[df.index]
    row_mask = row_mask.loc[df.index]

    normal = df.loc[~row_mask]
    anomalies = df.loc[row_mask]

    plot_scope = get_plot_scope(turbine_id)
    title = f"Anomaly scores of {method} for {plot_scope}"

    plt.figure(figsize=(10, 5), num=title)
    plt.scatter(normal.index, scores.loc[normal.index], label="Normal", alpha=0.6)
    plt.scatter(anomalies.index, scores.loc[anomalies.index], label="Anomaly", color=(1.0, 0.43, 0.0, 0.8), alpha=0.8)

    plt.xlabel("Time")
    plt.ylabel("Anomaly score")
    plt.title(title)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.25)
    plt.tight_layout()
    plt.show()


def plot_auc_roc_curve(fpr, tpr, auc: float, method: str):
    title = f"AUC ROC Curve for {method}"

    plt.figure(figsize=(6, 5), num=title)
    plt.plot(fpr, tpr, label=f"AUC = {auc:.3f}")
    plt.plot([0,1], [0,1], linestyle="--", color="gray")

    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_auc_pr_curve(recall, precision, auc: float, method: str):
    title = f"AUC PR Curve for {method}"

    plt.figure(figsize=(6, 5), num=title)
    plt.plot(recall, precision, label=f"AUC-PR = {auc:.3f}")

    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

