FROM python:3.11.12-alpine

LABEL org.opencontainers.image.authors="CHAOSS https://chaoss.community"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/chaoss/collectoss"
LABEL org.opencontainers.image.documentation="https://collectoss.readthedocs.io"

ARG VERSION
LABEL org.opencontainers.image.version=${VERSION}
ARG REVISION
LABEL org.opencontainers.image.revision=${REVISION}

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir redis==4.3.3

ENV KEYMAN_DOCKER=1
ENV PYTHONPATH="${PYTHONPATH}:/collectoss"
# Ensure Python output is sent straight to terminal (e.g. for Docker logs)
ENV PYTHONUMBUFFERED=1

WORKDIR /collectoss
COPY ./keyman keyman/
RUN find . -type d -exec chmod u=rwx,go=rx {} + && find . -type f -exec chmod u=rw,go=r {} +


ENTRYPOINT [ "python", "/collectoss/keyman/Orchestrator.py" ]
