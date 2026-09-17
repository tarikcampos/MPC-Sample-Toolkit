# MPC Sample Toolkit (MPCTK)

MPCTK is an open-source Python toolkit and desktop application for creating, inspecting, editing, and generating projects for the Akai MPC Sample.

The current workflow has been validated end-to-end on physical MPC Sample hardware: a source WAV can be turned into a playable MPC project from either the command line or the graphical macOS application.

## Current status

**First usable MVP: validated.**

MPCTK currently provides:

- gzip-compressed `.xpj` project reading and writing;
- structured project, track, instrument, layer, sample, and slice models;
- preservation of unknown XPJ fields while editing known data;
- coarse-tune editing and layer cloning;
- chromatic pad-bank generation;
- major and natural minor Scale Pad layouts;
- source-root to target-root transposition;
- MPC Bank A-H / Pad 1-16 addressing;
- WAV injection into MPC projects;
- automatic `_[ProjectData]` package creation and WAV copying;
- complete project generation through the `mpctk` CLI;
- a native PySide6 graphical generation workflow;
- a Finder-launchable macOS `.app` packaged with PyInstaller;
- GUI generation status, remembered browse locations, and reveal-in-Finder workflow.

Generated projects from both the CLI and graphical application have been successfully loaded and played on physical MPC Sample hardware.

The current automated test suite contains **146 passing tests** at the latest validated development checkpoint.

## Requirements

For development/source use:

- Python 3.11 or newer;
- an XPJ structural template;
- a WAV source sample.

The current generation workflow still uses an existing XPJ file as a structural template. Removing the user-facing template dependency is the next planned development milestone.

## Installation

Clone the repository, enter the project directory, create a virtual environment, and install MPCTK in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

For development and testing:

```bash
python -m pip install -e ".[dev]"
pytest -q
```

For the graphical application:

```bash
python -m pip install -e ".[gui]"
mpctk-gui
```

For macOS application packaging, install the app dependencies:

```bash
python -m pip install -e ".[app]"
```

## Graphical workflow

The PySide6 GUI exposes the validated generation pipeline without requiring CLI commands.

Current controls include:

- Source WAV;
- XPJ structural template;
- Source Root and Target Root;
- Scale Pads or Chromatic Keyboard layout;
- Major or Natural Minor scale;
- pad count, starting bank, starting pad, and starting octave;
- project name and destination.

The interface separates **Musical Setup** from **Pad Bank** configuration and provides generation progress, success/error feedback, and direct reveal-in-Finder access after a successful build.

The GUI reuses the same `BankSpec` and package-generation engine as the CLI rather than duplicating the musical or XPJ logic.

## Generate an MPC project from the CLI

Example: generate 16 pads of D natural minor from a sample whose musical root is C, beginning on MPC Bank B Pad 1:

```bash
mpctk generate \
  "/path/to/sample.wav" \
  --template "/path/to/template.xpj" \
  --source-root C \
  --target-root D \
  --layout scale-pads \
  --scale natural-minor \
  --pads 16 \
  --bank B \
  --start-pad 1 \
  --start-octave -1 \
  --name "D Minor Kit" \
  --output "/path/to/output"
```

MPCTK creates:

```text
D Minor Kit.xpj
D Minor Kit_[ProjectData]/
    sample.wav
```

The resulting pair can be transferred to the MPC Sample.

## Layouts

### Scale Pads

Currently implemented scales:

- `major`
- `natural-minor`

Example:

```text
--layout scale-pads --scale natural-minor
```

### Chromatic Keyboard

Generates consecutive chromatic semitone offsets:

```text
--layout chromatic-keyboard
```

This layout is useful for chromatic playing and controller-oriented workflows.

## Hardware tuning limits

Experimentally verified on the MPC Sample:

- Coarse Tune: `-24` to `+24` semitones;
- Fine Tune: `-90` to `+90`.

The current generation strategy uses MPC real-time coarse tuning. MPCTK rejects banks outside the verified coarse-tuning range instead of relying on the hardware to silently clamp values.

## Architecture

MPCTK deliberately separates musical intent from MPC-specific representation and project orchestration:

```text
music/       notes, scales, roots, layouts, BankSpec
    ↓
generation/  pad addressing, sample injection, bank/project/package generation
    ↓
xpj/         MPC project representation, editing, serialization

cli.py        command-line workflow
gui/          graphical project-generation workflow
```

This separation also leaves room for future rendered/hybrid audio transposition and connected-hardware workflows without coupling them to XPJ serialization.

## Current limitations

- project generation still requires an XPJ structural template;
- generation currently uses MPC real-time tuning rather than rendered transposed WAVs;
- implemented scale choices are currently major and natural minor;
- automatic pitch/root detection is not implemented;
- multi-bank project requests are not yet exposed as one user-facing specification;
- the macOS application has been validated locally but is not yet a signed/notarized public distribution.

## Planned development

The current roadmap prioritizes:

1. **Template Independence** — remove the user-facing XPJ template requirement;
2. **Interactive 4x4 Pad Bank** — preview generated pad assignments visually from `BankSpec`;
3. **Multi-Bank Generation** — extend one request across multiple MPC banks;
4. further validation, custom layouts, and release/portfolio polish.

Exploratory work includes MPC USB/MIDI connectivity, physical-pad/GUI interaction, sample pitch/key analysis, audio transposition strategies, larger banks, additional musical generators, and project inspection/batch tooling.

See `docs/ROADMAP.md` for the detailed separation between validated, planned, and exploratory capabilities.

## Validated end-to-end workflow

```text
WAV
  -> CLI or GUI/macOS app
  -> musical specification
  -> sample injection
  -> pad-bank generation
  -> XPJ serialization
  -> ProjectData packaging
  -> MPC Sample
```

The complete generation path has been tested successfully on physical MPC Sample hardware.
