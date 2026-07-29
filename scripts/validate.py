"""Validate Vantage-Mods without executing profile content."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_PROFILE_FILES = {"profile.json", "config.txt", "test-result.json"}
FORBIDDEN_SUFFIXES = {
    ".exe", ".dll", ".sys", ".bat", ".cmd", ".ps1", ".js", ".vbs", ".lua",
    ".zip", ".7z", ".rar", ".pak", ".ucas", ".utoc", ".sav", ".dmp", ".log",
}
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|authorization)\s*[:=]\s*\S+"),
    re.compile(r"(?i)\b[A-Z]:[\\/](?:Users|Documents and Settings)[\\/]"),
    re.compile(r"(?i)\bgh[opusr]_[A-Za-z0-9_]{20,}\b"),
)
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def validate_repository() -> list[str]:
    errors: list[str] = []
    manifest = load_json(ROOT / "manifest.json")
    if set(manifest) != {"schemaVersion", "profiles"} or manifest.get("schemaVersion") != 1:
        errors.append("manifest.json must contain only schemaVersion 1 and profiles")
        return errors
    entries = manifest.get("profiles")
    if not isinstance(entries, list):
        return ["manifest.json profiles must be an array"]
    active_games: set[tuple[str, str]] = set()
    declared_paths: set[str] = set()
    for index, entry in enumerate(entries):
        prefix = f"manifest profiles[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix} must be an object")
            continue
        required = {
            "profileId", "source", "storeId", "version", "validated", "state",
            "minimumVantageVersion", "releaseUrl", "profilePath", "payloadSha256",
        }
        optional = {"maximumVantageVersion"}
        if not required.issubset(entry) or not set(entry).issubset(required | optional):
            errors.append(f"{prefix} has missing or unknown fields")
            continue
        if entry["source"] not in {"Steam", "Xbox"} or entry["validated"] is not True or entry["state"] != "active":
            errors.append(f"{prefix} must be an active validated Steam or Xbox profile")
        if not SEMVER.fullmatch(str(entry["version"])) or not SEMVER.fullmatch(str(entry["minimumVantageVersion"])):
            errors.append(f"{prefix} contains an invalid semantic version")
        if not SHA256.fullmatch(str(entry["payloadSha256"])):
            errors.append(f"{prefix} contains an invalid payload checksum")
        game = (str(entry["source"]).casefold(), str(entry["storeId"]).casefold())
        if game in active_games:
            errors.append(f"{prefix} duplicates an active game profile")
        active_games.add(game)
        path_text = str(entry["profilePath"])
        declared_paths.add(path_text)
        profile_path = safe_repo_path(path_text, errors, prefix)
        if profile_path:
            validate_profile(profile_path, entry, errors)
    for profile_path in ROOT.glob("profiles/*/*/*/profile.json"):
        relative = profile_path.relative_to(ROOT).as_posix()
        profile = load_json(profile_path)
        if profile.get("state") == "active" and profile.get("validated") is True and relative not in declared_paths:
            errors.append(f"{relative} is active and validated but missing from manifest.json")
    scan_repository_text(errors)
    return errors


def safe_repo_path(value: str, errors: list[str], prefix: str) -> Path | None:
    path = (ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError:
        errors.append(f"{prefix} escapes the repository")
        return None
    if not path.is_file():
        errors.append(f"{prefix} references a missing profile")
        return None
    return path


def validate_profile(path: Path, entry: dict, errors: list[str]) -> None:
    profile = load_json(path)
    required = {
        "schemaVersion", "profileId", "source", "storeId", "gameTitle", "version",
        "adapter", "state", "validated", "minimumVantageVersion", "payload",
        "safety", "provenance", "knownLimitations",
    }
    optional = {"maximumVantageVersion"}
    relative = path.relative_to(ROOT).as_posix()
    if not required.issubset(profile) or not set(profile).issubset(required | optional):
        errors.append(f"{relative} has missing or unknown fields")
        return
    for field in ("profileId", "source", "storeId", "version", "minimumVantageVersion"):
        if str(profile.get(field)) != str(entry.get(field)):
            errors.append(f"{relative} {field} does not match manifest.json")
    if profile.get("schemaVersion") != 1 or profile.get("adapter") != "uevr":
        errors.append(f"{relative} must be a schema 1 UEVR profile")
    if profile.get("state") != "active" or profile.get("validated") is not True:
        errors.append(f"{relative} is not active and validated")
    safety = profile.get("safety")
    if not isinstance(safety, dict) or safety != {
        "antiCheatDetected": False,
        "testedOffline": True,
        "automaticInjectionAllowed": False,
        "antivirusStatus": "clean",
    }:
        errors.append(f"{relative} safety declaration is invalid")
    payload = profile.get("payload")
    if not isinstance(payload, dict) or set(payload) != {"path", "sha256", "format"}:
        errors.append(f"{relative} payload declaration is invalid")
        return
    payload_path = path.parent / str(payload["path"])
    if payload["path"] != "config.txt" or payload.get("format") != "uevr-config-txt" or not payload_path.is_file():
        errors.append(f"{relative} must reference config.txt")
        return
    digest = "sha256:" + hashlib.sha256(payload_path.read_bytes()).hexdigest()
    if payload.get("sha256") != digest or entry.get("payloadSha256") != digest:
        errors.append(f"{relative} payload checksum does not match config.txt")
    files = {item.name for item in path.parent.iterdir() if item.is_file()}
    if not files.issubset(ALLOWED_PROFILE_FILES):
        errors.append(f"{relative} folder contains unsupported files: {sorted(files - ALLOWED_PROFILE_FILES)}")


def scan_repository_text(errors: list[str]) -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if path.suffix.casefold() in FORBIDDEN_SUFFIXES:
            errors.append(f"{relative} uses a forbidden file type")
            continue
        if path.stat().st_size > 1024 * 1024:
            errors.append(f"{relative} exceeds the 1 MiB public-profile limit")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"{relative} is not UTF-8 text")
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"{relative} contains a credential or personal-path pattern")
                break


if __name__ == "__main__":
    problems = validate_repository()
    if problems:
        print("\n".join(f"ERROR: {problem}" for problem in problems))
        raise SystemExit(1)
    print("Vantage profile repository validation passed.")
