import contextlib
import shutil
import subprocess
import tempfile
from collections.abc import Iterator


@contextlib.contextmanager
def cloned_repository(repo_url: str) -> Iterator[str]:
    """Shallow-clones repo_url into a temp dir, yields the path, and always cleans up."""
    workdir = tempfile.mkdtemp(prefix="scan-")
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, workdir],
            check=True,
            capture_output=True,
            timeout=300,
        )
        yield workdir
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
