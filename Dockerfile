FROM ubuntu:20.04
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -qq -y update \
    && apt-get -q -y dist-upgrade \
    && apt-get -q -y install locales libreoffice libreoffice-writer curl \
        libreoffice-impress libreoffice-common fonts-opensymbol hyphen-fr hyphen-de \
        hyphen-en-us hyphen-it hyphen-ru fonts-dejavu fonts-dejavu-core fonts-dejavu-extra \
        fonts-droid-fallback fonts-dustin fonts-f500 fonts-fanwood fonts-freefont-ttf \
        fonts-liberation fonts-lmodern fonts-lyx fonts-sil-gentium fonts-texgyre \
        fonts-tlwg-purisa python3-pip python3-uno python3-lxml python3-icu unoconv \
    && apt-get -qq -y autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

ENV LANG='en_US.UTF-8'

# RUN echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections
# RUN apt-get -q -y install ttf-mscorefonts-installer

RUN groupadd -g 1000 -r app \
    && useradd -m -u 1000 -s /bin/false -g app app

RUN ln -s /usr/bin/python3 /usr/bin/python
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -q -r /tmp/requirements.txt
RUN mkdir -p /convert
COPY setup.py /convert
COPY convert /convert/convert
WORKDIR /convert
RUN pip3 install -q -e .

USER app

HEALTHCHECK --interval=5s --timeout=7s --retries=100 \
  CMD curl -f http://localhost:3000/healthz || exit 1

CMD ["gunicorn", \
     "--threads", "3", \
     "--bind", "0.0.0.0:3000", \
     # "--max-requests", "100", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--timeout", "600", \
     "--graceful-timeout", "500", \
     "convert.app:app"]
