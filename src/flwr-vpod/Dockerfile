FROM python:3.12.4


WORKDIR /app
COPY ./src .

ENV VIRTUALPOD_OUTGOING_URL=http://flwr-cec-kleint-gateway:11355

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD [ "python3","-u", "/app/main.py" ]