"""
Generate presentation diagrams for Rakuten MLOps project defence.
Run: python3 diagrams/generate_diagrams.py
Output: diagrams/*.png
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np


def draw_box(ax, x, y, w, h, label, sublabel="", color="#4A90D9", fontsize=11):
    """Draw a rounded box with label."""
    box = FancyBboxPatch(
        (x - w/2, y - h/2), w, h,
        boxstyle="round,pad=0.15",
        facecolor=color, edgecolor="white", linewidth=2, alpha=0.95
    )
    ax.add_patch(box)
    ax.text(x, y + (0.08 if sublabel else 0), label,
            ha='center', va='center', fontsize=fontsize,
            fontweight='bold', color='white')
    if sublabel:
        ax.text(x, y - 0.15, sublabel,
                ha='center', va='center', fontsize=8, color='white', alpha=0.9)


def draw_arrow(ax, x1, y1, x2, y2, color="#666666", style='->', lw=2):
    """Draw an arrow between two points."""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw))


# ===========================================================
# DIAGRAM 1: Overall MLOps Architecture
# ===========================================================
fig, ax = plt.subplots(1, 1, figsize=(16, 10))
ax.set_xlim(-0.5, 10.5)
ax.set_ylim(-0.5, 8.5)
ax.axis('off')
ax.set_facecolor('#1a1a2e')
fig.patch.set_facecolor('#1a1a2e')

ax.text(5, 8.1, "Rakuten MLOps - Complete Architecture", ha='center', va='center',
        fontsize=20, fontweight='bold', color='white')

# Data Layer
ax.add_patch(FancyBboxPatch((0.2, 5.8), 3.2, 2.0, boxstyle="round,pad=0.2",
             facecolor="#16213e", edgecolor="#4A90D9", linewidth=2, alpha=0.5))
ax.text(1.8, 7.5, "DATA LAYER", ha='center', fontsize=10, color='#4A90D9', fontweight='bold')
draw_box(ax, 1.0, 6.7, 1.2, 0.5, "Raw Data", "CSV + Images", "#2d6a4f")
draw_box(ax, 2.6, 6.7, 1.3, 0.5, "DVC", "Data Versioning", "#2d6a4f")

# ML Pipeline
ax.add_patch(FancyBboxPatch((0.2, 3.5), 9.6, 2.0, boxstyle="round,pad=0.2",
             facecolor="#16213e", edgecolor="#E67E22", linewidth=2, alpha=0.5))
ax.text(5, 5.2, "ML PIPELINE (Microservices)", ha='center', fontsize=10, color='#E67E22', fontweight='bold')
draw_box(ax, 1.5, 4.4, 1.8, 0.6, "Data Service", "Port 5001", "#E67E22")
draw_box(ax, 4.0, 4.4, 2.0, 0.6, "Training Service", "Port 5002", "#E67E22")
draw_box(ax, 6.8, 4.4, 2.2, 0.6, "Prediction Service", "Port 5003", "#E67E22")
draw_box(ax, 9.0, 4.4, 1.4, 0.6, "LSTM\nModel", "", "#c0392b")

draw_arrow(ax, 2.4, 4.4, 3.0, 4.4, "#E67E22")
draw_arrow(ax, 5.0, 4.4, 5.7, 4.4, "#E67E22")
draw_arrow(ax, 7.9, 4.4, 8.3, 4.4, "#E67E22")

# API Gateway - connects to ALL 3 services
draw_box(ax, 5, 2.5, 3.0, 0.7, "API Gateway", "Port 8080", "#8E44AD")
draw_arrow(ax, 3.8, 2.9, 1.8, 3.5, "#8E44AD")   # Gateway -> Data Service
draw_arrow(ax, 5.0, 2.9, 5.0, 3.5, "#8E44AD")    # Gateway -> Training Service (was wrong before: pointed to Training at y=3.5)
draw_arrow(ax, 6.2, 2.9, 6.8, 3.5, "#8E44AD")    # Gateway -> Prediction Service

# Experiment Tracking - ONLY Training Service connects to MLflow
ax.add_patch(FancyBboxPatch((3.8, 5.8), 3.0, 2.0, boxstyle="round,pad=0.2",
             facecolor="#16213e", edgecolor="#27AE60", linewidth=2, alpha=0.5))
ax.text(5.3, 7.5, "EXPERIMENT TRACKING", ha='center', fontsize=10, color='#27AE60', fontweight='bold')
draw_box(ax, 5.3, 6.7, 1.8, 0.5, "MLflow", "Port 5000", "#27AE60")

# Only Training Service -> MLflow (confirmed in docker-compose: only training_service has MLFLOW_TRACKING_URI)
draw_arrow(ax, 4.0, 5.0, 5.0, 6.4, "#27AE60", lw=1.5)
ax.text(4.0, 5.8, "logs metrics", fontsize=8, color='#27AE60', style='italic')

# Monitoring - Prometheus scrapes FROM all 4 services (arrows go FROM services TO Prometheus)
ax.add_patch(FancyBboxPatch((7.2, 5.8), 2.8, 2.0, boxstyle="round,pad=0.2",
             facecolor="#16213e", edgecolor="#E74C3C", linewidth=2, alpha=0.5))
ax.text(8.6, 7.5, "MONITORING", ha='center', fontsize=10, color='#E74C3C', fontweight='bold')
draw_box(ax, 8.0, 6.7, 1.4, 0.5, "Prometheus", "Port 9090", "#E74C3C")
draw_box(ax, 9.4, 6.7, 1.0, 0.5, "Grafana", "Port 3000", "#E74C3C")

# Prometheus scrapes all 4 services (dashed style to show "pull")
draw_arrow(ax, 7.5, 6.4, 1.5, 5.0, "#E74C3C", lw=1.5)   # Prometheus <- Data Service
draw_arrow(ax, 7.5, 6.4, 4.0, 5.0, "#E74C3C", lw=1.5)   # Prometheus <- Training Service
draw_arrow(ax, 7.5, 6.4, 6.8, 5.0, "#E74C3C", lw=1.5)   # Prometheus <- Prediction Service
ax.text(7.0, 5.8, "scrapes /metrics", fontsize=7, color='#E74C3C', style='italic')

# Prometheus -> Grafana
draw_arrow(ax, 8.7, 6.7, 8.9, 6.7, "#F39C12", lw=2)

# CI/CD
draw_box(ax, 9.0, 2.5, 1.6, 0.7, "GitHub\nActions", "CI/CD", "#3498DB")

# User
draw_box(ax, 5, 1.0, 2.0, 0.6, "User / Client", "HTTP Requests", "#95A5A6")
draw_arrow(ax, 5, 1.3, 5, 2.1, "#95A5A6")

# Docker
ax.text(5, 0.2, "All services run in Docker Compose on mlops_network",
        ha='center', fontsize=10, color='#95A5A6', style='italic')

plt.tight_layout()
plt.savefig('diagrams/1_complete_architecture.png', dpi=150, bbox_inches='tight',
            facecolor='#1a1a2e', edgecolor='none')
plt.close()
print("1. Complete Architecture - DONE")


# ===========================================================
# DIAGRAM 2: Microservices Communication
# ===========================================================
fig, ax = plt.subplots(1, 1, figsize=(14, 9))
ax.set_xlim(-0.5, 10.5)
ax.set_ylim(-0.5, 8)
ax.axis('off')
ax.set_facecolor('#1a1a2e')
fig.patch.set_facecolor('#1a1a2e')

ax.text(5, 7.6, "Microservices Architecture", ha='center', va='center',
        fontsize=20, fontweight='bold', color='white')

# Docker network boundary
ax.add_patch(FancyBboxPatch((0.3, 0.8), 9.4, 6.2, boxstyle="round,pad=0.3",
             facecolor="none", edgecolor="#4A90D9", linewidth=2, linestyle='dashed', alpha=0.6))
ax.text(5, 6.7, "Docker Compose - mlops_network", ha='center', fontsize=11,
        color='#4A90D9', fontweight='bold')

# Services
draw_box(ax, 5.0, 5.8, 2.5, 0.7, "API Gateway", "Port 8080 - Entry Point", "#8E44AD", fontsize=13)

draw_box(ax, 1.8, 4.0, 2.2, 0.7, "Data Service", "Port 5001", "#E67E22", fontsize=12)
draw_box(ax, 5.0, 4.0, 2.4, 0.7, "Training Service", "Port 5002", "#E67E22", fontsize=12)
draw_box(ax, 8.2, 4.0, 2.4, 0.7, "Prediction Service", "Port 5003", "#E67E22", fontsize=12)

draw_box(ax, 1.8, 2.2, 1.8, 0.7, "MLflow", "Port 5000", "#27AE60", fontsize=12)
draw_box(ax, 5.0, 2.2, 1.8, 0.7, "Prometheus", "Port 9090", "#E74C3C", fontsize=12)
draw_box(ax, 8.2, 2.2, 1.8, 0.7, "Grafana", "Port 3000", "#E74C3C", fontsize=12)

# Arrows from Gateway to all 3 services
draw_arrow(ax, 4.0, 5.4, 2.2, 4.4, "#8E44AD")
draw_arrow(ax, 5.0, 5.4, 5.0, 4.4, "#8E44AD")
draw_arrow(ax, 6.0, 5.4, 7.8, 4.4, "#8E44AD")

# ONLY Training Service -> MLflow (confirmed: only training_service has MLFLOW_TRACKING_URI in env)
draw_arrow(ax, 5.0, 3.6, 2.2, 2.6, "#27AE60", lw=1.5)
ax.text(3.0, 3.3, "logs to MLflow", fontsize=8, color='#27AE60', style='italic')

# Prometheus scrapes ALL 4 services (Gateway + Data + Training + Prediction)
draw_arrow(ax, 5.0, 5.4, 5.3, 2.6, "#E74C3C", lw=1.0)   # Prometheus <- API Gateway (via down)
draw_arrow(ax, 1.8, 3.6, 4.5, 2.6, "#E74C3C", lw=1.0)    # Prometheus <- Data Service
draw_arrow(ax, 5.2, 3.6, 5.1, 2.6, "#E74C3C", lw=1.0)    # Prometheus <- Training Service
draw_arrow(ax, 8.2, 3.6, 5.5, 2.6, "#E74C3C", lw=1.0)    # Prometheus <- Prediction Service

# Prometheus -> Grafana
draw_arrow(ax, 5.9, 2.2, 7.3, 2.2, "#E74C3C", lw=2)

# Labels on arrows
ax.text(3.0, 5.1, "REST API", fontsize=8, color='#cccccc', rotation=30)
ax.text(5.2, 4.8, "REST API", fontsize=8, color='#cccccc')
ax.text(7.0, 5.1, "REST API", fontsize=8, color='#cccccc', rotation=-30)
ax.text(6.8, 3.0, "/metrics", fontsize=8, color='#E74C3C', style='italic')
ax.text(6.4, 2.0, "PromQL query", fontsize=8, color='#E74C3C', style='italic')

# User
draw_box(ax, 5.0, 7.2, 1.5, 0.4, "User", "", "#95A5A6", fontsize=11)
draw_arrow(ax, 5.0, 7.0, 5.0, 6.2, "#95A5A6")

# Port labels at bottom
ax.text(5, 1.2, "Exposed Ports: 8080 (API) | 5000 (MLflow) | 9090 (Prometheus) | 3000 (Grafana)",
        ha='center', fontsize=10, color='#95A5A6', style='italic')

plt.tight_layout()
plt.savefig('diagrams/2_microservices_architecture.png', dpi=150, bbox_inches='tight',
            facecolor='#1a1a2e', edgecolor='none')
plt.close()
print("2. Microservices Architecture - DONE")


# ===========================================================
# DIAGRAM 3: ML Pipeline Flow
# DVC covers: data_import -> preprocess -> train (3 stages from dvc.yaml)
# MLflow covers: train -> evaluation -> registry -> prediction
# ===========================================================
fig, ax = plt.subplots(1, 1, figsize=(16, 6))
ax.set_xlim(-0.5, 15)
ax.set_ylim(-0.5, 4.5)
ax.axis('off')
ax.set_facecolor('#1a1a2e')
fig.patch.set_facecolor('#1a1a2e')

ax.text(7.5, 4.1, "ML Pipeline - From Data to Prediction", ha='center', va='center',
        fontsize=20, fontweight='bold', color='white')

# Steps
colors = ["#2d6a4f", "#2d6a4f", "#E67E22", "#E67E22", "#c0392b", "#8E44AD", "#3498DB"]
labels = ["Raw Data\n(CSV+Images)", "Preprocessing\n(Text+Image)", "Feature\nEngineering", "LSTM\nTraining",
          "Model\nEvaluation", "Model\nRegistry", "Prediction\nAPI"]
sublabels = ["5.6 GB", "Tokenization\nCleaning", "Sequences\nPadding", "10 Epochs\n27 Classes",
             "Loss, Accuracy\nMLflow Logging", "MLflow\nVersioning", "REST API\nReal-time"]

positions = [1, 3, 5, 7, 9, 11, 13]

for i, (pos, label, sub, color) in enumerate(zip(positions, labels, sublabels, colors)):
    draw_box(ax, pos, 2.5, 1.6, 1.2, label, sub, color, fontsize=10)
    if i < len(positions) - 1:
        draw_arrow(ax, pos + 0.85, 2.5, positions[i+1] - 0.85, 2.5, "white", lw=2)

# DVC covers stages: data_import (Raw Data) -> preprocess (Preprocessing) -> train (Training)
# That is positions 1, 3, 5, 7 = first 4 boxes
ax.text(4, 0.8, "DVC Pipeline (Reproducible)", ha='center', fontsize=10,
        color='#4A90D9', fontweight='bold')
ax.annotate('', xy=(0.3, 1.0), xytext=(7.8, 1.0),
            arrowprops=dict(arrowstyle='<->', color='#4A90D9', lw=2))

# MLflow covers: Training -> Evaluation -> Registry -> Prediction
ax.text(11, 0.8, "MLflow Tracking (Experiments)", ha='center', fontsize=10,
        color='#27AE60', fontweight='bold')
ax.annotate('', xy=(6.3, 1.0), xytext=(13.7, 1.0),
            arrowprops=dict(arrowstyle='<->', color='#27AE60', lw=2))

plt.tight_layout()
plt.savefig('diagrams/3_ml_pipeline.png', dpi=150, bbox_inches='tight',
            facecolor='#1a1a2e', edgecolor='none')
plt.close()
print("3. ML Pipeline - DONE")


# ===========================================================
# DIAGRAM 4: Monitoring Flow (was correct, no changes needed)
# ===========================================================
fig, ax = plt.subplots(1, 1, figsize=(14, 8))
ax.set_xlim(-0.5, 10.5)
ax.set_ylim(-0.5, 7)
ax.axis('off')
ax.set_facecolor('#1a1a2e')
fig.patch.set_facecolor('#1a1a2e')

ax.text(5, 6.6, "Monitoring Architecture (Prometheus + Grafana)", ha='center', va='center',
        fontsize=20, fontweight='bold', color='white')

# Services exposing metrics
services = [
    ("API Gateway\n:8080", 1.5, 5.2),
    ("Data Service\n:5001", 4.0, 5.2),
    ("Training Service\n:5002", 6.5, 5.2),
    ("Prediction Service\n:5003", 9.0, 5.2),
]
for label, x, y in services:
    draw_box(ax, x, y, 2.0, 0.7, label, "/metrics", "#E67E22", fontsize=10)

# Prometheus
draw_box(ax, 5.0, 3.2, 3.0, 1.0, "Prometheus", "Scrapes every 15s\nPort 9090", "#E74C3C", fontsize=13)

# Arrows from services to prometheus
for label, x, y in services:
    draw_arrow(ax, x, y - 0.4, 5.0, 3.8, "#E74C3C", lw=1.5)

# Grafana
draw_box(ax, 5.0, 1.0, 3.0, 1.0, "Grafana Dashboard", "Visualization\nPort 3000", "#F39C12", fontsize=13)

draw_arrow(ax, 5.0, 2.7, 5.0, 1.6, "#F39C12", lw=3)
ax.text(5.6, 2.1, "PromQL\nQueries", fontsize=9, color='#F39C12', style='italic')

# Metrics types on the right
ax.add_patch(FancyBboxPatch((7.8, 0.3), 2.5, 2.6, boxstyle="round,pad=0.2",
             facecolor="#16213e", edgecolor="#95A5A6", linewidth=1.5, alpha=0.7))
ax.text(9.05, 2.6, "Collected Metrics", ha='center', fontsize=10,
        color='white', fontweight='bold')
metrics_list = [
    "Request Count",
    "Request Latency",
    "Service Health (up/down)",
    "Prediction Count",
    "Prediction Confidence",
    "Inference Latency",
    "Training Status",
    "Training Loss/Accuracy",
]
for i, m in enumerate(metrics_list):
    ax.text(8.2, 2.3 - i * 0.25, f"• {m}", fontsize=8, color='#cccccc')

plt.tight_layout()
plt.savefig('diagrams/4_monitoring_architecture.png', dpi=150, bbox_inches='tight',
            facecolor='#1a1a2e', edgecolor='none')
plt.close()
print("4. Monitoring Architecture - DONE")


# ===========================================================
# DIAGRAM 5: Technology Stack
# Fixed: Added Grafana to Infrastructure layer
# ===========================================================
fig, ax = plt.subplots(1, 1, figsize=(14, 8))
ax.set_xlim(-0.5, 10.5)
ax.set_ylim(-0.5, 7.5)
ax.axis('off')
ax.set_facecolor('#1a1a2e')
fig.patch.set_facecolor('#1a1a2e')

ax.text(5, 7.1, "Technology Stack", ha='center', va='center',
        fontsize=20, fontweight='bold', color='white')

# Layers
layers = [
    ("Presentation / API", 6.0, "#8E44AD",
     [("Flask REST API", 1.5), ("API Gateway", 4.0), ("Grafana UI", 6.5), ("MLflow UI", 9.0)]),
    ("Application / ML", 4.5, "#E67E22",
     [("TensorFlow/Keras", 1.5), ("LSTM Model", 4.0), ("NLTK", 6.5), ("scikit-learn", 9.0)]),
    ("Data / Storage", 3.0, "#2d6a4f",
     [("pandas/numpy", 1.5), ("DVC", 4.0), ("CSV/Images", 6.5), ("SQLite", 9.0)]),
    ("Infrastructure", 1.5, "#E74C3C",
     [("Docker Compose", 1.5), ("Prometheus", 4.0), ("GitHub Actions", 6.5), ("Python 3.11", 9.0)]),
]

for layer_label, y, color, items in layers:
    ax.add_patch(FancyBboxPatch((0.2, y - 0.5), 9.9, 1.2, boxstyle="round,pad=0.15",
                 facecolor="#16213e", edgecolor=color, linewidth=2, alpha=0.5))
    ax.text(5, y + 0.45, layer_label, ha='center', fontsize=10, color=color, fontweight='bold')
    for label, x in items:
        draw_box(ax, x, y, 1.8, 0.5, label, "", color, fontsize=9)

plt.tight_layout()
plt.savefig('diagrams/5_technology_stack.png', dpi=150, bbox_inches='tight',
            facecolor='#1a1a2e', edgecolor='none')
plt.close()
print("5. Technology Stack - DONE")


print("\n=== All 5 diagrams saved in diagrams/ folder ===")
print("Files:")
print("  1. diagrams/1_complete_architecture.png")
print("  2. diagrams/2_microservices_architecture.png")
print("  3. diagrams/3_ml_pipeline.png")
print("  4. diagrams/4_monitoring_architecture.png")
print("  5. diagrams/5_technology_stack.png")
