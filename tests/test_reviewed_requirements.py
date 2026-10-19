import copy
import json
import runpy
from pathlib import Path

import pytest

from onepiece import IntegrityError, Store, make_record, ref
from onepiece.model import canonical_bytes, digest

ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture(scope='module')
def review():
    return runpy.run_path(str(ROOT/'projects/balancing-cube/review_requirements.py'))

@pytest.fixture(scope='module')
def released(review):
    history=review['load_records'](ROOT/'projects/balancing-cube/store')
    proposal=json.loads(review['PROPOSAL_PATH'].read_text())
    before=canonical_bytes(history)
    updates=review['build_review'](history,proposal)
    assert canonical_bytes(history)==before
    return history,proposal,updates


def test_human_review_preserves_requirement_meaning_and_evidence_states(review,released):
    history,proposal,updates=released
    old={(r['id'],r['revision']):r for r in history}
    reqs=[r for r in updates if r['kind']=='requirement']
    assert len(reqs)==29
    assert sum(r['data']['record_role']=='requirement' for r in reqs)==22
    def meaning(value):
        if isinstance(value,list):return [meaning(v) for v in value]
        if isinstance(value,dict):return {k:meaning(v) for k,v in value.items() if not (k=='revision' and set(value)=={'id','revision'})}
        return value
    for r in reqs:
        source=old[(r['id'],review['SOURCE_REVISION'])]
        assert r['data']['status']=='reviewed'
        assert r['data']['approval_state']=='human_reviewed'
        assert r['actor']=={'type':'human','id':'hirototamura'}
        for field in ['statement','translations','acceptance_criteria','verification_method','verification_status','physical_verified','unresolved_items','conditions']:
            assert meaning(r['data'].get(field))==meaning(source['data'].get(field)), (r['id'],field)
    decision=next(r for r in updates if r['kind']=='review_decision')
    assert decision['data']['scope_confirmation']=='Requirements and allocation split'
    assert 'physical verification' in decision['data']['excluded_scope']


def test_reviewed_allocation_chain_matches_accepted_proposal(review,released):
    history,proposal,updates=released
    latest={r['id']:r for r in updates if r['revision']==review['REVISION']}
    assert sum(r['kind']=='function' for r in updates)==8
    assert sum(r['kind']=='product' and r['data'].get('record_role')=='component' for r in updates)==10
    for allocation in proposal['requirement_allocations']+proposal['parameter_allocations']:
        links=latest[allocation['source']]['links']
        assert {l['target']['id'] for l in links if l['type']=='allocate'}==set(allocation['targets'])
        assert all(l['target']['revision']==review['REVISION'] for l in links if l['type']=='allocate')
    for function in proposal['functions']:
        assert {l['target']['id'] for l in latest[function['id']]['links']}==set(function['component_ids'])
        assert latest[function['id']]['data']['status']=='reviewed'
    for component in proposal['components']:
        assert latest[component['id']]['data']['parent_product_ref']['id']==component['parent_ref']['id']
    assert {r['id'] for r in updates if r['kind']=='requirement' and any(l['type']=='allocate' and l['target']['id']=='cube.system' for l in r['links'])}=={'M-VERTEX','C-BUDGET'}


def test_review_keeps_frozen_physics_contract_and_test_plans(review,released):
    history,_,updates=released
    old={(r['id'],r['revision']):r for r in history}
    snapshot=next(r for r in updates if r['kind']=='simulation_snapshot')
    source=old[('cube.simulation.snapshot',review['SOURCE_REVISION'])]
    for field in ['model','controller','contract','physical_fidelity','comparison_design_ref']:
        assert snapshot['data'].get(field)==source['data'].get(field)
    for r in updates:
        if r['kind']=='parameter':
            for field in ['value','unit','origin','bounds','standard_uncertainty']:
                assert r['data'].get(field)==old[(r['id'],review['SOURCE_REVISION'])]['data'].get(field)
        if r['kind']=='verification_case':
            assert r['data']['execution_status']=='not_run'
            assert r['data']['evidence_refs']==[]
            assert r['data'].get('physical_verified') is not True
            assert all(x['revision']==review['REVISION'] for x in r['data']['requirement_refs'])


def test_review_is_deterministic_and_baseline_hashes_detect_tampering(review,released):
    history,proposal,updates=released
    assert canonical_bytes(review['build_review']([*history,*updates],proposal))==canonical_bytes(updates)
    newkeys={(r['id'],r['revision']) for r in updates}
    universe=[r for r in history if (r['id'],r['revision']) not in newkeys]+updates
    Store._check_references(universe)
    baseline=next(r for r in updates if r['kind']=='baseline')
    assert baseline['actor']['type']=='human'
    assert baseline['data']['adopted_design_baseline'] is False
    assert baseline['data']['physical_verified'] is False
    assert len(baseline['data']['members'])==len(updates)-1
    by_ref={(r['id'],r['revision']):r for r in updates}
    assert all(digest(by_ref[(m['id'],m['revision'])])==m['sha256'] for m in baseline['data']['members'])
    altered=copy.deepcopy(universe)
    next(r for r in altered if r['id']=='R-HOLD' and r['revision']==review['REVISION'])['data']['statement']='Changed after review'
    with pytest.raises(IntegrityError,match='Baseline member digest mismatch'):
        Store._check_references(altered)


def test_requirement_function_product_allocations_are_typed(tmp_path):
    product=make_record(project_id='p',id='part',kind='product')
    function=make_record(project_id='p',id='balance',kind='function',links=[{'type':'allocate','target':ref(product)}])
    requirement=make_record(project_id='p',id='hold',kind='requirement',links=[{'type':'allocate','target':ref(function)}])
    store=Store(tmp_path/'valid');assert store.import_records([product,function,requirement])['imported']==3
    assert store.check()['ok']
    bad=make_record(project_id='p',id='bad',kind='function',links=[{'type':'allocate','target':ref(requirement)}])
    with pytest.raises(IntegrityError,match='Invalid allocate direction'):
        store.import_records([bad])


def test_reviewed_documents_put_review_state_above_preserved_statements(tmp_path,review,released):
    for language in ['en','ja']:(tmp_path/f'docs/{language}').mkdir(parents=True)
    review['write_documents'](released[2],tmp_path)
    for language in ['en','ja']:
        body=(tmp_path/f'docs/{language}/balancing_cube_requirements.md').read_text()
        assert review['REVISION'] in body
        assert 'human_reviewed' in body
        assert body.count('\n## ')==29
        assert 'R-HOLD' in body


def test_reviewed_context_pins_allocated_functions_and_components(tmp_path,monkeypatch,review,released):
    history,_,updates=released
    rows={(r['id'],r['revision']):r for r in [*history,*updates]}
    function=copy.deepcopy(next(r for r in updates if r['kind']=='function'))
    function['revision']='future-draft';function['created_at']='2026-10-20T00:00:00+00:00'
    rows[(function['id'],function['revision'])]=function
    store=Store(tmp_path/'context')
    monkeypatch.setattr(store,'records',lambda project_id=None,kinds=None:list(rows.values()))
    context=store.context('balancing-cube',product_node='cube.component.controller',max_designs=0,max_evidence=0)
    assert context['snapshot_ref']=={'id':'cube.simulation.snapshot','revision':review['REVISION']}
    selected={r['id']:r for r in context['records']}
    assert selected[function['id']]['revision']==review['REVISION']
    assert len([r for r in selected.values() if r['kind']=='function'])==8
    assert selected['cube.component.controller']['data']['status']=='reviewed'
