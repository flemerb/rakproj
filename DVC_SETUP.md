# DVC Setup Guide - Rakuten MLOps Project

## What is DVC?

DVC (Data Version Control) is a version control system for machine learning projects. It helps you:

1. **Track Data**: Version your datasets like code
2. **Track Models**: Store and version trained models
3. **Pipelines**: Define and run ML pipelines
4. **Experiments**: Manage different experiments

---

## Installation

DVC is already installed via pip. To verify:

```bash
cd ~/rakproj
source .venv_rakuten/bin/activate
dvc version
```

---

## Project Structure

```
rakproj/
├── .dvc/                  # DVC internal directory
├── .dvcignore            # Files to ignore
├── dvc.yaml              # Pipeline definition
├── params.yaml           # Parameters
├── data/
│   ├── raw/              # Raw data (tracked by DVC)
│   └── preprocessed/     # Processed data (tracked by DVC)
└── models/               # Trained models (tracked by DVC)
```

---

## DVC Pipeline

The pipeline is defined in `dvc.yaml`:

```yaml
stages:
  data_import:
    cmd: python src/data/import_raw_data.py
    deps:
      - src/data/import_raw_data.py
    outs:
      - data/raw
  
  preprocess:
    cmd: python src/data/make_dataset.py data/raw data/preprocessed
    deps:
      - src/data/make_dataset.py
      - data/raw
    outs:
      - data/preprocessed
  
  train:
    cmd: python src/main.py
    deps:
      - src/main.py
      - src/models/train_model.py
      - data/preprocessed
    params:
      - train.epochs
      - train.batch_size
    outs:
      - models/best_lstm_model.h5
```

---

## Common Commands

### Initialize DVC

```bash
dvc init
```

### Run the pipeline

```bash
dvc repro
```

### Track data files

```bash
dvc add data/raw
dvc add models/best_lstm_model.h5
```

### Set up remote storage

```bash
# Local remote
dvc remote add -d myremote /path/to/storage

# Or S3 remote
dvc remote add -d myremote s3://my-bucket/dvc-storage
```

### Push data to remote

```bash
dvc push
```

### Pull data from remote

```bash
dvc pull
```

### View pipeline status

```bash
dvc status
```

### View pipeline DAG

```bash
dvc dag
```

---

## Parameters

Parameters are defined in `params.yaml`:

```yaml
train:
  epochs: 10
  batch_size: 32
  max_words: 10000
  max_sequence_length: 10
```

Use in code:

```python
import yaml

with open("params.yaml", "r") as f:
    params = yaml.safe_load(f)

epochs = params["train"]["epochs"]
batch_size = params["train"]["batch_size"]
```

---

## Integration with Git

DVC works alongside Git:

1. Git tracks: code, configs, small files
2. DVC tracks: data, models, large files

Workflow:

```bash
# 1. Make changes to code
git add src/main.py
git commit -m "Update training code"

# 2. Track data with DVC
dvc add data/raw
git add data/raw.dvc .gitignore

# 3. Commit DVC changes
git commit -m "Track raw data"

# 4. Push to remotes
git push
dvc push
```

---

## Completed Tasks

- [x] Install DVC
- [x] Initialize DVC repository
- [x] Create dvc.yaml pipeline
- [x] Create params.yaml
- [x] Create .dvcignore

---

## Next Steps

1. Set up remote storage
2. Run the pipeline with `dvc repro`
3. Track experiments with DVC + MLflow

---

## Useful Links

- [DVC Documentation](https://dvc.org/doc)
- [DVC Pipeline](https://dvc.org/doc/user-guide/project-structure/pipelines)
- [DVC with MLflow](https://dvc.org/doc/use-cases/versioning-data-and-model-files)
