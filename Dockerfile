FROM python:latest
MAINTAINER Christoph Coijanovic <hi@coijanovic.com>

WORKDIR /code

COPY main.py /code
COPY genbench.py /code

COPY requirements.txt .
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
