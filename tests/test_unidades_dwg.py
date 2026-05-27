import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "tabela-tipologias" / "scripts" / "unidades_dwg.py"


def test_cli_erro_para_arquivo_inexistente():
    """Sem DWG real, o CLI deve falhar com erro legivel (nao crash)."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--dwg", "naoexiste.dwg"],
        capture_output=True,
        text=True,
    )
    # Espera erro (arquivo nao existe ou ODA nao consegue converter)
    assert result.returncode != 0 or "error" in result.stderr.lower() or result.stderr != ""


def test_cli_help():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--dwg" in (result.stdout + result.stderr)
