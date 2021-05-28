FROM testcab/yay
RUN sudo pacman -Sy --noconfirm
RUN yay --save --answerclean None --answerdiff None
RUN yay --save --nocleanmenu --nodiffmenu
#Force exit code of 0 because yay doesn't like to cooperate.
RUN yay -S python36 || :
RUN sudo pacman -S --noconfirm postgresql

#Create a working directory
WORKDIR /usr/src/augur
COPY ./augur/ augur/
COPY ./metadata.py .
COPY ./setup.py .
COPY ./scripts/ scripts/
COPY ./workers/ workers/

RUN pip install .
RUN ./scripts/install/workers.sh

COPY ./util/docker/backend/backend.docker.config.json .
RUN augur config init --rc-config-file backend.docker.config.json; mkdir repos/;

CMD augur db update-api-key docker_key; augur backend start