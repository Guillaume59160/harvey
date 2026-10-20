#!/usr/bin/env bash
# Staging-only Docker network isolation smoke test. Never touches existing containers.
# Requires Docker on an isolated CI runner or dedicated staging host.
set -euo pipefail

echo "Checking a throwaway container with --network none, no credentials."
docker run --rm --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges --pids-limit 64 --user 65534:65534 \
  --tmpfs /tmp:rw,noexec,nosuid,nodev,size=16m \
  --entrypoint python python:3.12-slim -c '
import os, socket
assert os.geteuid() != 0, "container must be unprivileged"
for host, port in [
    ("169.254.169.254", 80),  # Cloud instance metadata
    ("127.0.0.1", 22),       # No services inside sandbox
    ("10.0.0.1", 80),        # Private destination
    ("1.1.1.1", 443),       # Public destination: staging stays offline
]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        try:
            sock.connect((host, port))
        except OSError:
            print("BLOCKED", host, port)
        else:
            raise AssertionError(f"Unexpected connection allowed: {host}:{port}")
print("PASS: throwaway Docker container is network-isolated")
'
