from pathlib import Path

from build123d import Compound, Part, export_gltf, export_step, export_stl


def export_part(part: Part | Compound, name: str, out_dir: str | Path = "exports") -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    export_step(part, out / f"{name}.step")
    export_stl(part, out / f"{name}.stl")
    export_gltf(part, out / f"{name}.glb")
