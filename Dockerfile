
# https://hub.docker.com/_/rockylinux/tags
FROM rockylinux:9.3

ENV PYTHONUNBUFFERED=1

# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disk (equivalent to python -B option)
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /opt

COPY src/ .

RUN dnf install -y python3 python3-pip git 

COPY requirements.txt requirements.txt 
RUN pip install -r requirements.txt --no-cache-dir -vvv

# To pull github issues from command line, use `gh`; see https://github.com/cli/cli#installation
RUN dnf install 'dnf-command(config-manager)'
RUN dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
# https://github.com/cli/cli/blob/trunk/docs/install_linux.md#fedora-community
RUN dnf install gh -y

# Install the skill (user scope recommended)
RUN gh skill install cli/cli gh --scope user

# Update the skill after a `gh` release
RUN gh skill update gh

# TODO: 'glab' (for gitlab) is not available from dnf
RUN wget https://gitlab.com/gitlab-org/cli/-/releases/v1.106.0/downloads/glab_1.106.0_linux_arm64.rpm

