#!/usr/bin/env python3

import socket
import threading

from testcase.base import TestCase


class NetworkCompatibilityTest(TestCase):
    """Test basic Linux TCP socket operations."""

    def __init__(self):
        super().__init__(
            name="network_compatibility",
            category="network",
            description=(
                "Verify that basic Linux TCP socket creation, "
                "connection, data transfer and cleanup are supported."
            ),
            tags=[
                "network",
                "socket",
                "tcp",
                "compatibility",
            ],
        )

    def execute(self):
        checks = []

        server = None
        client = None
        connection = None

        try:
            # 1. Create TCP server socket
            server = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM,
            )

            server.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1,
            )

            # Use an ephemeral port instead of a fixed port.
            server.bind(
                ("127.0.0.1", 0)
            )

            server.listen(1)
            server.settimeout(5)

            host, port = server.getsockname()

            checks.append({
                "name": "socket_create",
                "status": "PASS",
                "message": (
                    "TCP socket can be created, "
                    "bound and put into listening state."
                ),
                "host": host,
                "port": port,
            })

            # 2. Start server accept thread
            connection_holder = []
            error_holder = []

            def accept_connection():
                try:
                    conn, address = server.accept()
                    connection_holder.append(
                        (conn, address)
                    )
                except Exception as exc:
                    error_holder.append(exc)

            accept_thread = threading.Thread(
                target=accept_connection,
                daemon=True,
            )

            accept_thread.start()

            # 3. Create TCP client
            client = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM,
            )

            client.settimeout(5)

            client.connect(
                ("127.0.0.1", port)
            )

            accept_thread.join(
                timeout=5
            )

            if error_holder:
                raise error_holder[0]

            if not connection_holder:
                return {
                    "status": "FAIL",
                    "message": (
                        "TCP server did not accept "
                        "the client connection."
                    ),
                    "checks": checks,
                }

            connection, address = (
                connection_holder[0]
            )

            connection.settimeout(5)

            checks.append({
                "name": "tcp_connect",
                "status": "PASS",
                "message": (
                    "TCP client can connect "
                    "to the local server."
                ),
                "client_address": list(address),
            })

            # 4. Client -> Server
            request_data = b"network-test-request"

            client.sendall(
                request_data
            )

            received_data = (
                connection.recv(1024)
            )

            if received_data != request_data:
                return {
                    "status": "FAIL",
                    "message": (
                        "TCP server received "
                        "unexpected data."
                    ),
                    "sent": request_data.decode(),
                    "received": received_data.decode(
                        errors="replace"
                    ),
                    "checks": checks,
                }

            checks.append({
                "name": "tcp_send",
                "status": "PASS",
                "message": (
                    "TCP client can send data "
                    "to the server."
                ),
                "output": received_data.decode(),
            })

            # 5. Server -> Client
            response_data = b"network-test-response"

            connection.sendall(
                response_data
            )

            received_response = (
                client.recv(1024)
            )

            if received_response != response_data:
                return {
                    "status": "FAIL",
                    "message": (
                        "TCP client received "
                        "unexpected response."
                    ),
                    "sent": response_data.decode(),
                    "received": received_response.decode(
                        errors="replace"
                    ),
                    "checks": checks,
                }

            checks.append({
                "name": "tcp_receive",
                "status": "PASS",
                "message": (
                    "TCP client can receive "
                    "data from the server."
                ),
                "output": received_response.decode(),
            })

            # 6. Verify socket cleanup
            connection.close()
            connection = None

            client.close()
            client = None

            server.close()
            server = None

            checks.append({
                "name": "socket_close",
                "status": "PASS",
                "message": (
                    "TCP sockets can be closed "
                    "and resources released."
                ),
            })

            return {
                "status": "PASS",
                "message": (
                    "Linux TCP socket creation, "
                    "connection, data transfer and "
                    "cleanup are supported."
                ),
                "checks": checks,
            }

        except socket.timeout as exc:
            return {
                "status": "FAIL",
                "message": (
                    "Network socket operation timed out."
                ),
                "error": str(exc),
                "checks": checks,
            }

        except OSError as exc:
            return {
                "status": "FAIL",
                "message": (
                    "Operating system network "
                    "operation failed."
                ),
                "error": str(exc),
                "checks": checks,
            }

        except Exception as exc:
            return {
                "status": "FAIL",
                "message": (
                    "Unexpected network compatibility "
                    "test error."
                ),
                "error": str(exc),
                "checks": checks,
            }

        finally:
            if connection is not None:
                try:
                    connection.close()
                except OSError:
                    pass

            if client is not None:
                try:
                    client.close()
                except OSError:
                    pass

            if server is not None:
                try:
                    server.close()
                except OSError:
                    pass
