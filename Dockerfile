FROM ubuntu:artful
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -qq -y update \
    && apt-get -qq -y install apt-utils \
    && apt-get -qq -y upgrade

RUN apt-get -qq -y install libreoffice unoconv nodejs npm \
    && apt-get -qq -y autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir -p /app
WORKDIR /app
ADD package.json /app
RUN npm install
ADD execute.sh index.js /app/
EXPOSE 3000
CMD ["/app/execute.sh"]