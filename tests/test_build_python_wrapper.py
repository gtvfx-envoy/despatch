import json
import subprocess
import sys
from pathlib import Path


def testBuildPythonWrapperPersistsChildExitCode(tmp_path):
    wrapper_path = Path(__file__).parents[1] / "scripts" / "invoke-build-python.py"
    status_path = tmp_path / "status.json"

    completed_process = subprocess.run(
        [
            sys.executable,
            str(wrapper_path),
            "--status",
            str(status_path),
            "--",
            "-c",
            "import sys; sys.exit(9)",
        ],
        check=False,
    )

    assert completed_process.returncode == 0
    assert json.loads(status_path.read_text(encoding="utf-8")) == {"exitCode": 9}
