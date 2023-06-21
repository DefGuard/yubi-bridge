FROM --platform=$TARGETPLATFORM python:3.11.4-slim AS deps
ARG TARGETPLATFORM
ARG BUILDPLATFORM
RUN echo " => Running on build platform: $BUILDPLATFORM, building for [ $TARGETPLATFORM ]"

RUN apt-get update && \
    apt-get -y install --no-install-recommends libpcsclite-dev swig pcscd build-essential gpg gpgconf && \
    apt-get autoremove -y && \
    apt-get purge -y --auto-remove && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/venv/bin:$PATH"
WORKDIR /app
RUN python3 -m venv /venv
RUN pip install poetry virtualenv
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction

FROM deps as builder

ENV PATH="/venv/bin:$PATH"
WORKDIR /app
COPY --from=deps  /venv /venv
COPY entrypoint.sh ./entrypoint.sh
COPY proto ./proto
COPY yubi-bridge ./yubi-bridge
RUN python3 -m grpc_tools.protoc -Iproto \
		--python_out=yubi-bridge --grpc_python_out=yubi-bridge \
		proto/worker/worker.proto

ENTRYPOINT ["./entrypoint.sh"]
