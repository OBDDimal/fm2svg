FROM python:3 AS builder

ENV FIREFOX_VER 87.0

WORKDIR /app

RUN apt-get update && apt-get install -y firefox-esr xvfb

RUN pip install selenium

RUN apt-get install -y xvfb xauth


#RUN set -x \
#    && apt-get update \
#    && apt-get install -y \
#    python3 python3-pip \
#    fonts-liberation libasound2 libatk-bridge2.0-0 \
#    libnspr4 libnss3 lsb-release xdg-utils libxss1 libdbus-glib-1-2 libcups2 \
#    libgtk-3-dev unzip \
#    curl unzip wget dumb-init nano libgbm1 libre2-dev \
#    xvfb \
#    expect openvpn openvpn-systemd-resolved
#
#RUN set -x \
#   && apt update \
#   && apt upgrade -y \
#   && apt install -y \
#       firefox-esr \
#   && pip install  \
#       requests \
#       selenium
#
## Add latest FireFox
#RUN set -x \
#   && apt install -y \
#       libx11-xcb1 \
#       libdbus-glib-1-2 \
#   && curl -sSLO https://download-installer.cdn.mozilla.net/pub/firefox/releases/${FIREFOX_VER}/linux-x86_64/en-US/firefox-${FIREFOX_VER}.tar.bz2 \
#   && tar -jxf firefox-* \
#   && mv firefox /opt/ \
#   && chmod 755 /opt/firefox \
#   && chmod 755 /opt/firefox/firefox

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# TODO setup wsgi
CMD [ "flask", "run", "--host", "0.0.0.0", "--port", "5000", "--debug"]