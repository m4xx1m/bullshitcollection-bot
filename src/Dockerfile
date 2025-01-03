FROM python:3.12.4-alpine3.20

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

COPY . .

CMD ["python", "-m", "app"]
