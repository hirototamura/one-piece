import json
import shutil
import subprocess

import pytest

from onepiece import Store, make_record, ref
from onepiece.report import report


def _run_report_javascript(html, expression):
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required to execute report JavaScript")
    data = json.loads(html.split('<script type="application/json" id="data">')[1].split('</script>')[0])
    script = html.split('<script>')[1].split('</script>')[0]
    harness = r"""
const {data,script,expression}=JSON.parse(require('node:fs').readFileSync(0,'utf8'));
const elements=new Map(),all=new Set(['#graph-focus','#param-kind','#param-owner','#design-status','#design-era']);
function element(selector){
  if(!elements.has(selector))elements.set(selector,{
    value:all.has(selector)?'all':'',checked:false,innerHTML:'',textContent:'',className:'',style:{},attributes:{},
    setAttribute(name,value){this.attributes[name]=value},querySelectorAll(){return []},
    getContext(){return {}},addEventListener(){}
  });
  return elements.get(selector);
}
element('#data').textContent=JSON.stringify(data);
global.document={getElementById:id=>element('#'+id),querySelector:element};
global.window={addEventListener(){}};
global.requestAnimationFrame=()=>{};
process.stdout.write(JSON.stringify(eval(script+'\n'+expression)));
"""
    result = subprocess.run([node, "-e", harness],
                            input=json.dumps({"data": data, "script": script, "expression": expression}),
                            text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


def test_report_uses_store_and_escapes_imported_text(tmp_path):
    store = Store(tmp_path / "store")
    payload = "</script><script>window.untrusted=true</script>"
    store.import_records([make_record(project_id="example", id="req", kind="requirement",
                                     data={"name": payload, "value": None, "unit": "m", "status": "draft"})])
    output = report(store, tmp_path / "report", "example")
    text = output.read_text()
    assert payload not in text
    assert "\\u003c/script>" in text
    assert "derive" in text and "constrain" in text and "context.json" in text
    context = json.loads((output.parent / "context.json").read_text())
    assert context["example"] == store.context("example")
    assert "新しい反復は固定刻み幅でCPU/GPUを照合" in text


def test_report_pins_system_snapshot_and_separates_statement_status(tmp_path):
    store = Store(tmp_path / "store")
    fixed = make_record(project_id="cube", id="cube.simulation.snapshot", kind="simulation_snapshot",
                        revision="fixed-dt-mvp-1", data={"model": {}, "context_refs": {}})
    child = make_record(project_id="cube", id="acceptance.snapshot", kind="simulation_snapshot",
                        created_at="2099-01-01T00:00:00+00:00", data={"model": {"wrong": True}})
    mission = make_record(project_id="cube", id="M-VERTEX", kind="requirement",
                          data={"status": "confirmed", "physical_verified": None})
    store.import_records([fixed, child, mission])
    output = report(store, tmp_path / "report", "cube")
    html = output.read_text()
    data = json.loads(html.split('<script type="application/json" id="data">')[1].split('</script>')[0])
    assert data["selected_snapshots"]["cube"] == {"id": fixed["id"], "revision": fixed["revision"]}
    assert data["contexts"]["cube"]["snapshot_ref"] == data["selected_snapshots"]["cube"]
    assert "要求文の状態 / 実機検証" in html
    assert "（検証結果ではない）" in html
    assert "合格フラグではない" in html
    assert "stage+' / '+origin(r.data.verification_origin)" in html
    assert "id:snap.id,revision:snap.revision" in html


def test_context_and_report_follow_explicit_active_model(tmp_path):
    store = Store(tmp_path / "store")
    fixed = make_record(project_id="cube", id="cube.simulation.snapshot", kind="simulation_snapshot",
                        revision="fixed-dt-mvp-2", data={"context_refs": {}})
    active = make_record(project_id="cube", id="cube.system-model.active", kind="system_model",
                         data={"simulation_snapshot_ref": {"id": fixed["id"], "revision": fixed["revision"]}})
    store.import_records([fixed, active])
    assert store.context("cube")["snapshot_ref"]["revision"] == "fixed-dt-mvp-2"
    output = report(store, tmp_path / "report", "cube")
    context = json.loads((output.parent / "context.json").read_text())
    assert context["cube"]["snapshot_ref"] == store.context("cube")["snapshot_ref"]


def test_current_projection_pins_campaign_summary_and_reference_versions(tmp_path):
    from onepiece.store import current_records
    old = make_record(project_id="cube", id="summary", revision="1", kind="campaign_summary", data={"prior46": {"pass": 31}})
    new = make_record(project_id="cube", id="summary", revision="2", kind="campaign_summary", created_at="2099-01-01T00:00:00+00:00", data={"prior46": {"pass": 0}})
    design = make_record(project_id="cube", id="best", revision="1", kind="design")
    changed = make_record(project_id="cube", id="best", revision="2", kind="design", created_at="2099-01-01T00:00:00+00:00")
    snapshot = make_record(project_id="cube", id="snapshot", kind="simulation_snapshot", data={
        "context_refs": {"campaign_summary": {"id": "summary", "revision": "1"}},
        "comparison_design_ref": {"id": "best", "revision": "1"}})
    records = [old, new, design, changed, snapshot]
    projected = current_records(records, snapshot)
    assert next(r for r in projected if r['id'] == 'summary') == old
    assert next(r for r in projected if r['id'] == 'best') == design


def test_report_displays_translated_drafts_without_reusing_old_revision_evidence(tmp_path):
    store = Store(tmp_path / "store")
    old_product = make_record(project_id="cube", id="cube.system", kind="product", revision="source",
                              data={"name": "Historical cube"}, created_at="2026-01-01T00:00:00+00:00")
    product = make_record(project_id="cube", id="cube.system", kind="product", revision="english",
                          data={"name": "Balancing cube", "translations": {"ja": {"name": "倒立キューブ"}}},
                          created_at="2026-10-11T00:00:00+00:00")
    original = make_record(project_id="cube", id="R-HOLD", kind="requirement", revision="source",
                           data={"name": "Historical hold", "status": "confirmed"},
                           links=[{"type": "allocate", "target": {"id": old_product["id"], "revision": old_product["revision"]}}],
                           created_at="2026-01-01T00:00:00+00:00")
    english = "The cube must keep vertex contact for 30 s."
    japanese = "キューブは30 sの間、頂点の接触を維持しなければならない。"
    revised = make_record(project_id="cube", id="R-HOLD", kind="requirement", revision="english",
                          data={"name": "Vertex contact", "statement": english, "status": "draft",
                                "source_status": "confirmed", "verification_status": "not_run",
                                "verification_method": "test", "rationale": "Keep the required contact.",
                                "conditions": ["Use the approved hardware configuration."],
                                "acceptance_criteria": {"duration": {"value": 30, "unit": "s"}},
                                "unresolved_items": [{"id": "OPEN-1", "description": "Define the contact tolerance.", "owner": "human"}],
                                "translations": {"ja": {"name": "頂点接触", "statement": japanese,
                                                         "rationale": "要求した接触を維持する。",
                                                         "conditions": ["承認した実機構成を使用する。"],
                                                         "acceptance_criteria": {"保持時間": {"value": 30, "unit": "s"}},
                                                         "unresolved_items": [{"id": "OPEN-1", "description": "接触の許容差を定義する。", "owner": "human"}]}}},
                          created_at="2026-10-11T00:00:00+00:00")
    evidence = make_record(project_id="cube", id="old.evidence", kind="evaluation",
                           links=[{"type": "verify", "target": {"id": original["id"], "revision": original["revision"]}}])
    current_evidence = make_record(project_id="cube", id="current.evidence", kind="analysis_result",
                                   links=[{"type": "verify", "target": {"id": revised["id"], "revision": revised["revision"]}}])
    planned = make_record(project_id="cube", id="hold.test", kind="verification_case",
                          data={"requirement_refs": [{"id": revised["id"], "revision": revised["revision"]}], "status": "planned"})
    group = make_record(project_id="cube", id="cube.req.system", kind="requirement",
                        data={"name": "System requirements", "record_role": "requirement_group", "status": "draft",
                              "translations": {"ja": {"name": "システム要求"}}})
    store.import_records([old_product, product, original, revised, evidence, current_evidence, planned, group])
    html = report(store, tmp_path / "report", "cube").read_text()
    data = json.loads(html.split('<script type="application/json" id="data">')[1].split('</script>')[0])
    view = data["requirement_views"]['["cube","R-HOLD","english"]']
    assert view["english"]["statement"] == english
    assert view["japanese"]["statement"] == japanese
    assert view["english"]["acceptance_criteria"]["duration"] == {"value": 30, "unit": "s"}
    assert view["japanese"]["unresolved_items"][0]["id"] == "OPEN-1"
    assert view["statement_status"] == "draft" and view["source_status"] == "confirmed"
    assert view["verification_status"] == "not_run"
    assert view["evidence_refs"] == [{"id": "current.evidence", "revision": "1"}]
    assert view["count_scope"] == "current_record_projection_only"
    assert view["historical_evidence_count"] == 1
    assert view["historical_target_refs"] == [{"id": "R-HOLD", "revision": "source"}]
    assert view["planned_case_refs"] == [{"id": "hold.test", "revision": "1"}]
    assert data["requirement_views"]['["cube","cube.req.system","1"]']["is_group"] is True
    assert data["requirement_views"]['["cube","cube.req.system","1"]']["english"]["statement"] is None
    # Historical graph nodes use their own record revision and retain allocation.
    trace = {(r["id"], r["revision"]): r for r in data["trace_records"]}
    assert trace[("R-HOLD", "source")] == original
    assert trace[("cube.system", "source")] == old_product
    assert ("R-HOLD", "english") not in trace
    assert data["missing_trace_targets"] == []
    assert 'lang="en"' in html and 'lang="ja"' in html
    assert "旧版への証拠を現在版へ付け替えません" in html


def test_trace_projection_does_not_replace_missing_revision_with_current_id():
    from onepiece.report import _trace_projection

    current = make_record(project_id="cube", id="R-HOLD", kind="requirement", revision="current")
    source = make_record(project_id="cube", id="test", kind="test_case",
                         links=[{"type": "verify", "target": {"id": "R-HOLD", "revision": "missing"}}])
    historical, missing = _trace_projection([current, source], [current, source])
    assert historical == []
    assert missing == [{"source": {"id": "test", "revision": "1"}, "project_id": "cube", "type": "verify",
                        "target": {"id": "R-HOLD", "revision": "missing"}}]


def test_multi_project_replay_resolves_design_and_provenance_within_its_project(tmp_path):
    import hashlib
    store = Store(tmp_path / 'store')
    records, objects, project_hashes = [], {}, {}
    for project, side in [('alpha', .18), ('beta', .32)]:
        design = make_record(project_id=project, id='same-design', revision='1', kind='design_candidate',
                             data={'mechanical_config': {'physics': {'cube_side_m': side}}})
        trial = {'domain_id': 'nominal', 'condition_id': 'hold', 'seed': 42,
                 'screening': [], 'physics_timestep_s': .001, 'backend': {'backend': 'native_mujoco_cpu'},
                 'frames': [{'time_s': .001, 'position_m': [side, 0, 0]}], 'summary': {'score': side}}
        result = {'candidate_id': 'same-design', 'stage': 'validation', 'records': [trial]}
        content = json.dumps(result).encode()
        sha = hashlib.sha256(content).hexdigest()
        objects[sha] = content
        project_hashes[project] = sha
        evaluation = make_record(project_id=project, id='same-run', kind='simulation_run',
            data={'candidate_ref': {'id': 'same-design', 'revision': '1'}},
            artifacts=[{'path': 'result.json', 'sha256': sha, 'size_bytes': len(content)}])
        records.extend([design, evaluation])
    store.import_records(records, artifact_objects=objects)
    output = report(store, tmp_path / 'report')
    data = json.loads(output.read_text().split('<script type="application/json" id="data">')[1].split('</script>')[0])
    cases = data['replay']['cases']
    assert len(cases) == 2 and len({case['id'] for case in cases}) == 2
    assert set(data['trial_views']) == {'["alpha","same-run","1"]', '["beta","same-run","1"]'}
    for case in cases:
        side = .18 if case['project_id'] == 'alpha' else .32
        assert case['geometry']['cube_side_m'] == side
        assert case['frames'][0]['position_m'][0] == side
        assert case['trajectory_origin']['project_id'] == case['project_id']
        assert case['trajectory_origin']['artifact_sha256'] == project_hashes[case['project_id']]


def test_report_current_projection_uses_timezone_instants(tmp_path):
    store = Store(tmp_path / 'store')
    older = make_record(project_id='cube', id='req', revision='1', kind='requirement',
        created_at='2026-01-01T01:00:00+02:00', data={'statement': 'Older statement'})
    newer = make_record(project_id='cube', id='req', revision='2', kind='requirement',
        created_at='2025-12-31T23:30:00Z', data={'statement': 'Newer statement'})
    store.import_records([older, newer])
    output = report(store, tmp_path / 'report')
    data = json.loads(output.read_text().split('<script type="application/json" id="data">')[1].split('</script>')[0])
    assert data['records'] == [newer]


def test_report_keeps_overlapping_project_views_and_evaluations_separate(tmp_path):
    store = Store(tmp_path / "store")
    records = []
    for project, status in [("alpha", "draft"), ("beta", "reviewed")]:
        requirement = make_record(project_id=project, id="R-HOLD", kind="requirement",
                                  data={"statement": project + " statement", "status": status})
        design = make_record(project_id=project, id="shared-design", kind="design")
        evidence = make_record(project_id=project, id="shared-evidence", kind="evaluation",
                               data={"candidate_id": design["id"], "design_ref": ref(design),
                                     "verification_origin": project, "summary": {}},
                               links=[{"type": "verify", "target": ref(requirement)}])
        fresh = make_record(project_id=project, id="fresh-design", kind="design_candidate")
        run = make_record(project_id=project, id="shared-run", kind="simulation_run",
                          data={"candidate_ref": ref(fresh), "numeric_gpu_verified": project == "alpha",
                                "all_screening_passed": True})
        product = make_record(project_id=project, id="shared-owner", kind="product", data={"name": "Owner"})
        parameter = make_record(project_id=project, id="shared-param", kind="parameter",
                                product_node=product['id'], data={"name": project + " parameter"})
        records.extend([requirement, design, evidence, fresh, run, product, parameter])
    records.append(make_record(project_id="alpha", id="summary", kind="campaign_summary",
                               data={"best": {"original_confirmed": ["shared-design"]},
                                     "prior46": {"ids": ["shared-design"]}}))
    store.import_records(records)
    html = report(store, tmp_path / "report").read_text()
    views = _run_report_javascript(html, """
['alpha','beta'].map(project=>{
  const requirement=byKey.get(key({project_id:project,id:'R-HOLD',revision:'1'}));
  reqDetail(requirement);
  const design=byKey.get(key({project_id:project,id:'shared-design',revision:'1'}));
  const fresh=byKey.get(key({project_id:project,id:'fresh-design',revision:'1'}));
  designDetail(design);
  $('#param-owner').value=idKey(project,'shared-owner');paramRows();
  $('#design-prior').checked=true;designRows();
  return {project,view:reqView(requirement),detail:$('#reqdetail').innerHTML,bestProject:best.project_id,
          evaluations:evalFor(design).map(e=>e.project_id),freshStatus:fresh.data.status,
          selectors: ['#graph-design','#compare-base','#compare-target'].map(s=>$(s).innerHTML),
          designDetail:$('#design-detail').innerHTML, requirementRows:$('#reqrows').innerHTML,
          ownerOptions:$('#param-owner').innerHTML, parameterRows:$('#paramrows').innerHTML,
          priorDesigns:shown.map(r=>r.project_id),designRows:$('#designrows').innerHTML};
})
""")
    for view, status in zip(views, ["draft", "reviewed"]):
        project = view["project"]
        assert view["view"]["english"]["statement"] == project + " statement"
        assert view["view"]["statement_status"] == status
        assert view["evaluations"] == [project]
        assert view["bestProject"] == "alpha"
        assert all(project + " / shared-design · 1" in options for options in view["selectors"])
        assert project + " / shared-design @1" in view["designDetail"]
        assert project + " / R-HOLD" in view["requirementRows"]
        assert project + " / R-HOLD @1" in view["detail"]
        assert project + " / Owner" in view["ownerOptions"]
        assert project + " parameter" in view["parameterRows"]
        assert ("beta" if project == "alpha" else "alpha") + " parameter" not in view["parameterRows"]
        assert view["priorDesigns"] == ["alpha"]
        assert "alpha / shared-design @1" in view["designRows"]
        assert "beta / shared-design @1" not in view["designRows"]
        assert project + ": 1" in view["detail"]
        assert ("beta" if project == "alpha" else "alpha") + ": 1" not in view["detail"]
        assert view["freshStatus"] == ("new_gpu_confirmed_pass" if project == "alpha"
                                        else "cpu_only_provisional_pass")


def test_report_renders_current_and_historical_function_allocation_chains(tmp_path):
    store = Store(tmp_path / "store")
    records = []
    for revision, date in [("old", "2026-01-01"), ("current", "2026-01-02")]:
        common = {"project_id": "cube", "revision": revision, "created_at": date + "T00:00:00Z"}
        product = make_record(**common, id="component", kind="product")
        function = make_record(**common, id="balance", kind="function",
                               links=[{"type": "allocate", "target": ref(product)}])
        requirement = make_record(**common, id="R-HOLD", kind="requirement",
                                  links=[{"type": "allocate", "target": ref(function)}])
        if revision == "current":
            requirement["links"].append({"type": "derive", "target": {"id": "R-HOLD", "revision": "old"}})
        records.extend([product, function, requirement])
    store.import_records(records)
    html = report(store, tmp_path / "report").read_text()
    rendered = _run_report_javascript(html, """
({graph:$('#graph').innerHTML,note:$('#graph-trace-note').innerHTML,
  bounds:$('#graph').attributes.viewBox,trace:D.trace_records.map(r=>key(r))})
""")
    for revision in ("old", "current"):
        key = json.dumps(["cube", "balance", revision], separators=(",", ":")).replace('"', '&quot;')
        assert 'data-node="' + key + '"' in rendered["graph"]
    assert rendered["graph"].count('marker-end="url(#arrow-allocate)"') == 4
    assert "表示を省略した関係" not in rendered["note"]
    assert '["cube","balance","old"]' in rendered["trace"]
    assert rendered["bounds"].startswith("0 0 1440 ")
