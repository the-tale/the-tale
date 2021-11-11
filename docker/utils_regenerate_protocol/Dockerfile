FROM the-tale/tt-base:latest AS tt-service-base

# Setup tt_protocols
# not ideal solution, since concrete service can require different package version,
# but for most cases it will spedup container builds
# in case of problems with packages versions, child container just install right version, specified in service lock file

########################################
USER root
RUN apt-get install -y protobuf-compiler
USER $TT_USER
########################################

RUN mkdir -p $TT_REPOSITORY/src/tt_protocol/tt_protocol && \
    touch $TT_REPOSITORY/src/tt_protocol/tt_protocol/__init__.py

COPY --chown=$TT_USER ./src/tt_protocol/pyproject.toml ./src/tt_protocol/poetry.lock $TT_REPOSITORY/src/tt_protocol/

RUN . $TT_VENV/bin/activate && \
    cd $TT_REPOSITORY/src/tt_protocol && poetry install
