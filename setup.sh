# setting up a network for the docker containers  
docker network create --subnet 172.50.0.0/16 --gateway 172.50.0.1 rakuten_network

# building the images:
# the images are build with docker compose

# running docker compose:
# go to /exam_FLEMER and run
docker compose up