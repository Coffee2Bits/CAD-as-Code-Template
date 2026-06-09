import json
import subprocess
from pathlib import Path


def test_artifacts_discovered():
    result = subprocess.run(
        ["uv", "run", "mr", "artifacts", "list", "-o", "json"],
        capture_output=True,
        text=True,
        check=True,
        cwd=Path(__file__).resolve().parents[1],
    )
    artifacts = json.loads(result.stdout)
    names = {item["name"] for item in artifacts}

    assert "sphere" in names


def test_generators_discovered():
    result = subprocess.run(
        ["uv", "run", "mr", "generators", "list", "-o", "json"],
        capture_output=True,
        text=True,
        check=True,
        cwd=Path(__file__).resolve().parents[1],
    )
    generators = json.loads(result.stdout)
    names = {item["name"] for item in generators}

    assert "sphere_generator" in names


def test_artifact_export_step(tmp_path: Path):
    out_dir = tmp_path / "artifacts"
    subprocess.run(
        [
            "uv",
            "run",
            "mr",
            "artifacts",
            "export",
            "sphere",
            "-o",
            str(out_dir),
            "--format",
            "step",
        ],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
    )

    step_files = list(out_dir.glob("*.step"))
    assert len(step_files) == 1
    assert step_files[0].stat().st_size > 0
