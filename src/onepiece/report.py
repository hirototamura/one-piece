"""Offline human view of the same versioned records supplied to engineering agents."""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from .store import current_records


def _json(value):
    # JSON is data, never executable source, including imported document content.
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def _trace_projection(records, history):
    """Keep exact revision targets separate from the current display projection."""
    identity = lambda r: (r["project_id"], r["id"], r["revision"])
    current = {identity(r): r for r in records}
    all_records = {identity(r): r for r in history}
    historical = {}
    missing = []
    graph_kinds = {"requirement", "product", "design", "design_candidate", "evaluation",
                   "simulation_run", "test_case", "verification_case", "specification", "parameter"}
    queue = [r for r in records if r["kind"] in graph_kinds]
    for record in queue:
        for edge in record["links"]:
            target = edge["target"]
            target_key = (record["project_id"], target["id"], target["revision"])
            if target_key in current or target_key in historical:
                continue
            found = all_records.get(target_key)
            if found is None:
                missing.append({"source": {"id": record["id"], "revision": record["revision"]},
                                "project_id": record["project_id"], "type": edge["type"], "target": target})
            elif found["kind"] in graph_kinds:
                historical[target_key] = found
                queue.append(found)
    return list(historical.values()), missing


def _requirement_views(records):
    """A report view, not a second source for requirement text or verification."""
    verified = {}
    for record in records:
        for edge in record["links"]:
            if edge["type"] == "verify":
                target = edge["target"]
                verified.setdefault((record["project_id"], target["id"], target["revision"]), []).append(record)
    views = {}
    fields = ("name", "statement", "rationale", "conditions", "acceptance_criteria", "unresolved_items")
    for record in records:
        if record["kind"] != "requirement":
            continue
        data = record["data"]
        linked = verified.get((record["project_id"], record["id"], record["revision"]), [])
        historical = [(target, evidence) for target, evidence in verified.items()
                      if target[:2] == (record["project_id"], record["id"]) and target[2] != record["revision"]]
        planned = [r for r in records if r["project_id"] == record["project_id"]
                   and r["kind"] in {"verification_case", "test_case"}
                   and {"id": record["id"], "revision": record["revision"]} in r["data"].get("requirement_refs", [])]
        views[record["id"] + "@" + record["revision"]] = {
            "english": {field: data.get(field) for field in fields},
            "japanese": data.get("translations", {}).get("ja", {}),
            "is_group": data.get("record_role") == "requirement_group",
            "statement_status": data.get("status"), "source_status": data.get("source_status"),
            "verification_status": data.get("verification_status", "not_recorded"),
            "verification_method": data.get("verification_method"),
            "count_scope": "current_record_projection_only",
            "planned_case_refs": [{"id": r["id"], "revision": r["revision"]} for r in planned],
            "evidence_refs": [{"id": r["id"], "revision": r["revision"]} for r in linked],
            "historical_evidence_count": sum(len(evidence) for _, evidence in historical),
            "historical_target_refs": [{"id": target[1], "revision": target[2]} for target, _ in historical],
        }
    return views


def report(store, output: str | Path, project_id: str | None = None) -> Path:
    output = Path(output).expanduser().resolve()
    if output.suffix.lower() != ".html":
        output = output / "index.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    history = store.records(project_id)
    projects = sorted({r["project_id"] for r in history})
    contexts = {}
    selected_snapshots = {}
    records = []
    for project in projects:
        project_history = [r for r in history if r["project_id"] == project]
        active = next((r for r in current_records(project_history) if r["id"] == "cube.system-model.active"), None)
        chosen = active["data"]["simulation_snapshot_ref"] if active else {"id": "cube.simulation.snapshot", "revision": "fixed-dt-mvp-1"}
        snapshot = next((r for r in project_history if r["id"] == chosen["id"] and r["revision"] == chosen["revision"]), None)
        records.extend(current_records(project_history, snapshot))
        if snapshot:
            selected_snapshots[project] = chosen
        contexts[project] = store.context(project, max_designs=5, max_evidence=8,
            kinds=["design", "design_candidate", "simulation_run", "design_policy", "iteration", "analysis_result"],
            snapshot_ref=chosen) if snapshot else store.context(project)
    assets = []
    replay = {"cases": []}
    trial_views = {}
    new_replays = []
    by_ref = {(r["id"], r["revision"]): r for r in records}
    for record in records:
        for artifact in record["artifacts"]:
            obj = store.artifact_path(artifact)
            name = Path(artifact["path"]).name
            # Every link remains usable when only the generated report folder
            # is moved or distributed. Canonical bytes stay in the Store.
            target = output.parent / "assets" / artifact["sha256"][:16] / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(obj, target)
            url = target.relative_to(output.parent).as_posix()
            assets.append({**artifact, "record_id": record["id"], "url": url})
            if record["id"] == "cube.artifact.replay":
                replay = json.loads(obj.read_text(encoding="utf-8"))
            if record["kind"] == "simulation_run" and name == "result.json":
                result = json.loads(obj.read_text(encoding="utf-8"))
                trials = result.get("records", [])
                trial_views[record["id"] + "@" + record["revision"]] = [
                    {"domain_id": t["domain_id"], "condition_id": t["condition_id"],
                     "seed": t["seed"], "trials": 1,
                     "failed_trials": int(any(not c["passed"] for c in t["screening"])),
                     "criteria": {c["metric"]: 1 for c in t["screening"] if not c["passed"]}}
                    for t in trials]
                reference = record["data"].get("candidate_ref") or {}
                design = by_ref.get((reference.get("id"), reference.get("revision")))
                if trials and design and trials[0].get("frames"):
                    trial = trials[0]
                    fields = {"time_s", "position_m", "quaternion_wxyz", "wheel_angle_rad",
                              "tilt_total_deg", "pivot_displacement_mm"}
                    new_replays.append({
                        "id": record["id"], "label": "新規固定dt CPU · " + result["candidate_id"] + " / " + result["stage"],
                        "candidate_id": result["candidate_id"], "domain_id": trial["domain_id"],
                        "condition_id": trial["condition_id"], "seed": trial["seed"],
                        "physics_timestep_s": trial["physics_timestep_s"],
                        "used_half_timestep_adjudication": False,
                        "geometry": design["data"]["mechanical_config"]["physics"],
                        "frames": [{k: v for k, v in f.items() if k in fields} for f in trial["frames"]],
                        "trajectory_origin": {"record_ref": reference, "evaluation_id": record["id"],
                                              "artifact_sha256": artifact["sha256"], "backend": trial["backend"]},
                        "source_summary": trial["summary"], "summary": trial["summary"],
                        "summary_comparison": "Rendered from the saved native CPU trajectory; no additional physics execution",
                    })
    replay["cases"] = replay.get("cases", []) + new_replays[-4:]
    # Context JSON is inspectable: bounded evidence is explicit; full registry view
    # below is a separate query, never silently presented as the LLM input.
    (output.parent / "context.json").write_text(json.dumps(contexts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    historical_targets, missing_targets = _trace_projection(records, history)
    data = {"records": records, "contexts": contexts, "artifacts": assets, "selected_snapshots": selected_snapshots,
            "trace_records": historical_targets, "missing_trace_targets": missing_targets,
            "requirement_views": _requirement_views(records),
            "canonical_record_count": len(history),
            "replay": replay, "trial_views": trial_views, "integrity": store.check(project_id)}
    output.write_text(_HTML.replace("__DATA__", _json(data)), encoding="utf-8")
    return output


_HTML = r'''<!doctype html>
<html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>One Piece · Balancing Cube system model</title>
<style>
:root{--ink:#182532;--muted:#627281;--line:#d5dfe7;--bg:#f4f6f8;--accent:#165e90;--good:#28734b;--bad:#a43d38;--warn:#98661d}*{box-sizing:border-box}body{margin:0;color:var(--ink);background:var(--bg);font:14px/1.65 system-ui,-apple-system,"Yu Gothic",sans-serif}main,header>div,nav>div{max-width:1440px;margin:auto;padding:0 28px}header{background:white;padding:28px 0 23px;border-bottom:1px solid var(--line)}h1{font-size:29px;letter-spacing:-.03em;margin:0}h2{font-size:22px;margin:0 0 8px}h3{font-size:16px;margin:0 0 9px}p{margin:5px 0 12px}a{color:var(--accent);text-underline-offset:3px}nav{position:sticky;top:0;background:#fffffff2;z-index:5;border-bottom:1px solid var(--line)}nav>div{display:flex;gap:23px;overflow:auto;white-space:nowrap;padding-top:13px;padding-bottom:13px}nav a{text-decoration:none;font-size:12px}section{padding:30px 0 5px;scroll-margin-top:65px}.muted,small{color:var(--muted)}.note{border-left:3px solid var(--accent);background:#eaf2f8;padding:12px 15px;font-size:12px}.warn{color:var(--warn)}.good{color:var(--good)}.bad{color:var(--bad)}.panel{background:white;border:1px solid var(--line);padding:20px;border-radius:8px}.row{display:flex;gap:12px;flex-wrap:wrap;align-items:center}.grid{display:grid;grid-template-columns:1.3fr 1fr;gap:18px}.grid>*{min-width:0}.row>*{max-width:100%;min-width:0}.panel{min-width:0}select{max-width:100%}.stats{display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin:15px 0}.stats strong{font-size:27px;display:block;font-weight:600}.stats span{font-size:12px;color:var(--muted)}button,input,select{font:inherit;padding:7px 9px;border:1px solid var(--line);border-radius:5px;background:white;color:var(--ink)}button,select{cursor:pointer}button:hover{color:var(--accent);border-color:var(--accent)}input[type=search]{width:235px}button:focus-visible,input:focus-visible,select:focus-visible,a:focus-visible{outline:3px solid #7db9e7;outline-offset:3px}.scroll{overflow:auto;max-height:510px}table{border-collapse:collapse;width:100%;font-size:12px;font-variant-numeric:tabular-nums}th,td{padding:9px 11px;border-bottom:1px solid #e5ebef;text-align:left;vertical-align:top}th{position:sticky;top:0;background:#f5f8fa;color:var(--muted);font-weight:600;white-space:nowrap}tr[data-key]{cursor:pointer}tr[data-key]:hover{background:#edf5fb}tr.selected{background:#eaf2f8}.mono{font:12px/1.6 ui-monospace,SFMono-Regular,monospace;overflow-wrap:anywhere}pre{font:11px/1.55 ui-monospace,monospace;background:#f5f8fa;padding:12px;overflow:auto;max-height:400px;white-space:pre-wrap}details{margin:10px 0}summary{cursor:pointer;color:var(--accent)}.badge{font-size:11px;display:inline-block;padding:2px 6px;background:#edf1f4;border-radius:4px}.graph-scroll{max-height:70vh;overflow:auto}.graph{width:100%;min-width:1200px;height:auto;display:block;background:#fbfcfd}.graph text{font:11px system-ui;fill:var(--ink)}.graph .node{cursor:pointer}.legend{display:flex;flex-wrap:wrap;gap:14px;font-size:11px;margin:12px 0}.legend i{display:inline-block;width:20px;height:3px;vertical-align:middle;margin-right:5px}.graph-detail{min-height:120px}.bars>div{display:grid;grid-template-columns:210px 1fr 70px;gap:10px;margin:8px 0;font-size:11px;align-items:center}.bars b{display:block;background:#c7dbe9;height:16px}.chart{width:100%;height:auto;display:block}.chart text{font:10px system-ui;fill:var(--muted)}.scene{height:420px;width:100%;display:block;touch-action:none;cursor:grab;background:#111b25}.frame-readout{display:flex;justify-content:space-between;font-size:12px}.timeline{border-left:2px solid var(--line);margin:14px 0;padding-left:16px}.timeline>div{padding:0 0 15px}.counts{display:flex;gap:24px;flex-wrap:wrap;margin:12px 0}.counts strong{font-size:21px;display:block}.diffchange{background:#fff4df}.parametername{min-width:210px}footer{padding:30px 0 45px;color:var(--muted);font-size:11px}@media(max-width:850px){main,header>div,nav>div{padding-left:16px;padding-right:16px}.grid{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}.scene{height:330px}.bars>div{grid-template-columns:130px 1fr 45px}h1{font-size:24px}}
</style>
<header><div><small>ONE PIECE ENGINEERING · VERSIONED SYSTEM MODEL</small><h1>要求から設計・検証まで、同じ記録を読む</h1><p class="muted">Balancing Cube · 既存のMuJoCo成果と、新しい設計反復の記録をつなぐシステムモデル</p><div class="row"><span id="integrity" class="badge"></span><span class="badge">OMG Systems Modeling API 1.0 · 注釈グラフ</span><a href="context.json">LLMへ渡すcontext.json</a></div></div></header>
<nav><div><a href="#overview">結果と範囲</a><a href="#system">システムモデル</a><a href="#requirements">要求と根拠</a><a href="#parameters">KDP・詳細設定</a><a href="#designs">設計差分</a><a href="#new-loop">新しい反復</a><a href="#history">反復と失敗</a><a href="#replay">3D再現</a><a href="#evidence">原本と出典</a></div></nav>
<main>
<section id="overview"><h2>数値確認と、実機の妥当性を分けて記録</h2><p class="muted">元のGPU・CPU確認と、追加CPUの刻み幅安定性確認は異なる検証経路です。要求・評価条件・採用baselineの確定は人間が行います。</p><div class="stats" id="stats"></div><div class="grid"><div class="panel"><h3>前回の46候補</h3><div id="prior" class="counts"></div><p class="muted">同じ46のIDを最後まで追跡。探索全合格62候補の44合格・9不合格・9保留とは別の母集団です。</p></div><div class="panel"><h3>最良の元GPU・CPU確認済み設計</h3><div id="best"></div></div></div><div class="note" style="margin-top:16px">実機忠実度・実機成功・電気エネルギー・温度予測は未確認です。固定した公開seedによる数値開発試験で、物理要求の承認や採用baselineを自動で確定しません。履歴のdt/2裁定は保存し、新しい反復は固定刻み幅でCPU/GPUを照合します。</div></section>
<section id="system"><h2>システムモデル</h2><p class="muted">要求・KDP・製品・設計・検証を版付き参照で結ぶ最小グラフです。関係を選び、ノードを押すと記録を確認できます。OMG Systems Modeling API 1.0の注釈グラフとして交換します。5関係は名前付きDependencyです。satisfyは設計意図の宣言で、合格の証拠ではありません。</p><div class="panel"><div class="row"><label>設計 <select id="graph-design"></select></label><label><input type="checkbox" id="graph-kdps"> KDPも表示（先頭17）</label><label>表示中心 <select id="graph-focus"><option value="all">全体</option><option value="cube.mechanical">機械</option><option value="cube.actuation">駆動</option><option value="cube.gnc">GNC</option><option value="cube.verification">検証</option></select></label></div><div class="legend" id="legend"></div><div class="graph-scroll" tabindex="0" role="region" aria-label="システムグラフのスクロール領域"><svg class="graph" id="graph" width="1200" height="550" viewBox="0 0 1200 550" role="img" aria-label="要求・設計・検証の関係グラフ"></svg></div><div id="graph-trace-note" class="muted"></div><div class="graph-detail" id="graph-detail"></div></div></section>
<section id="requirements"><h2>要求から検証根拠へ</h2><p class="muted">英語を正本とし、日本語を英語からの翻訳として表示します。改訂要求は人間の承認前の草案です。旧版の値・単位・出典・証拠は保持し、現在版の検証へ移し替えません。ISO/IEC/IEEE 29148:2018を第一参照とし、ASD-STE100の書き方を適用しています。規格への完全適合認証を示すものではありません。</p><div class="grid"><div class="panel scroll"><table><thead><tr><th>ID / 階層</th><th>英語正本 / 日本語訳</th><th>値・単位</th><th>要求文の状態 / 実機検証</th></tr></thead><tbody id="reqrows"></tbody></table></div><div class="panel" id="reqdetail"></div></div></section>
<section id="parameters"><h2>KDPと、シミュレータへ渡した詳細設定</h2><p class="muted">37 KDPの役割・由来・不確かさ・要求への対応を保持。詳細設定の値は固定snapshotのmodelが正本で、各leafはその欄への参照です。登録KDPとの差は明示し、上書きで隠しません。</p><div class="panel"><div class="row"><input id="param-search" type="search" placeholder="ID・名前・model_pathで検索" aria-label="パラメータ検索"><select id="param-kind"><option value="all">KDP + 詳細設定</option><option value="parameter">37 KDP</option><option value="model_parameter">詳細model設定</option></select><select id="param-owner"><option value="all">全製品</option></select><span id="param-count" class="muted"></span></div><div class="scroll"><table><thead><tr><th>ID / model_path</th><th>値</th><th>単位</th><th>役割・由来</th><th>不確かさ / 範囲 / 出典</th></tr></thead><tbody id="paramrows"></tbody></table></div><details><summary>固定snapshotと参照規約を表示</summary><pre id="snapshot-raw"></pre></details></div></section>
<section id="designs"><h2>設計を比較し、どの条件で失敗したかを見る</h2><div class="panel"><div class="row"><input type="search" id="design-search" placeholder="候補ID・部品系統" aria-label="候補検索"><select id="design-status"><option value="all">全状態</option><option value="confirmed_numerical_pass">数値確認合格</option><option value="confirmed_numerical_fail">数値確認不合格</option><option value="inconclusive_numerical_agreement">数値一致保留</option><option value="exploration_failed_screening">探索screen不合格</option><option value="cpu_only_provisional_pass">新規CPU暫定・合格</option><option value="cpu_only_provisional_fail">新規CPU暫定・不合格</option><option value="new_gpu_confirmed_pass">新規CPU/GPU確認合格</option></select><select id="design-era"><option value="all">既存 + 新規</option><option value="legacy">既存2048候補</option><option value="new">新しい反復の候補</option></select><label><input type="checkbox" id="design-prior">前回46のみ</label><span id="design-count" class="muted"></span></div><svg id="scatter" class="chart" viewBox="0 0 1000 240" aria-label="探索スコア対確認スコア"></svg><div class="scroll"><table><thead><tr><th>設計ID</th><th>部品系統</th><th>確認状態</th><th>確認経路</th><th>探索 / 確認</th></tr></thead><tbody id="designrows"></tbody></table></div></div><div class="grid" style="margin-top:18px"><div class="panel"><h3>設計差分</h3><div class="row"><label>比較元 <select id="compare-base"></select></label><label>対象 <select id="compare-target"></select></label></div><div id="diff"></div></div><div class="panel" id="design-detail"></div></div></section>
<section id="new-loop"><h2>新しいEN → PI → R → E反復</h2><p class="muted">環境と評価規約を固定し、LLMの設定提案を実行して、測定結果から探索方針データを更新します。CPUのみの実行をGPU確認済みへ昇格させません。</p><div id="offline-check"></div><div id="new-runs"></div></section>
<section id="history"><h2>反復履歴と失敗の根拠</h2><div class="grid"><div class="panel"><h3>反復・判断の記録</h3><div id="iterations" class="timeline"></div><details><summary>人間とLLMが読む現在のcontext</summary><pre id="context-raw"></pre></details></div><div class="panel"><h3>探索で違反した数値判定（重複計上あり）</h3><div id="failures" class="bars"></div><p class="muted">1試行で複数の閾値を超える場合があります。候補の詳細ではdomain・conditionごとの不合格数と、元CSVの抽出条件を確認できます。</p></div></div></section>
<section id="replay"><h2>保存した状態から描く3D再現</h2><p class="muted">固定入力を用いたnative MuJoCo CPU再現です。元GPU実行の録画ではありません。記録フレームを保持して表示し、失敗後の運動を生成しません。</p><div class="grid"><div class="panel"><div class="row"><select id="case" aria-label="再現ケース"></select><button id="play">再生</button><button id="step">1フレーム</button><button id="camera">視点リセット</button></div><canvas id="scene" class="scene" tabindex="0" aria-label="3D状態。ドラッグで回転、ホイールで拡大"></canvas><input type="range" id="frame" min="0" max="0" value="0" style="width:100%" aria-label="記録フレーム"><div class="frame-readout"><span id="replay-time"></span><span id="replay-state"></span></div><small>ドラッグで視点回転・ホイールで拡大。物理シミュレーションの再実行ではありません。</small></div><div class="panel"><h3 id="case-title"></h3><p id="case-source" class="muted"></p><div id="live"></div><svg id="replay-chart" class="chart" viewBox="0 0 600 230"></svg><details><summary>元の評価値と再現値</summary><pre id="case-raw"></pre></details></div></div></section>
<section id="evidence"><h2>原本・GNC解析・再生成の出典</h2><p class="muted">詳細な全試行、元SQLiteとWAL、旧HTML・動画・GNC資料は内容SHA-256付きartifactとして保存します。canonical記録は集計と参照を保持し、原本を変更しません。</p><div class="panel"><div id="primary-links" class="row"></div><div class="scroll"><table><thead><tr><th>原本</th><th>バイト数</th><th>SHA-256</th></tr></thead><tbody id="artifactrows"></tbody></table></div><details><summary>整合性検査と制限</summary><pre id="checks"></pre></details></div></section>
<footer>One Piece · versioned JSON is the source of truth. SQLite index / HTML are rebuildable views. Imported document text is data, never agent instructions.</footer></main>
<script type="application/json" id="data">__DATA__</script>
<script>
'use strict';const D=JSON.parse(document.getElementById('data').textContent),rs=D.records,$=s=>document.querySelector(s),esc=s=>String(s??'—').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),raw=v=>JSON.stringify(v,null,2),num=(v,n=3)=>typeof v==='number'?v.toLocaleString('ja-JP',{maximumFractionDigits:n}):'—',key=r=>r.id+'@'+r.revision,kinds=k=>rs.filter(r=>r.kind===k),byKey=new Map(rs.map(r=>[key(r),r])),byId=new Map(rs.map(r=>[r.id,r])),summary=kinds('campaign_summary').at(-1)?.data||{},counts=summary.overview?.counts||{},prior=new Set(summary.prior46?.ids||[]),sourceEvaluations=kinds('simulation_run'),newLoops=kinds('analysis_result').filter(r=>r.data.scenario==='balancing_cube'),legacyDesigns=kinds('design'),freshDesigns=kinds('design_candidate').map(normalizeDesign),designs=legacyDesigns.concat(freshDesigns),evals=kinds('evaluation').concat(sourceEvaluations.map(normalizeEvaluation)),reqs=kinds('requirement'),params=rs.filter(r=>['parameter','kdp','model_parameter'].includes(r.kind)),products=kinds('product'),snap=rs.find(r=>r.kind==='simulation_snapshot'&&Object.values(D.selected_snapshots).some(s=>r.id===s.id&&r.revision===s.revision)),labels={confirmed_numerical_pass:'数値確認合格',confirmed_numerical_fail:'数値確認不合格',inconclusive_numerical_agreement:'数値一致保留',exploration_failed_screening:'探索screen不合格',gpu_only_provisional_pass:'GPUのみ暫定',cpu_only_provisional_pass:'CPU暫定・screen合格',cpu_only_provisional_fail:'CPU暫定・screen不合格',new_gpu_confirmed_pass:'新規CPU/GPU確認合格',new_gpu_confirmed_fail:'新規CPU/GPU確認不合格'},origin=o=>o==='new_fixed_timestep_cpu'?'新規固定dt・CPUのみ暫定':o==='new_fixed_timestep_cpu_gpu'?'新規固定dt・CPU/GPU照合':o==='supplemental_native_cpu'?'追加CPU dt安定性（履歴）':o==='original_campaign'?'元GPU・CPU確認':o||'—';
$('#integrity').textContent=D.integrity.ok?'記録・出典の整合性検査: PASS':'整合性検査: 要確認';$('#integrity').className+=' '+(D.integrity.ok?'good':'bad');$('#stats').innerHTML=[[legacyDesigns.length,'既存探索候補の記録'],[freshDesigns.length,'新しい反復の候補'],[counts.original_confirmed_pass,'元GPU・CPU確認合格'],[counts.supplemental_confirmed_pass,'追加CPU安定性合格（履歴）'],['null','実機忠実度・物理成功']].map(([v,l])=>`<div><strong>${esc(v)}</strong><span>${esc(l)}</span></div>`).join('');$('#prior').innerHTML=Object.entries(summary.prior46?.status_counts||{}).sort((a,b)=>['confirmed_numerical_pass','confirmed_numerical_fail','inconclusive_numerical_agreement'].indexOf(a[0])-['confirmed_numerical_pass','confirmed_numerical_fail','inconclusive_numerical_agreement'].indexOf(b[0])).map(([s,v])=>`<div><strong>${v}</strong><small>${esc(labels[s]||s)}</small></div>`).join('');const bestId=summary.best?.original_confirmed?.[0],best=byId.get(bestId);$('#best').innerHTML=best?`<strong class="mono">${esc(bestId)}</strong><p>${esc(best.data.family)} · 同じ固定制御器を適用</p><p>探索11/12・確認12/12。採用baselineは未確定。</p><button id="open-best">設計差分を確認</button>`:'<p>確認済み設計の参照を記録していません。</p>';$('#snapshot-raw').textContent=raw(snap?{id:snap.id,revision:snap.revision,data:snap.data}:{});$('#context-raw').textContent=raw(D.contexts);$('#checks').textContent=raw({integrity:D.integrity,limitations:summary.limitations,null_unmeasured:summary.null_unmeasured,historical_policy_note:summary.historical_policy_note});
function normalizeDesign(r){let es=sourceEvaluations.filter(e=>e.data.candidate_ref?.id===r.id&&e.data.candidate_ref?.revision===r.revision),v=es.filter(e=>e.data.stage==='validation').at(-1),e=v||es.at(-1),d=r.data,p=d.proposal||{},gpu=e?.data.numeric_gpu_verified===true,pass=e?.data.all_screening_passed===true;return {...r,__source:r,data:{...d,family:p.family,parameters:p.parameters,physics:d.mechanical_config?.physics,actuation:d.mechanical_config?.actuation,hypothesis:p.hypothesis,parent_id:p.parent_id,status:gpu?(pass?'new_gpu_confirmed_pass':'new_gpu_confirmed_fail'):(pass?'cpu_only_provisional_pass':'cpu_only_provisional_fail'),validation_origin:gpu?'new_fixed_timestep_cpu_gpu':'new_fixed_timestep_cpu',history_only:false}}}
function normalizeEvaluation(r){let d=r.data,n=d.trial_count||0;return {...r,__source:r,data:{...d,candidate_id:d.candidate_ref?.id||d.candidate_id,design_ref:d.candidate_ref,verification_origin:d.numeric_gpu_verified?'new_fixed_timestep_cpu_gpu':'new_fixed_timestep_cpu',summary:{score:d.score,trials:n,passed_trials:Math.round(n*(d.screening_pass_fraction||0)),all_pass:d.all_screening_passed,numeric_verified:d.numeric_gpu_verified,numeric_cpu_verified:d.numeric_cpu_verified,gpu_state:d.gpu_state,agreement_state:d.agreement_state,failures:d.failure_metrics||{}},coverage:{actual:n,expected:n,complete:d.numeric_cpu_verified===true},conditions:D.trial_views[key(r)]||[]}}}
for(const r of [...freshDesigns,...evals])byKey.set(key(r),r);
const evalFor=r=>evals.filter(e=>e.data.candidate_id===r.id&&(!e.data.design_ref||e.data.design_ref.revision===r.revision)),stageEval=(r,s)=>evalFor(r).filter(e=>e.data.stage===s).at(-1),options=designs.map(r=>`<option value="${esc(key(r))}">${esc(r.id)} · ${esc(r.revision)}</option>`).join('');['#graph-design','#compare-base','#compare-target'].forEach(s=>$(s).innerHTML=options);function setSelect(s,id){let r=byId.get(id);if(r)$(s).value=key(r)}setSelect('#graph-design',bestId);setSelect('#compare-base','baseline');setSelect('#compare-target',bestId);
const edgeInfo={derive:['#536f91','子要求 → 親要求 / 同kindの祖先'],satisfy:['#31826d','設計・製品 → 要求（意図）'],verify:['#a05b3d','検証根拠 → 要求・test case'],allocate:['#8a6da5','要求・KDP → 担当製品'],constrain:['#a99035','要求・仕様 → 設定・設計']},enabled=new Set(Object.keys(edgeInfo));$('#legend').innerHTML=Object.entries(edgeInfo).map(([type,[c,l]])=>`<label><input type="checkbox" data-edge="${type}" checked><i style="background:${c}"></i>${type} · ${esc(l)}</label>`).join('');$('#legend').onchange=e=>{e.target.checked?enabled.add(e.target.dataset.edge):enabled.delete(e.target.dataset.edge);drawGraph()};
function graphLayout(columns){
  const height=Math.max(550,80+34*Math.max(1,...columns.map(column=>column.length))),xs=[125,360,565,775,1045],positions=new Map();
  columns.forEach((column,i)=>column.forEach((record,j)=>positions.set(key(record),[xs[i],40+(j+.5)*(height-80)/Math.max(1,column.length)])));
  return {height,positions};
}
const traceByKey=new Map([...(D.trace_records||[]),...rs].map(r=>[key(r),r])),historicalKeys=new Set((D.trace_records||[]).map(key));
function drawGraph(){
  const selected=byKey.get($('#graph-design').value),evidence=selected?evalFor(selected):[];
  let nodes=[...reqs,...products,...(selected?[selected]:[]),...evidence,...kinds('test_case'),...kinds('verification_case'),...kinds('specification')];
  if($('#graph-kdps').checked)nodes.push(...kinds('parameter').slice(0,17));
  const focus=$('#graph-focus').value;
  if(focus!=='all')nodes=nodes.filter(r=>r.product_node===focus||r.id==='M-VERTEX'||r.id==='cube.req.system'||r.id==='cube.system'||r===selected||evidence.includes(r));
  const included=new Set(nodes.map(key));
  // An edge can reach its saved revision only. Never substitute the current ID.
  for(let i=0;i<nodes.length;i++)for(const edge of nodes[i].links){
    const targetKey=key(edge.target),target=traceByKey.get(targetKey);
    if(enabled.has(edge.type)&&historicalKeys.has(targetKey)&&!included.has(targetKey)&&target){nodes.push(target);included.add(targetKey)}
  }
  const cols=[nodes.filter(r=>r.kind==='requirement'),nodes.filter(r=>r.kind==='parameter'),nodes.filter(r=>r.kind==='product'),nodes.filter(r=>['design','design_candidate'].includes(r.kind)),nodes.filter(r=>['evaluation','simulation_run','test_case','verification_case','specification'].includes(r.kind))],layout=graphLayout(cols),pos=layout.positions;
  $('#graph').setAttribute('viewBox','0 0 1200 '+layout.height);
  $('#graph').setAttribute('height',layout.height);
  let h='<defs>'+Object.entries(edgeInfo).map(([t,[c]])=>`<marker id="arrow-${t}" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="none" stroke="${c}"/></marker>`).join('')+'</defs>',omitted=[];
  for(const r of nodes)for(const edge of r.links){
    if(!enabled.has(edge.type))continue;
    const a=pos.get(key(r)),b=pos.get(key(edge.target));
    if(!a||!b){omitted.push(key(r)+' —'+edge.type+'→ '+key(edge.target));continue}
    const c=edgeInfo[edge.type][0];
    h+=`<path d="M${a[0]},${a[1]} C${(a[0]+b[0])/2},${a[1]} ${(a[0]+b[0])/2},${b[1]} ${b[0]},${b[1]}" fill="none" stroke="${c}" stroke-width="1" opacity=".35" marker-end="url(#arrow-${edge.type})"><title>${esc(key(r)+' —'+edge.type+'→ '+key(edge.target))}</title></path>`;
  }
  for(const r of nodes){
    const [x,y]=pos.get(key(r)),historical=historicalKeys.has(key(r)),ja=r.data.translations?.ja;
    let name=r.data.name||r.data.proposal?.id||r.data.candidate_id||r.id;
    if(['evaluation','simulation_run'].includes(r.kind))name=r.data.stage+' / '+origin(r.data.verification_origin);
    const label=historical?'旧版 '+r.id+' @'+r.revision:name,title=key(r)+' · '+name+(ja?.name?' / '+ja.name:'');
    h+=`<g class="node" tabindex="0" role="button" aria-label="${esc(title)}" data-node="${esc(key(r))}"><rect x="${x-95}" y="${y-11}" width="190" height="22" rx="4" fill="${historical?'#fff4df':r.kind==='product'?'#e5eef5':'white'}" stroke="#ccd9e3"/><text x="${x}" y="${y+4}" text-anchor="middle">${esc(String(label).slice(0,28))}</text><title>${esc(title)}</title></g>`;
  }
  $('#graph').innerHTML=h;
  $('#graph-trace-note').innerHTML=`<p>旧版ノード: ${nodes.filter(r=>historicalKeys.has(key(r))).length}件。旧版への証拠を現在版へ付け替えません。</p>`+(omitted.length?`<details><summary>表示を省略した関係: ${omitted.length}件（参照先の版を保持）</summary><pre>${esc(omitted.join('\n'))}</pre></details>`:'');
  $('#graph').querySelectorAll('[data-node]').forEach(n=>{const pick=()=>{const r=byKey.get(n.dataset.node)||traceByKey.get(n.dataset.node);$('#graph-detail').innerHTML=`<strong>${esc(r.id)} <small>@${esc(r.revision)} · ${esc(r.kind)}${historicalKeys.has(key(r))?' · 旧版':''}</small></strong><p>${esc(r.data.name)}${r.data.translations?.ja?.name?' / '+esc(r.data.translations.ja.name):''}</p><details open><summary>正本の記録を表示</summary><pre>${esc(raw(r.__source||r))}</pre></details>`};n.onclick=pick;n.onkeydown=e=>{if(e.key==='Enter')pick()}});
}
['#graph-design','#graph-kdps','#graph-focus'].forEach(s=>$(s).onchange=drawGraph);drawGraph();
const methodLabels={test:'試験',analysis:'解析',inspection:'検査',demonstration:'実演'},methodLabel=v=>typeof v==='string'&&methodLabels[v]?methodLabels[v]+' / '+v:typeof v==='object'?raw(v):v;
const reqViews=D.requirement_views||{},reqView=r=>reqViews[key(r)]||{},structured=v=>v==null?'<p class="muted">未定義 / Not recorded</p>':`<pre>${esc(typeof v==='string'?v:raw(v))}</pre>`;
function requirementLanguages(r){
  const v=reqView(r),en=v.english||r.data,ja=v.japanese||{},group=v.is_group;
  return `<div lang="en"><small>EN · source</small><h3>${esc(en.name||r.id)}</h3>${group?'<p>Requirement group. This record has no normative obligation.</p>':`<p>${esc(en.statement||'Statement not recorded.')}</p>`}</div><div lang="ja"><small>日本語 · 英語からの翻訳</small><h3>${esc(ja.name||'日本語訳は未記録')}</h3><p>${esc(group?'要求グループです。この記録に規範的な義務はありません。':ja.statement||'日本語訳は未記録')}</p></div>`;
}
$('#reqrows').innerHTML=reqs.map(r=>{const v=reqView(r),ja=v.japanese||{};return `<tr data-key="${esc(key(r))}"><td class="mono">${esc(r.id)}<br><small>@${esc(r.revision)} · ${esc(r.data.level)}${v.is_group?' · 要求グループ':''}</small></td><td><span lang="en">${esc(r.data.name)}<br>${esc(r.data.statement||'')}</span><br><small lang="ja">${esc(ja.name||'日本語訳は未記録')}<br>${esc(ja.statement||'')}</small></td><td>${esc(r.data.value)} ${esc(r.data.unit)}</td><td>要求文: ${esc(v.statement_status)}<br>元出典の状態: ${esc(v.source_status)}<br>検証: ${esc(v.verification_status)}<br>実機検証: ${r.data.physical_verified===true?'実証済み':'未実施・未判定'}${r.data.hardware_verification_required?'<br>実機で示す項目（合格フラグではない）':''}${v.is_group?'<br>階層用グループ（規範的な要求ではない）':''}</td></tr>`}).join('');
function reqDetail(r){
  const v=reqView(r),en=v.english||r.data,ja=v.japanese||{},linkedRefs=new Set((v.evidence_refs||[]).map(key)),linked=rs.filter(e=>linkedRefs.has(key(e))),byOrigin={};
  linked.forEach(e=>{const o=e.data.verification_origin||e.kind;byOrigin[o]=(byOrigin[o]||0)+1});
  $('#reqdetail').innerHTML=requirementLanguages(r)+`<p>${esc(r.data.value)} ${esc(r.data.unit)} · 要求文の状態: ${esc(v.statement_status)}（検証結果ではない）<br>元出典の状態: ${esc(v.source_status)}（旧版の由来。改訂版の承認ではない）</p><p>計画した検証方法: ${esc(methodLabel(v.verification_method))}<br>現在版の検証状態: ${esc(v.verification_status)}<br>実機検証: ${r.data.physical_verified===true?'実証済み':'未実施・未判定'}${r.data.hardware_verification_required?' · 実機で示す項目（合格フラグではない）':''}</p><p class="note">${v.is_group?'この記録は要求を整理するグループです。実行可能な合否条件を持つ要求とは区別します。':r.data.status==='draft'?'改訂要求は草案です。人間の承認と、現在版に対する検証は未完了です。':'要求文の状態と検証結果は別に管理します。数値試験リンクは物理合格を意味しません。'}</p>`+
  [['rationale','根拠 / Rationale'],['conditions','試験条件 / Conditions'],['acceptance_criteria','合格条件 / Acceptance criteria'],['unresolved_items','未解決事項 / Open items']].map(([field,label])=>`<details ${['acceptance_criteria','unresolved_items'].includes(field)?'open':''}><summary>${label}</summary><div lang="en"><small>EN · source</small>${structured(en[field])}</div><div lang="ja"><small>日本語訳</small>${structured(ja[field])}</div></details>`).join('')+
  `<p>計画した検証ケース: ${(v.planned_case_refs||[]).length}件（実行結果ではない）</p>${v.planned_case_refs?.length?`<details><summary>検証ケースの版参照</summary><pre>${esc(raw(v.planned_case_refs))}</pre></details>`:''}<p>現在版に対応する試験・数値記録: ${linked.length}記録（実機合格の証拠としては未採用）</p>${Object.entries(byOrigin).map(([o,n])=>`<p>${esc(origin(o))}: ${n}</p>`).join('')}<p>表示中の記録で旧版だけに対応する証拠: ${v.historical_evidence_count||0}記録。全履歴の集計ではなく、現在版の検証数に含めません。</p>${v.historical_target_refs?.length?`<details><summary>証拠の対象となった旧版（表示中の記録）</summary><pre>${esc(raw(v.historical_target_refs))}</pre></details>`:''}<details><summary>値・単位・出典と関係</summary><pre>${esc(raw(r))}</pre></details>`;
}
$('#reqrows').onclick=e=>{const tr=e.target.closest('[data-key]');if(tr)reqDetail(byKey.get(tr.dataset.key))};if(reqs.length)reqDetail(reqs.find(r=>r.id==='R-HOLD')||reqs[0]);
$('#param-owner').innerHTML+=products.map(r=>`<option value="${esc(r.id)}">${esc(r.data.name)}${r.data.translations?.ja?.name?' / '+esc(r.data.translations.ja.name):''}</option>`).join('');
function parameterLanguages(data,field){
  const en=data[field],ja=data.translations?.ja?.[field];
  return (en?`<div lang="en"><small>EN · source</small><br>${esc(en)}</div>`:'')+(ja?`<div lang="ja"><small>日本語訳</small><br>${esc(ja)}</div>`:'');
}
function paramRows(){
  const query=$('#param-search').value.toLowerCase(),kind=$('#param-kind').value,owner=$('#param-owner').value,list=params.filter(r=>(kind==='all'||r.kind===kind)&&(owner==='all'||r.product_node===owner)&&raw(r).toLowerCase().includes(query));
  $('#param-count').textContent=list.length+'設定';
  $('#paramrows').innerHTML=list.map(r=>{const d=r.data;return `<tr><td class="parametername"><strong class="mono">${esc(r.id)}</strong>${parameterLanguages(d,'name')}<small class="mono">${esc(d.model_path)}</small></td><td class="mono">${esc(typeof d.value==='object'?raw(d.value):d.value)}</td><td>${esc(d.unit)}</td><td>${esc(d.role||d.status)}<br>${esc(d.origin||'frozen model')}${d.method||d.translations?.ja?.method?`<details><summary>値の決定方法 / Method</summary>${parameterLanguages(d,'method')}</details>`:''}</td><td>u = ${esc(d.standard_uncertainty)}<br>${d.bounds?'範囲 '+esc(raw(d.bounds))+'<br>':''}${esc(d.source||d.authoritative_field||'')} ${d.registry_binding&&!d.registry_binding.values_match?'<p class="warn">登録値とmodel値の差あり</p>':''}${d.note||d.translations?.ja?.note?`<details><summary>注記 / Note</summary>${parameterLanguages(d,'note')}</details>`:''}<details><summary>記録詳細</summary><pre>${esc(raw(d))}</pre></details></td></tr>`}).join('');
}
['#param-search','#param-kind','#param-owner'].forEach(s=>{$(s).oninput=paramRows;$(s).onchange=paramRows});paramRows();
let shown=[];function designRows(){let q=$('#design-search').value.toLowerCase(),st=$('#design-status').value,p=$('#design-prior').checked,era=$('#design-era').value;shown=designs.filter(r=>(era==='all'||(era==='legacy')===!!r.data.history_only)&&(r.id+' '+r.data.family).toLowerCase().includes(q)&&(st==='all'||r.data.status===st)&&(!p||prior.has(r.id)));$('#design-count').textContent=shown.length+'候補（表は先頭150）';$('#designrows').innerHTML=shown.slice(0,150).map(r=>{let e=stageEval(r,'exploration')?.data.summary,v=stageEval(r,'validation')?.data.summary;return `<tr data-key="${esc(key(r))}"><td class="mono">${esc(r.id)}</td><td>${esc(r.data.family)}</td><td>${esc(labels[r.data.status]||r.data.status)}</td><td>${esc(origin(r.data.validation_origin))}</td><td>${e?.passed_trials??'—'}/${e?.trials??'—'} / ${v?.passed_trials??'—'}/${v?.trials??'—'}</td></tr>`}).join('');scatter()}function scatter(){let points=shown.map(r=>({r,x:stageEval(r,'exploration')?.data.summary.score,y:stageEval(r,'validation')?.data.summary.score})).filter(p=>typeof p.x==='number'&&typeof p.y==='number');let x=v=>70+(v+1)*420,y=v=>195-(v+1)*80;$('#scatter').innerHTML=`<path d="M70,20V195H930" fill="none" stroke="#cbd8e2"/><text x="500" y="232" text-anchor="middle">探索スコア [無次元proxy]</text><text transform="translate(18 110)rotate(-90)" text-anchor="middle">確認スコア [無次元proxy]</text>`+[-1,-.5,0,.5,1].map(v=>`<text x="${x(v)}" y="214" text-anchor="middle">${v}</text><text x="60" y="${y(v)+3}" text-anchor="end">${v}</text>`).join('')+points.map(p=>`<circle data-key="${esc(key(p.r))}" cx="${x(p.x)}" cy="${y(p.y)}" r="3.5" fill="${p.r.data.status==='confirmed_numerical_pass'?'#28734b':p.r.data.status==='confirmed_numerical_fail'?'#a43d38':'#98661d'}" opacity=".65"><title>${esc(p.r.id)}: 探索${num(p.x)} / 確認${num(p.y)}</title></circle>`).join('')}function chooseDesign(r){if(!r)return;$('#compare-target').value=key(r);$('#graph-design').value=key(r);renderDiff();designDetail(r);drawGraph()}$('#designrows').onclick=e=>{let t=e.target.closest('[data-key]');if(t)chooseDesign(byKey.get(t.dataset.key))};$('#scatter').onclick=e=>{let t=e.target.closest('[data-key]');if(t)chooseDesign(byKey.get(t.dataset.key))};['#design-search','#design-status','#design-prior','#design-era'].forEach(s=>{$(s).oninput=designRows;$(s).onchange=designRows});
function flatten(o,p='',out={}){for(const[k,v]of Object.entries(o||{})){let path=p?p+'.'+k:k;if(v&&typeof v==='object'&&!Array.isArray(v))flatten(v,path,out);else out[path]=v}return out}function renderDiff(){let a=byKey.get($('#compare-base').value),b=byKey.get($('#compare-target').value);if(!a||!b)return;let x=flatten({parameters:a.data.parameters,physics:a.data.physics,actuation:a.data.actuation,controller:a.data.controller}),y=flatten({parameters:b.data.parameters,physics:b.data.physics,actuation:b.data.actuation,controller:b.data.controller});$('#diff').innerHTML='<div class="scroll"><table><thead><tr><th>設定</th><th>比較元</th><th>対象</th></tr></thead><tbody>'+[...new Set([...Object.keys(x),...Object.keys(y)])].map(k=>`<tr class="${raw(x[k])===raw(y[k])?'':'diffchange'}"><td class="mono">${esc(k)}</td><td class="mono">${esc(raw(x[k]))}</td><td class="mono">${esc(raw(y[k]))}</td></tr>`).join('')+'</tbody></table></div><small>黄色は設定差分。機械変更と制御変更の因果は別試験なしに断定しません。</small>'}function designDetail(r){let es=evalFor(r);$('#design-detail').innerHTML=`<h3 class="mono">${esc(r.id)} @${esc(r.revision)}</h3><p>${esc(labels[r.data.status]||r.data.status)} · ${esc(origin(r.data.validation_origin))}</p><p>${esc(r.data.hypothesis)}</p><p>元の状態: ${esc(labels[r.data.original_status]||r.data.original_status)} · 実機忠実度 null</p>`+es.map(e=>`<details ${e.data.stage==='validation'?'open':''}><summary>${esc(e.data.stage)} / ${esc(origin(e.data.verification_origin))} · ${e.data.summary.passed_trials}/${e.data.summary.trials}</summary><p>数値確認 ${esc(e.data.summary.numeric_verified)} · coverage ${e.data.coverage?.actual}/${e.data.coverage?.expected}</p><table><thead><tr><th>domain / condition</th><th>不合格</th><th>違反条件</th></tr></thead><tbody>${(e.data.conditions||[]).map(c=>`<tr><td>${esc(c.domain_id)}<br>${esc(c.condition_id)}</td><td>${c.failed_trials}/${c.trials}</td><td>${esc(Object.keys(c.criteria).join(', ')||'なし')}</td></tr>`).join('')}</tbody></table><details><summary>数値・出典・CSV抽出条件</summary><pre>${esc(raw(e.data))}</pre></details></details>`).join('')+`<details><summary>設計の全設定・仮定</summary><pre>${esc(raw(r.data))}</pre></details>`}$('#compare-base').onchange=renderDiff;$('#compare-target').onchange=()=>chooseDesign(byKey.get($('#compare-target').value));if($('#open-best'))$('#open-best').onclick=()=>{chooseDesign(best);$('#designs').scrollIntoView()};designRows();renderDiff();if(best)designDetail(best);
const acceptance=kinds('verification').filter(r=>r.data.acceptance_type==='offline_mvp').at(-1)?.data,providers=new Map((acceptance?.executions||[]).map(x=>[x.run_id,x.provider]));if(acceptance)$('#offline-check').innerHTML=`<div class="note"><strong>オフライン受入: ${acceptance.passed?'PASS':'要確認'}</strong><p>Engineering Agents ${acceptance.tests.engineering_agents.passed}件 / OnePiece ${acceptance.tests.onepiece.passed}件成功。代表CPU 4ケース再現、ECLSSの2回実行、Fake LLMの保存・再読込を確認しました。</p><p>実LLMによる改善、新しいGPU実行、実機での妥当性確認は未実施です。Fake提案による改善は確認されず、既存の比較基準を保持しています。</p></div>`;
$('#new-runs').innerHTML=newLoops.map(r=>{let d=r.data;return `<div class="panel" style="margin-bottom:18px"><h3 class="mono">${esc(d.run_id)}</h3><div class="counts"><div><strong>${d.iterations_completed}/${d.iterations_requested}</strong><small>完了 / 予定反復</small></div><div><strong>${d.candidates_evaluated}</strong><small>実行候補</small></div><div><strong>${d.numeric_gpu_verified?'CPU/GPU照合済み':'CPUのみ暫定'}</strong><small>選抜確認状態</small></div></div><p>提案: ${esc(providers.get(d.run_id)||'provider未記録')} · 停止理由: <span class="mono">${esc(d.stopped_reason)}</span> · 実機忠実度 null · ${num(d.wall_time_s,2)} s</p><div class="scroll"><table><thead><tr><th>反復</th><th>EN → PI → R → E</th><th>方針revision</th><th>観測した失敗</th><th>改善 / 因子比較</th></tr></thead><tbody>${(d.rounds||[]).map(x=>`<tr><td>${x.round}</td><td>${esc(x.stage_sequence?.join(' → ')||x.status)}<br>${x.context_reread?'context再読あり':''}</td><td>${esc(x.policy_revision_in)} → ${esc(x.policy_revision_out)}</td><td>${esc(x.error||x.feedback?.failure_metrics?.map(m=>summary.criteria?.find(c=>c.metric===m)?.label||m).join(', ')||'数値screen違反なし')}</td><td>${esc(x.improved)}<br>${esc(x.factorial_cells?.join(', '))}</td></tr>`).join('')}</tbody></table></div><details><summary>結果・検証・停止の正本</summary><pre>${esc(raw(r))}</pre></details></div>`}).join('')+kinds('design_policy').map(r=>`<details><summary>探索方針 ${esc(r.id)} · revision ${esc(r.data.revision)}</summary><pre>${esc(raw(r))}</pre></details>`).join('')+kinds('design_proposal').filter(r=>r.data.status==='rejected').map(r=>`<p class="note warn">提案棄却 ${esc(r.id)}: ${esc(r.data.error)}</p>`).join('');if(!newLoops.length)$('#new-loop').hidden=true;
$('#iterations').innerHTML=kinds('iteration').concat(newLoops).map(r=>`<div><strong>${esc(r.id)} @${esc(r.revision)}</strong><br><small>${esc(r.created_at)} · ${esc(r.data.status)}</small><p>${esc(r.data.outcome||r.data.next_action||r.data.stopped_reason||'')}</p><details><summary>変更・判定の記録</summary><pre>${esc(raw(r))}</pre></details></div>`).join('');let fails=summary.failure_analysis?.exploration?.criterion_counts||{},maxFail=Math.max(1,...Object.values(fails));$('#failures').innerHTML=Object.entries(fails).sort((a,b)=>b[1]-a[1]).map(([m,n])=>`<div><span>${esc(summary.criteria?.find(c=>c.metric===m)?.label||m)}</span><b style="width:${100*n/maxFail}%"></b><span>${num(n,0)} 試行</span></div>`).join('');
$('#artifactrows').innerHTML=D.artifacts.map(a=>`<tr><td><a href="${esc(a.url)}">${esc(a.path)}</a></td><td>${num(a.size_bytes,0)}</td><td class="mono">${esc(a.sha256)}</td></tr>`).join('');$('#primary-links').innerHTML=D.artifacts.filter(a=>['cube.artifact.gnc-report','cube.artifact.legacy-report','cube.artifact.best-video','cube.artifact.baseline-video'].includes(a.record_id)).map(a=>`<a href="${esc(a.url)}">${esc(a.record_id.split('.').at(-1))}</a>`).join('');
const cases=D.replay.cases||[],canvas=$('#scene'),cx=canvas.getContext('2d');let ci=0,fi=0,playing=false,t=0,last=0,yaw=-.78,pitch=.34,zoom=1,drag=null;const add=(a,b)=>a.map((v,i)=>v+b[i]),sub=(a,b)=>a.map((v,i)=>v-b[i]),mul=(a,s)=>a.map(v=>v*s),dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],norm=a=>mul(a,1/Math.max(1e-9,Math.sqrt(dot(a,a)))),rotate=(v,q)=>{let [w,...a]=q,t=mul(cross(a,v),2);return add(v,add(mul(t,w),cross(a,t)))};function drawScene(){let c=cases[ci],f=c?.frames?.[fi];if(!f)return;const box=canvas.getBoundingClientRect(),ratio=Math.min(2,devicePixelRatio||1),W=box.width,H=box.height;canvas.width=Math.round(W*ratio);canvas.height=Math.round(H*ratio);cx.setTransform(ratio,0,0,ratio,0,0);cx.fillStyle='#111b25';cx.fillRect(0,0,W,H);let s=c.geometry.cube_side_m,q=f.quaternion_wxyz,p=f.position_m,target=[0,0,s*.68],d=s*5.3/zoom,eye=add(target,[d*Math.cos(pitch)*Math.cos(yaw),d*Math.cos(pitch)*Math.sin(yaw),d*Math.sin(pitch)]),fw=norm(sub(target,eye)),right=norm(cross(fw,[0,0,1])),up=cross(right,fw),project=v=>{let u=sub(v,eye),z=dot(u,fw);return [W/2+Math.min(W,H)*1.55*dot(u,right)/z,H*.57-Math.min(W,H)*1.55*dot(u,up)/z,z]},local=v=>add(rotate(v,q),p),line=(a,b,color,width=1)=>{a=project(a);b=project(b);cx.beginPath();cx.moveTo(...a.slice(0,2));cx.lineTo(...b.slice(0,2));cx.strokeStyle=color;cx.lineWidth=width;cx.stroke()};for(let i=-4;i<=4;i++){line([-s*2,i*s/2,0],[s*2,i*s/2,0],'#283846');line([i*s/2,-s*2,0],[i*s/2,s*2,0],'#283846')}let vs=[];for(let z of [0,s])for(let y of [0,s])for(let x of [0,s])vs.push(local([x,y,z]));let faces=[[0,1,3,2],[4,5,7,6],[0,1,5,4],[2,3,7,6],[0,2,6,4],[1,3,7,5]].map(v=>({v,z:v.reduce((a,i)=>a+project(vs[i])[2],0)/4})).sort((a,b)=>b.z-a.z);for(const face of faces){let pts=face.v.map(i=>project(vs[i]));cx.beginPath();pts.forEach((v,i)=>i?cx.lineTo(v[0],v[1]):cx.moveTo(v[0],v[1]));cx.closePath();cx.fillStyle='#8ea9bd22';cx.fill();cx.strokeStyle='#a9c4d8';cx.stroke()}const axes=[[1,0,0],[0,1,0],[0,0,1]],colors=['#77b4dd','#dbac6e','#7bb7a0'],r=c.geometry.wheel_radius_m||s*.28;axes.forEach((axis,i)=>{let center=[s/2,s/2,s/2];center[i]=s-(c.geometry.wheel_face_inset_m||.012);let u=axes[(i+1)%3],v=axes[(i+2)%3],pts=[];for(let a=0;a<=64;a++)pts.push(local(add(center,add(mul(u,r*Math.cos(a/64*Math.PI*2)),mul(v,r*Math.sin(a/64*Math.PI*2))))));for(let j=1;j<pts.length;j++)line(pts[j-1],pts[j],colors[i],2);let angle=f.wheel_angle_rad?.[i]||0;line(local(center),local(add(center,add(mul(u,r*Math.cos(angle)),mul(v,r*Math.sin(angle))))),colors[i],2)});let pivot=project(p);cx.beginPath();cx.arc(pivot[0],pivot[1],4,0,Math.PI*2);cx.fillStyle='#f3f6f8';cx.fill();cx.fillStyle='#d7e0e8';cx.font='12px system-ui';cx.fillText(c.candidate_id+' · '+num(f.time_s,3)+' s',16,25)}
function updateFrame(){let c=cases[ci],f=c?.frames[fi];if(!f)return;$('#frame').value=fi;$('#replay-time').textContent=num(f.time_s,3)+' / '+num(c.frames.at(-1).time_s,3)+' s';$('#replay-state').textContent=(fi+1)+' / '+c.frames.length+' 記録フレーム';$('#live').innerHTML=`<div class="counts"><div><strong>${num(f.tilt_total_deg,2)}°</strong><small>合成傾斜</small></div><div><strong>${num(f.pivot_displacement_mm,2)} mm</strong><small>支点移動</small></div></div>`;drawScene();let fs=c.frames,x=t=>50+t/fs.at(-1).time_s*520,max=Math.max(5,...fs.map(f=>f.tilt_total_deg)),y=v=>190-v/max*160;$('#replay-chart').innerHTML=`<path d="M50,25V190H570" fill="none" stroke="#c8d5df"/><text x="310" y="225" text-anchor="middle">記録時刻 [s]</text><text transform="translate(15 105)rotate(-90)" text-anchor="middle">合成傾斜 [deg]</text><text x="40" y="193" text-anchor="end">0</text><text x="40" y="33" text-anchor="end">${num(max,1)}</text><text x="570" y="207" text-anchor="end">${num(fs.at(-1).time_s,2)}</text><path d="${fs.map((v,i)=>(i?'L':'M')+x(v.time_s)+','+y(v.tilt_total_deg)).join(' ')}" fill="none" stroke="#216d9a" stroke-width="2"/><path d="M${x(f.time_s)},25V190" stroke="#a43d38" stroke-width="1"/>`}
function setCase(i){ci=Number(i);fi=0;playing=false;t=0;$('#play').textContent='再生';let c=cases[ci];if(!c)return;$('#frame').max=c.frames.length-1;$('#case-title').textContent=c.label||c.id;$('#case-source').textContent=c.domain_id+' / '+c.condition_id+' · seed '+c.seed+' · dt '+c.physics_timestep_s+' s'+(c.used_half_timestep_adjudication?'（歴史的dt/2確認の再現）':'');$('#case-raw').textContent=raw({trajectory_origin:c.trajectory_origin,source_summary:c.source_summary,reproduced_summary:c.summary,summary_comparison:c.summary_comparison});updateFrame()}$('#case').innerHTML=cases.map((c,i)=>`<option value="${i}">${esc(c.label||c.id)}</option>`).join('');$('#case').onchange=e=>setCase(e.target.value);$('#play').onclick=()=>{if(fi===cases[ci].frames.length-1){fi=0;t=0}playing=!playing;$('#play').textContent=playing?'一時停止':'再生';last=performance.now()};$('#step').onclick=()=>{playing=false;$('#play').textContent='再生';fi=Math.min(fi+1,cases[ci].frames.length-1);t=cases[ci].frames[fi].time_s;updateFrame()};$('#frame').oninput=e=>{playing=false;$('#play').textContent='再生';fi=Number(e.target.value);t=cases[ci].frames[fi].time_s;updateFrame()};$('#camera').onclick=()=>{yaw=-.78;pitch=.34;zoom=1;drawScene()};canvas.onpointerdown=e=>{drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId)};canvas.onpointermove=e=>{if(!drag)return;yaw-=(e.clientX-drag[0])*.008;pitch=Math.max(.06,Math.min(1.4,pitch+(e.clientY-drag[1])*.007));drag=[e.clientX,e.clientY];drawScene()};canvas.onpointerup=()=>drag=null;canvas.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(.45,Math.min(2.4,zoom*Math.exp(-e.deltaY*.001)));drawScene()},{passive:false});function animate(now){if(playing&&cases.length){let fs=cases[ci].frames;t+=Math.min(.1,(now-last)/1000);while(fi<fs.length-1&&fs[fi+1].time_s<=t)fi++;if(t>=fs.at(-1).time_s){playing=false;$('#play').textContent='再生'}updateFrame()}last=now;requestAnimationFrame(animate)}window.addEventListener('resize',drawScene);if(cases.length)setCase(0);else $('#replay').hidden=true;requestAnimationFrame(animate);window.REPORT_READY=true;
</script></html>'''
