#!/usr/bin/env python3

"""
Environment Configuration Manager

Modes:
1. build   -> scans repository env files and encrypts them into config.gpg
2. decrypt -> decrypts config.gpg and reconstructs env files

Usage:
    python env_manager.py build
    python env_manager.py decrypt

Optional:
    --root .
    --output config.gpg
    --force
    --dry-run
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
}

ENV_FILES = {
    ".env": "base",
    ".env.dev": "dev",
    ".env.prod": "prod",
}


def parse_env_file(path: Path) -> Dict[str, str]:
    """
    Parse dotenv file into dictionary.
    """
    env_vars = {}

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            env_vars[key.strip()] = value.strip()

    return env_vars


def scan_env_files(root: Path) -> Dict:
    """
    Scan repository recursively for env files.
    """
    result = {}

    for current_root, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        current_path = Path(current_root)

        env_data = {}

        for env_filename, env_type in ENV_FILES.items():
            if env_filename in files:
                env_path = current_path / env_filename
                env_data[env_type] = parse_env_file(env_path)

        if env_data:
            relative_path = str(current_path.relative_to(root))

            if relative_path == ".":
                relative_path = "root"

            result[relative_path] = {
                "path": relative_path,
                "env": env_data,
            }

    return result


def encrypt_json(
    json_data: Dict,
    output_file: Path,
) -> None:
    """
    Encrypt JSON data into GPG file.
    """
    password = getpass.getpass("Enter encryption password: ")
    confirm = getpass.getpass("Confirm encryption password: ")

    if password != confirm:
        raise ValueError("Passwords do not match.")

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False,
        encoding="utf-8",
    ) as temp_file:
        json.dump(json_data, temp_file, indent=2)
        temp_json_path = Path(temp_file.name)

    try:
        subprocess.run(
            [
                "gpg",
                "--batch",
                "--yes",
                "--passphrase",
                password,
                "--symmetric",
                "--cipher-algo",
                "AES256",
                "-o",
                str(output_file),
                str(temp_json_path),
            ],
            check=True,
        )

    finally:
        if temp_json_path.exists():
            temp_json_path.unlink()


def decrypt_json(gpg_file: Path) -> Dict:
    """
    Decrypt GPG file and return JSON object.
    """
    password = getpass.getpass("Enter decryption password: ")

    with tempfile.NamedTemporaryFile(
        mode="r",
        suffix=".json",
        delete=False,
        encoding="utf-8",
    ) as temp_file:
        temp_json_path = Path(temp_file.name)

    try:
        subprocess.run(
            [
                "gpg",
                "--batch",
                "--yes",
                "--passphrase",
                password,
                "-o",
                str(temp_json_path),
                "-d",
                str(gpg_file),
            ],
            check=True,
        )

        with temp_json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return data

    finally:
        if temp_json_path.exists():
            temp_json_path.unlink()


def confirm_overwrite(path: Path) -> bool:
    """
    Ask user for overwrite confirmation.
    """
    answer = input(f"Overwrite {path}? [y/N]: ").strip().lower()
    return answer == "y"


def write_env_files(
    data: Dict,
    root: Path,
    force: bool = False,
    dry_run: bool = False,
) -> None:
    """
    Reconstruct env files from decrypted JSON.
    """
    reverse_env_map = {
        "base": ".env",
        "dev": ".env.dev",
        "prod": ".env.prod",
    }

    for _, service_data in data.items():
        relative_path = service_data["path"]

        if relative_path == "root":
            target_dir = root
        else:
            target_dir = root / relative_path

        target_dir.mkdir(parents=True, exist_ok=True)

        for env_type, env_vars in service_data["env"].items():
            filename = reverse_env_map[env_type]
            target_file = target_dir / filename

            if target_file.exists() and not force:
                if not confirm_overwrite(target_file):
                    print(f"Skipping {target_file}")
                    continue

            if dry_run:
                print(f"[DRY RUN] Would write: {target_file}")
                continue

            with target_file.open("w", encoding="utf-8") as f:
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")

            print(f"Written: {target_file}")


def build_mode(args) -> None:
    """
    Build encrypted GPG config from env files.
    """
    root = Path(args.root).resolve()
    output = Path(args.output).resolve()

    json_output = output.with_suffix(".json")

    # Decide whether to scan or reuse existing JSON
    if json_output.exists() and not args.force_scan:
        print(f"Using existing JSON file: {json_output}")

        with json_output.open("r", encoding="utf-8") as f:
            data = json.load(f)

    else:
        print("Scanning env files...")
        data = scan_env_files(root)

        with json_output.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"Plain JSON saved to: {json_output}")

    print(f"Encrypting configuration into: {output}")
    encrypt_json(data, output)

    print("Done.")


def decrypt_mode(args) -> None:
    """
    Decrypt GPG config and rebuild env files.
    """
    root = Path(args.root).resolve()
    gpg_file = Path(args.output).resolve()

    print(f"Decrypting: {gpg_file}")

    data = decrypt_json(gpg_file)

    # Save decrypted JSON for inspection/debugging
    json_output = gpg_file.with_suffix(".json")

    with json_output.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Decrypted JSON saved to: {json_output}")

    write_env_files(
        data=data,
        root=root,
        force=args.force,
        dry_run=args.dry_run,
    )

    print("Done.")


def ensure_gpg_exists() -> None:
    """
    Ensure GPG is installed.
    """
    if shutil.which("gpg") is None:
        raise RuntimeError(
            "gpg is not installed or not available in PATH."
        )


def main() -> None:
    ensure_gpg_exists()

    parser = argparse.ArgumentParser(
        description="Encrypted environment manager"
    )

    subparsers = parser.add_subparsers(dest="mode", required=True)

    build_parser = subparsers.add_parser("build")

    build_parser.add_argument(
        "--root",
        default=".",
        help="Root folder to scan",
    )

    build_parser.add_argument(
        "--output",
        default="config.gpg",
        help="Encrypted output file",
    )

    build_parser.add_argument(
        "--force-scan",
        action="store_true",
        help="Force filesystem scan even if config.json exists",
    )

    decrypt_parser = subparsers.add_parser("decrypt")
    decrypt_parser.add_argument(
        "--root",
        default=".",
        help="Root folder for reconstruction",
    )
    decrypt_parser.add_argument(
        "--output",
        default="config.gpg",
        help="Encrypted input file",
    )
    decrypt_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite env files without confirmation",
    )
    decrypt_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview file reconstruction",
    )

    args = parser.parse_args()

    if args.mode == "build":
        build_mode(args)

    elif args.mode == "decrypt":
        decrypt_mode(args)


if __name__ == "__main__":
    main()