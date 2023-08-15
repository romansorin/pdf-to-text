FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add -u zlib-dev jpeg-dev gcc musl-dev
# TODO: move reqs to setup.py/requirements.txt
RUN python3 -m pip install --upgrade pip && pip install pdf2image==1.16.0 Pillow==8.3.1 pytesseract==0.3.8

WORKDIR /app

COPY . .

CMD ["python", "run_script.py"]