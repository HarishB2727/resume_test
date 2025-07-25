# Use an official Python image for amd64
FROM --platform=linux/amd64 python:3.11-slim-bullseye

# Install system dependencies for lxml and tectonic
RUN apt-get update && \
    apt-get install -y gcc libxml2-dev libxslt1-dev curl wget ca-certificates libgraphite2-3 libssl1.1 && \
    wget https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.13.0/tectonic-0.13.0-x86_64-unknown-linux-gnu.tar.gz && \
    tar -xzf tectonic-0.13.0-x86_64-unknown-linux-gnu.tar.gz && \
    mv tectonic /usr/local/bin/tectonic && \
    chmod +x /usr/local/bin/tectonic && \
    rm tectonic-0.13.0-x86_64-unknown-linux-gnu.tar.gz && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose port
EXPOSE 8000

# Start the app
CMD ["uvicorn", "main1:app", "--host", "0.0.0.0", "--port", "8000"]