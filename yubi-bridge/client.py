import collections
import logging

import grpc

from worker.worker_pb2 import JobStatus, Worker
from worker.worker_pb2_grpc import WorkerServiceStub


class _ClientCallDetails(
    collections.namedtuple(
        "_ClientCallDetails", ("method", "timeout", "metadata", "credentials")
    ),
    grpc.ClientCallDetails,
):
    pass


class WorkerTokenInterceptor(grpc.UnaryUnaryClientInterceptor):
    """Inject secret token to authenticate the worker."""

    def __init__(self, secret: str):
        self.secret = secret

    def intercept_unary_unary(self, continuation, client_call_details, request):
        new_details = self.inject_token(client_call_details)
        response = continuation(new_details, request)
        return response

    def inject_token(self, client_call_details):
        if client_call_details.metadata is None:
            metadata = []
        else:
            metadata = list(client_call_details.metadata)
        metadata.append(
            (
                "authorization",
                self.secret,
            )
        )
        client_call_details = _ClientCallDetails(
            client_call_details.method,
            client_call_details.timeout,
            metadata,
            client_call_details.credentials,
        )
        return client_call_details


class WorkerHandler:
    """Handle communication with gRPC server."""

    def __init__(self, worker_id: str, address: str, secret: str, secure=False):
        if secure:
            channel_credential = grpc.ssl_channel_credentials()
            channel = grpc.secure_channel(address, channel_credential)
        else:
            channel = grpc.insecure_channel(address)
        self.channel = grpc.intercept_channel(channel, WorkerTokenInterceptor(secret))
        self.worker_id = worker_id

    def register(self):
        stub = WorkerServiceStub(self.channel)
        request = Worker(id=self.worker_id)
        logging.debug(request)
        try:
            response = stub.RegisterWorker(request)
            logging.debug(response)
        except grpc.RpcError as err:
            if err.code() != grpc.StatusCode.ALREADY_EXISTS:
                logging.error("Server error: %s %s", err.code(), err.details())

    def get_job(self) -> tuple:
        stub = WorkerServiceStub(self.channel)
        request = Worker(id=self.worker_id)
        try:
            response = stub.GetJob(request)
            return (
                response.first_name,
                response.last_name,
                response.email,
                response.job_id,
            )

        except grpc.RpcError as err:
            if err.code() != grpc.StatusCode.NOT_FOUND:
                logging.error("Server error: %s %s", err.code(), err.details())

        return ()

    def send_job_status(
        self,
        job_id: int,
        success: bool,
        public_key: str,
        ssh_key: str,
        fingerprint: str,
        error: str,
    ):
        stub = WorkerServiceStub(self.channel)
        request = JobStatus(
            id=self.worker_id,
            job_id=job_id,
            success=success,
            public_key=public_key,
            ssh_key=ssh_key,
            fingerprint=fingerprint,
            error=error,
        )
        try:
            stub.SetJobDone(request)
            if success:
                logging.info("Keys sent to DG")
        except grpc.RpcError as err:
            logging.error("Server error: %s %s", err.code(), err.details())
