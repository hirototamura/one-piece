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
