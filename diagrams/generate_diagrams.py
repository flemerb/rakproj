"""
Generate presentation diagrams for Rakuten MLOps project defence.
Run: python3 diagrams/generate_diagrams.py
Output: diagrams/*.png
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


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
# DIAGRAM 1: Overall MLOps Architecture (13 containers)
# ===========================================================
fig, ax = plt.subplots(1, 1, figsize=(18, 12))
ax.set_xlim(-0.5, 12.5)
ax.set_ylim(-0.5, 10.5)
ax.axis('off')
ax.set_facecolor('#1a1a2e')
fig.patch.set_facecolor('#1a1a2e')

ax.text(6, 10.1, "Rakuten MLOps - Complete Architecture (13 Containers)",
        ha='center', va='center', fontsize=20, fontweight='bold', color='white')

# User / UI Layer
ax.add_patch(FancyBboxPatch((1.5, 8.5), 9.0, 1.2, boxstyle="round,pad=0.2",
             facecolor="#16213e", edgecolor="#95A5A6", linewidth=2, alpha=0.5))
ax.text(6, 9.5, "USER LAYER", ha='center', fontsize=10, color='#95A5A6', fontweight='bold')
draw_box(ax, 3.5, 8.9, 2.0, 0.6, "Web UI", "Port 8082 (Nginx)", "#34495E")
draw_box(ax, 6, 8.9, 2.0, 0.6, "User / Client", "HTTP Requests", "#95A5A6")
draw_box(ax, 8.5, 8.9, 2.0, 0.6, "Auth Service", "Port 5004", "#1ABC9C")

# API Gateway + Auth
draw_box(ax, 6, 7.5, 3.0, 0.7, "API Gateway", "Port 8080 - Entry Point", "#8E44AD")
draw_arrow(ax, 6, 8.6, 6, 7.9, "#95A5A6")  # User -> Gateway
draw_arrow(ax, 3.5, 8.6, 5.0, 7.9, "#34495E")  # UI -> Gateway
draw_arrow(ax, 7.2, 7.5, 8.5, 8.6, "#1ABC9C", lw=1.5)  # Gateway -> Auth Service

# ML Pipeline (Microservices)
ax.add_patch(FancyBboxPatch((0.2, 4.8), 11.6, 2.0, boxstyle="round,pad=0.2",
             facecolor="#16213e", edgecolor="#E67E22", linewidth=2, alpha=0.5))
ax.text(6, 6.5, "ML PIPELINE (Microservices)", ha='center', fontsize=10,
        color='#E67E22', fontweight='bold')
draw_box(ax, 2.0, 5.7, 2.0, 0.6, "Data Service", "Port 5001", "#E67E22")
draw_box(ax, 5.0, 5.7, 2.2, 0.6, "Training Service", "Port 5002", "#E67E22")
draw_box(ax, 8.2, 5.7, 2.4, 0.6, "Prediction Service", "Port 5003", "#E67E22")
draw_box(ax, 11.0, 5.7, 1.4, 0.6, "LSTM\nModel", "", "#c0392b")

draw_arrow(ax, 3.0, 5.7, 3.9, 5.7, "#E67E22")
draw_arrow(ax, 6.1, 5.7, 7.0, 5.7, "#E67E22")
draw_arrow(ax, 9.4, 5.7, 10.3, 5.7, "#E67E22")

# Gateway -> Services
draw_arrow(ax, 4.8, 7.1, 2.5, 6.0, "#8E44AD")
draw_arrow(ax, 6.0, 7.1, 5.0, 6.0, "#8E44AD")
draw_arrow(ax, 7.2, 7.1, 8.0, 6.0, "#8E44AD")

# Data Layer
ax.add_patch(FancyBboxPatch((0.2, 3.0), 3.5, 1.5, boxstyle="round,pad=0.2",
             facecolor="#16213e", edgecolor="#4A90D9", linewidth=2, alpha=0.5))
ax.text(2.0, 4.2, "DATA LAYER", ha='center', fontsize=10, color='#4A90D9', fontweight='bold')
draw_box(ax, 1.2, 3.6, 1.2, 0.5, "Raw Data", "CSV + Images", "#2d6a4f")
draw_box(ax, 2.8, 3.6, 1.3, 0.5, "DVC", "Versioning", "#2d6a4f")

# Experiment Tracking
ax.add_patch(FancyBboxPatch((4.0, 3.0), 2.5, 1.5, boxstyle="round,pad=0.2",
             facecolor="#16213e", edgecolor="#27AE60", linewidth=2, alpha=0.5))
ax.text(5.25, 4.2, "EXPERIMENT TRACKING", ha='center', fontsize=9,
        color='#27AE60', fontweight='bold')
draw_box(ax, 5.25, 3.6, 1.8, 0.5, "MLflow", "Port 5000", "#27AE60")

# Training Service -> MLflow
draw_arrow(ax, 5.0, 5.4, 5.25, 3.9, "#27AE60", lw=1.5)
ax.text(4.4, 4.7, "logs metrics", fontsize=8, color='#27AE60', style='italic')

# Orchestration (Airflow)
ax.add_patch(FancyBboxPatch((6.8, 3.0), 3.0, 1.5, boxstyle="round,pad=0.2",
             facecolor="#16213e", edgecolor="#F39C12", linewidth=2, alpha=0.5))
ax.text(8.3, 4.2, "ORCHESTRATION", ha='center', fontsize=10,
        color='#F39C12', fontweight='bold')
draw_box(ax, 7.6, 3.6, 1.4, 0.5, "Airflow\nWebserver", "Port 8081", "#F39C12")
draw_box(ax, 9.2, 3.6, 1.2, 0.5, "Scheduler", "", "#F39C12")

# Airflow -> ML services (triggers pipeline)
draw_arrow(ax, 7.6, 3.9, 5.0, 5.4, "#F39C12", lw=1.0)
ax.text(6.8, 4.8, "triggers", fontsize=7, color='#F39C12', style='italic')

# Monitoring
ax.add_patch(FancyBboxPatch((0.2, 0.8), 11.6, 1.8, boxstyle="round,pad=0.2",
             facecolor="#16213e", edgecolor="#E74C3C", linewidth=2, alpha=0.5))
ax.text(6, 2.3, "MONITORING", ha='center', fontsize=10, color='#E74C3C', fontweight='bold')
draw_box(ax, 4.0, 1.5, 2.0, 0.6, "Prometheus", "Port 9090", "#E74C3C")
draw_box(ax, 7.0, 1.5, 2.0, 0.6, "Grafana", "Port 3000", "#E74C3C")
draw_box(ax, 10.0, 1.5, 2.0, 0.6, "GitHub\nActions", "CI/CD", "#3498DB")
draw_arrow(ax, 5.0, 1.5, 6.0, 1.5, "#F39C12", lw=2)  # Prometheus -> Grafana

# Prometheus scrapes services
draw_arrow(ax, 3.5, 1.8, 2.0, 5.4, "#E74C3C", lw=1.0)
draw_arrow(ax, 4.0, 1.8, 5.0, 5.4, "#E74C3C", lw=1.0)
draw_arrow(ax, 4.5, 1.8, 8.0, 5.4, "#E74C3C", lw=1.0)
ax.text(1.5, 2.5, "scrapes /metrics", fontsize=7, color='#E74C3C', style='italic')

# Docker label
ax.text(6, 0.2, "All 13 containers run in Docker Compose on mlops_network (bridge)",
        ha='center', fontsize=10, color='#95A5A6', style='italic')

plt.tight_layout()
plt.savefig('diagrams/1_complete_architecture.png', dpi=150, bbox_inches='tight',
            facecolor='#1a1a2e', edgecolor='none')
plt.close()
print("1. Complete Architecture - DONE")


# ===========================================================
# DIAGRAM 2: Microservices Communication (all 13 containers)
# ===========================================================
fig, ax = plt.subplots(1, 1, figsize=(16, 11))
ax.set_xlim(-0.5, 12.5)
ax.set_ylim(-0.5, 9.5)
ax.axis('off')
ax.set_facecolor('#1a1a2e')
fig.patch.set_facecolor('#1a1a2e')

ax.text(6, 9.1, "Microservices Architecture (13 Containers)", ha='center', va='center',
        fontsize=20, fontweight='bold', color='white')

# Docker network boundary
ax.add_patch(FancyBboxPatch((0.3, 0.5), 11.5, 8.0, boxstyle="round,pad=0.3",
             facecolor="none", edgecolor="#4A90D9", linewidth=2, linestyle='dashed', alpha=0.6))
ax.text(6, 8.2, "Docker Compose - mlops_network", ha='center', fontsize=11,
        color='#4A90D9', fontweight='bold')

# User + UI
draw_box(ax, 4.0, 7.6, 1.8, 0.5, "Web UI", "Port 8082", "#34495E", fontsize=11)
draw_box(ax, 6.5, 7.6, 1.5, 0.5, "User", "", "#95A5A6", fontsize=11)

# API Gateway
draw_box(ax, 5.5, 6.5, 2.8, 0.7, "API Gateway", "Port 8080 - Entry Point", "#8E44AD", fontsize=13)
draw_arrow(ax, 4.0, 7.3, 5.0, 6.9, "#34495E")
draw_arrow(ax, 6.5, 7.3, 6.0, 6.9, "#95A5A6")

# Auth Service
draw_box(ax, 9.5, 6.5, 2.0, 0.7, "Auth Service", "Port 5004", "#1ABC9C", fontsize=12)
draw_arrow(ax, 6.9, 6.5, 8.5, 6.5, "#1ABC9C", lw=1.5)
ax.text(7.5, 6.8, "verify token", fontsize=8, color='#1ABC9C', style='italic')

# ML Services
draw_box(ax, 2.0, 4.8, 2.2, 0.7, "Data Service", "Port 5001", "#E67E22", fontsize=12)
draw_box(ax, 5.5, 4.8, 2.4, 0.7, "Training Service", "Port 5002", "#E67E22", fontsize=12)
draw_box(ax, 9.5, 4.8, 2.4, 0.7, "Prediction Service", "Port 5003", "#E67E22", fontsize=12)

# Gateway -> Services
draw_arrow(ax, 4.5, 6.1, 2.5, 5.2, "#8E44AD")
draw_arrow(ax, 5.5, 6.1, 5.5, 5.2, "#8E44AD")
draw_arrow(ax, 6.5, 6.1, 9.0, 5.2, "#8E44AD")
ax.text(3.0, 5.8, "REST API", fontsize=8, color='#cccccc', rotation=25)
ax.text(5.7, 5.7, "REST API", fontsize=8, color='#cccccc')
ax.text(8.0, 5.8, "REST API", fontsize=8, color='#cccccc', rotation=-20)

# Bottom row: MLflow, Airflow, Prometheus, Grafana
draw_box(ax, 1.5, 3.0, 1.8, 0.7, "MLflow", "Port 5000", "#27AE60", fontsize=12)
draw_box(ax, 4.0, 3.0, 1.8, 0.7, "Airflow", "Port 8081", "#F39C12", fontsize=12)
draw_box(ax, 6.5, 3.0, 1.8, 0.7, "Prometheus", "Port 9090", "#E74C3C", fontsize=12)
draw_box(ax, 9.0, 3.0, 1.8, 0.7, "Grafana", "Port 3000", "#E74C3C", fontsize=12)

# Airflow infra
draw_box(ax, 4.0, 1.5, 1.8, 0.5, "Airflow DB", "PostgreSQL", "#F39C12", fontsize=9)
draw_box(ax, 6.5, 1.5, 1.8, 0.5, "Scheduler", "", "#F39C12", fontsize=9)
draw_arrow(ax, 4.0, 2.6, 4.0, 1.8, "#F39C12", lw=1.0)
draw_arrow(ax, 4.9, 3.0, 5.6, 1.8, "#F39C12", lw=1.0)

# Training -> MLflow
draw_arrow(ax, 5.5, 4.4, 2.0, 3.4, "#27AE60", lw=1.5)
ax.text(3.2, 4.0, "logs to MLflow", fontsize=8, color='#27AE60', style='italic')

# Airflow -> Training Service (triggers)
draw_arrow(ax, 4.0, 3.4, 5.0, 4.4, "#F39C12", lw=1.5)
ax.text(4.0, 3.9, "triggers DAG", fontsize=8, color='#F39C12', style='italic')

# Prometheus scrapes services
draw_arrow(ax, 6.5, 3.4, 2.0, 4.4, "#E74C3C", lw=1.0)
draw_arrow(ax, 6.5, 3.4, 5.5, 4.4, "#E74C3C", lw=1.0)
draw_arrow(ax, 6.5, 3.4, 9.5, 4.4, "#E74C3C", lw=1.0)
ax.text(8.5, 4.0, "/metrics", fontsize=8, color='#E74C3C', style='italic')

# Prometheus -> Grafana
draw_arrow(ax, 7.4, 3.0, 8.1, 3.0, "#E74C3C", lw=2)
ax.text(7.5, 2.7, "PromQL", fontsize=8, color='#E74C3C', style='italic')

# Port labels at bottom
ax.text(6, 0.8, "Exposed Ports: 8082 (UI) | 8080 (API) | 5004 (Auth) | 5000 (MLflow) | 8081 (Airflow) | 9090 (Prometheus) | 3000 (Grafana)",
        ha='center', fontsize=9, color='#95A5A6', style='italic')

plt.tight_layout()
plt.savefig('diagrams/2_microservices_architecture.png', dpi=150, bbox_inches='tight',
            facecolor='#1a1a2e', edgecolor='none')
plt.close()
print("2. Microservices Architecture - DONE")


# ===========================================================
# DIAGRAM 3: ML Pipeline Flow (with Airflow orchestration)
# ===========================================================
fig, ax = plt.subplots(1, 1, figsize=(16, 7))
ax.set_xlim(-0.5, 15)
ax.set_ylim(-0.5, 5.5)
ax.axis('off')
ax.set_facecolor('#1a1a2e')
fig.patch.set_facecolor('#1a1a2e')

ax.text(7.5, 5.1, "ML Pipeline - From Data to Prediction", ha='center', va='center',
        fontsize=20, fontweight='bold', color='white')

# Steps
colors = ["#2d6a4f", "#2d6a4f", "#E67E22", "#E67E22", "#c0392b", "#8E44AD", "#3498DB"]
labels = ["Raw Data\n(CSV+Images)", "Preprocessing\n(Text+Image)", "Feature\nEngineering",
          "LSTM\nTraining", "Model\nEvaluation", "Model\nRegistry", "Prediction\nAPI"]
sublabels = ["5.6 GB", "Tokenization\nCleaning", "Sequences\nPadding", "10 Epochs\n27 Classes",
             "Loss, Accuracy\nMLflow Logging", "MLflow\nVersioning", "REST API\nReal-time"]

positions = [1, 3, 5, 7, 9, 11, 13]

for i, (pos, label, sub, color) in enumerate(zip(positions, labels, sublabels, colors)):
    draw_box(ax, pos, 3.0, 1.6, 1.2, label, sub, color, fontsize=10)
    if i < len(positions) - 1:
        draw_arrow(ax, pos + 0.85, 3.0, positions[i+1] - 0.85, 3.0, "white", lw=2)

# DVC Pipeline span
ax.text(4, 1.1, "DVC Pipeline (Reproducible)", ha='center', fontsize=10,
        color='#4A90D9', fontweight='bold')
ax.annotate('', xy=(0.3, 1.3), xytext=(7.8, 1.3),
            arrowprops=dict(arrowstyle='<->', color='#4A90D9', lw=2))

# MLflow span
ax.text(11, 1.1, "MLflow Tracking (Experiments)", ha='center', fontsize=10,
        color='#27AE60', fontweight='bold')
ax.annotate('', xy=(6.3, 1.3), xytext=(13.7, 1.3),
            arrowprops=dict(arrowstyle='<->', color='#27AE60', lw=2))

# Airflow orchestration span (covers the full pipeline)
ax.text(7.5, 0.3, "Airflow Orchestration (DAG scheduling & triggering)", ha='center', fontsize=10,
        color='#F39C12', fontweight='bold')
ax.annotate('', xy=(0.3, 0.5), xytext=(13.7, 0.5),
            arrowprops=dict(arrowstyle='<->', color='#F39C12', lw=2))

plt.tight_layout()
plt.savefig('diagrams/3_ml_pipeline.png', dpi=150, bbox_inches='tight',
            facecolor='#1a1a2e', edgecolor='none')
plt.close()
print("3. ML Pipeline - DONE")


# ===========================================================
# DIAGRAM 4: Monitoring Architecture (unchanged, already correct)
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
# DIAGRAM 5: Technology Stack (updated with Airflow, UI, Auth)
# ===========================================================
fig, ax = plt.subplots(1, 1, figsize=(16, 9))
ax.set_xlim(-0.5, 12.5)
ax.set_ylim(-0.5, 8.5)
ax.axis('off')
ax.set_facecolor('#1a1a2e')
fig.patch.set_facecolor('#1a1a2e')

ax.text(6, 8.1, "Technology Stack", ha='center', va='center',
        fontsize=20, fontweight='bold', color='white')

# Layers with 5 items each
layers = [
    ("Presentation / UI", 7.0, "#8E44AD",
     [("Web UI", 1.5), ("API Gateway", 3.8), ("Grafana UI", 6.0), ("MLflow UI", 8.2), ("Airflow UI", 10.5)]),
    ("Application / ML", 5.5, "#E67E22",
     [("TensorFlow/Keras", 1.5), ("LSTM Model", 3.8), ("NLTK", 6.0), ("scikit-learn", 8.2), ("Flask", 10.5)]),
    ("Data / Storage", 4.0, "#2d6a4f",
     [("pandas/numpy", 1.5), ("DVC", 3.8), ("CSV/Images", 6.0), ("SQLite", 8.2), ("PostgreSQL", 10.5)]),
    ("Orchestration / CI", 2.5, "#F39C12",
     [("Airflow", 1.5), ("DVC Pipeline", 3.8), ("GitHub Actions", 6.0), ("DAG Scheduler", 8.2), ("Nginx", 10.5)]),
    ("Infrastructure", 1.0, "#E74C3C",
     [("Docker Compose", 1.5), ("Prometheus", 3.8), ("Python 3.11", 6.0), ("mlops_network", 8.2), ("Healthchecks", 10.5)]),
]

for layer_label, y, color, items in layers:
    ax.add_patch(FancyBboxPatch((0.2, y - 0.5), 11.6, 1.2, boxstyle="round,pad=0.15",
                 facecolor="#16213e", edgecolor=color, linewidth=2, alpha=0.5))
    ax.text(6, y + 0.45, layer_label, ha='center', fontsize=10, color=color, fontweight='bold')
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
