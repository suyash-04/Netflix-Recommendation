FROM python:3.11-slim-buster 
WORKDIR /app
COPY . /app
COPY main_data.csv /app/main_data.csv

RUN apt update -y 
RUN apt-get update && pip install -r requirements.txt
CMD ["python", "run.py"]