# MPC Sample Toolkit — Roadmap

MPCTK is an open-source toolkit for creating, inspecting, editing, and
organizing projects for the Akai MPC Sample.

This roadmap records the current architectural direction of the project.
Experimental ideas are intentionally separated from committed plans.

## Current milestone

### First usable MVP

Goal:

> Take one or more WAV samples and generate or modify a valid MPC Sample
> project that opens and works correctly on the hardware.

Current estimated progress: ~74%.

## Validated foundations

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

### Experimentally verified tuning limits

MPC Sample:

- Coarse Tune: -24 to +24 semitones.
- Fine Tune: -90 to +90.

MPCTK rejects coarse-tune values outside the verified hardware range instead
of silently generating layouts that the MPC will clamp.

## Planned

### Musical bank specification

Allow complete banks to be described through a higher-level specification
rather than calling individual music and XPJ functions manually.

Remaining concepts:

- named scale selection
- number of pads
- octave/range strategy
- layout selection
- validation against the chosen tuning strategy

The user should not need to manually calculate semitone offsets.

### Custom layouts

Allow explicit or reusable musical layouts beyond chromatic and scale modes.

## Exploration

The following ideas are promising but are not yet implementation commitments.

### Sample pitch and key analysis

Analyze source audio before building a bank.

Possible capabilities:

- fundamental/root-note estimation for monophonic samples
- pitch-class analysis for polyphonic samples
- chord estimation
- key estimation
- confidence values
- manual confirmation/correction

Detected musical information should be treated as an estimate rather than an
absolute truth.

### Audio transposition

MPCTK may eventually transpose/render WAV audio itself instead of relying
entirely on MPC real-time tuning.

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

Initial audio-transposition research should consider traditional sampler-style
resampling before more complex pitch shifting with duration preservation.

### Larger banks

Extend musical layouts beyond 16 pads:

- 32 pads
- 48 pads
- 64 pads
- up to the MPC Sample's available pad/instrument capacity

This must account for hardware tuning limits and, if necessary, future
render/hybrid transposition strategies.

## Architecture direction

```text
audio/
    future pitch/key analysis
    future resampling/transposition

music/
    notes
    intervals
    scales
    roots
    musical transformations

layouts/
    future chromatic keyboard layouts
    future scale pad layouts
    future custom layouts

xpj/
    MPC project representation
    layer cloning/editing
    pad/instrument manipulation
    serialization

build/
    future orchestration from user specification to finished project



q
eof
