"""Build and check the pinned, lossless Cube SysML migration experiment."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'store/commits/a9ba4933a54b413437f8487b847f8ff4e7e26c79292cc3ce79457307197ac6dd/records.json'
REVISION = 'reviewed-20261019-1'
PROFILE = 'cube-hold-migration-spike-1'
MODEL_HASH = '5dacea2bb34de547e05a4be4c1728b434edb5d74697f8d980e8724b7b2a8cfcb'
RECORD_HASHES = {
    'R-HOLD': '6b288640d7495fda2983773d5ef8667e720a9a2b48d6e6b71907a72d0474dc6f',
    'cube.function.control-balance': '73cb69050ecdedbd11db8d1556f2e24193d254886d32f28b754ed396423a314b',
    'cube.component.controller': '13568a538013b6c46ccc4f2676be6a861222cef2fda74661a562d261dc93a50f',
    'D-SIDE': 'b923fe9514b821272c08197d8dc54a0480dbc0b63c5c72b2abd9c91b8b81ed92',
    'cube.verify.R-HOLD': 'e7136b5b844d06ce3a80797a29f14a378209580683325c79f037d354397a7572',
}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(data):
    return base64.b64encode(data).decode('ascii')


def build():
    records = json.loads(SOURCE.read_bytes())
    selected = [r for r in records if r['project_id'] == 'balancing-cube'
                and r['revision'] == REVISION and r['id'] in RECORD_HASHES]
    if len(selected) != len(RECORD_HASHES) or {r['id'] for r in selected} != set(RECORD_HASHES):
        raise ValueError('Pinned source records missing or duplicated')
    entries = {r['id']: encoded(canonical(r)) for r in selected}
    package = {'profile': PROFILE, 'model': encoded((ROOT / 'hold.sysml').read_bytes()), 'records': entries}
    verify(package)
    return package


def verify(package):
    if package.get('profile') != PROFILE or set(package.get('records', {})) != set(RECORD_HASHES):
        raise ValueError('Unexpected profile or record set')
    model = base64.b64decode(package['model'], validate=True)
    if sha(model) != MODEL_HASH:
        raise ValueError('Native model digest mismatch')
    recovered = {}
    for name, expected in RECORD_HASHES.items():
        raw = base64.b64decode(package['records'][name], validate=True)
        if sha(raw) != expected:
            raise ValueError('Record digest mismatch: ' + name)
        record = json.loads(raw)
        if canonical(record) != raw or (record['project_id'], record['id'], record['revision']) != ('balancing-cube', name, REVISION):
            raise ValueError('Record identity or canonical bytes mismatch: ' + name)
        recovered[name] = raw
    return model, recovered


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument('--build', type=Path, metavar='PACKAGE')
    operation.add_argument('--check', type=Path, metavar='PACKAGE')
    args = parser.parse_args()
    if args.build:
        args.build.write_bytes(canonical(build()) + b'\n')
        print('Wrote', args.build)
    else:
        _, records = verify(json.loads(args.check.read_bytes()))
        print('Verified native model and', len(records), 'canonical record byte strings')


if __name__ == '__main__':
    main()
