FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
RUN mkdir -p /logs
EXPOSE 5001
CMD ["python", "gateway.py"]
