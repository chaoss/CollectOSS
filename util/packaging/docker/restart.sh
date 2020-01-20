#!/bin/bash
imageName=augur_test
containerName=augur_test

docker build -t $imageName -f util/packaging/docker/Dockerfile  .

echo Delete old container...
docker rm -f $containerName

echo Run new container...
# docker run -d -p 5000:5000 --name $containerName $imageName --env-file env.txt
docker container run --publish 5000:5000 --name $containerName --env-file env.txt $image_name
echo $!
