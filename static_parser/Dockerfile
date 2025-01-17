FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY parse_static_gtfs.py .
COPY gtfs_subway.zip .
COPY gtfs_supplemented.zip .

RUN apt-get update && apt-get install -y unzip
RUN unzip gtfs_subway.zip -d gtfs_subway
RUN unzip gtfs_supplemented.zip -d gtfs_supplemented

CMD ["python", "parse_static_gtfs.py"]