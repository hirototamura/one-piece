"""Exact-revision satisfaction intents; historical claims are never carried forward."""
from __future__ import annotations


def project_claims(records, models):
    cube = models["balancing_cube"]
    target_refs = {(r["id"], r["revision"]) for r in cube["requirements"]}
    previous_revision = cube["model"].get("supersedes", {}).get("revision")
    visible_refs = target_refs | {(r["id"], previous_revision) for r in cube["requirements"]}
    sources = {key: f"{record['project_id']}:{key[0]}@{key[1]}" for key, record in records.items()}
    designs=[];historical=[]
    for key,record in sorted(records.items()):
        if record.get('kind') not in ('design','design_candidate','design_proposal'):continue
        links=[link for link in record.get('links',[]) if link.get('type')=='satisfy' and (link.get('target',{}).get('id'),link.get('target',{}).get('revision')) in visible_refs]
        if not links:continue
        body=record.get('data',{})
        runs=[r for r in records.values() if r.get('kind')=='simulation_run' and r.get('data',{}).get('candidate_ref')=={'id':key[0],'revision':key[1]}]
        results=[]
        for run in sorted(runs,key=lambda r:(r['id'],r['revision'])):
            results.append({'id':run['id'],'revision':run['revision'],'kind':run['kind'],'data':run['data'],'source':sources[(run['id'],run['revision'])]})
        short=record['id'].removeprefix('cube-').split('.')[0][:8]
        hypothesis=body.get('proposal',{}).get('hypothesis','')
        description=body.get('description') or ('Frozen reference mechanics and controller settings used for numerical comparison.' if hypothesis.startswith('Frozen SSOT numerical comparison') else hypothesis)
        item={'id':key[0],'revision':key[1],'kind':record['kind'],'name':body.get('name') or f'Reference candidate · {short}','description':description,'source_hypothesis':hypothesis,'physical_verified':body.get('physical_verified'),'input_digest':body.get('input_digest'),'claim_scope':'Design intent only; not physical verification.','links':links,'numerical_results':results,'source':sources[key],'source_record':record}
        current=[l for l in links if (l['target']['id'],l['target']['revision']) in target_refs]
        previous=[l for l in links if l not in current]
        if current:designs.append({**item,'links':current})
        if previous:historical.append({**item,'links':previous})
    result={'base_model_ref':{'id':cube['model']['id'],'revision':cube['model']['revision']},'selection_rule':'Only source-recorded satisfy links to the exact displayed revision appear in the current graph. Historical claims retain their original targets.','designs':designs,'historical_designs':historical,'requirements_with_claims':sorted({link['target']['id'] for d in designs for link in d['links']}),'unique_design_inputs':len({d.get('input_digest') or f"{d['id']}@{d['revision']}" for d in designs})}
    return result
