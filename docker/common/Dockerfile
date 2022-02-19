FROM python:3.10-bullseye

ARG TT_USER=tt_service

RUN apt-get update && apt-get install wait-for-it

RUN useradd -m $TT_USER

USER $TT_USER

ENV HOME="/home/$TT_USER"

ENV HOME_BIN="$HOME/.local/bin/" \
    TT_REPOSITORY="$HOME/repository" \
    TT_VENV="$HOME/venv"

ENV PATH="$PATH:$HOME_BIN"

WORKDIR $HOME

RUN mkdir -p $TT_REPOSITORY

COPY --chown=$TT_USER ./docker/common/bin/* $HOME_BIN

COPY --chown=$TT_USER ./docker/common/requirements.txt $HOME

# Use virtual environment, since poetry can not detect packages, installed outside environments,
# and always reinstalls them, even if their version did not changed

RUN python -m pip install --upgrade pip

RUN python -m venv $TT_VENV

RUN . $TT_VENV/bin/activate && pip install -r ./requirements.txt

# Copy actual code to container
# It will be runing in production
# In development environment it will be replaced by mounted volume
COPY --chown=$TT_USER ./src  $TT_REPOSITORY/src

# Setup tt_web & tt_protocols
# not ideal solution, since concrete service can require different package version,
# but for most cases it will spedup container builds
# in case of problems with packages versions, child container could install right version, specified in service lock file

RUN . $TT_VENV/bin/activate && \
    cd $TT_REPOSITORY/src/tt_web && poetry install && \
    cd $TT_REPOSITORY/src/tt_protocol && poetry install

ENTRYPOINT ["entrypoint.sh"]
