FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apk add -u zlib-dev jpeg-dev gcc musl-dev

COPY . .

RUN python3 -m pip install --upgrade pip && pip install -r requirements.txt

CMD ["python", "src/pdf_to_text.py"]
