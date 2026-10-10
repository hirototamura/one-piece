import json

from onepiece import Store, make_record
from onepiece.report import report


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
