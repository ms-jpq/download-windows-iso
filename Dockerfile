FROM mcr.microsoft.com/playwright/python:latest

COPY ./requirements.txt /
RUN pip3 install --no-cache-dir --requirement /requirements.txt && \
    playwright install

COPY ./scripts/ /srv/
ENTRYPOINT [ "python3", "-m", "srv" ]
CMD [ "--language", "English" ]
