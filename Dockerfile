FROM python:3

# Copy the repo
COPY ./ /ghdata/
RUN rm -rf ghdata/ghdata.cfg && pip install --upgrade ./ghdata

EXPOSE 80

CMD ["ghdata"]