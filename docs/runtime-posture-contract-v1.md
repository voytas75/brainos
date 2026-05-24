# Runtime posture contract v1

## Purpose
This document defines the current difference between **ambient runtime capability** and **explicit-path runtime readiness** in BrainOS vector operation.

These two signals may differ without either one being a bug on its own.

## Ambient runtime capability
Ambient runtime capability answers:
- can this process use sqlite-vec without performing an explicit readiness-style load step first?

Current surfaces that report this posture:
- `brainos capabilities`
- `retrieval-health.runtime.capabilities`

Current interpretation:
- `sqlite_vec=true` means vec0 is available to the process in its ordinary capability path
- `sqlite_vec=false` means vec0 is not currently available in that ambient path
- `sqlite_vec_probe_mode=ambient` means this posture was evaluated without an explicit configured-path load step

## Explicit-path runtime readiness
Explicit-path readiness answers:
- if BrainOS is given an explicit configured sqlite-vec extension path, can it successfully load it and execute a real probe query?

Current surface that reports this posture:
- `brainos sqlite-vec-readiness`

Current interpretation:
- `ok=true` means BrainOS can explicitly load the configured vec0 extension path and execute the readiness probe successfully
- this is stronger than a mere config echo, but narrower than claiming ambient availability

## Why these can differ
A system may validly report:
- ambient capability = unavailable
- explicit readiness = available

because the runtime can require an explicit extension path/load step that ordinary ambient capability detection does not assume.

## Current operator rule
Read runtime posture in this order:
1. `sqlite-vec-readiness` for explicit configured-path truth
2. `capabilities` / `retrieval-health.runtime.capabilities` for ambient process truth
3. `retrieval-health` overall for operational consequences in the current surface design

## Current surface contract
- `capabilities` currently reports ambient posture
- `retrieval-health.runtime.capabilities` currently mirrors ambient posture
- `sqlite-vec-readiness` currently reports explicit-path readiness posture

So if these differ, the correct reading is not automatically contradiction.
The correct reading is usually: explicit loading works, but ambient process availability is not yet established.

## Stability note
This contract should remain stable until BrainOS intentionally changes which runtime posture is treated as the primary operational source of truth.
