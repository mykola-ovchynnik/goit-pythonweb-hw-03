FROM python:3.12

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

VOLUME /app/storage

EXPOSE 3000

CMD ["python", "main.py"]