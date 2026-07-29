# Contributing a profile

Every profile change must arrive through a pull request. Do not commit directly to
`main`.

Required files:

- `profile.json` — identity, compatibility, provenance, safety, and payload checksum
- `config.txt` — sanitized UEVR per-game configuration
- `test-result.json` — the completed hands-on validation checklist
- an updated `manifest.json` only when publishing a reviewed active profile

Profiles must not include DLL, EXE, script, shader, archive, asset, save, dump, or
log files. Advanced plugins and scripts require a future security-review process and
are deliberately outside schema version 1.

Pull requests must state the tested game version, UEVR version, Vantage version,
OpenXR transport/runtime family, GPU family, known limitations, and whether the test
was single-player/offline.

Never include a Windows username, absolute path, API key, token, private key, email
address, raw crash log, or hardware serial number.
