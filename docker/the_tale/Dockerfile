FROM the-tale/tt-base:latest AS tt-service-base

########################################
# required for development environment
# TODO: remove in production environment?
USER root
RUN apt-get install -y node-less
USER $TT_USER
########################################

ARG TT_PACKAGE=the_tale
ARG TT_USER=tt_service

COPY --chown=$TT_USER ./docker/the_tale/bin/* $HOME_BIN

RUN mkdir -p $TT_REPOSITORY/src/tt_protocol/tt_protocol \
    mkdir -p $TT_REPOSITORY/src/tt_logic/tt_logic \
    mkdir -p $TT_REPOSITORY/src/tt_calendar/tt_calendar \
    $TT_REPOSITORY/src/$TT_PACKAGE/$TT_PACKAGE && \

    touch $TT_REPOSITORY/src/tt_protocol/tt_protocol/__init__.py \
    touch $TT_REPOSITORY/src/tt_logic/tt_logic/__init__.py \
    touch $TT_REPOSITORY/src/tt_calendar/tt_calendar/__init__.py \
    $TT_REPOSITORY/src/$TT_PACKAGE/$TT_PACKAGE/__init__.py

COPY --chown=$TT_USER ./src/tt_protocol/pyproject.toml $TT_REPOSITORY/src/tt_protocol/
COPY --chown=$TT_USER ./src/tt_logic/pyproject.toml $TT_REPOSITORY/src/tt_logic/
COPY --chown=$TT_USER ./src/tt_calendar/pyproject.toml $TT_REPOSITORY/src/tt_calendar/
COPY --chown=$TT_USER ./src/$TT_PACKAGE/pyproject.toml ./src/$TT_PACKAGE/poetry.lock $TT_REPOSITORY/src/$TT_PACKAGE/

RUN . $TT_VENV/bin/activate && cd $TT_REPOSITORY/src/$TT_PACKAGE && poetry install

ENV TT_PACKAGE="$TT_PACKAGE"
