import base64
import copy
import json
import runpy
from pathlib import Path

import pytest

from onepiece.model import canonical_bytes

ROOT = Path(__file__).resolve().parents[1]
SPIKE = ROOT / 'projects/balancing-cube/sysml_migration'


def test_pinned_cube_package_recovers_original_canonical_records():
    spike = runpy.run_path(str(SPIKE / 'spike.py'))
    package = spike['build']()
    model, recovered = spike['verify'](json.loads(json.dumps(package)))
    source = json.loads(spike['SOURCE'].read_bytes())
    original = {r['id']: r for r in source if r['id'] in spike['RECORD_HASHES']
                and r['revision'] == spike['REVISION']}
    assert recovered == {name: canonical_bytes(record) for name, record in original.items()}
    requirement = original['R-HOLD']
    assert requirement['data']['statement'].encode() in model
    assert b'0.18[SI::m]' in model
    assert original['D-SIDE']['data']['value'] == 0.18 and original['D-SIDE']['data']['unit'] == 'm'
    assert requirement['data']['approval_state'] == 'human_reviewed'
    assert requirement['data']['verification_status'] == original['cube.verify.R-HOLD']['data']['execution_status'] == 'not_run'
    assert any(link['type'] == 'allocate' and link['target']['id'] == 'cube.function.control-balance'
               and link['target']['revision'] == spike['REVISION'] for link in requirement['links'])
    assert any(link['type'] == 'allocate' and link['target']['id'] == 'cube.component.controller'
               and link['target']['revision'] == spike['REVISION']
               for link in original['cube.function.control-balance']['links'])


@pytest.mark.parametrize('target', ['model', 'record', 'missing'])
def test_pinned_cube_package_rejects_changed_or_missing_content(target):
    spike = runpy.run_path(str(SPIKE / 'spike.py'))
    package = copy.deepcopy(spike['build']())
    if target == 'model':
        package['model'] = base64.b64encode(b'changed model').decode()
    elif target == 'record':
        record = json.loads(base64.b64decode(package['records']['R-HOLD']))
        record['data']['verification_status'] = 'pass'
        package['records']['R-HOLD'] = base64.b64encode(canonical_bytes(record)).decode()
    else:
        del package['records']['D-SIDE']
    with pytest.raises(ValueError):
        spike['verify'](package)
