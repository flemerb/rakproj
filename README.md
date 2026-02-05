
## New Environment setup

#### in the terminal run the following to set up a new uv environment:
`uv venv --python 3.11 .venv_rakuten`  

#### activate the environment
`source .venv_rakuten/bin/activate`  

#### install requirements
```
uv pip install --upgrade pip  
uv pip install -r requirements.txt  
```

#### get raw data (csv files)  
```
python src/data/import_raw_data.py
```  

- then download data from https://challengedata.ens.fr/participants/challenges/35/  
- save the images in 'raw/image_test' and 'raw/image_train'  

#### preprocess the data
```
python src/data/make_dataset.py data/raw data/preprocessed
```

#### train the text model
```
python src/main.py
```

### changes compared to the original version

In `src/models/train_model.py`, line 203 I commented out `new_y_train = new_y_train.values.reshape(1350).astype("int")` because of 
`ValueError: cannot reshape array of size 2700 into shape (1350,)`. I think this was due to dataframe/array coversion issues, but it seemed to work without it anyways. 

In `src/main.py` line 29 and following (i. e. training the image and the concatenate model) were removed. A new file `src/main_with_image_and_concatenate_model.py` with the original contents of `main.py` was created to be able to go back to it later.  





Project Name
==============================

This project is a starting Pack for MLOps projects based on the subject "movie_recommandation". It's not perfect so feel free to make some modifications on it.

Project Organization
------------

    ├── LICENSE
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources -> the external data you want to make a prediction on
    │   ├── preprocessed      <- The final, canonical data sets for modeling.
    |   |  ├── image_train <- Where you put the images of the train set
    |   |  ├── image_test <- Where you put the images of the predict set
    |   |  ├── X_train_update.csv    <- The csv file with te columns designation, description, productid, imageid like in X_train_update.csv
    |   |  ├── X_test_update.csv    <- The csv file with te columns designation, description, productid, imageid like in X_train_update.csv
    │   └── raw            <- The original, immutable data dump.
    |   |  ├── image_train <- Where you put the images of the train set
    |   |  ├── image_test <- Where you put the images of the predict set
    │
    ├── logs               <- Logs from training and predicting
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   ├── main.py        <- Scripts to train models 
    │   ├── predict.py     <- Scripts to use trained models to make prediction on the files put in ../data/preprocessed
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   ├── check_structure.py    
    │   │   ├── import_raw_data.py 
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models                
    │   │   └── train_model.py
    │   └── config         <- Describe the parameters used in train_model.py and predict_model.py

--------

Once you have downloaded the github repo, open the anaconda powershell on the root of the project and follow those instructions :

> `conda create -n "Rakuten-project"`    <- It will create your conda environement

> `conda activate Rakuten-project`       <- It will activate your environment

> `conda install pip`                    <- May be optionnal

> `pip install -r requirements.txt`      <- It will install the required packages

> `python src/data/import_raw_data.py`   <- It will import the tabular data on data/raw/

> Upload the image data folder set directly on local from https://challengedata.ens.fr/participants/challenges/35/, you should save the folders image_train and image_test respecting the following structure

    ├── data
    │   └── raw           
    |   |  ├── image_train 
    |   |  ├── image_test 

> `python src/data/make_dataset.py data/raw data/preprocessed`      <- It will copy the raw dataset and paste it on data/preprocessed/

> `python src/main.py`                   <- It will train the models on the dataset and save them in models. By default, the number of epochs = 1

> `python src/predict.py`                <- It will use the trained models to make a prediction (of the prdtypecode) on the desired data, by default, it will predict on the train. You can pass the path to data and images as arguments if you want to change it
>
    Exemple : python src/predict_1.py --dataset_path "data/preprocessed/X_test_update.csv" --images_path "data/preprocessed/image_test"
                                        
                                         The predictions are saved in data/preprocessed as 'predictions.json'

> You can download the trained models loaded here : https://drive.google.com/drive/folders/1fjWd-NKTE-RZxYOOElrkTdOw2fGftf5M?usp=drive_link and insert them in the models folder
> 
<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
python make_dataset.py "../../data/raw" "../../data/preprocessed"
