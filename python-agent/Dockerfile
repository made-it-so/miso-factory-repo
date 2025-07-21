FROM python:3.11-slim
# Install dependencies for gcloud SDK
RUN apt-get update && apt-get install -y curl gnupg
# Add the gcloud CLI to PATH
ENV PATH /usr/lib/google-cloud-sdk/bin:$PATH
# Download and install the Google Cloud SDK
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    apt-get update -y && apt-get install google-cloud-sdk -y
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
EXPOSE 5002
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5002", "src.main:app"]
