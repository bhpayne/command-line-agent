# Get the machine architecture.
# On arm64 (Apple Silicon M1/M2/etc.), `uname -m` outputs "arm64".
# On amd64 (Intel), `uname -m` outputs "x86_64".
ARCH := $(shell uname -m)

ifeq ($(ARCH), arm64)
        this_arch=arm64
else ifeq ($(ARCH), x86_64)
        this_arch=amd64
else
        @echo "Unknown architecture: $(ARCH). Cannot determine if Mac is new (arm64) or old (amd64)."
endif

IMAGE_NAME=agent_container

CONTAINER_TAG=latest-$(this_arch)

DOCKER_OR_PODMAN=docker
#DOCKER_OR_PODMAN=podman

container_build:
	$(DOCKER_OR_PODMAN) build -t $(IMAGE_NAME):$(CONTAINER_TAG) .

container_live:
	$(DOCKER_OR_PODMAN) run -it --rm \
                -v `pwd`:/scratch -w /scratch/ \
                --user $(id -u):$(id -g) \
                $(IMAGE_NAME):$(CONTAINER_TAG) /bin/bash

black_out:
	$(DOCKER_OR_PODMAN) run --rm -v`pwd`:/scratch --entrypoint='' --workdir /scratch/ $(IMAGE_NAME):$(CONTAINER_TAG) make black_in

black_in:
	black -v --workers 1 *.py

mypy_out:
	$(DOCKER_OR_PODMAN) run --rm -v`pwd`:/scratch --entrypoint='' --workdir /scratch/ $(IMAGE_NAME):$(CONTAINER_TAG) mypy --install-types --non-interactive --check-untyped-defs webserver_for_pdg/pdg_app.py webserver_for_pdg/library

