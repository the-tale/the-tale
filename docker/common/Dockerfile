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

RUN pip install --user -r ./requirements.txt

# Use virtual environment, since poetry can not detect packages, installed outside environments,
# and always reinstalls reinstalls them, even if their version did not changed

RUN python -m venv $TT_VENV

ENTRYPOINT ["entrypoint.sh"]
