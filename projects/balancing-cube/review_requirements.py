"""Append the human-reviewed requirement/allocation release; historical records are immutable."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
from onepiece.model import canonical_bytes, digest, make_record, ref
from onepiece.store import Store

ROOT=Path(__file__).resolve().parent
PROJECT='balancing-cube'
SOURCE_REVISION='standards-draft-20261011-2'
REVISION='reviewed-20261019-1'
CREATED_AT='2026-10-19T12:28:34+00:00'
ACTOR={'type':'human','id':'hirototamura'}
AUTHORIZATION='I think the new drafted requirements are okay. I want to mark them as reviewed in one piece repo and release the new version'
SCOPE_REPLY='Requirements and allocation split'
PROPOSAL_PATH=ROOT/'review_inputs/allocation_draft_20261017.json'


def load_records(store_path):
    records={}
    for path in sorted(Path(store_path).glob('commits/*/records.json')):
        for record in json.loads(path.read_text()):
            key=(record['id'],record['revision'])
            if key in records and records[key]!=record:raise ValueError(f'Conflicting record {key}')
            records[key]=record
    return list(records.values())


def build_review(records, proposal):
    by_ref={(r['id'],r['revision']):r for r in records}
    requirements=[r for r in records if r['kind']=='requirement' and r['revision']==SOURCE_REVISION]
    obligations=[r for r in requirements if r['data'].get('record_role')=='requirement']
    if len(requirements)!=29 or len(obligations)!=22:raise ValueError('Expected 22 obligations and 7 groups')
    parameters=[r for r in records if r['kind']=='parameter' and r['revision']==SOURCE_REVISION]
    cases=[by_ref[(r['data']['verification_case_ref']['id'],r['data']['verification_case_ref']['revision'])] for r in obligations]
    allocations={a['source']:a for a in proposal['requirement_allocations']}
    parameter_allocations={a['source']:a for a in proposal['parameter_allocations']}
    if set(allocations)!={r['id'] for r in obligations}:raise ValueError('Allocation proposal must cover exactly the reviewed obligations')
    if set(parameter_allocations)!={r['id'] for r in parameters}:raise ValueError('Allocation proposal must cover exactly the preserved parameters')
    roots={id:by_ref[(id,'standards-draft-20261011-1')] for id in ['cube.system','cube.verification']}
    updates=[make_record(project_id=PROJECT,id=proposal['id'],revision=proposal['revision'],kind='architecture_proposal',product_node='cube.system',created_at=CREATED_AT,actor={'type':'automation','id':'site-proposal-import'},data=copy.deepcopy(proposal))]
    def add(id,kind,data,owner='cube.system',links=()):
        result=make_record(project_id=PROJECT,id=id,revision=REVISION,kind=kind,product_node=owner,created_at=CREATED_AT,actor=ACTOR,data=data,links=list(links))
        updates.append(result);return result
    def edge(type,id,revision=REVISION,**metadata):return {'type':type,'target':ref(id,revision),**metadata}
    reviewed_ids={r['id'] for r in [*requirements,*parameters,*cases]}|set(roots)|{r['id'] for r in proposal['functions']+proposal['components']}
    def retarget(value):
        if isinstance(value,list):return [retarget(v) for v in value]
        if not isinstance(value,dict):return value
        if set(value)=={'id','revision'} and value['id'] in reviewed_ids and value['revision']==SOURCE_REVISION:return ref(value['id'],REVISION)
        return {k:retarget(v) if k not in {'supersedes','source_record','original_record','source_snapshot_ref'} else copy.deepcopy(v) for k,v in value.items()}
    decision=add('cube.review.requirements-allocation','review_decision',{
        'name':'Human review of Cube requirements and allocation split','decision':'accepted',
        'reviewed_on':'2026-10-19','reviewed_timezone':'Asia/Tokyo','reviewer':ACTOR,
        'authorization':AUTHORIZATION,'scope_confirmation':SCOPE_REPLY,
        'scope':['22 requirement statements','7 requirement groups','8 functions','10 components','requirement and parameter allocations'],
        'source_model_ref':ref('cube.system-model.active',SOURCE_REVISION),
        'source_proposal_revision':proposal['revision'],'source_proposal_sha256':hashlib.sha256(canonical_bytes(proposal)).hexdigest(),
        'open_items_policy':'Preserve unresolved limits, methods and evidence gaps. Review acceptance is not a verification result.',
        'excluded_scope':['physical verification','adoption of a hardware design','retroactive evidence applicability'],
    })
    review_meta={'status':'reviewed','approval_state':'human_reviewed','review_decision_ref':ref(decision)}
    for id,source in roots.items():
        data=copy.deepcopy(source['data']);data.update(review_meta,supersedes=ref(source))
        data['function_refs']=[ref(f['id'],REVISION) for f in proposal['functions'] if f['parent_ref']['id']==id]
        data['component_refs']=[ref(c['id'],REVISION) for c in proposal['components'] if c['parent_ref']['id']==id]
        data['description']='Three-wheel Cube with reviewed onboard functions and components.' if id=='cube.system' else 'External independent measurement, acquisition and analysis context for Cube verification.'
        add(id,'product',data,id)
    for item in proposal['components']:
        data=copy.deepcopy(item)
        for key in ['id','revision','kind','proposal']:data.pop(key,None)
        data.update(review_meta,record_role='component',source_proposal_ref={'id':proposal['id'],'revision':proposal['revision']})
        data['parent_ref']=ref(item['parent_ref']['id'],REVISION)
        data['parent_product_ref']=ref(item['parent_ref']['id'],REVISION)
        add(item['id'],'product',data,item['id'])
    for item in proposal['functions']:
        data=copy.deepcopy(item)
        for key in ['id','revision','kind','proposal']:data.pop(key,None)
        data.update(review_meta,record_role='function',source_proposal_ref={'id':proposal['id'],'revision':proposal['revision']})
        data['parent_ref']=ref(item['parent_ref']['id'],REVISION)
        data['component_refs']=[ref(id,REVISION) for id in item['component_ids']]
        add(item['id'],'function',data,item['parent_ref']['id'],[edge('allocate',id,scope='reviewed functional responsibility; not satisfaction evidence') for id in item['component_ids']])
    functions={f['id']:f for f in proposal['functions']}
    for source in requirements:
        data=retarget(copy.deepcopy(source['data']));data.update(review_meta,supersedes=ref(source))
        data['status_semantics']='Human-reviewed requirement wording and allocation; verification status is independent.'
        links=[retarget(l) for l in source['links'] if l['type']!='allocate']
        allocation=allocations.get(source['id'])
        owner=source['product_node']
        if allocation:
            data['allocation_scope']=allocation['scope'];data['allocation_rationale']=allocation['rationale']
            targets=allocation['targets'];owner=functions[targets[0]]['component_ids'][0] if targets[0] in functions else targets[0]
            links.extend(edge('allocate',id,scope=allocation['scope'],rationale=allocation['rationale']) for id in targets)
        add(source['id'],'requirement',data,owner,links)
    for source in parameters:
        data=retarget(copy.deepcopy(source['data']));data.update(supersedes=ref(source),allocation_review_ref=ref(decision))
        targets=parameter_allocations[source['id']]['targets']
        add(source['id'],'parameter',data,targets[0],[edge('allocate',id,scope='reviewed parameter responsibility') for id in targets])
    for source in cases:
        data=retarget(copy.deepcopy(source['data']));data['supersedes']=ref(source)
        add(source['id'],'verification_case',data,'cube.verification',[retarget(l) for l in source['links']])
    source_snapshot=by_ref[('cube.simulation.snapshot',SOURCE_REVISION)]
    snapshot_data=copy.deepcopy(source_snapshot['data'])
    snapshot_data.update(supersedes=ref(source_snapshot),source_snapshot_ref=ref(source_snapshot),requirements_approval_state='human_reviewed',review_decision_ref=ref(decision),trace_correction_note='Human-reviewed wording and allocations. Frozen numerical values, controller, evaluation contract and historical evidence retain their scope.')
    new_requirements=[r for r in updates if r['kind']=='requirement']
    new_parameters=[r for r in updates if r['kind']=='parameter']
    snapshot_data['context_refs']['requirements']=[ref(r) for r in new_requirements]
    snapshot_data['context_refs']['kdps']=[ref(r) for r in new_parameters]
    snapshot_data['context_refs']['verification_cases']=[ref(r) for r in updates if r['kind']=='verification_case']
    snapshot_data['context_refs']['functions']=[ref(r) for r in updates if r['kind']=='function']
    snapshot_data['context_refs']['products']=[ref(r) for r in updates if r['kind']=='product']
    snapshot_data['kdps']['entries']=[r['data'] for r in new_parameters];snapshot_data['kdps']['revision']=REVISION
    snapshot_data['mission']['requirements']=[r['data'] for r in new_requirements];snapshot_data['mission']['revision']=REVISION
    for binding in snapshot_data.get('parameter_bindings',[]):
        if binding.get('parameter_ref',{}).get('id') in parameter_allocations:binding['parameter_ref']['revision']=REVISION
    snapshot=add('cube.simulation.snapshot','simulation_snapshot',snapshot_data,links=[{'type':'derive','target':ref(source_snapshot)}])
    source_model=by_ref[('cube.system-model.active',SOURCE_REVISION)]
    model_data=copy.deepcopy(source_model['data'])
    model_data.update(review_meta,supersedes=ref(source_model),simulation_snapshot_ref=ref(snapshot),source_snapshot_ref=ref(source_snapshot),scope='Human-reviewed Cube requirement wording and function/component allocations; open items and verification gaps remain explicit.',baseline_ref=ref('cube.baseline.requirements-allocation',REVISION),architecture_ref=ref(decision))
    model_data['translations']['ja']['scope']='人によるレビュー済みのCube要求文と機能・構成品への割当。未解決事項と未検証項目は明示したままとする。'
    add('cube.system-model.active','system_model',model_data)
    add('cube.baseline.requirements-allocation','baseline',{
        'name':'Reviewed Cube requirements and allocation baseline','reason':AUTHORIZATION+'; '+SCOPE_REPLY,
        'scope':'reviewed_requirements_and_allocations_not_physical_acceptance','review_decision_ref':ref(decision),
        'members':[{**ref(r),'sha256':digest(r)} for r in updates],
        'physical_verified':False,'adopted_design_baseline':False,
    })
    return updates


def write_documents(records, repository_root=None):
    root=repository_root or ROOT.parents[1]
    selected=sorted((r for r in records if r['kind']=='requirement' and r['revision']==REVISION),key=lambda r:r['id'])
    if len(selected)!=29:raise ValueError('Reviewed requirement records are incomplete')
    for language in ['en','ja']:
        en=language=='en'
        lines=['# '+('Balancing Cube reviewed requirements' if en else 'Balancing Cubeのレビュー済み要求'),'',f'`{REVISION}` · human review: 2026-10-19 · reviewer: hirototamura','',('The human accepted the requirement wording and the function/component allocation split. Verification results, unresolved items and historical evidence retain their separate states.' if en else '要求文と機能・構成品への割当は人によるレビュー済み。検証結果、未解決事項、過去の証拠の適用範囲は別に管理する。'),'',f'Canonical baseline: `cube.baseline.requirements-allocation@{REVISION}`.','',('There are 22 obligations and 7 organizational groups. Open numerical limits and verification procedures remain open; review is not a hardware pass.' if en else '22個の義務と7個の整理用グループを含む。未確定の数値限界と検証手順は未確定のままであり、レビューは実機試験の合格を意味しない。'),'','Regenerate: `python projects/balancing-cube/review_requirements.py --write-docs`.','']
        for r in selected:
            d=r['data'];t=d if en else d['translations']['ja']
            lines += [f"## {r['id']}: {t['name']}",'',f"`{r['id']}@{REVISION}` · reviewed · human_reviewed · {d.get('verification_status','not_applicable')}",'']
            if t.get('statement'):lines += [t['statement'],'']
            if t.get('rationale'):lines += [t['rationale'],'']
            if d.get('record_role')=='requirement':
                lines += [('Acceptance / 合否基準: ')+json.dumps(d['acceptance_criteria'],ensure_ascii=False),'','Allocation: '+', '.join(l['target']['id'] for l in r['links'] if l['type']=='allocate'),'']
            if d.get('unresolved_items'):lines += ['Open items / 未解決事項:']+[f"- {u.get('id','')}: {u.get('description','')}" for u in (d['unresolved_items'] if en else t.get('unresolved_items',d['unresolved_items']))]+['']
        (root/f'docs/{language}/balancing_cube_requirements.md').write_text('\n'.join(lines).rstrip()+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--store',type=Path,default=ROOT/'store')
    parser.add_argument('--write-docs',action='store_true')
    args=parser.parse_args()
    history=load_records(args.store)
    proposal=json.loads(PROPOSAL_PATH.read_text())
    updates=build_review(history,proposal)
    result=Store(args.store).import_records(updates)
    if args.write_docs:write_documents(updates)
    print(json.dumps({'review_revision':REVISION,'records':len(updates),'import':result},indent=2))

if __name__=='__main__':main()
