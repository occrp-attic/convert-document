FROM ubuntu:bionic
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -qq -y update \
    && apt-get -qq -y install libreoffice libreoffice-writer ure libreoffice-java-common \
        libreoffice-core libreoffice-common openjdk-8-jre fonts-opensymbol \
        hyphen-fr hyphen-de hyphen-en-us hyphen-it hyphen-ru fonts-dejavu \
        fonts-dejavu-core fonts-dejavu-extra fonts-droid-fallback fonts-dustin \
        fonts-f500 fonts-fanwood fonts-freefont-ttf fonts-liberation fonts-lmodern \
        fonts-lyx fonts-sil-gentium fonts-texgyre fonts-tlwg-purisa python3-pip \
        python3-uno python3-lxml libicu-dev \
    && apt-get -qq -y autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip3 install aiohttp \
                 celestial>=0.2.3 \
                 pyicu>=2.0.3
RUN mkdir -p /unoservice
COPY setup.py /unoservice
COPY unoservice /unoservice/unoservice
WORKDIR /unoservice
RUN pip3 install -e . 

CMD ["python3", "unoservice/async.py"]