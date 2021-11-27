ARG TT_BASE_IMAGE_VERSION
ARG TT_CONTAINERS_REGISTRY

FROM $TT_CONTAINERS_REGISTRY/the-tale/tt-base:$TT_BASE_IMAGE_VERSION

ARG TT_PACKAGE=the_tale
ARG TT_USER=tt_service
ARG TT_SITE_STATIC_DIR

########################################
USER root
RUN apt-get install -y node-less

RUN mkdir -p $TT_SITE_STATIC_DIR && \
    chown $TT_USER $TT_SITE_STATIC_DIR

USER $TT_USER
########################################

COPY --chown=$TT_USER ./docker/the_tale/bin/* $HOME_BIN

RUN . $TT_VENV/bin/activate && \
    cd $TT_REPOSITORY/src/$TT_PACKAGE && poetry install

ENV TT_PACKAGE="$TT_PACKAGE"
