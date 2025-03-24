FROM python:3.12.4

WORKDIR /app
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD [ "python3","-u", "/app/client.py" ]