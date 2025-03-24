# Usa un'immagine di Node.js come base
FROM node:16-slim

# Installa dipendenze necessarie
RUN apt-get update && apt-get install -y wget gnupg --no-install-recommends && \
    apt-get install -y chromium && \
    apt-get clean && rm -rf /var/lib/apt/lists/*;

# Imposta variabili d'ambiente per Puppeteer
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Crea la directory di lavoro
WORKDIR /usr/src/app

# Copia il package.json e installa le dipendenze
COPY package.json ./
RUN npm install

# Copia il resto dei file dell'applicazione
COPY . .

# Rendi eseguibile lo script di avvio
RUN chmod +x start.sh

# Comando di avvio
CMD ["./start.sh"]