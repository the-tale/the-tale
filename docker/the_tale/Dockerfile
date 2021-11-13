ARG_TT_BASE_VERSION

FROM the-tale/tt-base:$TT_BASE_VERSION

ARG TT_PACKAGE=the_tale
ARG TT_USER=tt_service

########################################
# required for development environment
# TODO: remove in production environment?
USER root
RUN apt-get install -y node-less
USER $TT_USER
########################################

COPY --chown=$TT_USER ./docker/the_tale/bin/* $HOME_BIN

RUN . $TT_VENV/bin/activate && \
    cd $TT_REPOSITORY/src/$TT_PACKAGE && poetry install

ENV TT_PACKAGE="$TT_PACKAGE"
