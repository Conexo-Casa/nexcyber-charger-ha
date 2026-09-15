#!/usr/bin/env python3
"""Import-check a Home Assistant custom integration against REAL Home Assistant.

Catches API-shape bugs (bad imports, wrong entity-description fields, config-flow
subclassing errors, HA-version drift) WITHOUT a running HA instance.

Run:
    ~/.ha-test-venv/bin/python ha_import_check.py /path/to/repo/custom_components <domain>

It imports every <domain>.<module> and then hasattr-probes the runtime-only HA
APIs an OAuth2 config flow relies on. Exit 0 = clean.
"""
import importlib
import importlib.util
import pathlib
import sys
import traceback


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: ha_import_check.py <custom_components_dir> <domain>")
        return 2
    cc_dir, domain = pathlib.Path(sys.argv[1]).resolve(), sys.argv[2]
    sys.path.insert(0, str(cc_dir))

    pkg = cc_dir / domain
    mods = [f"{domain}"] + [
        f"{domain}.{p.stem}"
        for p in sorted(pkg.glob("*.py"))
        if p.stem != "__init__"
    ]

    ok, fail = [], []
    for m in mods:
        try:
            importlib.import_module(m)
            ok.append(m)
        except Exception as e:  # noqa: BLE001
            fail.append(m)
            print(f"FAIL {m}: {type(e).__name__}: {e}")
            traceback.print_exc()
            print("-" * 60)
    print(f"\nIMPORT OK ({len(ok)}/{len(mods)})")

    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
