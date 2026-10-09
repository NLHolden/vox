# Vox

Voice commentary tools for the NLHolden universe. Vox is being developed from
an earlier script that used spoken audio to drive NLHolden's animated
commentary.

## Development setup

Vox requires Python 3.11 or newer. From the repository root, create and
activate a virtual environment, then install the project with its development
tools:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Install the Git hooks once per checkout:

```powershell
python -m pre_commit install
```

The pull request workflow runs formatting and repository checks, plus mypy.
