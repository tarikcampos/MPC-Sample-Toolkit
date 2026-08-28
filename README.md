# MPC Sample Toolkit (MPCTK)

MPCTK is an open-source Python toolkit for creating, inspecting, editing, and
generating projects for the Akai MPC Sample.

The first usable MVP has been validated end-to-end on physical MPC Sample
hardware.

## Current capabilities

MPCTK can:

- read gzip-compressed `.xpj` projects;
- preserve and write MPC project data;
- edit layer coarse tuning;
- clone sample layers between pads;
- generate chromatic pad banks;
- generate major and natural minor scale-pad layouts;
- transpose layouts from a source root to a target root;
- inject a WAV into an MPC project;
- create the required `_[ProjectData]` directory automatically;
- copy the source WAV into the generated project package;
- generate a complete MPC project from the command line.

Generated projects have been successfully loaded and played on physical
MPC Sample hardware.

## Requirements

- Python 3.11 or newer
- An XPJ structural template
- A WAV source sample

The current MVP uses an existing XPJ file as a structural template. Removing
or embedding this dependency is planned as a post-MVP improvement.

## Installation

Clone the repository, enter the project directory, create a virtual
environment, and install MPCTK in editable mode:

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

## Generate an MPC project

Example: generate 16 pads of D natural minor from a sample whose musical root
is C, beginning on MPC Bank B Pad 1:

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

Available CLI scales:

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

This layout is useful when pads are mapped for chromatic playing, including
controller-oriented workflows.

## Hardware tuning limits

Experimentally verified on the MPC Sample:

- Coarse Tune: `-24` to `+24` semitones
- Fine Tune: `-90` to `+90`

The current generation strategy uses MPC real-time coarse tuning. MPCTK
rejects banks outside the verified coarse-tuning range rather than relying on
the hardware to silently clamp values.

## MVP limitations

The current MVP intentionally has a narrow scope:

- project generation still requires an XPJ structural template;
- generation currently uses MPC real-time tuning rather than rendered
  transposed WAVs;
- CLI scale choices are currently major and natural minor;
- automatic pitch/root detection is not implemented;
- multi-bank project requests are not yet exposed as one user-facing
  specification;
- graphical interfaces are not part of the MVP.

These are post-MVP development areas, not requirements for the validated
first workflow.

## Project status

**First usable MVP: validated.**

Validated end-to-end workflow:

```text
WAV
  -> mpctk generate
  -> musical specification
  -> sample injection
  -> pad-bank generation
  -> XPJ serialization
  -> ProjectData packaging
  -> MPC Sample
```

The complete workflow has been tested successfully on physical hardware.

See `docs/ROADMAP.md` for validated foundations, planned work, and exploratory
ideas.
