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

The pull request workflow runs formatting and repository checks, mypy, and the
test suite.

## Render a video

Create a JSON configuration containing paths to the still image, talking
animation, and closing animation. Relative asset paths are resolved from the
directory containing the configuration file:

```json
{
  "static_image_filename": "assets/images/Holden_Final.png",
  "animation_filename": "assets/graphics/Holden_talking_half_open.mp4",
  "end_animation_filename": "assets/graphics/Holden_talking_full.mp4"
}
```

Run Vox with the configuration, an audio file, and the desired MP4 output:

```powershell
vox --config vox.json --audio commentary.wav --output output/commentary.mp4
```

The same command can be run with `python -m main` instead of `vox`. Use
`--help` to see all options; `--verbose` enables informational logging.
