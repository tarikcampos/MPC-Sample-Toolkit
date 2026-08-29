# MPC Sample Toolkit — Roadmap

MPCTK is an open-source toolkit for creating, inspecting, editing, and
organizing projects for the Akai MPC Sample.

This roadmap separates capabilities already validated on physical hardware
from planned development and exploratory ideas.

## Current milestone

### First usable MVP — Validated

The first usable MPCTK MVP is complete.

Validated end-to-end capability:

```text
WAV
  -> CLI
  -> musical specification
  -> sample injection
  -> pad-bank generation
  -> XPJ serialization
  -> ProjectData packaging
  -> MPC Sample
```

The generated package opens, loads, and plays correctly on physical MPC
Sample hardware.

The current MVP still uses an XPJ structural template. Removing or embedding
that dependency is a post-MVP improvement rather than a blocker for the first
usable workflow.

## Validated

### XPJ format

- Read gzip-compressed XPJ projects.
- Parse and preserve the XPJ header.
- Parse project, track, instrument, layer, sample reference, and slice data.
- Preserve unknown XPJ fields through `raw_data`.
- Write semantically valid XPJ projects.
- Written projects have been successfully opened on MPC Sample hardware.

### Layer editing

- Edit coarse tuning through the structured model.
- Clone layers between instruments/pads.
- Preserve sample references and nested layer data while cloning.

### Chromatic banks

- Generate chromatic tuning across consecutive pads.
- 16-pad chromatic banks have been validated on MPC Sample hardware.
- A single WAV can be referenced and independently tuned across multiple pads.

### Musical scale foundation

- Musical logic is separated from XPJ serialization.
- Chromatic, major, and natural minor interval definitions exist.
- Scale intervals can be expanded across multiple octaves.
- Arbitrary semitone layouts can be applied to MPC pads.

### Musical roots and layouts

- Musical note names are mapped to pitch classes.
- Sharps, flats, and common enharmonic spellings are supported.
- Source root and target root are handled separately.
- Root transposition is converted into semitone offsets.
- Chromatic Keyboard and Scale Pads are separate layout concepts.
- Scale Pad generation has been validated on MPC Sample hardware.

### Bank specification and generation

- A complete musical bank request can be represented by `BankSpec`.
- Bank specifications support source root, target root, layout, pad count,
  scale, and starting octave.
- Chromatic Keyboard and Scale Pads can be selected by name.
- Major and natural minor scales can be selected by name.
- Musical specifications are converted into semitone offsets automatically.
- The `generation` layer applies a musical specification to an MPC track.
- MPC real-time tuning generation validates the hardware range before writing.
- Musical specifications remain independent from the MPC tuning limit so
  future rendered-audio and hybrid strategies can execute wider ranges.

### Project generation

- MPC Bank A-H / Pad 1-16 addressing is supported.
- Bank/pad addresses are translated into instrument indexes internally.
- The first populated source sample can be discovered automatically.
- Musical banks can be generated without exposing instrument indexes.
- Complete XPJ projects can be generated from an existing template.
- Source templates are preserved while generated projects are written
  separately.
- High-level project generation has been validated on MPC Sample hardware.

### Sample injection

- WAV frame count can be read directly from source audio.
- Full-sample layer regions use zero-based inclusive bounds:
  `Start = 0`, `End = frame_count - 1`.
- Sample references can be created from a physical WAV instead of requiring
  a pre-existing populated XPJ layer.
- Sample entries are injected into both project-level and track-level pools.
- Source layers can be populated with the WAV name, file reference, and
  complete sample region.
- Injected source layers can immediately feed the bank-generation pipeline.
- WAV injection through bank generation has been physically validated.
- Persisted MPC `metadata.key` is not treated as authoritative musical
  pitch/key information.

### Project package generation

- Complete MPC packages can be generated from a source WAV, structural XPJ
  template, `BankSpec`, destination, and project name.
- MPC package naming has been confirmed experimentally:
  `Project.xpj` + `Project_[ProjectData]/`.
- The source WAV is copied automatically into ProjectData.
- Sample injection, bank generation, XPJ serialization, directory creation,
  and WAV copying are orchestrated by one high-level operation.
- Existing project files/directories are protected from accidental overwrite.
- Automatically packaged projects have been physically validated.

### User-facing generation workflow

- MPCTK exposes the `mpctk` command-line entry point.
- `mpctk generate` accepts a WAV, structural template, musical roots, layout,
  scale, pad count, bank, starting pad, octave offset, project name, and
  destination.
- CLI input is translated into `BankSpec` and the validated generation
  pipeline.
- Scale Pads and Chromatic Keyboard are exposed through the CLI.
- Complete project packages can be generated without writing Python scripts.
- The real CLI workflow has been physically validated on MPC Sample hardware.

### Graphical application

- MPCTK exposes a native graphical workflow built with PySide6.
- Source WAV, XPJ template, musical configuration, project name, and
  destination can be selected without using the command line.
- The GUI reuses the existing validated `BankSpec` and project-package
  generation pipeline rather than duplicating generation logic.
- GUI-generated projects have been successfully loaded and played on physical
  MPC Sample hardware.

### macOS application

- MPCTK can be packaged as `MPC Sample Toolkit.app` with PyInstaller.
- The application launches directly from Finder without requiring a Terminal
  session.
- PySide6 and the MPCTK generation engine are bundled into the application.
- File and directory selection works from the packaged application.
- The complete packaged-app workflow has been physically validated:
  `Finder -> GUI -> XPJ + ProjectData -> MPC Sample`.
- Generated build, dist, and PyInstaller spec artifacts remain outside
  version control.

### GUI workflow and visual foundation

- Generation success, failure, and working states are presented in the GUI.
- The Generate action is protected against duplicate activation while a
  project is being created.
- Source, template, and destination selectors remember their most recently
  used directories.
- Generated projects can be revealed directly in Finder.
- The interface separates `Musical Setup` from `Pad Bank` configuration.
- A dedicated result panel and primary Generate action establish the initial
  visual hierarchy.
- The current visual direction is evolving toward an MPC companion-tool
  workflow rather than a generic configuration form.

### Experimentally verified tuning limits

MPC Sample:

- Coarse Tune: -24 to +24 semitones.
- Fine Tune: -90 to +90.

MPCTK rejects coarse-tune values outside the verified range instead of
silently generating layouts that the MPC will clamp.

## Planned

### Remove the user-facing template dependency

Move from a user-supplied structural XPJ template toward a self-contained
generation workflow.

Possible implementation directions include:

- a neutral internal structural template;
- programmatic creation of the required project structure;
- validation of the minimum structure required by the hardware.

### Interactive 4x4 Pad Bank

Represent the generated MPC bank visually as a 4x4 pad surface.

Initial goals include:

- previewing pad assignments before project generation;
- displaying pad number and generated musical note/tuning information;
- updating the preview when musical settings change;
- selecting and inspecting individual pads;
- keeping the visual pad model driven by `BankSpec` rather than duplicating
  musical-generation logic.

The pad surface should also provide a reusable UI foundation for future MIDI
and connected-hardware experiments.

### Multi-bank generation

Allow one user-facing request to describe layouts spanning or targeting
multiple MPC banks.

### Friendly validation and reporting

Improve user-facing errors and reporting around:

- invalid musical specifications;
- MPC tuning-range limits;
- destination conflicts;
- unsupported or invalid WAV files.

### Custom layouts

Allow explicit or reusable musical layouts beyond the current chromatic and
scale modes.

### User-facing configuration

Consider a reusable configuration-file format for generation requests in
addition to CLI flags.

## Exploration

The following ideas are promising but are not implementation commitments.

### Connected MPC mode

Investigate using the MPC Sample as connected hardware rather than only as the
destination for generated project files.

Research areas include:

- detecting the MPC Sample as a USB/MIDI device;
- receiving physical MPC pad events in MPCTK;
- reflecting hardware pad activity on the graphical 4x4 pad surface;
- sending MIDI note events from MPCTK pads to the MPC;
- auditioning samples through a connected workflow where technically
  supported;
- determining which capabilities are available through standard MIDI/USB and
  which, if any, would require MPC-specific communication.

This remains exploratory until the hardware communication paths are verified
experimentally.

### Sample pitch and key analysis

Analyze source audio before building a bank.

Possible capabilities:

- fundamental/root-note estimation for monophonic samples;
- pitch-class analysis for polyphonic samples;
- chord estimation;
- key estimation;
- confidence values;
- manual confirmation/correction.

Detected musical information should be treated as an estimate rather than
absolute truth.

### Audio transposition

MPCTK may eventually transpose/render WAV audio instead of relying entirely
on MPC real-time tuning.

Potential strategies:

#### MPC

Use the original WAV and the MPC's -24 to +24 semitone tuning range.

#### Render

Create already-transposed WAV files and leave MPC coarse tuning at zero.

#### Hybrid

Create a limited number of transposed base WAV files and combine them with
MPC real-time tuning.

The hybrid approach may provide a much larger playable range while avoiding
one rendered WAV per note.

Initial research should consider traditional sampler-style resampling before
more complex pitch shifting with duration preservation.

### Larger banks

Extend musical layouts beyond 16 pads:

- 32 pads;
- 48 pads;
- 64 pads;
- up to the MPC Sample's available pad/instrument capacity.

This must account for hardware tuning limits and, if necessary, future
render/hybrid transposition strategies.

### Additional musical generators

Potential future generators include:

- additional scales and modes;
- chord layouts;
- reusable performance layouts.

These are not part of the validated MVP.

### Project inspection and batch tooling

Potential higher-level tooling includes:

- project explorer functionality;
- batch editing;
- project comparison and reporting;
- reusable editing operations.

These remain post-MVP concepts.

## Architecture

```text
audio/
    future WAV analysis
    future pitch/key analysis
    future resampling/transposition

music/
    notes
    scales
    roots
    musical layouts
    BankSpec

generation/
    pad addressing
    sample injection
    bank generation
    project generation
    project package generation

xpj/
    MPC project representation
    layer cloning/editing
    serialization

gui/
    graphical project-generation workflow
    future interactive pad surface

cli.py
    user-facing command-line workflow
```

The architecture intentionally separates musical intent from MPC-specific
serialization and from higher-level project orchestration.
