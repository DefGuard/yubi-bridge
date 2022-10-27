FROM python:3.10

RUN apt-get update && apt-get -y install libpcsclite-dev swig

ENV PATH="/venv/bin:$PATH"
WORKDIR /app
RUN python -m venv /venv
RUN pip install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction

FROM python:3.10-slim

RUN apt-get update && apt-get -y install pcscd scdaemon gnupg

ENV PATH="/venv/bin:$PATH"
WORKDIR /app
COPY --from=0  /venv /venv
COPY entrypoint.sh ./entrypoint.sh
COPY proto ./proto
COPY yubi-bridge ./yubi-bridge
RUN python3 -m grpc_tools.protoc -Iproto \
		--python_out=yubi-bridge --grpc_python_out=yubi-bridge \
		proto/worker/worker.proto

ENTRYPOINT ["./entrypoint.sh"]
