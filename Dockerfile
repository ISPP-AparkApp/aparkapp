FROM python:3.10
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
COPY /aparkapp/initial_data.json /code/
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY /aparkapp/ /code/
RUN rm aparkapp/settings.py
COPY docker-settings.py aparkapp/settings.py
COPY .env /code/