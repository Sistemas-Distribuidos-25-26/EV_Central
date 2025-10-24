FROM python:3.12
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 10000

ENTRYPOINT ["python3", "app/__init__.py"]
CMD ["10001", "127.0.0.1", "9092"]
