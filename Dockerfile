FROM ubuntu:bionic
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -qq -y update \
    && apt-get -qq -y install apt-utils \
    && apt-get -qq -y upgrade \
    && apt-get -qq -y install libreoffice libreoffice-writer ure libreoffice-java-common \
        libreoffice-core libreoffice-common openjdk-8-jre fonts-opensymbol \
        hyphen-fr hyphen-de hyphen-en-us hyphen-it hyphen-ru fonts-dejavu \
        fonts-dejavu-core fonts-dejavu-extra fonts-droid-fallback fonts-dustin \
        fonts-f500 fonts-fanwood fonts-freefont-ttf fonts-liberation fonts-lmodern \
        fonts-lyx fonts-sil-gentium fonts-texgyre fonts-tlwg-purisa unoconv nodejs npm

RUN apt-get -qq -y install python3-pip python3-uno
# && apt-get -qq -y autoremove \
# && apt-get clean \
# && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir -p /unoservice
COPY setup.py /unoservice
COPY unoservice /unoservice/unoservice
WORKDIR /unoservice
RUN pip3 install -e . 
# WORKDIR /app
# ADD package.json /app
# RUN npm install
# ADD index.js /app/
# EXPOSE 3000

# CMD ["node", "index.js"]

