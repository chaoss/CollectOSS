FROM python:3

RUN mkdir /ghdata
WORKDIR /ghdata
ADD . /ghdata
RUN pip install --upgrade .

CMD ["ghdata"]