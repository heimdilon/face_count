FROM python:3.7

ADD main.py .

RUN apt-get -y update && \
    apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagic1-dev \
    libavcodec-dev \
    libavformat-dev \
    libboost-add-dev \
    libgtk2.0-dev \
    libjped-dev \
    liblapack-dev \
    libwscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    software-properties-common \
    zip\
    && apt-get clean && rm -rf /tmp/* /var/tmp/* \

RUN cd ~ && \
    mkdir -p dlib && \
    git clone -b 'v19.7' --single-branch https://github.com/davisking/dlib.git dlib/ && \
    cd dlib/ && \
    python3 setup.py install --yes USE_AVX_INSTRUCTIONS


COPY requirments.txt .

RUN pip install -r requirments.txt

CMD [ "python", "./main.py" ]




