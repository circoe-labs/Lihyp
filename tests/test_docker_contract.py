from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_container_is_single_worker_loopback_only_and_persistent():
    docker = (ROOT / "Dockerfile").read_text()
    compose = (ROOT / "compose.yaml").read_text()
    assert "python:3.12-slim" in docker
    assert "USER 10001:10001" in docker
    assert '"--workers", "1"' in docker
    assert "127.0.0.1:8000:8000" in compose
    assert "lihyp_data:/data" in compose
    assert "SIMCO2_DB_PATH: /data/simco2.sqlite" in compose
    assert "healthcheck:" in compose
    assert "down -v" in (ROOT / "docs" / "docker-et-conservation.md").read_text()
