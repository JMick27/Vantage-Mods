# Vantage Mods

Public, review-gated VR profiles discovered by the Vantage desktop launcher.

This repository stores declarative configuration and compatibility evidence only.
It must never contain game binaries, copyrighted assets, saves, personal paths,
credentials, raw logs, unreviewed executable code, or redistributed third-party tools.

## Profile lifecycle

1. Vantage creates an immutable local candidate.
2. A user runs a real headset test and Vantage captures a sanitized UEVR `config.txt`.
3. Vantage prepares a review bundle on a new branch.
4. Vantage requires a clean Microsoft Defender scan before submission.
5. A pull request runs schema, checksum, privacy, and safety validation.
6. A reviewer confirms the test evidence and compatibility claim.
7. The accepted profile is added to `manifest.json` as `validated: true`.
8. Replaced versions remain in history and are marked `superseded`.

AI and the desktop application must never push directly to the protected `main` branch.

## Layout

```text
manifest.json
profiles/
  steam/
    12345/
      1.0.0/
        profile.json
        config.txt
        test-result.json
schemas/
scripts/
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for submission requirements.
