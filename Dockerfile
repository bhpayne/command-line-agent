


# https://hub.docker.com/_/rockylinux/tags
FROM rockylinux:9.3

ENV PYTHONUNBUFFERED=1

# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disk (equivalent to python -B option)
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /opt

COPY src/ .

RUN dnf install -y python3 python3-pip

COPY requirements.txt requirements.txt 
RUN pip install -r requirements.txt --no-cache-dir -vvv

