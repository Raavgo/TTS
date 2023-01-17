FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu20.04

#Setup base image and update the
RUN apt-get update && apt-get upgrade -y
RUN apt-get update &&\
    apt-get install -y wget &&\
    #libsox-fmt-all &&\
    #sox &&\
    rm -rf /var/lib/apt/lists/*

ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda

ENV PATH=$CONDA_DIR/bin:$PATH

COPY environment.yml .
RUN conda env create -f environment.yml
RUN pip install stt \
    && pip install sox\
    && pip install flask\
    && pip install tts
RUN apt-get update &&\
    apt-get install -y sox &&\
    apt-get install -y ffmpeg &&\
    apt-get install -y espeak
SHELL ["conda", "run", "-n", "myenv", "/bin/bash", "-c"]

COPY lang_config/ /lang_config/
COPY src/ .


ENTRYPOINT [ "python", "app.py" ]
