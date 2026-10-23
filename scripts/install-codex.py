#!/usr/bin/env python3
"""Link Workgraph skills into Codex without copying their upstream dependencies."""
import argparse
import os
import shutil
import subprocess
from pathlib import Path, PureWindowsPath
import sys


def windows_path(path):
    # wslpath follows existing symlinks; convert the destination lexically.
    if len(path.parts) > 2 and path.parts[1] == 'mnt' and len(path.parts[2]) == 1:
        return str(PureWindowsPath(path.parts[2].upper() + ':/' , *path.parts[3:]))
    return subprocess.check_output(['wslpath', '-w', str(path)], text=True).strip()


def link_skill(source, target):
    # WSL symlinks on NTFS are unreadable by the Windows desktop skill scanner.
    # Directory junctions work in both Windows and WSL and preserve upstream paths.
    on_wsl = 'microsoft' in os.uname().release.lower() if hasattr(os, 'uname') else False
    on_windows_drive = len(target.parts) > 2 and target.parts[1] == 'mnt' and len(target.parts[2]) == 1
    if on_wsl and on_windows_drive and shutil.which('powershell.exe'):
        quote = lambda value: "'" + value.replace("'", "''") + "'"
        win_target = quote(windows_path(target))
        win_source = quote(windows_path(source))
        readable = subprocess.run(
            ['powershell.exe', '-NoProfile', '-NonInteractive', '-Command',
             f'if (Test-Path -LiteralPath {win_target} -PathType Container) {{ exit 0 }} else {{ exit 1 }}'],
            capture_output=True)
        if readable.returncode == 0:
            return
        # install() preflights ownership of every existing destination first.
        if target.is_symlink():
            target.unlink()
        subprocess.run(
            ['powershell.exe', '-NoProfile', '-NonInteractive', '-Command',
             f"$ErrorActionPreference = 'Stop'; New-Item -ItemType Junction -Path {win_target} -Target {win_source} | Out-Null"],
            check=True)
    elif not target.exists() and not target.is_symlink():
        target.symlink_to(source, target_is_directory=True)


def install(skills_dir):
    root = Path(__file__).resolve().parents[1]
    sources = sorted((root / 'skills').glob('*/SKILL.md'))
    required = [
        'conventions.md',
        'vendor/mattpocock-skills/skills/engineering/improve-codebase-architecture/SKILL.md',
        'vendor/mattpocock-skills/skills/engineering/improve-codebase-architecture/HTML-REPORT.md',
        'vendor/mattpocock-skills/skills/engineering/codebase-design/SKILL.md',
        'vendor/mattpocock-skills/skills/engineering/domain-modeling/SKILL.md',
        'vendor/mattpocock-skills/skills/productivity/grilling/SKILL.md',
        'vendor/addyosmani-agent-skills/skills/test-driven-development/SKILL.md',
        'vendor/cursor-plugins/pstack/skills/architect/SKILL.md',
        'vendor/spec-kit/templates/commands/specify.md',
        'vendor/claude-code/plugins/feature-dev/agents/code-explorer.md',
        'vendor/claude-plugins-community/html-plan/skills/html-plan/SKILL.md',
        'vendor/claude-plugins-community/html-plan/skills/html-plan/references/blocks.md',
        'vendor/claude-plugins-community/html-plan/skills/html-plan/examples/scheduled-send.html',
        'vendor/claude-plugins-community/html-plan/skills/html-plan/runtime/pack.mjs',
        'vendor/claude-plugins-community/html-plan/skills/html-plan/runtime/htmlplan.js',
        'vendor/claude-plugins-community/html-plan/skills/html-plan/runtime/htmlplan.css',
    ]
    missing = [p for p in required if not (root / p).is_file()]
    if missing:
        raise RuntimeError('Missing plugin resources: ' + ', '.join(missing)
                           + '. Run git submodule update --init --recursive in ' + str(root))
    if not sources:
        raise RuntimeError('No Workgraph skills found in ' + str(root / 'skills'))
    skills_dir = skills_dir.expanduser().absolute()
    # Check every destination before creating anything; never replace another skill.
    for source in sources:
        target = skills_dir / source.parent.name
        if (target.exists() or target.is_symlink()) and not (target.exists() and target.samefile(source.parent)):
            raise RuntimeError('Existing skill conflicts with Workgraph: ' + str(target))
    skills_dir.mkdir(parents=True, exist_ok=True)
    for source in sources:
        target = skills_dir / source.parent.name
        link_skill(source.parent, target)
        print(str(target) + ' -> ' + str(source.parent))
    print('Installed ' + str(len(sources)) + ' skills. Restart Codex, then use $wg.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    codex_home = Path(os.environ.get('CODEX_HOME') or (Path.home() / '.codex'))
    parser.add_argument('--skills-dir', type=Path, default=codex_home / 'skills',
                        help='Destination (default: $CODEX_HOME/skills or ~/.codex/skills)')
    args = parser.parse_args()
    try:
        install(args.skills_dir)
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print('Installation failed: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
