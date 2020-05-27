FROM debian:buster-slim

# Install some prerequisites needed for the
# python requirements
RUN apt-get update && apt-get -y install --no-install-recommends \
    python3 \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-dev \

# Install the requirements in it's own layer
# When they are changed, this layer and all
# after it are rebuilt
COPY requirements /
RUN pip3 install -r requirements

# Copy entrypoint (Start docker command)
COPY docker/entrypoint.sh /srv/

# Copy source file
COPY src /srv/

# Set the working directory
WORKDIR /srv

# Default command
CMD /bin/sh entrypoint.sh
