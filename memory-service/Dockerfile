FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
EXPOSE 5003
# CORRECTED STARTUP COMMAND:
CMD ["flask", "--app", "src/main", "run", "--host=0.0.0.0", "--port=5003"]
