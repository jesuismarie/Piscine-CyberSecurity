#!/bin/bash

docker-compose down
docker volume rm ft_onion_tor-hidden-service
docker rmi my_onion_tor my_onion_nginx
docker builder prune -f