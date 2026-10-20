"""Unit checks for effective Docker Compose security preflight (no Docker daemon)."""
from scripts.check_security_compose import validate


def config(source="/srv/harvey-auth", **overrides):
    service = {
        "cap_drop": ["ALL"],
        "security_opt": ["no-new-privileges:true"],
        "volumes": [{"type": "bind", "source": source, "target": "/home/harvey/.claude"}],
    }
    service.update(overrides)
    return {"services": {"harvey": service}}


def test_isolated_credentials_accepted():
    assert validate(config(), "/srv/harvey-auth") == []


def test_shared_profile_rejected():
    assert validate(config(source="/home/operator/.claude"), "/srv/harvey-auth")


def test_docker_socket_rejected():
    c = config()
    c["services"]["harvey"]["volumes"].append(
        {"type": "bind", "source": "/var/run/docker.sock", "target": "/var/run/docker.sock"}
    )
    assert any("socket" in e.lower() for e in validate(c, "/srv/harvey-auth"))


def test_privileged_or_public_port_rejected():
    c = config(privileged=True, ports=[{"target": 8000, "published": 8000}])
    errors = validate(c, "/srv/harvey-auth")
    assert any("privileged" in e for e in errors)
    assert any("Ports" in e for e in errors)


def test_duplicate_credential_mount_rejected():
    c = config()
    c["services"]["harvey"]["volumes"].append(
        {"source": "/home/operator/.claude", "target": "/home/harvey/.claude"}
    )
    assert validate(c, "/srv/harvey-auth")
