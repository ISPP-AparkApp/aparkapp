FROM python:3.10
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY /aparkapp/ /code/
RUN rm aparkapp/settings.py
ADD docker-settings.py aparkapp/settings.py