FROM python:3.11.12-alpine

RUN pip install --upgrade pip 

RUN pip install redis==4.3.3

ENV KEYMAN_DOCKER=1
ENV PYTHONPATH="${PYTHONPATH}:/augur"

WORKDIR /augur
COPY ./keyman keyman/

ENTRYPOINT [ "python", "/augur/keyman/Orchestrator.py" ]
