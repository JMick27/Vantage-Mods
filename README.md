# Vantage Mods

Public, review-gated VR profiles discovered by the Vantage desktop launcher.

This repository stores declarative configuration and compatibility evidence only.
It must never contain game binaries, copyrighted assets, saves, personal paths,
credentials, raw logs, unreviewed executable code, or redistributed third-party tools.

`runtime-catalog.json` is the review-gated index for Vantage-authored engine runtime
packages. Runtime binaries belong in immutable GitHub releases, never normal Git
history. Every active entry requires an exact SHA-256 digest, architecture, minimum
Vantage version, and package entry point. The desktop app downloads these packages
only on demand, verifies the hash and archive paths, scans them with Microsoft
Defender, and caches them outside the application installation.

## Profile lifecycle

1. Vantage creates an immutable local candidate.
2. A user runs a real headset test and Vantage captures a sanitized UEVR `config.txt`.
3. Vantage prepares a review bundle on a new branch.
4. A pull request runs schema, checksum, privacy, and safety validation.
5. A reviewer confirms the test evidence and compatibility claim.
6. The accepted profile is added to `manifest.json` as `validated: true`.
7. Replaced versions remain in history and are marked `superseded`.

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
