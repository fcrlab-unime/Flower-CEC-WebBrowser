FROM jupyter/tensorflow-notebook

WORKDIR /app
COPY ./src .

ENV VIRTUALPOD_OUTGOING_URL=http://flwr-cec-kleint-gateway:11355

# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     cmake \
#     git \
#     wget \
#     libssl-dev \
#     && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
#RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt
#RUN pip install tensorflow

CMD [ "python3","-u", "/app/main.py" ]