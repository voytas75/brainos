# Security Policy

## Reporting a vulnerability

If you believe you have found a security issue in BrainOS, please do **not** open a public issue with exploit details.

Instead, contact the maintainer privately first and include:
- a short description of the issue
- affected component or command
- reproduction steps
- impact assessment
- any suggested mitigation

Until a better dedicated channel is published, use a private maintainer contact path rather than public issue discussion.

## Scope

BrainOS is currently an early-stage, local-first project.

The most relevant security areas today are:
- local data handling
- accidental exposure through config or docs
- unsafe assumptions around runtime extensions or embedding configuration
- future API/runtime surfaces as they are introduced

## Expectations

Please:
- give reasonable time for triage and remediation
- avoid publishing proof-of-concept details before first contact
- keep reports focused and reproducible
