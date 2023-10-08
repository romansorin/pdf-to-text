FROM python:3.8-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apk add -u zlib-dev jpeg-dev gcc musl-dev poppler-utils tesseract-ocr tesseract-ocr-dev

RUN wget https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata -O /usr/share/tessdata/eng.traineddata

COPY . .

RUN python3 -m pip install --upgrade pip && pip install -r requirements.txt

ENTRYPOINT ["python", "src/pdf_to_text.py"]
