FROM python:3.10 as deps

RUN apt-get update && apt-get -y install libpcsclite-dev swig

ENV PATH="/venv/bin:$PATH"
WORKDIR /app
RUN python -m venv /venv
RUN pip install poetry
RUN pip install virtualenv
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
