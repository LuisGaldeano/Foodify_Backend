# Get the last python image version and update all the repositories
FROM python:3.11

# Install tools needed for translations
RUN apt-get update && apt-get install -y wget make gettext bzip2 ffmpeg libsm6 libxext6 libxtst6 libgtk-3-0  \
    libx11-xcb-dev libdbus-glib-1-2 libxt6 libpci-dev zbar-tools && apt-get clean

RUN apt-get autoclean

# Prepare work directory
RUN mkdir -p /foodify
WORKDIR /foodify

# Install dockerize to avoid startup problems (waiting for DB to start)
ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz -O - | tar -C /usr/local/bin -xzv

# Load source code from the repository or local to the container
COPY foodify/ /foodify/

# Install all the requirements
RUN pip install poetry==1.6.1
RUN poetry config virtualenvs.create false && poetry install

# Add terminal colors
COPY docker/.bashrc /root/.bashrc

## Prepare the CMD command with the script to be run at the begining of the deploy
RUN mkdir -p /scripts
COPY docker/post_deploy.sh /scripts/post_deploy.sh

CMD /scripts/post_deploy.sh
