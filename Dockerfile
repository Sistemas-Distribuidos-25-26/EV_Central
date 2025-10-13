FROM python:3.12
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
EXPOSE 5001
CMD ["python3", "app/__init__.py", "5000", "127.0.0.1", "5000"]
