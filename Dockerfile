FROM tiangolo/uwsgi-nginx-flask:python3.7-alpine3.7

RUN apk --update add bash nano && \
    apt-get install -y tesseract-ocr libtesseract-dev

ENV STATIC_URL /static
ENV STATIC_PATH /static
ENV FLASK_APP application
ENV FLASK_RUN_PORT 8080
ENV MAX_CONTENT_LENGTH 16*1024*1024
ENV TEMPLATES_AUTO_RELOAD true
ENV DEBUG_TB_INTERCEPT_REDIRECTS false
RUN pip install -r requirements.txt