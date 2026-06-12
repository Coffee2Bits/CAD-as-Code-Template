from typing import Annotated

import dagger
from dagger import DefaultPath, Ignore, dag, function, object_type

SOURCE_IGNORE = Ignore(
    [
        ".git",
        ".venv",
        "ci/.venv",
        "ci/sdk",
        "**/__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "ocp-cad-viewer-*.vsix",
        ".cursor",
    ]
)


@object_type
class Ci:
    def _devcontainer(self, source: dagger.Directory) -> dagger.Container:
        return (
            source.directory(".devcontainer")
            .docker_build(dockerfile="Dockerfile")
            .with_mounted_cache("/root/.cache/uv", dag.cache_volume("cad-uv-cache"))
        )

    def _project(self, source: dagger.Directory) -> dagger.Container:
        return (
            self._devcontainer(source)
            .with_mounted_directory("/src", source)
            .with_workdir("/src")
            .with_exec(["uv", "sync", "--group", "dev", "--frozen"])
        )

    @function
    async def test(
        self,
        source: Annotated[dagger.Directory, DefaultPath("."), SOURCE_IGNORE],
    ) -> str:
        """Run pytest for geometry and export tests."""
        return await self._project(source).with_exec(["uv", "run", "pytest"]).stdout()

    @function
    async def lint(
        self,
        source: Annotated[dagger.Directory, DefaultPath("."), SOURCE_IGNORE],
    ) -> str:
        """Run ruff, mypy, and vulture."""
        base = self._project(source)
        await base.with_exec(["uv", "run", "ruff", "check", "."]).stdout()
        await base.with_exec(["uv", "run", "ruff", "format", "--check", "."]).stdout()
        await base.with_exec(
            ["uv", "run", "mypy", "cad", "cad_tooling", "tests", "cad_tooling_tests"]
        ).stdout()
        return await base.with_exec(["uv", "run", "vulture"]).stdout()

    @function
    async def artifacts(
        self,
        source: Annotated[dagger.Directory, DefaultPath("."), SOURCE_IGNORE],
    ) -> str:
        """Discover and export MakerRepo artifacts (python -m cad_tooling.export smoke)."""
        return (
            await self._project(source)
            .with_exec(["uv", "run", "python", "-m", "cad_tooling.export", "smoke"])
            .stdout()
        )

    @function
    async def release_artifact(
        self,
        source: Annotated[dagger.Directory, DefaultPath("."), SOURCE_IGNORE],
    ) -> dagger.Directory:
        """Export release STL and PNG preview artifacts for GitHub Releases."""
        return (
            self._project(source)
            .with_exec(
                [
                    "uv",
                    "run",
                    "python",
                    "-m",
                    "cad_tooling.export",
                    "release",
                    "-o",
                    "/tmp/release-artifacts",
                    "--lighting-preset",
                    "default",
                ]
            )
            .directory("/tmp/release-artifacts")
        )

    @function
    async def check(
        self,
        source: Annotated[dagger.Directory, DefaultPath("."), SOURCE_IGNORE],
    ) -> str:
        """Run lint, artifacts, then test."""
        await self.lint(source)
        await self.artifacts(source)
        return await self.test(source)
