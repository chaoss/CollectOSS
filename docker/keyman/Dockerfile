FROM python:3.11.12-alpine

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir redis==4.3.3

ENV KEYMAN_DOCKER=1
ENV PYTHONPATH="${PYTHONPATH}:/augur"
# Ensure Python output is sent straight to terminal (e.g. for Docker logs)
ENV PYTHONUMBUFFERED=1

WORKDIR /augur
COPY --chmod=u=rw,u+X,go=r,go+X ./keyman keyman/

ENTRYPOINT [ "python", "/augur/keyman/Orchestrator.py" ]
