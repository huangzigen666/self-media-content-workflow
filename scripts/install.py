#!/usr/bin/env python3
"""Install all self-media Skills into a Codex user or project Skill directory."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills"


def default_target() -> Path:
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    return codex_home.expanduser() / "skills"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        type=Path,
        default=default_target(),
        help="Skill directory to install into",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace existing Skill directories with the same names",
    )
    return parser.parse_args()


def remove_existing(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def main() -> int:
    args = parse_args()
    if not SOURCE.is_dir():
        print(f"Source directory not found: {SOURCE}", file=sys.stderr)
        print("Run this script from a complete checkout of the repository.", file=sys.stderr)
        return 1

    target = args.target.expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)

    skill_dirs = sorted(path for path in SOURCE.iterdir() if path.is_dir())
    conflicts = [
        target / skill.name
        for skill in skill_dirs
        if (target / skill.name).is_symlink() or (target / skill.name).exists()
    ]
    if conflicts and not args.force:
        print("Installation stopped. Existing Skills:")
        for conflict in conflicts:
            print(f"- {conflict}")
        print("Run again with --force only if these directories may be replaced.")
        return 1

    for source in skill_dirs:
        destination = target / source.name
        remove_existing(destination)
        shutil.copytree(source, destination)
        print(f"Installed {source.name} -> {destination}")

    print(f"Installed {len(skill_dirs)} Skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
