
# create a python image
# ===============
FROM python:3.11.14-alpine3.23

# install requirements 
# ===============
RUN pip install requirements.txt

# add script (/src/main.py)
# =============================
ADD /src/main.py /scripts/main.py

# change working directory inside the image to /scripts/ 
# =========================================
# WORKDIR /scripts/  

# Specifying an entry point
# =========================================
CMD python3 /scripts/main.py
