#!/usr/bin/env python3
"""Link Workgraph skills into Codex without copying their upstream dependencies."""
import argparse
import os
from pathlib import Path
import sys


def install(skills_dir):
    root = Path(__file__).resolve().parents[1]
    sources = sorted((root / 'skills').glob('*/SKILL.md'))
    required = [
        'conventions.md',
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
        if (target.exists() or target.is_symlink()) and target.resolve() != source.parent.resolve():
            raise RuntimeError('Existing skill conflicts with Workgraph: ' + str(target))
    skills_dir.mkdir(parents=True, exist_ok=True)
    for source in sources:
        target = skills_dir / source.parent.name
        if not target.is_symlink() and not target.exists():
            target.symlink_to(source.parent, target_is_directory=True)
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
    except (OSError, RuntimeError) as error:
        print('Installation failed: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
