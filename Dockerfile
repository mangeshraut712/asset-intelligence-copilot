FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# public sample dataset baked in; mount more data at /data/extra and set DATA_DIRS to add the test set
RUN git clone --depth 1 https://github.com/FlytBaseAILabs/flytbase-ahc-swe-asset-intelligence-dataset /data/ds && mv /data/ds/sample-data /data/sample-data && rm -rf /data/ds
COPY . .
ENV PORT=8765 AIC_TODAY=2026-10-17 DATA_DIRS=/data/sample-data
EXPOSE 8765
CMD ["sh", "scripts/start.sh"]
