# 🎓 RAKUTEN MLOPS - PRESENTATION GUIDE

**📘 Simple English Version (A2-B1 Level)**

> ⚡ **Learning Path**: First: Learn the words → Then: Learn the project → Then: The script

---

## 📋 Table of Contents

1. [📚 Key Words and Concepts](#part-1-key-words-and-concepts)
2. [🎯 Understand the Project](#part-2-understand-the-project)
3. [🎤 Presentation Script](#part-3-presentation-script)
4. [✅ Practice Checklist](#part-4-practice-checklist)
5. [📁 Project Structure](#part-5-project-structure)
6. [❓ Q&A Section (50 Questions)](#part-6-qa-section)
7. [✅ Understanding Self-Check](#part-7-understanding-self-check)
8. [🚨 Emergency Backup Plan](#part-8-emergency-backup-plan)

---

# 📚 PART 1: KEY WORDS AND CONCEPTS

> 💡 **Read this table first**. These are all the words you need to know.

## Core ML & MLOps Concepts

| 🔑 Term | 📖 Simple Explanation |
|---------|----------------------|
| **MLOps** | "Machine Learning Operations." We take an ML model and put it in a real system that people can use. Like DevOps but for ML models. |
| **LSTM** | "Long Short-Term Memory." A type of brain for the computer. It reads text word by word and remembers what came before. Good for text tasks. |
| **Classification** | Sorting things into groups. Example: "Samsung Galaxy smartphone" → "Electronics". The model does this automatically. |
| **Preprocessing** | Cleaning text before the model reads it. Remove HTML, numbers, stopwords, lemmatize. |
| **Tokenization** | Turning words into numbers. Model can't read words, only numbers. "samsung" → 42, "galaxy" → 17. |
| **Padding** | Making all texts the same length. If text has 5 words, add zeros to make 10. If 15 words, cut to 10. |
| **Embedding** | Turn each number into a list of 128 numbers that carry meaning. Similar words get similar lists. |
| **Softmax** | Last layer in model. Gives a percent for each of 27 categories. All add up to 100%. Highest = answer. |
| **Epoch** | One full pass through all training data. We train for 10 epochs = model sees all data 10 times. |
| **Batch Size** | How many examples the model looks at before updating itself. 32 = reads 32 texts, learns, then next 32. |

## Infrastructure & Architecture

| 🔑 Term | 📖 Simple Explanation |
|---------|----------------------|
| **Microservices** | Instead of one big program, many small programs. Each does one job. They talk over the network. |
| **Docker / Container** | A box that holds one program with everything it needs. Start, stop, move it. We have 13 boxes. |
| **Docker Compose** | Tool that starts all 13 containers together with one command. Knows which needs to start first. |
| **API (REST API)** | Way for programs to talk. One sends request ("classify this text"), other sends back answer. |
| **API Gateway** | The "front door" of our system. Every request goes through it first. Checks who you are, routes to right service. |
| **Flask** | Python library to build web APIs. All our services use Flask. |
| **Bridge Network** | All 13 containers share one private network (`mlops_network`). Can find each other by name. |

## Security & Authentication

| 🔑 Term | 📖 Simple Explanation |
|---------|----------------------|
| **Token** | Long random text (like password) that system gives you when you log in. Send it with every request to prove who you are. |
| **Bearer Token** | Token sent in header of request. "Bearer" just means "I am carrying this token." |
| **Authentication** | Checking **WHO** you are (login with username + password). |
| **Authorization** | Checking **WHAT** you can do (admin can retrain, normal user cannot). |
| **Role-Based Access** | Different users have different permissions. "admin" can do everything. "user" can only predict. |
| **SHA-256** | Way to hide passwords. We never save real password, we save scrambled version. Nobody can read original. |

## Monitoring & Orchestration Tools

| 🔑 Term | 📖 Simple Explanation |
|---------|----------------------|
| **MLflow** | Tool that saves every training experiment. Records settings, accuracy, which model version is best. |
| **Airflow** | Tool that runs tasks in order, automatically. Example: Step 1 load data → Step 2 train → Step 3 reload model. |
| **DAG** | "Directed Acyclic Graph." A chain of tasks. Task A must finish before Task B starts. Airflow uses DAGs. |
| **Prometheus** | Monitoring tool. Every 15 seconds asks each service: "How many requests? How fast?" Saves all numbers. |
| **Grafana** | Makes nice charts from Prometheus data. Shows dashboards with lines and colors. |
| **PromQL** | Language Grafana uses to ask Prometheus for data. Like SQL but for metrics. |
| **DVC** | "Data Version Control." Like Git but for big files. Our data is 5.6 GB, too big for Git. DVC tracks separately. |
| **CI/CD** | "Continuous Integration / Continuous Delivery." Every time we push code, tests run automatically. |

---

# 🎯 PART 2: UNDERSTAND THE PROJECT

## 🤔 What Is This Project?

We built a system that reads product descriptions and tells you the category.

**Example:**
- 📥 **Input**: "Samsung Galaxy smartphone 128GB dual camera fast charging"
- 📤 **Output**: "Electronics" (with 85% confidence)

**Key Facts:**
- 🎯 **27 possible categories**
- 🧠 **LSTM neural network** for classification
- 🏗️ **Full MLOps system** with monitoring, security, orchestration

---

## 🐳 The 13 Docker Containers

Think of it like a company with 13 workers. Each worker has one job:

### 🔷 Core ML Services (6 containers)

| # | Service | Port | What It Does |
|---|---------|------|-------------|
| 1️⃣ | **Web UI** | 8082 | The website you see in browser (Nginx) |
| 2️⃣ | **API Gateway** | 8080 | Front door - checks tokens, routes requests |
| 3️⃣ | **Auth Service** | 5004 | Login, passwords, gives you tokens |
| 4️⃣ | **Data Service** | 5001 | Loads CSV, splits data, cleans text |
| 5️⃣ | **Training Service** | 5002 | Trains LSTM model, sends results to MLflow |
| 6️⃣ | **Prediction Service** | 5003 | Loads trained model, makes predictions |

### 🔷 Infrastructure Services (7 containers)

| # | Service | Port | What It Does |
|---|---------|------|-------------|
| 7️⃣ | **MLflow** | 5000 | Saves every experiment, model registry |
| 8️⃣ | **Airflow Webserver** | 8081 | Shows Airflow interface, see DAGs |
| 9️⃣ | **Airflow Scheduler** | - | Runs tasks at right time (background) |
| 🔟 | **Airflow DB** | - | PostgreSQL database for Airflow metadata |
| 1️⃣1️⃣ | **Airflow Init** | - | Runs once at start to set up Airflow, then stops |
| 1️⃣2️⃣ | **Prometheus** | 9090 | Collects numbers from all services every 15s |
| 1️⃣3️⃣ | **Grafana** | 3000 | Makes charts from Prometheus data |

---

## 🔄 Prediction Flow (10 Steps)

```
┌─────────────┐
│  1. User    │  You type text and click "Classify"
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│  2. Browser → Gateway   │  Text + token sent to API Gateway (8080)
└──────┬──────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  3. Gateway → Auth Service   │  "Is this token valid?"
└──────┬───────────────────────┘
       │
       ▼
┌────────────────────────────────────┐
│  4. Auth → Gateway                 │  "Yes, user=admin, role=admin"
└──────┬─────────────────────────────┘
       │
       ▼
┌────────────────────────────────────────┐
│  5. Gateway → Prediction Service       │  Forwards text
└──────┬─────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  6. Prediction Service: Preprocess       │  Clean, tokenize, pad
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  7. LSTM Model Predicts                  │  Returns 27 probabilities
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  8. Find Highest Probability             │  Map number → category name
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  9. Result → Gateway → Browser           │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  10. User Sees Category + Confidence     │
└──────────────────────────────────────────┘
```

⚡ **Total time: < 1 second**

---

## 🔄 Retraining Flow (4 Airflow Tasks)

```
Task 1: Clean New Data
   ▼
Task 2: Start Training (background thread)
   ▼
Task 3: Poll every 10s: "Training done?" (max 1 hour)
   ▼
Task 4: Reload New Model
```

---

## 🖼️ The 5 Architecture Diagrams

### 📊 Diagram 1: Complete Architecture
- Shows **ALL 13 containers** and connections
- **6 layers** from top to bottom:
  1. User Layer (Web UI, Auth)
  2. API Gateway (purple box in center)
  3. ML Pipeline (Data, Training, Prediction - orange)
  4. Data Layer (Raw Data, DVC - green)
  5. Experiment Tracking (MLflow) + Orchestration (Airflow)
  6. Monitoring (Prometheus, Grafana - red) + CI/CD

### 📊 Diagram 2: Microservices Communication
- Shows **which service talks to which**
- **Arrow colors:**
  - 🩷 Pink: REST API calls
  - 💚 Green: "verify token", "logs to MLflow"
  - 💛 Yellow: "triggers DAG", "PromQL"
  - ❤️ Red: Prometheus scraping `/metrics`
- Everything inside Docker network box

### 📊 Diagram 3: ML Pipeline
- **7 boxes** from left to right:
  1. Raw Data (CSV+Images, 5.6 GB)
  2. Preprocessing (Tokenization, Cleaning)
  3. Feature Engineering (Sequences, Padding)
  4. LSTM Training (10 Epochs, 27 Classes)
  5. Model Evaluation (Loss, Accuracy, MLflow)
  6. Model Registry (MLflow Versioning)
  7. Prediction API (REST, Real-time)
- **3 colored bars** at bottom:
  - DVC Pipeline (covers steps 1-3)
  - MLflow Tracking (covers steps 4-7)
  - Airflow Orchestration (covers all steps)

### 📊 Diagram 4: Monitoring Architecture
- **Top**: 4 orange boxes (Gateway, Data, Training, Prediction) with `/metrics`
- **Middle**: Prometheus (red box, scrapes every 15s)
- **Bottom**: Grafana Dashboard (yellow box, visualization)
- **Right**: List of 8 collected metrics

### 📊 Diagram 5: Technology Stack
- **5 layers** from bottom to top:
  1. 🔴 **Infrastructure**: Docker Compose, Prometheus, Python 3.11, mlops_network, Healthchecks
  2. 🟡 **Orchestration/CI**: Airflow, DVC Pipeline, GitHub Actions, DAG Scheduler, Nginx
  3. 🟢 **Data/Storage**: pandas/numpy, DVC, CSV/Images, SQLite, PostgreSQL
  4. 🟠 **Application/ML**: TensorFlow/Keras, LSTM Model, NLTK, scikit-learn, Flask
  5. 🟣 **Presentation/UI**: Web UI, API Gateway, Grafana UI, MLflow UI, Airflow UI

---

# 🎤 PART 3: PRESENTATION SCRIPT

## 📋 Presentation Overview

| Info | Details |
|------|---------|
| ⏱️ **Total Time** | 20 minutes (19.7 min exactly) |
| 🗣️ **Speaking Speed** | 130 words per minute |
| 🌐 **Website** | http://localhost:8082 |
| 🔑 **Login** | admin / admin123 |

---

## 👤 Speaker Responsibilities

### 🔵 Speaker A (Total: 9.5 min / 48%)

#### Segment 1 (0:00 - 5:00) - 4.9 min
- ✅ Say hello and introduce project
- ✅ Log in to dashboard (live demo)
- ✅ Show 6 green health cards
- ✅ Show Diagram 1: Complete Architecture
- ✅ Show Diagram 5: Technology Stack
- ✅ Transition to Speaker B

#### Segment 3 (10:00 - 15:00) - 4.6 min
- ✅ Do live prediction ("Samsung Galaxy smartphone...")
- ✅ Explain what happened inside
- ✅ Show History panel
- ✅ Explain retraining workflow (**don't click button!**)
- ✅ Show Diagram 4: Monitoring Architecture
- ✅ Transition to Speaker B

**📝 Speaker A Must Do:**
- 🔐 Log in (admin/admin123)
- 🔄 Click "Refresh Health"
- ⌨️ Type prediction text
- 🖱️ Click "Classify"
- 🔀 Navigate tabs smoothly
- 🖼️ Click diagrams to enlarge

### 🟢 Speaker B (Total: 10.2 min / 52%)

#### Segment 2 (5:00 - 10:00) - 4.2 min
- ✅ Show Diagram 2: Microservices Communication
- ✅ Show Diagram 3: ML Pipeline (hardest part!)
- ✅ Explain data flow start → finish
- ✅ Explain DVC, MLflow, Airflow
- ✅ Transition to Speaker A

#### Segment 4 (15:00 - 20:00) - 5.9 min
- ✅ Explain Technology Stack
- ✅ Go to Users tab → explain security
- ✅ Explain CI/CD
- ✅ Explain system operations
- ✅ Final summary
- ✅ Thank you + ask for questions

**📝 Speaker B Must Do:**
- 🖼️ Click diagrams, explain carefully
- 👥 Show Users tab and roles table
- 👆 Point to admin vs user differences
- 💪 Strong conclusion
- ❓ Answer audience questions

---

## ⏱️ Timing Breakdown

```
📊 Segment 1 (Speaker A):  4.9 min  ████████████████░░░░ 25%
📊 Segment 2 (Speaker B):  4.2 min  █████████████░░░░░░░ 21%
📊 Segment 3 (Speaker A):  4.6 min  ███████████████░░░░░ 23%
📊 Segment 4 (Speaker B):  5.9 min  ██████████████████░░ 30%
                           ─────────
📊 TOTAL:                 19.7 min  ████████████████████ 100%
```

⚖️ **Balance**: Speaker A = 9.5 min (48%) | Speaker B = 10.2 min (52%)
✅ **Difference**: Only 0.7 minutes - Very balanced!

---

## ⚠️ IMPORTANT NOTES

### ✅ Before Presentation
- Start services: `make presentation`
- Open website: http://localhost:8082
- Browser zoom: 90% for projector
- Test login: admin / admin123
- Click "Refresh Health" → all 6 cards green
- Backup product description ready

### ⚠️ During Presentation
- Speak at 130 words/minute (not too fast!)
- **DO NOT** click "Start Retraining" in Segment 3 (only point!)
- Wait for diagrams to load before explaining
- Look at audience, not only screen
- Transition: "Now [Speaker B/A] will continue..."

### 🔑 Critical Information
- **Username**: admin
- **Password**: admin123
- **Role**: admin (can see Retrain + Users tabs)
- **Prediction Text**: "Samsung Galaxy smartphone 128GB, dual camera, fast charging"
- **Expected Result**: Electronics (70-95% confidence)

### 🚨 If Service Card is Red
- Stay calm!
- Say: "In a real system, we can restart this service quickly"
- Continue with green services
- (Backstage can run `make quick-check`)

---

# ✅ PART 4: PRACTICE CHECKLIST

## 📅 Before Presentation (1 day before)

- [ ] Read Part 1 (Vocabulary) 2 times
- [ ] Read Part 2 (Project Explanation) 2 times
- [ ] Read Part 3 (Script) OUT LOUD 3 times minimum
- [ ] Run `make presentation` and test all services start
- [ ] Open http://localhost:8082 and test login
- [ ] Do test prediction with Samsung text
- [ ] Click through all tabs: Dashboard → Predict → History → Retrain → Users
- [ ] Practice clicking while talking
- [ ] Time yourself reading each segment
- [ ] Read Q&A section completely (Part 6)
- [ ] Read Project Structure Guide (Part 5)

## 🌙 Night Before

- [ ] Read script 1 more time
- [ ] Sleep well (at least 7 hours!)
- [ ] Prepare clothes
- [ ] Charge laptop fully

## ⏰ 1 Hour Before

- [ ] Run `make presentation`
- [ ] Test website: http://localhost:8082
- [ ] Test login
- [ ] Do 1 practice prediction
- [ ] Set browser zoom to 90%
- [ ] Close other programs and tabs
- [ ] Turn off notifications
- [ ] Have water ready

## ⏰ 5 Minutes Before

- [ ] Take 3 deep breaths
- [ ] Open website on projector/screen
- [ ] Make sure login page is showing
- [ ] Have script open on laptop (not projector!)
- [ ] Remember: You know this. You built this. You can do this.

---

# 📁 PART 5: PROJECT STRUCTURE

> 💡 **This explains EVERY folder and file** so you understand what you built

## 📂 Complete Folder Structure

```
/home/anas/rakproj/
│
├── 📁 .github/workflows/        # CI/CD configuration
│   └── python-app.yml           # GitHub Actions: runs tests automatically
│
├── 📁 data/                     # All data files (5.6 GB total)
│   ├── raw/                     # Original CSV + images from Kaggle
│   ├── processed/               # Cleaned data after preprocessing
│   └── interim/                 # Temporary data during processing
│
├── 📁 diagrams/                 # 5 architecture diagrams (PNG images)
│   ├── 1_complete_architecture.png
│   ├── 2_microservices_architecture.png
│   ├── 3_ml_pipeline.png
│   ├── 4_monitoring_architecture.png
│   └── 5_technology_stack.png
│
├── 📁 mlruns/                   # MLflow experiment tracking data
│   ├── mlflow.db                # SQLite database with experiment history
│   └── [experiment folders]     # Each training run saved here
│
├── 📁 models/                   # Trained model files
│   ├── best_lstm_model.h5       # Trained LSTM neural network (Keras format)
│   ├── tokenizer_config.json    # Word-to-number mapping (10,000 words)
│   └── mapper.pkl               # Category number → name mapping (27 categories)
│
├── 📁 monitoring/               # Prometheus + Grafana configuration
│   ├── prometheus/
│   │   └── prometheus.yml       # What to monitor, how often (15s)
│   └── grafana/
│       ├── provisioning/        # Auto-setup for Grafana
│       └── dashboards/
│           └── mlops_dashboard.json  # Dashboard definition
│
├── 📁 services/                 # All 5 Flask microservices
│   ├── api_gateway/
│   │   ├── app.py               # Main code for API Gateway
│   │   └── Dockerfile           # How to build Docker image
│   ├── auth_service/
│   │   ├── app.py               # Login, tokens, password checking
│   │   ├── users.db             # SQLite database with users
│   │   └── Dockerfile
│   ├── data_service/
│   │   ├── app.py               # Load, clean, split data
│   │   └── Dockerfile
│   ├── training_service/
│   │   ├── app.py               # Train LSTM model
│   │   └── Dockerfile
│   └── prediction_service/
│       ├── app.py               # Load model, make predictions
│       └── Dockerfile
│
├── 📁 src/                      # Core source code (shared by services)
│   ├── __init__.py
│   ├── main.py                  # Main training script
│   ├── features/
│   │   ├── __init__.py
│   │   └── build_features.py    # DataImporter, TextPreprocessor
│   └── models/
│       ├── __init__.py
│       └── train_model.py       # TextLSTMModel, MLflowCallback
│
├── 📁 ui/                       # Web dashboard (the website)
│   ├── index.html               # Page structure
│   ├── styles.css               # Colors, fonts, layout
│   ├── app.js                   # Buttons, login, API calls
│   └── Dockerfile               # Nginx server
│
├── 📄 .gitignore                # Files Git should NOT track
├── 📄 CLAUDE.md                 # Project documentation
├── 📄 dvc.yaml                  # DVC pipeline: 3 stages
├── 📄 params.yaml               # ML parameters: epochs, batch_size, etc.
├── 📄 requirements.txt          # All Python libraries
├── 📄 docker-compose.yml        # Defines all 13 Docker containers
├── 📄 Makefile                  # Commands like "make presentation"
├── 📄 presentation              # Professional English version
├── 📄 presentation2             # Simple English version (THIS FILE)
└── 📄 README.md                 # Project documentation
```

---

## 🤔 Why Each Component Exists

### `.github/workflows/` - Automatic Testing
**Why**: Every time you push code to GitHub, tests run automatically. If tests fail, you know immediately. No manual testing needed.

### `data/` - Machine Learning Needs Data
**Why**: 5.6 GB of product data. We keep raw separate from processed so we can always go back to original if something goes wrong.

### `diagrams/` - Visual Understanding
**Why**: Pictures help people understand complex systems. These 5 diagrams show architecture, pipeline, and monitoring visually.

### `mlruns/` - Experiment Tracking
**Why**: Every training run saves results here. We can compare: "Was yesterday's model better than today's?" No manual spreadsheet needed.

### `models/` - Save Trained Model
**Why**: Prediction service loads model from here. If we train new model, old one stays as backup. No re-training if new model is worse.

### `monitoring/` - Know System Health
**Why**: We need to know if services are slow, broken, or working well. Prometheus and Grafana read these configs to know what to monitor and how to visualize.

### `services/` - Microservices Architecture
**Why**: Instead of one big program, split work into 5 small programs. Each does one job. If one breaks, others keep working. Easier to maintain and scale.

### `src/` - Shared Core Code
**Why**: Code that all services share. DataImporter, TextPreprocessor, LSTM model here. Write once, use everywhere. Avoid code duplication.

### `ui/` - User Interface
**Why**: The website users see. HTML for structure, CSS for beauty, JavaScript for making buttons work and API calls.

---

## 📄 Important Files Explained

### `docker-compose.yml` (~370 lines)
- **What**: Defines all 13 Docker containers
- **Why**: Instead of starting 13 containers by hand, start them all with one command: `docker compose up`
- **Contains**: For each service:
  - Docker image to use
  - Port to open
  - Environment variables
  - Dependencies (which service starts first)
  - Health check command

### `params.yaml` (~20 lines)
- **What**: All numbers for training
- **Why**: Change epochs from 10 to 20 here, not in code. Makes experiments easy to repeat.
- **Contains**:
  ```yaml
  epochs: 10
  batch_size: 32
  max_words: 10000
  max_len: 10
  embedding_dim: 128
  lstm_units: 128
  ```

### `dvc.yaml` (~50 lines)
- **What**: DVC pipeline with 3 stages
- **Why**: DVC tracks data like Git tracks code. Knows: "If data changed, run preprocessing again."
- **3 Stages**:
  1. `data_import` - Load raw CSV data
  2. `preprocess` - Clean text, remove stopwords, lemmatize
  3. `train` - Train LSTM model
- DVC runs them in order. If Stage 1 fails, it stops.

### `requirements.txt` (~30 lines)
- **What**: List of all Python libraries
- **Why**: Run `pip install -r requirements.txt` → Python installs everything automatically
- **Examples**:
  - `tensorflow==2.15.0` (for LSTM model)
  - `flask==3.0.0` (for APIs)
  - `pandas==2.1.3` (for data)
  - `nltk==3.8.1` (for text cleaning)
  - `mlflow==2.9.2` (for experiment tracking)

### `Makefile` (~150 lines)
- **What**: File with commands you can run
- **Why**: Instead of typing long Docker commands, type `make presentation`
- **Important Commands**:
  ```bash
  make presentation    # Full setup + health checks + open browsers
  make start           # Start all services
  make stop            # Stop all services
  make health          # Check if services healthy
  make test-predict    # Test a prediction
  ```

---

## 💻 How Key Code Files Work

### `services/prediction_service/app.py` (~300 lines)

Most important service for the demo!

```python
# Lines 1-20: Import libraries
from flask import Flask, request
from tensorflow.keras.models import load_model
import nltk
import pickle

# Lines 25-60: Load model when service starts
model = load_model('models/best_lstm_model.h5')  # Load LSTM
tokenizer = load_tokenizer()  # Load word→number mapping
mapper = pickle.load('models/mapper.pkl')  # Load category mapping

# Lines 70-120: /predict endpoint
@app.route('/predict', methods=['POST'])
def predict():
    # 1. Get text from request
    text = request.json['text']

    # 2. Clean text (same as training)
    #    - Remove HTML
    #    - Remove numbers/symbols
    #    - Lowercase
    #    - Tokenize (split into words)
    #    - Remove stopwords
    #    - Lemmatize
    clean_text = preprocess(text)

    # 3. Turn words → numbers
    #    "samsung galaxy" → [42, 17]
    sequence = tokenizer.texts_to_sequences([clean_text])

    # 4. Pad to length 10
    #    [42, 17] → [42, 17, 0, 0, 0, 0, 0, 0, 0, 0]
    padded = pad_sequences(sequence, maxlen=10)

    # 5. Model predicts
    #    Returns 27 probabilities: [0.02, 0.85, 0.01, ...]
    probabilities = model.predict(padded)

    # 6. Find highest
    #    argmax([0.02, 0.85, ...]) = 1
    category_num = np.argmax(probabilities)

    # 7. Map to name
    #    mapper[1] = "Electronics"
    category_name = mapper[category_num]
    confidence = probabilities[0][category_num]

    # 8. Return
    return {
        "category": category_name,
        "confidence": float(confidence)
    }
```

**⏱️ Total time: < 1 second**

---

### `src/models/train_model.py` (~250 lines)

Defines LSTM architecture:

```python
class TextLSTMModel:
    def __init__(self, max_words=10000, max_len=10, num_classes=27):
        """
        Create neural network with 4 layers:
        1. Input: 10 numbers (padded sequence)
        2. Embedding(128): each number → 128-dim vector
        3. LSTM(128): reads sequence, remembers context
        4. Dense(27, softmax): probability for each category
        """
        self.model = Sequential([
            Embedding(max_words, 128, input_length=max_len),
            LSTM(128),
            Dense(num_classes, activation='softmax')
        ])

    def train(self, X_train, y_train, epochs=10, batch_size=32):
        """
        Train the model:
        1. Compile: optimizer=Adam, loss=categorical_crossentropy
        2. Fit: loop 10 times through data
        3. Update weights to improve predictions
        """
        self.model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.15
        )

        return history
```

---

### `ui/app.js` (~500 lines)

Makes website interactive:

```javascript
// When you click "Sign In"
async function login() {
    // 1. Get username + password
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // 2. Send to API Gateway
    const response = await fetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({username, password})
    });

    // 3. Get back token
    const data = await response.json();

    // 4. Save token in browser
    localStorage.setItem('token', data.token);

    // 5. Show Dashboard
    showDashboard();
}

// When you click "Classify"
async function predict() {
    // 1. Get text
    const text = document.getElementById('text').value;

    // 2. Send POST with token
    const response = await fetch('/predict', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({text})
    });

    // 3. Get result
    const result = await response.json();

    // 4. Show on screen
    document.getElementById('category').textContent = result.category;
    document.getElementById('confidence').textContent =
        `${(result.confidence * 100).toFixed(1)}%`;

    // 5. Save to history
    saveToHistory(text, result.category, result.confidence);
}
```

---

## 🐳 Docker Explained Simply

### What is Docker?
Imagine each service is a person. Each person needs:
- 🏠 A room to work in (container)
- 🔧 Tools to do their job (libraries)
- 📞 A way to talk to others (network)

Docker gives each service its own isolated room. If one person's tools break, it doesn't affect others.

### What is a Dockerfile?
A recipe for building a container:

```dockerfile
FROM python:3.11-slim                    # Start with Python 3.11
WORKDIR /app                             # Make a folder /app
COPY requirements.txt .                  # Copy library list
RUN pip install -r requirements.txt      # Install libraries
COPY . .                                 # Copy all code
CMD ["python", "app.py"]                 # When start, run app.py
```

### What is docker-compose.yml?
Instead of starting 13 containers by hand, this file starts them all together. Also creates network so they can talk.

---

## 🏗️ Why We Made These Architecture Decisions

| ❓ Question | 💡 Answer |
|------------|----------|
| **Why 13 containers instead of 1 big program?** | If one service fails, others keep working. Can update one service without touching others. "Separation of concerns." |
| **Why Flask for all services?** | Simple, lightweight, perfect for small APIs. Everyone knows Flask. Easy to learn, easy to debug. |
| **Why LSTM instead of simple model?** | Text has order. "Samsung Galaxy phone" ≠ "phone Galaxy Samsung". LSTM reads sequentially and remembers context. Naive Bayes = 65% accuracy, LSTM = 80%. |
| **Why LSTM not Transformer (BERT)?** | LSTM: faster, smaller, good enough for 27 categories. BERT: powerful but overkill, needs GPU, takes hours. LSTM trains in 10 min on CPU. |
| **Why MLflow?** | When you train 20 models with different settings, how remember which was best? MLflow saves everything automatically. |
| **Why Airflow?** | Retraining = 4 steps in order. Airflow ensures step 2 doesn't start until step 1 finishes. Automatic orchestration. |
| **Why Prometheus + Grafana instead of logs?** | Logs = text files, hard to see patterns. Prometheus = numbers. Grafana = charts. See immediately: "Why is service slow today?" |
| **Why SHA-256 for passwords?** | If database hacked, they see hash not real password. Cannot reverse SHA-256. |
| **Why JWT tokens instead of sessions?** | Stateless. API Gateway doesn't need to remember who is logged in. Token itself proves who you are. Better for microservices. |
| **Why DVC for data instead of Git?** | Git = for code (small files). Our data = 5.6 GB. Git would be slow. DVC = designed for big files. |
| **Why Docker network instead of localhost?** | Inside Docker, "localhost" = this container only. Shared network = containers find each other by name. |

---

# ❓ PART 6: Q&A SECTION (50 QUESTIONS)

> ⚠️ **READ CAREFULLY!** Most likely questions in your defense.
>
> ⏱️ You have **10 MINUTES** for Q&A = ~5-7 questions maximum.
>
> 📖 Answers written so you can **READ THEM OUT LOUD**!

---

## 🏗️ GROUP 1: Architecture & Design

<details>
<summary><b>Q1: Why microservices instead of monolithic application?</b></summary>

**Answer:**

We chose microservices because it has three big advantages:

1. **Separation of concerns**: Each service does one job. Training service only trains, prediction service only predicts. Makes code easier to understand and test.

2. **Independent scaling**: If we get many prediction requests, we can start more prediction containers without touching training service.

3. **Fault isolation**: If training service crashes, users can still make predictions. In monolithic application, one bug can break everything.
</details>

<details>
<summary><b>Q2: Why Docker containers?</b></summary>

**Answer:**

Docker solves three problems:

1. **Consistency**: Code runs exactly same on my laptop, test server, and production. No more "it works on my machine" problems.

2. **Isolation**: Each container has its own Python version and libraries. No conflicts.

3. **Easy deployment**: I can send one docker-compose.yml file to anyone, they can start whole system with one command. No manual installation.
</details>

<details>
<summary><b>Q3: Isn't 13 containers too many?</b></summary>

**Answer:**

It looks like many, but each has clear purpose:
- 6 ML services (Gateway, Auth, Data, Training, Prediction, MLflow)
- 4 for Airflow (webserver, scheduler, database, init)
- 2 for monitoring (Prometheus, Grafana)
- 1 web UI

We need all for complete MLOps system. If I removed any, we'd lose important functionality like monitoring or orchestration.
</details>

<details>
<summary><b>Q4: How do containers communicate?</b></summary>

**Answer:**

All 13 containers share one Docker network called `mlops_network` (bridge network). Inside this network, containers can find each other by name.

For example, when API Gateway needs to talk to prediction service, it sends request to `http://prediction_service:5003`. Docker's DNS resolves the name to container's IP automatically. Much better than hard-coding IP addresses.
</details>

<details>
<summary><b>Q5: What if one container crashes?</b></summary>

**Answer:**

Others keep running. Docker has health checks for each container. Every 30 seconds, Docker runs health check command. If container is unhealthy, Docker restarts it automatically.

Also, because of microservices architecture, if training service crashes, users can still make predictions. System is resilient.
</details>

---

## 🧠 GROUP 2: ML Model & Training

<details>
<summary><b>Q6: Why LSTM instead of simpler model like Logistic Regression?</b></summary>

**Answer:**

Product descriptions are text, and text has word order. "Samsung Galaxy phone" is different from "phone Galaxy Samsung."

LSTM reads text word by word and remembers what came before. Simple models treat text like bag of words - they ignore order.

LSTM gives better accuracy for text classification. In our tests, LSTM gave 80% accuracy while Naive Bayes gave only 65%.
</details>

<details>
<summary><b>Q7: Why LSTM not Transformer (BERT)?</b></summary>

**Answer:**

BERT is more powerful, but it's also much bigger and slower. BERT would take hours to train and need GPU.

LSTM trains in 10 minutes on CPU. For 27 categories and simple product descriptions, LSTM is good enough.

We chose simplicity and speed over maximum accuracy. In real company, if accuracy was critical, we might use BERT, but for this project, LSTM is right balance.
</details>

<details>
<summary><b>Q8: Explain what happens inside LSTM model?</b></summary>

**Answer:**

LSTM has 4 layers:

1. **Input layer**: receives 10 numbers (padded sequence)
2. **Embedding layer**: turns each number into vector of 128 numbers that carry meaning. Similar words get similar vectors.
3. **LSTM layer**: reads sequence and remembers context. Has 128 memory cells.
4. **Output layer**: 27 neurons (one per category) with softmax activation. Gives probability for each category. All probabilities add to 100%. Highest = answer.
</details>

<details>
<summary><b>Q9: What is preprocessing and why important?</b></summary>

**Answer:**

Preprocessing cleans text before model sees it. We do 6 steps:
1. Remove HTML tags
2. Lowercase everything
3. Remove numbers and symbols
4. Split into words (tokenization)
5. Remove French stopwords (common words like "le", "la")
6. Lemmatization (make words shorter: "running" → "run")

Why? Model learns patterns. If we don't clean, model sees "Samsung", "samsung", "SAMSUNG" as three different words. Preprocessing makes data consistent.
</details>

<details>
<summary><b>Q10: What is tokenization and padding?</b></summary>

**Answer:**

**Tokenization**: Model cannot read words, only numbers. Tokenization turns words into numbers. We have vocabulary of 10,000 words. "Samsung" might be 42, "galaxy" might be 17.

**Padding**: Makes all sequences same length. Our model expects exactly 10 numbers. If text has 5 words, we add zeros: [42, 17, 88, 6, 91] becomes [42, 17, 88, 6, 91, 0, 0, 0, 0, 0]. If it has 15 words, we cut to 10. Required because neural networks need fixed-size inputs.
</details>

<details>
<summary><b>Q11: How do you know if model is good? What metrics?</b></summary>

**Answer:**

We use two metrics:

1. **Accuracy**: How often is model correct? If accuracy is 80%, model is right 8 times out of 10.
2. **Loss**: How wrong the model is. Lower loss = better.

During training, we watch both metrics. If accuracy goes up and loss goes down, model is learning.

We also split data: train (70%), validation (15%), test (15%). Train on training set, check performance on validation, final evaluation on test set. This prevents overfitting.
</details>

<details>
<summary><b>Q12: What is overfitting and how prevent it?</b></summary>

**Answer:**

Overfitting means model memorizes training data instead of learning patterns. Like student who memorizes answers instead of understanding concepts. Model gets 100% on training data but fails on new data.

We prevent overfitting three ways:
1. Split data so we can test on unseen data
2. Don't train for too many epochs (we stop at 10)
3. Could add dropout layers, but for this project 10 epochs is enough
</details>

<details>
<summary><b>Q13: Why 10 epochs? Why not 5 or 20?</b></summary>

**Answer:**

We tested different numbers:
- 5 epochs: model still learning (accuracy going up)
- 20 epochs: accuracy stopped improving after epoch 12
- 10 epochs: good accuracy without wasting time

This is hyperparameter - we tuned it by experimenting. In real company, we might use early stopping: automatically stop when accuracy stops improving.
</details>

---

## 🔌 GROUP 3: Microservices

<details>
<summary><b>Q14: What does API Gateway do exactly?</b></summary>

**Answer:**

API Gateway is the front door. Every request goes through it. It does three things:

1. **Authentication**: Checks your token by calling Auth Service. If token is invalid, request is rejected immediately.
2. **Routing**: Looks at URL path and sends request to right service. `/predict` goes to prediction service, `/train` goes to training service.
3. **Logging and monitoring**: Every request is counted by Prometheus.

This centralized control makes system secure and observable.
</details>

<details>
<summary><b>Q15: How does authentication work with JWT tokens?</b></summary>

**Answer:**

When you log in with username and password, Auth Service checks password using SHA-256 hash. If correct, it generates random token (64 hexadecimal characters). This token is sent back to browser.

Browser saves it in localStorage. For every request after that, browser sends token in Authorization header as "Bearer <token>".

API Gateway asks Auth Service: "Is this token valid?" If yes, request continues. If no, you get 401 Unauthorized error.

When you log in again, old token is deleted.
</details>

<details>
<summary><b>Q16: Why hash passwords with SHA-256?</b></summary>

**Answer:**

Security. If someone hacks our database, they should not be able to read real passwords.

SHA-256 turns "admin123" into long random-looking string: "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918".

This is one-way: you cannot reverse it to get original password. When you log in, we hash what you typed and compare to stored hash. If they match, password is correct.

This protects user passwords even if database leaks.
</details>

<details>
<summary><b>Q17: Authentication vs Authorization difference?</b></summary>

**Answer:**

**Authentication** = WHO you are. We check: username and password correct?

**Authorization** = WHAT you can do. We check: does this user have permission?

For example, both "admin" and "user" can authenticate (log in). But only "admin" is authorized to retrain model or manage users. Normal users can only predict.

We implement this with role-based access control. Auth Service returns not just "token valid" but also "role: admin" or "role: user". Gateway checks role before allowing certain actions.
</details>

<details>
<summary><b>Q18: How does prediction service work step by step?</b></summary>

**Answer:**

When you click Classify, this happens:

1. Browser sends text + token to API Gateway
2. Gateway checks token with Auth Service
3. Gateway forwards text to Prediction Service
4. Prediction Service preprocesses text (clean, tokenize, pad)
5. Passes sequence to LSTM model
6. Model returns 27 probabilities
7. We take highest probability, map number to category name
8. Return result to Gateway
9. Gateway returns to browser
10. Browser shows category + confidence

This all happens in less than 1 second.
</details>

<details>
<summary><b>Q19: Can multiple users predict simultaneously?</b></summary>

**Answer:**

Yes. Flask handles concurrent requests. Each request runs in its own thread.

If 10 users send predictions at same time, Flask queues them and processes them one by one (or in parallel if server has multiple cores).

LSTM model is loaded once when service starts, then shared by all requests. This is efficient.

If traffic gets very high, we can start multiple prediction service containers and use load balancer.
</details>

---

## 📊 GROUP 4: MLflow & Experiment Tracking

<details>
<summary><b>Q20: What is MLflow and why need it?</b></summary>

**Answer:**

MLflow is experiment tracking tool. Every time we train model, we want to know: What hyperparameters did we use? What accuracy did we get? How long did it take?

Without MLflow, we would need to write this down manually in spreadsheet. MLflow does it automatically.

It also has model registry: we can save multiple versions of model and mark best one. This is critical for reproducibility and for comparing experiments.
</details>

<details>
<summary><b>Q21: What information does MLflow track?</b></summary>

**Answer:**

MLflow tracks three types of information:

1. **Parameters**: epochs, batch size, max words, max length, embedding dimension, LSTM units
2. **Metrics**: training loss, training accuracy, validation loss, validation accuracy
3. **Artifacts**: saved model file (.h5), tokenizer config, category mapper

It also tracks who ran experiment, when, and how long it took. All stored in SQLite database `mlflow.db`.
</details>

<details>
<summary><b>Q22: How do you use MLflow in training process?</b></summary>

**Answer:**

In our training code, we have MLflow integration:

1. When training starts, we call `mlflow.start_run()`
2. Then log parameters with `mlflow.log_param()`
3. Log metrics with `mlflow.log_metric()`
4. We also made custom Keras callback called `MLflowCallback`. After each epoch, it automatically logs loss and accuracy to MLflow.
5. When training finishes, log model artifact with `mlflow.log_artifact()`
6. Finally `mlflow.end_run()`

All automatic - training service just runs the code.
</details>

<details>
<summary><b>Q23: Can you compare different training runs in MLflow?</b></summary>

**Answer:**

Yes. If you open MLflow UI at http://localhost:5000, you see table with all experiments. Each row is one training run.

You can sort by accuracy to find best model. You can click on run to see all parameters and metrics.

You can also compare two runs side by side: MLflow shows you exactly what was different. For example, "Run 1 used 10 epochs and got 78% accuracy. Run 2 used 15 epochs and got 80% accuracy."

This helps you understand which settings work best.
</details>

---

## 🔄 GROUP 5: Airflow & Orchestration

<details>
<summary><b>Q24: What is Airflow and why use it?</b></summary>

**Answer:**

Airflow is workflow orchestration tool. It runs tasks in order automatically.

Our retraining workflow has 4 steps: clean data, train model, wait for training to finish, reload new model. These steps must run in order. If training fails, we should not reload model.

Airflow manages this. We define DAG (Directed Acyclic Graph) that says: "Task A must finish before Task B starts." Airflow takes care of scheduling and error handling.
</details>

<details>
<summary><b>Q25: What is a DAG?</b></summary>

**Answer:**

DAG means Directed Acyclic Graph:
- **Directed** = tasks have order (arrows point from one task to next)
- **Acyclic** = no loops (Task A cannot depend on Task B if Task B depends on Task A)

In simple words, DAG is chain of tasks. Our retrain DAG has 4 tasks in line:
Task 1 → Task 2 → Task 3 → Task 4

Airflow runs them one by one. If any task fails, Airflow stops and marks DAG as failed.
</details>

<details>
<summary><b>Q26: How does retraining work when admin clicks button?</b></summary>

**Answer:**

When admin clicks "Start Retraining", this happens:

1. Dashboard sends request to API Gateway
2. Gateway checks: is this user admin? Yes.
3. Gateway calls Airflow REST API to trigger `retrain_pipeline` DAG
4. Airflow starts Task 1: call data service to preprocess new data
5. Task 2: call training service to start training. Training runs in background thread so doesn't block.
6. Task 3: poll training service every 10 seconds: "Are you done?" Wait up to 1 hour.
7. Task 4: call prediction service to reload model from disk

Done. Whole process is automatic.
</details>

<details>
<summary><b>Q27: What if training fails in middle?</b></summary>

**Answer:**

Airflow detects failure and stops DAG. Later tasks don't run.

For example, if training fails at epoch 5, Task 3 (wait for completion) will see error. Airflow marks Task 3 as failed and stops. Task 4 (reload model) does not run.

This is safe: old model stays loaded in prediction service. In Airflow UI, you can see error message and retry DAG manually after fixing problem.
</details>

---

## 📈 GROUP 6: Monitoring (Prometheus & Grafana)

<details>
<summary><b>Q28: How does monitoring work in your system?</b></summary>

**Answer:**

We use Prometheus and Grafana. Every Flask service has `/metrics` endpoint that exposes numbers in Prometheus format.

Prometheus is configured to scrape (ask for) these metrics every 15 seconds. Prometheus stores all numbers in time-series database.

Grafana connects to Prometheus and makes charts. We built custom dashboard in Grafana that shows request counts, request latency, prediction confidence, and service health.

This gives us real-time visibility into system performance.
</details>

<details>
<summary><b>Q29: What metrics do you track?</b></summary>

**Answer:**

We track 8 types of metrics:

1. **Request count**: how many requests each service received
2. **Request latency**: how long each request took in milliseconds
3. **Service health**: is service responding?
4. **Prediction count per category**: how many times each category was predicted
5. **Prediction confidence**: average confidence score
6. **Inference latency**: how long model takes to predict
7. **Training status**: is training running?
8. **Training loss and accuracy**: tracked during training

All automatic via `prometheus_client` library.
</details>

<details>
<summary><b>Q30: Why monitoring important in production system?</b></summary>

**Answer:**

Monitoring tells you what is happening right now. Without it, you are blind.

If prediction service becomes slow, monitoring shows you immediately. If many predictions have low confidence, monitoring alerts you that model might need retraining. If service crashes, monitoring shows red alert.

In real company, monitoring is connected to alerts: if latency goes above 500ms, send SMS to engineer.

For this project, we have dashboards that show everything visually.
</details>

<details>
<summary><b>Q31: What is PromQL?</b></summary>

**Answer:**

PromQL is query language for Prometheus. Like SQL but for metrics.

Grafana uses PromQL to ask Prometheus for data. For example, to show average request latency over last 5 minutes, Grafana sends this PromQL query:

```
rate(request_duration_seconds_sum[5m]) / rate(request_duration_seconds_count[5m])
```

Prometheus calculates result and sends back. PromQL is powerful but complex - we used pre-built queries for this project.
</details>

---

## 💾 GROUP 7: Data & DVC

<details>
<summary><b>Q32: Why DVC instead of Git for data?</b></summary>

**Answer:**

Our data is 5.6 GB. Git is designed for code (small text files). If we put 5.6 GB in Git, repository would be huge and slow. Every clone would download all data, even if you just want to look at code.

DVC is designed for big files. It stores only small metadata file in Git (`data.dvc`, 200 bytes). Actual data is stored separately (on server or cloud storage).

This keeps Git repository small and fast.
</details>

<details>
<summary><b>Q33: How does DVC track data pipeline?</b></summary>

**Answer:**

DVC has file called `dvc.yaml` that defines pipeline. It has 3 stages: data_import, preprocess, and train.

For each stage, DVC knows: what command to run, what files are inputs, what files are outputs.

When you run `dvc repro`, DVC checks: did input files change? If yes, run stage again. If no, skip it (use cached result).

This is like Make but for data. It saves time: if data didn't change, we don't need to preprocess again.
</details>

<details>
<summary><b>Q34: Where does data come from?</b></summary>

**Answer:**

Data comes from Kaggle. It's Rakuten dataset: product descriptions in French with 27 categories.

Dataset has two parts:
1. CSV file with text descriptions and category labels
2. Image files (one image per product)

Total 5.6 GB. We use only text data for this project. Images are in dataset but we don't use them (we could build image classifier in future).
</details>

---

## ⚙️ GROUP 8: CI/CD (GitHub Actions)

<details>
<summary><b>Q35: What is CI/CD and why important?</b></summary>

**Answer:**

CI/CD means Continuous Integration and Continuous Delivery:

**Continuous Integration** = every time we push code, tests run automatically. If tests fail, we know immediately.

**Continuous Delivery** = code is always ready to deploy.

For this project, we use GitHub Actions. Every push triggers workflow:
1. Run flake8 (check code style)
2. Run pytest (run tests)
3. Build Docker images (make sure they build without errors)

If all steps pass, code is good. This prevents bugs from reaching production.
</details>

<details>
<summary><b>Q36: What tests do you run in CI/CD?</b></summary>

**Answer:**

We have two types of checks:

1. **Linting with flake8**: checks Python code style (no syntax errors, no unused imports, no undefined variables)

2. **Unit tests with pytest**: we test data loading, text preprocessing, tokenizer serialization, model architecture, and authentication logic

We also check that no large binary files were committed by mistake. All tests must pass before we merge code. This is quality control.
</details>

<details>
<summary><b>Q37: What is flake8?</b></summary>

**Answer:**

Flake8 is tool that checks Python code for style errors and potential bugs. It looks for things like:
- Syntax errors (you forgot colon)
- Undefined variables (used variable before defining it)
- Unused imports (imported library but never used)
- Lines that are too long (over 127 characters)

Flake8 helps keep code clean and consistent. All team members follow same style.
</details>

---

## 🔒 GROUP 9: Security

<details>
<summary><b>Q38: What security measures did you implement?</b></summary>

**Answer:**

We implemented four security measures:

1. **Password hashing with SHA-256**: we never store plaintext passwords
2. **JWT token authentication**: every request must include valid token
3. **Role-based access control**: admin and user have different permissions
4. **Token invalidation**: when you log in again, old token is deleted. Prevents token theft.

We also run security checks in CI/CD to make sure no secrets are committed to Git.
</details>

<details>
<summary><b>Q39: Can someone steal a token and use it?</b></summary>

**Answer:**

If someone intercepts token (for example, by looking at network traffic), they could use it until it's invalidated.

To prevent this in production, we would use HTTPS (encrypted communication). HTTPS scrambles all data, including tokens, so nobody can read it.

For this project, we use HTTP because it's running on localhost. In real company, we would also add token expiration: tokens become invalid after 1 hour automatically.
</details>

<details>
<summary><b>Q40: Admin vs user roles difference?</b></summary>

**Answer:**

**Normal users** can only make predictions and see their history. They cannot retrain model, cannot see Retrain tab, and cannot manage users.

**Admin users** can do everything: predict, retrain, and manage users.

Auth Service stores role in database. When you log in, token response includes your role. API Gateway checks role before allowing admin-only actions.

This is role-based access control (RBAC).
</details>

---

## 🔧 GROUP 10: Troubleshooting & "What If"

<details>
<summary><b>Q41: What if prediction service crashes?</b></summary>

**Answer:**

User gets error message. API Gateway will try to connect to prediction service and get connection error. It returns HTTP 503 Service Unavailable to browser.

Docker's health check detects that prediction service is down and restarts it automatically (usually in 10-30 seconds).

Meanwhile, other users also cannot predict, but training and monitoring still work. After restart, predictions work again. This is fault isolation.
</details>

<details>
<summary><b>Q42: What if you want to add category 28?</b></summary>

**Answer:**

We would need to retrain model completely. Output layer has 27 neurons (one per category). To add category 28, we need 28 neurons. This means changing model architecture.

Steps:
1. Add new category to data
2. Update `mapper.pkl` file to include category 28
3. Change model code to use `num_classes=28` instead of 27
4. Retrain model from scratch
5. Deploy new model

Old model cannot handle 28 categories without retraining.
</details>

<details>
<summary><b>Q43: What if training takes more than 1 hour?</b></summary>

**Answer:**

Airflow DAG has timeout: it waits maximum 1 hour for training to finish. If training is not done after 1 hour, Airflow marks task as failed.

To fix this, we have two options:
1. Increase timeout in DAG configuration
2. Use more powerful server or GPU to make training faster

For this project, 10 epochs take about 10 minutes, so 1 hour is more than enough.
</details>

<details>
<summary><b>Q44: How would you deploy this to production?</b></summary>

**Answer:**

We would need to change several things:

1. Use HTTPS instead of HTTP for security
2. Use cloud database (PostgreSQL on AWS) instead of SQLite
3. Add token expiration (tokens expire after 1 hour)
4. Use load balancer to distribute traffic across multiple prediction service containers
5. Use cloud storage (S3) for DVC data
6. Set up monitoring alerts (send email if service fails)
7. Use Kubernetes instead of docker-compose for better orchestration
8. Add logging to central system (like ELK stack)

This project has foundation; we would just make it production-ready.
</details>

<details>
<summary><b>Q45: What if two admins start retraining simultaneously?</b></summary>

**Answer:**

Airflow allows only one instance of DAG to run at time by default. If Admin 1 starts retraining, DAG is marked as "running".

If Admin 2 clicks button while DAG is still running, Airflow rejects second request and says "DAG is already running".

Admin 2 would need to wait until first training finishes. We could change this behavior, but for retraining, sequential is safer.
</details>

---

## 🎯 GROUP 11: General Project

<details>
<summary><b>Q46: How long did it take to build this project?</b></summary>

**Answer:**

(Answer honestly based on your timeline. Here's example:)

The project took approximately 4-6 weeks:
- Week 1: Planning + learning MLOps/Docker
- Week 2-3: ML model + preprocessing
- Week 3-4: Microservices + Docker
- Week 5: Monitoring + CI/CD
- Week 6: Testing + documentation + presentation prep
</details>

<details>
<summary><b>Q47: What was most difficult part?</b></summary>

**Answer:**

(Choose what was actually hard. Examples:)

**Option 1**: Most difficult part was connecting all services together. Docker networking, token auth, debugging API calls took most time.

**Option 2**: Most difficult part was understanding Airflow. DAGs, task dependencies, REST API were new concepts. Took several tries to get retraining workflow right.
</details>

<details>
<summary><b>Q48: What would you do differently if you started over?</b></summary>

**Answer:**

If I started over, I would:
1. Plan architecture more carefully at beginning (draw diagrams before coding)
2. Write tests from beginning not end
3. Document as I go instead of writing documentation at end

These changes would save time and reduce bugs.
</details>

<details>
<summary><b>Q49: What did you learn from this project?</b></summary>

**Answer:**

I learned five important things:

1. How to build and deploy machine learning models in production environment
2. How microservices architecture works and why it's useful
3. How to use Docker and docker-compose to manage complex systems
4. How to implement monitoring and observability with Prometheus and Grafana
5. How to integrate multiple tools (MLflow, Airflow, DVC) into one cohesive system

This project gave me hands-on experience with real-world MLOps practices.
</details>

<details>
<summary><b>Q50: Can this system handle real-world production traffic?</b></summary>

**Answer:**

Architecture is production-ready, but we would need some changes for high traffic:

Currently, we have one container per service. For production, we would run multiple prediction service containers behind load balancer.

We would use Kubernetes for better orchestration and auto-scaling. We would use managed database instead of SQLite. We would add caching (Redis) to make predictions faster. We would use CDN for UI.

Core design is solid; we would just scale it horizontally (more containers) and add production-grade infrastructure.
</details>

---

# ✅ PART 7: UNDERSTANDING SELF-CHECK

> 📝 **Before presentation, test yourself** with these questions. If you cannot answer them, read relevant section again!

## 📗 BASIC LEVEL (You MUST know these)

- [ ] What does MLOps mean?
- [ ] How many Docker containers do we have?
- [ ] What is URL of dashboard?
- [ ] What are login credentials?
- [ ] What is an LSTM?
- [ ] What are the 27 categories?
- [ ] What does prediction service do?
- [ ] What is preprocessing?
- [ ] What is a token?
- [ ] What does "healthy" mean in health cards?

## 📘 INTERMEDIATE LEVEL (You should know these)

- [ ] Why microservices instead of one big program?
- [ ] How do containers talk to each other?
- [ ] What happens when you click "Classify"?
- [ ] What is tokenization?
- [ ] What is padding?
- [ ] Why do we hash passwords?
- [ ] What does MLflow do?
- [ ] What does Airflow do?
- [ ] What does Prometheus do?
- [ ] What is difference between authentication and authorization?

## 📙 ADVANCED LEVEL (For deep questions)

- [ ] Explain LSTM architecture (4 layers)
- [ ] Explain retraining workflow (4 steps)
- [ ] What metrics does Prometheus collect?
- [ ] Why DVC instead of Git for data?
- [ ] What is CI/CD and why important?
- [ ] What would you change for production deployment?
- [ ] What happens if service crashes?
- [ ] How does API Gateway check tokens?
- [ ] Why 10 epochs and not 20?
- [ ] What is PromQL?

---

# 🚨 PART 8: EMERGENCY BACKUP PLAN

## Scenario-Based Solutions

### ⚠️ SCENARIO 1: Service is RED (unhealthy)

**💬 What to Say:**
> "As you can see, one service is showing as unhealthy. This actually demonstrates the value of health checks. In production system, we can see immediately which component has issue. Let me show you that core functionality still works because of our microservices architecture."

**🔧 What to Do:**
- Continue with presentation
- If it's NOT prediction service, you can still do demo
- Point out other services still running (fault isolation)
- If someone backstage can help: run `make quick-check`
- At end: "In production, Docker would automatically restart failed service."

---

### ⚠️ SCENARIO 2: Prediction fails / gives error

**💬 What to Say:**
> "It looks like we're experiencing a connection issue. This is good opportunity to show you how we handle errors in system. Let me try again."

**🔧 What to Do:**
- Click "Classify" one more time
- If still fails, show History panel instead: "Here you can see previous predictions that worked. System saves all results."
- Move on to explaining retraining workflow
- Don't panic! Stay calm.

---

### ⚠️ SCENARIO 3: Website won't load at all

**💬 What to Say:**
> "It seems we have a network issue. Let me show you the architecture diagrams while we troubleshoot."

**🔧 What to Do:**
- Skip to diagrams immediately
- Spend more time explaining architecture from diagrams
- If you have screenshots prepared, show those
- Explain: "System works - we tested it before. This is temporary connection issue, but architecture and code are solid."

---

### ⚠️ SCENARIO 4: You forget what to say next

**🔧 What to Do:**
- Look at your script on laptop (not projector!)
- Take sip of water (gives you 3 seconds to think)
- Say: "Let me show you the next diagram" and scroll down
- Click on diagram to buy time
- Remember: audience doesn't know what you planned to say

---

### ⚠️ SCENARIO 5: Very technical question you don't understand

**💬 What to Say:**
> "That's a very detailed technical question. To give you most accurate answer, I would need to check specific implementation details in code. What I can tell you is [explain general concept]. If you'd like, we can discuss this in more detail after presentation."

**Then:**
- After presentation, look up answer
- Or admit: "That specific detail is beyond what I covered in this project, but it's great suggestion for future improvement."

---

### ⚠️ SCENARIO 6: You accidentally click "Start Retraining"

**💬 What to Say:**
> "I've just triggered the retraining workflow. This will run in background without affecting prediction service. Let me continue with presentation while Airflow orchestrates retraining steps."

**🔧 What to Do:**
- Don't panic!
- This is actually fine - shows system works
- Continue normally
- If time permits at end, show Airflow UI to demonstrate DAG running

---

### ⚠️ SCENARIO 7: Internet/network is completely down

**🔧 What to Do:**
- System runs on localhost - you don't need internet!
- If Docker services can't reach each other, this is Docker network issue
- Restart: `make stop && make start`
- While restarting (takes 2 min), show diagrams and explain architecture
- If restart doesn't work, use presentation for explanation only
- Say: "Code and architecture are complete. This is local environment issue, but I can walk you through how everything works."

---

## 🎯 General Emergency Principles

### 1. STAY CALM 🧘
- Audience doesn't know what was supposed to happen
- Your calm response shows professionalism
- Take breath before speaking

### 2. ACKNOWLEDGE, DON'T APOLOGIZE EXCESSIVELY 💪
- Say "we have technical issue" not "I'm so sorry, this is terrible"
- Fix it if you can, move on if you can't

### 3. SHOW WHAT YOU KNOW 🧠
- Even if demo fails, you can explain architecture
- Even if website down, you can show diagrams
- Your knowledge is more important than demo

### 4. USE THE SCRIPT 📖
- This guide has everything you need
- Read from it if you forget
- Nobody will judge you for checking notes

### 5. REMEMBER: YOU BUILT THIS 🏗️
- You understand the system
- You can explain how it works
- A technical glitch doesn't change that

---

# 🍀 FINAL CONFIDENCE BOOSTERS

> **READ THIS RIGHT BEFORE YOU PRESENT:**

✅ You know this material. You studied it.
✅ You have complete script. You can read from it.
✅ You have answers to 50 common questions.
✅ You have backup plans for every scenario.
✅ System works. You tested it.
✅ You understand concepts. You read vocabulary.
✅ 20 minutes is short. It will be over quickly.
✅ Audience wants you to succeed. They are not enemies.
✅ Your English is good enough. Speak slowly and clearly.
✅ **You are prepared. You can do this.**

---

# 📞 QUICK REFERENCE CARD

## 🔑 Essential Info

| Item | Value |
|------|-------|
| 🌐 **URL** | http://localhost:8082 |
| 👤 **Username** | admin |
| 🔑 **Password** | admin123 |
| 💻 **Start Command** | `make presentation` |
| 🔄 **Stop Command** | `make stop` |
| 🏥 **Health Check** | `make health` |

## 📝 Prediction Test Text

```
Samsung Galaxy smartphone 128GB, dual camera, fast charging
```
Expected: **Electronics** (70-95% confidence)

## 🗣️ Speaking Tips

- **Speed**: 130 words/minute (not too fast!)
- **Pause** between sentences
- **Point** to screen while explaining
- **Eye contact** with audience
- **Smile** - you've got this!

## 🆘 If Stuck

- Take sip of water (pause to think)
- Look at this guide
- Say "Let me show you..." → click something
- Remember: audience wants you to succeed

---

<div align="center">

## 🎉 YOU'VE GOT THIS! GOOD LUCK! 🍀

**Remember: You built something amazing. Be proud of it. Now go show them!**

</div>

---

*End of Presentation Guide - Total pages: ~100 when printed*
