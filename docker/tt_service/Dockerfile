FROM the-tale/tt-base:latest AS tt-service-base

# Setup tt_web & tt_protocols
# not ideal solution, since concrete service can require different package version,
# but for most cases it will spedup container builds
# in case of problems with packages versions, child container just install right version, specified in service lock file

RUN mkdir -p $TT_REPOSITORY/src/tt_web/tt_web \
    $TT_REPOSITORY/src/tt_protocol/tt_protocol && \

    touch $TT_REPOSITORY/src/tt_web/tt_web/__init__.py \
    $TT_REPOSITORY/src/tt_protocol/tt_protocol/__init__.py

COPY --chown=$TT_USER ./src/tt_web/pyproject.toml ./src/tt_web/poetry.lock  $TT_REPOSITORY/src/tt_web/
COPY --chown=$TT_USER ./src/tt_protocol/pyproject.toml ./src/tt_protocol/poetry.lock $TT_REPOSITORY/src/tt_protocol/

RUN . $TT_VENV/bin/activate && \
    cd $TT_REPOSITORY/src/tt_web && poetry install && \
    cd $TT_REPOSITORY/src/tt_protocol && poetry install

FROM tt-service-base

ARG TT_SERVICE
ARG TT_PACKAGE

COPY --chown=$TT_USER ./docker/tt_service/bin/* $HOME_BIN

RUN mkdir -p  $TT_REPOSITORY/src/$TT_PACKAGE/$TT_PACKAGE && \
    touch $TT_REPOSITORY/src/$TT_PACKAGE/$TT_PACKAGE/__init__.py

COPY --chown=$TT_USER ./src/$TT_PACKAGE/pyproject.toml ./src/$TT_PACKAGE/poetry.lock $TT_REPOSITORY/src/$TT_PACKAGE/

RUN . $TT_VENV/bin/activate && cd $TT_REPOSITORY/src/$TT_PACKAGE && poetry install

ENV TT_PACKAGE="$TT_PACKAGE" \
    TT_SERVICE="$TT_SERVICE" \
    TT_CONFIG="$HOME/repository/docker/$TT_SERVICE/config.json"
