const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

const COPY = {
  en: {
    requirements: "Explore the obligations", all: "All groups", open: "Open questions",
    group: "GROUP", show: "SHOW", clear: "Clear filters", noResults: "No requirements match these filters.",
    draft: "Draft", pending: "Pending review", notRun: "Not run", hardware: "Hardware test needed",
    statement: "REQUIREMENT STATEMENT", rationale: "WHY IT MATTERS", acceptance: "ACCEPTANCE RULE",
    conditions: "CONDITIONS", method: "VERIFICATION METHOD", case: "PLANNED VERIFICATION CASE",
    unresolved: "OPEN ITEMS", links: "TRACE LINKS", designParams: "RELATED DESIGN PARAMETERS",
    source: "SOURCE LINEAGE", propose: "PROPOSE A REVISION", current: "Current wording",
  },
  ja: {
    requirements: "要求を確認する", all: "すべてのグループ", open: "未解決項目あり",
    group: "グループ", show: "表示", clear: "絞り込みを解除", noResults: "条件に一致する要求はありません。",
    draft: "草案", pending: "人によるレビュー待ち", notRun: "未実施", hardware: "実機検証が必要",
    statement: "要求文", rationale: "背景", acceptance: "合否基準",
    conditions: "条件", method: "検証方法", case: "計画中の検証ケース",
    unresolved: "未解決項目", links: "トレース関係", designParams: "関連する設計パラメータ",
    source: "出典", propose: "改訂案を作成", current: "現在の文言",
  },
};

let DATA;
let activeView = "cube";
let selectedId = null;
let language = "en";
let searchText = "";
let toastTimer;
let drafts = {};
let graphFocusId = "cube.system";
let graphSelectedId = "cube.system";
let graphEdgeFilter = "performs";
let architectureMode = "proposed";

let draftStorageKey;

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
}

function humanize(key) {
  return String(key).replace(/_/g, " ").replace(/\b[a-z]/g, (m) => m.toUpperCase());
}

function flattenLeaves(value, prefix = "") {
  if (Array.isArray(value)) return value.flatMap((item, i) => flattenLeaves(item, `${prefix}[${i}]`));
  if (value && typeof value === "object") return Object.entries(value).flatMap(([key, child]) => flattenLeaves(child, prefix ? `${prefix}.${key}` : key));
  return [{ path: prefix, value }];
}

function formatValue(value) {
  if (value === null || value === undefined) return "Not specified";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function requirement(id) { return DATA.balancing_cube.requirements.find((r) => r.id === id); }

function statusPill(label, tone = "", title = "") { return `<span class="pill ${tone}"${title ? ` title="${esc(title)}"` : ""}>${esc(label)}</span>`; }

function groupName(groupId) {
  return DATA.balancing_cube.groups.find((g) => g.id === groupId)?.name || "Mission";
}

function requirementsForGroup(groupId) {
  return DATA.balancing_cube.requirements.filter((r) => r.group_id === groupId);
}

function setView(view) {
  activeView = view;
  $$(".view").forEach((panel) => panel.classList.toggle("is-visible", panel.id === `view-${view}`));
  $$(".model-link").forEach((button) => button.classList.toggle("is-active", button.dataset.view === view));
  const labels = { cube: "BALANCING CUBE", eclss: "SPACECRAFT ECLSS", scrubber: "SCRUBBER DEMO", basics: "MODEL GUIDE" };
  $("#crumb-model").textContent = labels[view] || "SYSTEM MODEL";
  $("#group-nav").classList.toggle("is-hidden", view !== "cube");
  if (view === "cube") renderRequirements();
}

function renderCubeStats() {
  const data = DATA.balancing_cube;
  const unresolved = data.requirements.reduce((sum, r) => sum + r.unresolved_items.length, 0);
  const reviewCount = data.requirements.filter((r) => r.approval_state === "human_reviewed").length;
  const rows = [
    { label: "TEST OBLIGATIONS", value: data.counts.obligations, suffix: "requirements", style: "stat-amber" },
    { label: "ORGANIZATIONAL GROUPS", value: data.counts.groups, suffix: "containers", style: "stat-blue" },
    { label: "OPEN ITEMS", value: unresolved, suffix: "to resolve", style: "stat-coral" },
    { label: "HUMAN REVIEW", value: `${reviewCount}/${data.counts.obligations}`, suffix: "reviewed", style: "stat-green" },
  ];
  $("#cube-stats").innerHTML = rows.map((s, i) => `<article class="stat-card ${s.style}"><span class="stat-label">${s.label}</span><div><b>${esc(s.value)}</b><small>${esc(s.suffix)}</small></div><span class="stat-index">0${i + 1}</span></article>`).join("");
  $("#model-revision").textContent = `${data.model.revision}  ·  ${data.model.approval_state.replaceAll("_", " ")}`;
}

function initGroupControls() {
  const groups = [{ id: "M-VERTEX", name: "Mission" }, ...DATA.balancing_cube.groups.map((g) => ({ id: g.id, name: g.name }))];
  const filter = $("#group-filter");
  filter.innerHTML = `<option value="all">${esc(COPY[language].all)}</option>` + groups.map((g) => `<option value="${esc(g.id)}">${esc(g.name)}</option>`).join("");
  const nav = $("#group-nav");
  nav.innerHTML = groups.map((g) => `<button class="group-link" type="button" data-group="${esc(g.id)}"><span class="group-bullet"></span><span>${esc(g.name)}</span><small>${requirementsForGroup(g.id).length.toString().padStart(2, "0")}</small></button>`).join("") + `<button type="button" data-view="basics" class="guide-link"><span>＋</span> MODEL GUIDE <span class="guide-arrow">↗</span></button>`;
  nav.addEventListener("click", (event) => {
    const groupButton = event.target.closest("[data-group]");
    const guideButton = event.target.closest("[data-view]");
    if (groupButton) {
      setView("cube");
      filter.value = groupButton.dataset.group;
      renderRequirements();
      $(".explorer-head").scrollIntoView({ behavior: "smooth", block: "start" });
    } else if (guideButton) setView("basics");
  });
}

function filteredRequirements() {
  const group = $("#group-filter").value;
  const filter = $("#status-filter").value;
  const query = searchText.trim().toLocaleLowerCase();
  return DATA.balancing_cube.requirements.filter((r) => {
    const groupMatch = group === "all" || r.group_id === group;
    const statusMatch = filter === "all" || (filter === "open" ? r.unresolved_items.length > 0 : filter === "hardware" ? r.hardware_verification_required : filter === "not-run" ? r.verification_status === "not_run" : true);
    const queryHaystack = [r.id, r.name, r.name_ja, r.statement, r.statement_ja, r.rationale, ...r.unresolved_items.map((i) => i.description), ...r.kdps.map((k) => k.id)].join(" ").toLocaleLowerCase();
    return groupMatch && statusMatch && (!query || queryHaystack.includes(query));
  });
}

function renderRequirements() {
  const visible = filteredRequirements();
  $("#list-count").textContent = `${String(visible.length).padStart(2, "0")} OF ${DATA.balancing_cube.counts.obligations} OBLIGATIONS`;
  $("#no-results").hidden = visible.length > 0;
  const grouped = new Map();
  const ordered = [{ id: "M-VERTEX", name: "Mission" }, ...DATA.balancing_cube.groups.map((g) => ({ id: g.id, name: g.name }))];
  for (const item of visible) {
    const list = grouped.get(item.group_id) || [];
    list.push(item);
    grouped.set(item.group_id, list);
  }
  $("#requirements-list").innerHTML = ordered.filter((g) => grouped.has(g.id)).map((g) => {
    const items = grouped.get(g.id);
    return `<section class="req-group"><div class="req-group-head"><span>${esc(g.name)}</span><small>${items.length.toString().padStart(2, "0")}</small></div>${items.map((r) => {
      const selected = r.id === selectedId;
      const statement = language === "ja" ? (r.statement_ja || r.statement) : r.statement;
      const title = language === "ja" ? (r.name_ja || r.name) : r.name;
      return `<button type="button" class="req-row ${selected ? "is-selected" : ""}" data-requirement="${esc(r.id)}"><span class="req-row-id">${esc(r.id)}</span><b>${esc(title)}</b><p>${esc(statement)}</p><span class="req-row-meta">${r.unresolved_items.length ? `<i class="tbr-dot"></i>${r.unresolved_items.length} OPEN` : `<i class="check-dot"></i>NO OPEN ITEMS`}<span>${esc(r.verification_method || "—").toUpperCase()}</span></span></button>`;
    }).join("")}</section>`;
  }).join("");
  $$(".req-row").forEach((button) => button.addEventListener("click", () => selectRequirement(button.dataset.requirement)));
  if (!visible.some((r) => r.id === selectedId)) selectRequirement(visible[0]?.id || null);
  else renderRequirementDetail(requirement(selectedId));
}

function formatAcceptance(criteria, lang = language) {
  if (!criteria || typeof criteria !== "object") return "Not specified";
  const translated = lang === "ja" ? requirement(selectedId)?.acceptance_ja : null;
  if (translated) return translated;
  const bits = [];
  if (criteria.metric) bits.push(criteria.metric.replaceAll("_", " "));
  if (criteria.operator) bits.push(criteria.operator);
  if (criteria.value !== undefined && criteria.value !== null) bits.push(String(criteria.value));
  if (criteria.unit && criteria.unit !== "1") bits.push(criteria.unit);
  if (criteria.sample_count !== undefined) bits.push(`(${criteria.sample_count} ${criteria.unit || "samples"})`);
  if (criteria.limits_status === "unresolved") bits.push("· limits unresolved");
  if (criteria.reason) bits.push(`· ${criteria.reason}`);
  if (criteria.target_only) bits.push(`· target only: ${JSON.stringify(criteria.target_only)}`);
  return bits.join(" ") || JSON.stringify(criteria);
}

function renderLinks(r) {
  const items = (r.links || []).map((link) => {
    const target = link.target || {};
    return `<span class="trace-chip"><small>${esc(link.type)}</small><b>${esc(target.id)}</b><i>@${esc(target.revision || "?")}</i></span>`;
  });
  return items.length ? `<div class="trace-chip-list">${items.join("")}</div>` : `<span class="empty-note">No explicit graph edges in this revision.</span>`;
}

function showArchitectureObject(id, filter = "all") {
  if (!DATA.balancing_cube.reviewed_architecture && DATA.balancing_cube.architecture_draft.status !== "unavailable" && architectureMode !== "proposed") {
    architectureMode = "proposed";
    renderArchitecturePanel();
  }
  openGraphNode(id, filter);
  $("#model-graph").scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderArchitecturePanel() {
  const data = DATA.balancing_cube;
  if (data.reviewed_architecture) { renderReviewedArchitecture(); return; }
  const proposal = data.architecture_draft;
  if (proposal.status === "unavailable") {
    $("#architecture-panel").innerHTML = `<p>No architecture proposal is pinned to this model revision. The graph shows its recorded relationships.</p>`;
    return;
  }
  const architecture = proposal;
  const allNodes = [...proposal.functions, ...proposal.components];
  const nodeName = (id) => allNodes.find((n) => n.id === id)?.name || data.products.find((p) => p.id === id)?.name || id;
  const nodeButton = (id, caption = nodeName(id), filter = "all") => `<button type="button" data-architecture-node="${esc(id)}" data-architecture-filter="${esc(filter)}">${esc(caption)}</button>`;
  const rows = proposal.requirement_allocations.map((allocation) => {
    const item = requirement(allocation.source);
    const recorded = (item.links || []).filter((l) => l.type === "allocate").map((l) => nodeName(l.target.id));
    return `<tr><td>${nodeButton(item.id, item.id)}<span>${esc(item.name)}</span></td><td>${esc(recorded.join(", "))}</td><td>${allocation.targets.map((id) => nodeButton(id)).join("")}<small>${esc(allocation.scope)}</small></td><td>${esc(allocation.rationale)}</td></tr>`;
  }).join("");
  $("#architecture-panel").innerHTML = `<div class="architecture-header"><div><span class="section-kicker">ALLOCATION REVIEW · DRAFT</span><h3>Split responsibility below the overall Cube</h3></div><div class="architecture-mode" role="group" aria-label="Allocation model"><button type="button" data-architecture-mode="proposed" aria-pressed="${architectureMode === "proposed"}">Proposed split · DRAFT</button><button type="button" data-architecture-mode="recorded" aria-pressed="${architectureMode === "recorded"}">Recorded model</button></div></div>
    <p>${architectureMode === "proposed" ? "The graph shows proposed requirement → function → component allocations. New objects and edges are marked DRAFT; coarse recorded allocations are replaced in this view. Derivation, constraints and verification links are preserved." : "The graph shows the recorded model and its original allocation targets. Select Proposed split to review the finer decomposition."}</p>
    <div class="architecture-actions">${nodeButton("cube.system", `Cube functions · ${architecture.functions.filter(n => n.parent_ref?.id === "cube.system").length}`, "performs")}${nodeButton("cube.system", `Cube components · ${architecture.components.filter(n => n.parent_ref?.id === "cube.system").length}`, "comprises")}${nodeButton("cube.verification", `External verification functions · ${architecture.functions.filter(n => n.parent_ref?.id === "cube.verification").length}`, "performs")}<button type="button" id="export-architecture">Export allocation draft ↗</button></div>
    <p class="architecture-scope">The mission and total cost budget retain system-level responsibility. Installation and sourcing constraints span several components. Independent metrology and test equipment belong to the external verification context.</p>
    <details class="architecture-review"><summary>Review all 22 requirement assignments and their rationale</summary><div class="architecture-table-wrap"><table><thead><tr><th>Requirement</th><th>Recorded allocation</th><th>Proposed allocation</th><th>Reason</th></tr></thead><tbody>${rows}</tbody></table></div></details>
    <details class="architecture-review"><summary>Browse ${architecture.functions.length} functions and ${architecture.components.length} components</summary><div class="architecture-catalog">${allNodes.map((n) => `<article><small>${esc(n.kind.toUpperCase())} · ${esc(n.boundary)}</small>${nodeButton(n.id)}<p>${esc(n.description)}</p></article>`).join("")}</div></details>
    <details class="architecture-review"><summary>Questions for the next review</summary><ul>${proposal.open_questions.map((q) => `<li>${esc(q)}</li>`).join("")}</ul></details>`;
  $$('[data-architecture-mode]').forEach((button) => button.addEventListener("click", () => {
    architectureMode = button.dataset.architectureMode;
    if (!graphNode(graphFocusId)) graphFocusId = "cube.system";
    graphSelectedId = graphFocusId;
    graphEdgeFilter = architectureMode === "proposed" && graphFocusId === "cube.system" ? "performs" : "all";
    renderArchitecturePanel();
    renderSystemGraph();
  }));
  $$('[data-architecture-node]', $("#architecture-panel")).forEach((button) => button.addEventListener("click", () => showArchitectureObject(button.dataset.architectureNode, button.dataset.architectureFilter)));
  $("#export-architecture").addEventListener("click", () => {
    const url = URL.createObjectURL(new Blob([JSON.stringify(proposal, null, 2)], { type: "application/json" }));
    const link = document.createElement("a"); link.href = url; link.download = `${proposal.revision}.json`; link.click(); URL.revokeObjectURL(url);
  });
}

function renderReviewedArchitecture() {
  const data = DATA.balancing_cube;
  const architecture = data.reviewed_architecture;
  const nodes = [...architecture.functions, ...architecture.components];
  const name = (id) => nodes.find((n) => n.id === id)?.name || data.products.find((p) => p.id === id)?.name || id;
  const button = (id, caption = name(id), filter = "all") => `<button type="button" data-architecture-node="${esc(id)}" data-architecture-filter="${esc(filter)}">${esc(caption)}</button>`;
  const rows = architecture.requirement_allocations.map((allocation) => {
    const r = requirement(allocation.source);
    return `<tr><td>${button(r.id, r.id)}<span>${esc(r.name)}</span></td><td>${esc(r.previous_allocations.map((ref) => ref.id).join(", "))}</td><td>${allocation.targets.map((id) => button(id)).join("")}<small>${esc(allocation.scope)}</small></td><td>${esc(allocation.rationale)}</td></tr>`;
  }).join("");
  $("#architecture-panel").innerHTML = `<div class="architecture-header"><div><span class="section-kicker">ALLOCATION · HUMAN REVIEWED · ${esc(architecture.reviewed_on || architecture.revision)}</span><h3>Responsibility below the overall Cube</h3></div><a class="text-link" href="./provenance.json" target="_blank" rel="noreferrer">Build provenance ↗</a></div><p>The recorded model includes the accepted requirement → function → component allocations. The graph reads each connection in sentence order. Select an object to inspect it; double-click to focus one level of connections.</p><div class="architecture-actions">${button("cube.system", `Cube functions · ${architecture.functions.filter(n => n.parent_ref?.id === "cube.system").length}`, "performs")}${button("cube.system", `Cube components · ${architecture.components.filter(n => n.parent_ref?.id === "cube.system").length}`, "comprises")}${button("cube.verification", `External verification functions · ${architecture.functions.filter(n => n.parent_ref?.id === "cube.verification").length}`, "performs")}<button type="button" id="export-architecture">Export reviewed allocation ↗</button></div><p class="architecture-scope">${architecture.functions.length} functions · ${architecture.components.length} components · ${architecture.requirement_allocations.length} requirement assignments · ${architecture.parameter_allocations.length} parameter assignments. Mission and total budget retain system responsibility. External verification tools are separate from onboard hardware. Review does not establish physical verification.</p><details class="architecture-review"><summary>Review all ${architecture.requirement_allocations.length} assignments and their rationale</summary><div class="architecture-table-wrap"><table><thead><tr><th>Requirement</th><th>Previous draft allocation</th><th>Reviewed allocation</th><th>Reason</th></tr></thead><tbody>${rows}</tbody></table></div></details><details class="architecture-review"><summary>Browse ${architecture.functions.length} functions and ${architecture.components.length} components</summary><div class="architecture-catalog">${nodes.map((n) => `<article><small>${esc(n.kind.toUpperCase())} · REVIEWED · ${esc(n.boundary)}</small>${button(n.id)}<p>${esc(n.description)}</p></article>`).join("")}</div></details>`;
  $$('[data-architecture-node]', $("#architecture-panel")).forEach((b) => b.addEventListener("click", () => showArchitectureObject(b.dataset.architectureNode, b.dataset.architectureFilter)));
  $("#export-architecture").addEventListener("click", () => {
    const url = URL.createObjectURL(new Blob([JSON.stringify(architecture, null, 2)], { type: "application/json" }));
    const link = document.createElement("a"); link.href = url; link.download = `${architecture.revision}.json`; link.click(); URL.revokeObjectURL(url);
  });
}

function renderDesignCoverage() {
  const coverage = DATA.balancing_cube.design_claims;
  const designs = coverage.designs;
  const targetCount = coverage.requirements_with_claims.length;
  const screening = [...new Set(designs.flatMap((design) => (design.numerical_results || []).map((r) => `${r.data.stage || "recorded"}: ${screeningCaseCount(r.data)} numerical cases passed; ${r.data.all_screening_passed === true ? "all screening passed" : "screening incomplete"}; physical verification ${String(r.data.physical_verified)}`)))];
  const sharedInput = designs.length > 1 && coverage.unique_design_inputs === 1 ? "The candidate records share the same design input. " : "";
  $("#design-coverage").innerHTML = `<span class="section-kicker">RECORDED DESIGN SATISFACTION</span><h3>${designs.length} candidate records · ${coverage.unique_design_inputs} distinct design input${coverage.unique_design_inputs === 1 ? "" : "s"}</h3><p>Source-recorded satisfaction intent covers ${targetCount} of ${DATA.balancing_cube.requirements.length} current requirements: ${esc(coverage.requirements_with_claims.join(", ") || "none")}. ${esc(sharedInput)}Recorded results: ${esc(screening.join(". ") || "no linked screening results")}.</p><div class="architecture-actions">${designs.length ? `<button type="button" data-design-focus="${esc(designs[0].id)}">Show satisfies arrows ↗</button>` : ""}${designs.map((design) => `<button type="button" data-design-focus="${esc(design.id)}">${esc(design.name)}</button>`).join("")}</div><p class="design-coverage-note">A recorded <code>satisfies</code> arrow declares design intent. It does not establish a verified pass. No satisfaction links to the other ${DATA.balancing_cube.requirements.length - targetCount} current requirements are recorded in this projection.</p>`;
  const historical = coverage.historical_designs || [];
  if (historical.length) $("#design-coverage").insertAdjacentHTML("beforeend", `<details class="architecture-review"><summary>${historical.length} historical candidate records retain their original satisfaction targets</summary><p>These declarations and numerical runs apply to earlier requirement revisions. A new applicability decision is needed before linking them to this reviewed baseline.</p>${historical.map((design) => `<article><b>${esc(design.name)}</b><p>${esc(design.description)}</p><code>${esc(design.id)}@${esc(design.revision)}</code><p>${design.links.map((l) => `satisfies → ${esc(l.target.id)}@${esc(l.target.revision)}`).join("<br>")}</p>${renderDesignScreening(design)}</article>`).join("")}</details>`);
  $$('[data-design-focus]', $("#design-coverage")).forEach((button) => button.addEventListener("click", () => {
    openGraphNode(button.dataset.designFocus, "satisfy");
    $("#model-graph").scrollIntoView({ behavior: "smooth", block: "start" });
  }));
}

function screeningCaseCount(data) {
  return Number.isFinite(data.screening_pass_fraction) && Number.isFinite(data.trial_count) ? `${Math.round(data.screening_pass_fraction * data.trial_count)}/${data.trial_count}` : "not recorded";
}

function renderDesignScreening(design) {
  const results = design.numerical_results || [];
  return `<div class="design-screening"><b>RECORDED INTENT · NUMERICAL SCREENING</b>${results.map((result) => {
    const data = result.data;
    const count = screeningCaseCount(data);
    return `<p><strong>${esc(humanize(data.stage || "Recorded"))} · numerical only</strong><br>${esc(count)} screening cases passed · ${data.all_screening_passed === true ? "all screening passed" : "screening incomplete"}</p><dl><dt>CPU numerical verification</dt><dd>${esc(formatValue(data.numeric_cpu_verified))}</dd><dt>GPU state</dt><dd>${esc(data.gpu_state || "not recorded")}</dd><dt>Agreement state</dt><dd>${esc(data.agreement_state || "not recorded")}</dd><dt>Physical verification</dt><dd>${esc(formatValue(data.physical_verified))}</dd></dl><code>${esc(result.id)}@${esc(result.revision)}</code>`;
  }).join("") || "<p>No linked numerical result recorded.</p>"}<p>The arrow is a design-intent declaration; it is not a physical compliance result.</p></div>`;
}

function graphInspectorDescription(node) {
  const record = node.record || {};
  const body = record.data || record;
  const translated = language === "ja" ? body.translations?.ja || {} : {};
  const text = (...values) => values.find((value) => typeof value === "string" && value.trim()) || "";
  const statement = text(language === "ja" && record.statement_ja, translated.statement, record.statement, body.statement);
  const description = text(language === "ja" && record.description_ja, translated.description, record.description, body.description, body.purpose, record.note, body.note, language === "ja" && record.rationale_ja, translated.rationale, record.rationale, body.rationale, record.scope);
  const paragraphs = [statement, description].filter((value, index, values) => value && values.indexOf(value) === index);
  return `<div class="graph-inspector-description${paragraphs.length ? "" : " is-empty"}">${paragraphs.length ? paragraphs.map((value) => `<p>${esc(value)}</p>`).join("") : "<p>No statement or description is recorded for this object.</p>"}</div>`;
}

function graphNode(id) {
  const data = DATA.balancing_cube;
  const proposal = architectureMode === "proposed" && data.architecture_draft;
  const proposed = proposal && [...proposal.functions, ...proposal.components].find((item) => item.id === id);
  if (proposed) return { id, revision: proposed.revision, name: proposed.name, kind: proposed.kind, record: proposed };
  const design = (data.designs || []).find((item) => item.id === id);
  if (design) return { id, revision: design.revision, name: design.name, kind: "design_candidate", record: design };
  const group = data.groups.find((item) => item.id === id);
  if (group) return { id, revision: group.revision, name: language === "ja" ? (group.name_ja || group.name) : group.name, kind: "requirement_group", record: group };
  const item = requirement(id);
  if (item) return { id, revision: item.revision, name: language === "ja" ? (item.name_ja || item.name) : item.name, kind: item.level === "mission" ? "mission" : "requirement", record: item };
  const parameter = (data.kdps || []).find((record) => record.id === id);
  if (parameter) return { id, revision: parameter.revision, name: parameter.name || id, kind: parameter.role === "design" ? "design_parameter" : parameter.role === "identify" ? "identification_parameter" : "parameter", record: parameter };
  const product = (data.products || []).find((record) => record.id === id);
  if (product) return { id, revision: product.revision, name: language === "ja" ? (product.name_ja || product.name) : product.name, kind: product.record_role === "component" ? "component" : "product", record: product };
  const fn = (data.functions || []).find((record) => record.id === id);
  if (fn) return { id, revision: fn.revision, name: fn.name, kind: "function", record: fn };
  const testCase = (data.verification_cases || []).find((record) => record.id === id);
  if (testCase) return { id, revision: testCase.revision, name: language === "ja" ? (testCase.data?.translations?.ja?.name || testCase.data?.name || id) : (testCase.data?.name || id), kind: "verification_case", record: testCase };
  if (data.model?.id === id) return { id, revision: data.model.revision, name: "Active system model", kind: "system_model", record: data.model };
  if (data.model?.simulation_snapshot_ref?.id === id) return { id, revision: data.model.simulation_snapshot_ref.revision, name: "Simulation snapshot", kind: "simulation_snapshot", record: data.model.simulation_snapshot_ref };
  return null;
}

function graphParentId(id) {
  const proposed = graphNode(id);
  if (proposed?.record.parent_ref) return proposed.record.parent_ref.id;
  const group = DATA.balancing_cube.groups.find((item) => item.id === id);
  if (group) return group.parent_ref?.id || null;
  const item = requirement(id);
  if (item && item.group_id !== id) return item.group_id;
  const product = (DATA.balancing_cube.products || []).find((record) => record.id === id);
  return product?.parent_product_ref?.id || null;
}

function graphPath(id) {
  const path = [];
  const seen = new Set();
  let current = id;
  while (current && !seen.has(current)) {
    seen.add(current);
    const node = graphNode(current);
    if (node) path.unshift(node);
    current = graphParentId(current);
  }
  return path;
}

function graphEdges() {
  const data = DATA.balancing_cube;
  const proposal = architectureMode === "proposed" ? data.architecture_draft : null;
  const replaced = new Set(proposal ? [...proposal.requirement_allocations, ...proposal.parameter_allocations, ...data.groups.map((g) => ({ source: g.id }))].map((a) => a.source) : []);
  const edges = [];
  const seen = new Set();
  const add = (source, target, type, sourceRevision = "", targetRevision = "", proposed = false, rationale = "") => {
    if (!source || !target || !type || source === target) return;
    const key = `${source}\u0000${type}\u0000${target}`;
    if (seen.has(key)) return;
    seen.add(key);
    edges.push({ source, target, type, sourceRevision, targetRevision, proposal: proposed, rationale, intent: type === "satisfy" });
  };
  const records = [...data.groups, ...data.requirements, ...(data.kdps || []), ...(data.products || []), ...(data.functions || []), ...(data.verification_cases || []), ...(data.designs || [])];
  records.forEach((record) => (record.links || []).forEach((link) => {
    if (proposal && link.type === "allocate" && replaced.has(record.id)) return;
    if (link.type === "satisfy" && requirement(link.target?.id)?.revision !== link.target?.revision) return;
    // Preserve the recorded relationship type, including derivations through requirement sets.
    if (link.type === "derive") {
      // The source record stores derived → source; the explorer reads the relationship as a sentence.
      add(link.target?.id, record.id, "derives", link.target?.revision, record.revision);
    } else {
      add(record.id, link.target?.id, link.type, record.revision, link.target?.revision, false, link.scope || link.note || "");
    }
  }));
  data.requirements.forEach((item) => {
    if (item.verification_case_ref?.id) add(item.verification_case_ref.id, item.id, "verify", item.verification_case_ref.revision, item.revision);
  });
  (data.kdps || []).forEach((parameter) => (parameter.requirements || []).forEach((requirementId) => add(requirementId, parameter.id, "constrain", "", parameter.revision)));
  (data.verification_cases || []).forEach((testCase) => {
    const record = testCase.data || {};
    (record.requirement_refs || []).forEach((ref) => add(testCase.id, ref.id, "verify", testCase.revision, ref.revision));
    if (!proposal && testCase.product_node) {
      const product = (data.products || []).find((candidate) => candidate.id === testCase.product_node);
      if (product) add(testCase.id, product.id, "allocate", testCase.revision, product.revision);
    }
  });
  (data.products || []).forEach((product) => {
    const parent = product.parent_product_ref;
    if (!proposal && parent?.id) add(product.id, parent.id, "parent_product_ref", product.revision, parent.revision);
    (product.function_refs || []).forEach((ref) => add(product.id, ref.id, "performs", product.revision, ref.revision));
    (product.component_refs || []).forEach((ref) => add(product.id, ref.id, "comprises", product.revision, ref.revision));
  });
  if (data.reviewed_architecture) add("cube.system", "cube.verification", "references", data.model.revision, data.model.revision, false, "External verification context; equipment is not onboard hardware.");
  if (proposal) {
    const draftAdd = (source, target, type, rationale = "") => add(source, target, type, graphNode(source)?.revision, graphNode(target)?.revision, true, rationale);
    proposal.functions.forEach((fn) => {
      draftAdd(fn.parent_ref.id, fn.id, "performs", fn.description);
      fn.component_ids.forEach((id) => draftAdd(fn.id, id, "allocate", fn.description));
    });
    proposal.components.forEach((part) => draftAdd(part.parent_ref.id, part.id, "comprises", part.description));
    [...proposal.requirement_allocations, ...proposal.parameter_allocations].forEach((allocation) => allocation.targets.forEach((id) => draftAdd(allocation.source, id, "allocate", allocation.rationale || "Proposed parameter responsibility; source values and uncertainty remain unchanged.")));
    draftAdd("cube.system", "cube.verification", "references", "External verification context; its equipment is not onboard hardware.");
  }
  const model = data.model || {};
  if (model.simulation_snapshot_ref) add(model.id, model.simulation_snapshot_ref.id, "references_snapshot", model.revision, model.simulation_snapshot_ref.revision);
  return edges;
}

function graphEdgeVerb(type) {
  return ({ allocate: "allocates", verify: "verifies", constrain: "constrains", satisfy: "satisfies", derives: "derives", contains: "contains", references_snapshot: "references", parent_product_ref: "belongs to" })[type] || type;
}

function graphEdgeSentence(edge) {
  return `${edge.source} ${graphEdgeVerb(edge.type)} ${edge.target}`;
}

function graphEdgesFor(id) { return graphEdges().filter((edge) => edge.source === id || edge.target === id); }

function graphKindLabel(kind) {
  return ({ mission: "MISSION", requirement: "REQUIREMENT", requirement_group: "REQUIREMENT GROUP", design_parameter: "DESIGN PARAMETER", identification_parameter: "IDENTIFICATION PARAMETER", parameter: "PARAMETER", product: "PRODUCT / PART", function: "FUNCTION", component: "COMPONENT", design_candidate: "DESIGN CANDIDATE", verification_case: "VERIFICATION CASE", system_model: "SYSTEM MODEL", simulation_snapshot: "SIMULATION SNAPSHOT" })[kind] || "MODEL OBJECT";
}

function graphNodeSummary(node) {
  const record = node.record || {};
  if (node.kind === "design_candidate") return "Recorded satisfaction intent · not physically verified";
  if (record.proposal) return `DRAFT · ${record.boundary} · ${record.approval_state.replaceAll("_", " ")}`;
  if (node.kind === "requirement_group") return `${record.level || "group"} · ${(record.members || []).length} members`;
  if (node.kind === "mission" || node.kind === "requirement") return `${record.level || "requirement"} · ${record.status || "status not recorded"} · ${record.verification_method || "method not recorded"}`;
  if (["design_parameter", "identification_parameter", "parameter"].includes(node.kind)) return `${record.role || "parameter"} · ${formatValue(record.value)}${record.unit ? ` ${record.unit}` : ""} · ${record.origin || "origin not recorded"}`;
  if (["product", "component", "function"].includes(node.kind)) return `${record.status || "status not recorded"} · ${record.physical_verified === true ? "physically verified" : "not physically verified"}`;
  if (node.kind === "verification_case") return `${record.data?.status || "planned"} · ${record.data?.method || "method not recorded"} · ${record.data?.execution_status || "not run"}`;
  if (node.kind === "system_model") return `${record.approval_state || "approval not recorded"} · ${record.scope || "model scope not recorded"}`;
  if (node.kind === "simulation_snapshot") return `${node.revision || "revision not recorded"} · pinned snapshot`;
  return "";
}

function graphNodeCard(node, focused = false) {
  if (!node) return `<span class="graph-vertex-missing">Unresolved model reference</span>`;
  return `<article class="graph-vertex-card ${focused ? "is-focus" : ""} ${graphSelectedId === node.id ? "is-selected" : ""}">
    <button type="button" class="graph-vertex" data-graph-select="${esc(node.id)}" title="Click to inspect attributes; double-click to focus this object">
      <span class="graph-vertex-kind">${esc(graphKindLabel(node.kind))}${node.record?.proposal ? " · PROPOSED" : ""}</span><code>${esc(node.id)}${node.revision ? ` <i>@${esc(node.revision)}</i>` : ""}</code><b>${esc(node.name)}</b><small>${esc(graphNodeSummary(node))}</small>
    </button>
    ${focused ? `<span class="graph-focus-marker">CURRENT FOCUS</span>` : `<button type="button" class="graph-vertex-focus" data-graph-center="${esc(node.id)}" aria-label="Center graph on ${esc(node.id)}">Center graph ↗</button>`}
  </article>`;
}

function selectGraphObject(id) {
  if (!graphNode(id)) return;
  graphSelectedId = id;
  $$(".graph-vertex-card").forEach((card) => card.classList.toggle("is-selected", card.querySelector("[data-graph-select]")?.dataset.graphSelect === id));
  renderGraphInspector(id);
}

function renderGraphInspector(id) {
  const node = graphNode(id);
  const panel = $("#graph-inspector");
  if (!node) { panel.innerHTML = `<b>No model object selected</b>`; return; }
  const record = node.record || {};
  const attributes = [];
  const push = (label, value) => { if (value !== undefined && value !== null && value !== "") attributes.push([label, formatValue(value)]); };
  if (node.kind === "mission" || node.kind === "requirement") {
    push("level", record.level); push("status", record.status); push("approval_state", record.approval_state);
    push("verification_method", record.verification_method); push("verification_status", record.verification_status);
    push("physical_verified", record.physical_verified); push("hardware_verification_required", record.hardware_verification_required);
  } else if (node.kind === "requirement_group") {
    push("level", record.level); push("record_role", record.record_role); push("members", (record.members || []).length);
    push("status", record.status); push("approval_state", record.approval_state);
  } else if (["design_parameter", "identification_parameter", "parameter"].includes(node.kind)) {
    push("role", record.role); push("origin", record.origin); push("value", record.value);
    push("unit", record.unit); push("bounds", record.bounds); push("uncertainty", record.uncertainty ?? record.standard_uncertainty);
    push("model_path", record.model_path); push("method", record.method); push("source", record.source);
  } else if (record.proposal || ["function", "component"].includes(node.kind)) {
    push("status", record.status); push("approval_state", record.approval_state); push("boundary", record.boundary); push("scope", record.scope);
    push("inputs", record.inputs); push("outputs", record.outputs);
    push("quantity", record.quantity); push("physical_verified", record.physical_verified);
    push("allocated_components", record.component_ids); push("related_requirements", record.requirement_ids);
  } else if (node.kind === "design_candidate") {
    push("claim_scope", record.claim_scope); push("physical_verified", record.physical_verified);
    push("source_record", record.source); push("input_digest", record.input_digest);
    push("snapshot_ref", record.source_record?.data?.snapshot_ref);
  } else if (node.kind === "product") {
    push("status", record.status); push("physical_verified", record.physical_verified);
    push("parent_product_ref", record.parent_product_ref?.id); push("method", record.method); push("note", record.note);
  } else if (node.kind === "verification_case") {
    push("status", record.data?.status); push("execution_status", record.data?.execution_status);
    push("method", record.data?.method); push("physical_verified", record.data?.physical_verified);
    push("conditions", record.data?.conditions?.join("; ")); push("evidence_count", (record.data?.evidence_refs || []).length);
  } else if (node.kind === "system_model") {
    push("approval_state", record.approval_state); push("api_profile", record.api_profile);
    push("scope", record.scope); push("snapshot_ref", record.simulation_snapshot_ref?.id);
  } else if (node.kind === "simulation_snapshot") {
    push("revision", node.revision); push("reference_kind", "pinned simulation snapshot");
  }
  const attributesMarkup = attributes.length ? `<dl class="graph-attribute-list">${attributes.map(([key, value]) => `<div><dt>${esc(key)}</dt><dd>${esc(value)}</dd></div>`).join("")}</dl>` : `<span class="empty-note">No additional attributes are included in this projection.</span>`;
  const incident = graphEdgesFor(id);
  const relationsMarkup = incident.length ? `<ul class="graph-link-list">${incident.map((edge) => {
    const outgoing = edge.source === id;
    const other = graphNode(outgoing ? edge.target : edge.source);
    return `<li><code>${edge.proposal ? "DRAFT · " : edge.intent ? "RECORDED INTENT · " : ""}${esc(graphEdgeSentence(edge))}</code><button type="button" data-graph-select="${esc(other?.id || "")}">${esc(other?.id || "unresolved reference")}${other ? ` · ${esc(other.name)}` : ""}</button>${edge.rationale ? `<span>${esc(edge.rationale)}</span>` : ""}</li>`;
  }).join("")}</ul>` : `<span class="empty-note">No direct relationships are recorded.</span>`;
  const sourceAttributes = `<details class="graph-source-attributes"><summary>All source attributes</summary><pre>${esc(JSON.stringify(record, null, 2))}</pre></details>`;
  const allocation = architectureMode === "proposed" && DATA.balancing_cube.architecture_draft.requirement_allocations.find((a) => a.source === id);
  const allocationNote = allocation ? `<div class="architecture-allocation-note"><b>DRAFT ALLOCATION · ${esc(allocation.scope.toUpperCase())}</b><p>${esc(allocation.rationale)}</p><small>Recorded targets: ${esc((record.links || []).filter((l) => l.type === "allocate").map((l) => l.target.id).join(", "))}</small></div>` : "";
  const screening = node.kind === "design_candidate" ? renderDesignScreening(record) : "";
  panel.innerHTML = `<span class="section-kicker">MODEL OBJECT INSPECTOR</span><h3>${esc(node.name)}</h3>${graphInspectorDescription(node)}<span class="graph-inspector-kind">${esc(graphKindLabel(node.kind))}${record.proposal ? " · DRAFT" : ""}</span><code class="graph-inspector-id">${esc(node.id)}${node.revision ? `@${esc(node.revision)}` : ""}</code>${allocationNote}${screening}<div class="graph-inspector-section"><b>Object attributes</b>${attributesMarkup}${sourceAttributes}</div><div class="graph-inspector-section"><b>Incident relationships · ${incident.length}</b>${relationsMarkup}</div>${id !== graphFocusId ? `<button type="button" class="graph-open-requirement" data-center-inspector="${esc(id)}">Center graph on this object ↗</button>` : ""}${requirement(id) ? `<button type="button" class="graph-open-requirement" data-open-requirement="${esc(id)}">Open requirement detail ↓</button>` : ""}`;
  $$(`[data-graph-select]`, panel).forEach((button) => button.addEventListener("click", () => selectGraphObject(button.dataset.graphSelect)));
  const center = $(`[data-center-inspector]`, panel);
  if (center) center.addEventListener("click", () => openGraphNode(center.dataset.centerInspector));
  const openRequirement = $("[data-open-requirement]", panel);
  if (openRequirement) openRequirement.addEventListener("click", () => {
    const target = requirement(openRequirement.dataset.openRequirement);
    if (!target) return;
    setView("cube");
    $("#group-filter").value = "all";
    searchText = "";
    $("#global-search").value = "";
    renderRequirements();
    selectRequirement(target.id);
    $("#requirement-detail").scrollIntoView({ behavior: "smooth", block: "center" });
  });
}

function openGraphNode(id, filter = "all") {
  if (!graphNode(id)) return;
  graphFocusId = id;
  graphSelectedId = id;
  graphEdgeFilter = filter;
  renderSystemGraph();
}

function renderSystemGraph() {
  const model = DATA.balancing_cube.model;
  const snapshot = model.simulation_snapshot_ref || {};
  const focus = graphNode(graphFocusId) || graphNode("M-VERTEX");
  if (!focus) return;
  graphFocusId = focus.id;
  const path = graphPath(focus.id);
  const allEdges = graphEdgesFor(focus.id);
  const counts = new Map();
  allEdges.forEach((edge) => counts.set(edge.type, (counts.get(edge.type) || 0) + 1));
  const filters = ["all", ...[...counts.keys()].sort()].map((type) => {
    const label = type === "all" ? `All edges · ${allEdges.length}` : `${graphEdgeVerb(type)} · ${counts.get(type)}`;
    return `<button type="button" class="graph-edge-filter ${graphEdgeFilter === type ? "is-active" : ""}" data-edge-filter="${esc(type)}" aria-pressed="${graphEdgeFilter === type}">${esc(label)}</button>`;
  }).join("");
  const visibleEdges = graphEdgeFilter === "all" ? allEdges : allEdges.filter((edge) => edge.type === graphEdgeFilter);
  const edgeRows = visibleEdges.map((edge, index) => {
    const outgoing = edge.source === focus.id;
    const neighbor = graphNode(outgoing ? edge.target : edge.source);
    const arrowhead = outgoing ? "M 90 3 L 97 7 L 90 11" : "M 10 3 L 3 7 L 10 11";
    return `<div class="graph-edge-row" style="grid-row:${index + 1};grid-column:2"><div class="graph-edge-connector ${outgoing ? "is-outgoing" : "is-incoming"}${edge.proposal ? " is-proposed" : ""}" role="img" aria-label="${esc(graphEdgeSentence(edge))}${edge.proposal ? " (draft)" : edge.intent ? " (recorded intent)" : ""}" title="${esc(graphEdgeSentence(edge))}"><code>${esc(graphEdgeVerb(edge.type))}</code><svg viewBox="0 0 100 14" preserveAspectRatio="none" aria-hidden="true"><path d="M 3 7 H 97"/><path class="graph-arrowhead" d="${arrowhead}"/></svg><small>${edge.proposal ? "DRAFT · " : edge.intent ? "INTENT · " : ""}${outgoing ? "outgoing →" : "← incoming"}</small></div>${graphNodeCard(neighbor)}</div>`;
  }).join("");
  const graphContents = visibleEdges.length
    ? `<div class="graph-focus-vertex" style="grid-column:1;grid-row:1 / span ${visibleEdges.length}">${graphNodeCard(focus, true)}</div>${edgeRows}`
    : `<div class="graph-focus-vertex" style="grid-column:1;grid-row:1">${graphNodeCard(focus, true)}</div><div class="graph-empty-edges" style="grid-column:2;grid-row:1">No direct edges match this relationship filter.</div>`;
  $("#graph-version").innerHTML = `<span><small>${architectureMode === "proposed" ? "RECORDED BASE MODEL" : "RECORDED MODEL"}</small><button type="button" class="graph-model-ref" data-graph-center="${esc(model.id)}"><code>${esc(model.id)}@${esc(model.revision)}</code><i>Inspect model object ↗</i></button></span><i>references →</i><span><small>PINNED SNAPSHOT</small><button type="button" class="graph-model-ref" data-graph-center="${esc(snapshot.id || "")}"><code>${esc(snapshot.id || "not recorded")}@${esc(snapshot.revision || "")}</code><i>Inspect snapshot object ↗</i></button></span>`;
  $("#model-graph").innerHTML = `<div class="graph-path" aria-label="Model path">${path.map((node, index) => `${index ? `<span aria-hidden="true">›</span>` : ""}<button type="button" data-graph-crumb="${esc(node.id)}" ${node.id === focus.id ? 'aria-current="page"' : ""}>${esc(node.name)}</button>`).join("")}</div>
    <div class="graph-layer-label"><span>ONE-HOP OBJECT GRAPH · ${esc(graphKindLabel(focus.kind))}</span><small>${allEdges.length} incident ${allEdges.length === 1 ? "edge" : "edges"}</small></div>
    <div class="graph-edge-filters" aria-label="Filter graph by relationship type">${filters}</div>
    <div class="graph-column-labels"><span>CURRENT FOCUS</span><span>CONNECTED OBJECTS</span></div><div class="graph-star">${graphContents}</div>
    <div class="graph-map-footer"><span>EDGE LABELS ARE RELATIONSHIP TYPES</span><span>DOUBLE-CLICK A NEIGHBOR OR USE CENTER GRAPH TO FOLLOW</span></div>`;
  $$(`[data-graph-select]`, $("#model-graph")).forEach((button) => {
    button.addEventListener("click", () => selectGraphObject(button.dataset.graphSelect));
    button.addEventListener("dblclick", () => openGraphNode(button.dataset.graphSelect));
  });
  $$(`[data-graph-center]`).forEach((button) => button.addEventListener("click", () => openGraphNode(button.dataset.graphCenter)));
  $$(`[data-edge-filter]`).forEach((button) => button.addEventListener("click", () => { graphEdgeFilter = button.dataset.edgeFilter; renderSystemGraph(); }));
  $$(`[data-graph-crumb]`).forEach((button) => button.addEventListener("click", () => openGraphNode(button.dataset.graphCrumb)));
  renderGraphInspector(graphSelectedId && graphNode(graphSelectedId) ? graphSelectedId : focus.id);
}

function renderRequirementDetail(r) {
  const card = $("#requirement-detail");
  if (!r) {
    card.innerHTML = `<div class="empty-detail"><span class="empty-orbit">§</span><b>No requirement selected</b><p>Change the filters or choose an obligation in the list.</p></div>`;
    return;
  }
  const t = COPY[language];
  const title = language === "ja" ? (r.name_ja || r.name) : r.name;
  const statement = language === "ja" ? (r.statement_ja || r.statement) : r.statement;
  const rationale = language === "ja" ? (r.rationale_ja || r.rationale) : r.rationale;
  const conditions = language === "ja" ? (r.conditions_ja || r.conditions) : r.conditions;
  const openItems = language === "ja" ? (r.unresolved_items_ja || r.unresolved_items) : r.unresolved_items;
  const allocation = DATA.balancing_cube.architecture_draft.requirement_allocations.find((a) => a.source === r.id);
  const proposedNodes = [...DATA.balancing_cube.architecture_draft.functions, ...DATA.balancing_cube.architecture_draft.components, ...DATA.balancing_cube.products];
  const allocationMarkup = allocation ? `<section class="detail-section architecture-allocation-note"><span class="detail-label">${DATA.balancing_cube.reviewed_architecture ? "REVIEWED ALLOCATION" : "PROPOSED ALLOCATION · DRAFT"}</span><p>${esc(allocation.rationale)}</p><div class="architecture-actions">${allocation.targets.map((id) => `<button type="button" data-architecture-node="${esc(id)}">${esc(proposedNodes.find((n) => n.id === id)?.name || id)} ↗</button>`).join("")}</div><small>${DATA.balancing_cube.reviewed_architecture ? "Recorded trace links below use this reviewed allocation." : "Recorded trace links below retain the source model's allocation."}</small></section>` : "";
  card.innerHTML = `
    <div class="detail-topline"><span class="req-row-id">${esc(r.id)} <i>@ ${esc(r.revision)}</i></span><button type="button" class="detail-menu" id="copy-id" aria-label="Copy requirement ID">⧉</button></div>
    <div class="detail-title-row"><div><span class="level-kicker">${esc(r.level || "requirement").toUpperCase()} · ${esc(r.group)}</span><h3>${esc(title)}</h3></div><span class="detail-symbol">§</span></div>
    <div class="detail-pills">${statusPill(humanize(r.status || "status not recorded"), "pill-draft", `status: ${r.status || "not recorded"}`)}${statusPill(humanize(r.approval_state || "review state not recorded"), "pill-pending", `approval_state: ${r.approval_state || "not recorded"}`)}${statusPill(humanize(r.verification_status || "verification not recorded"), "pill-notrun", `verification_status: ${r.verification_status || "not recorded"}`)}${statusPill(r.physical_verified === true ? "Physically verified" : "Not physically verified", "pill-unverified", `physical_verified: ${r.physical_verified === null ? "null" : r.physical_verified}`)}${r.hardware_verification_required ? statusPill("Hardware check required", "pill-hardware", "hardware_verification_required: true") : ""}</div>
    <section class="detail-section statement-section"><span class="detail-label">${t.statement}</span><blockquote>${esc(statement || "Organizational group — no standalone statement")}</blockquote></section>
    ${allocationMarkup}
    <section class="detail-section"><span class="detail-label">${t.acceptance}</span><div class="acceptance-box"><span class="acceptance-check">⊙</span><div><b>${esc(formatAcceptance(r.acceptance))}</b><small>${esc(r.verification_status || "not_run").replaceAll("_", " ")} · ${r.hardware_verification_required ? esc(t.hardware) : "hardware evidence not flagged"}</small></div></div></section>
    ${rationale ? `<section class="detail-section"><span class="detail-label">${t.rationale}</span><p class="detail-copy">${esc(rationale)}</p></section>` : ""}
    ${conditions?.length ? `<section class="detail-section"><span class="detail-label">${t.conditions}</span><ul class="detail-list">${conditions.map((x) => `<li>${esc(x)}</li>`).join("")}</ul></section>` : ""}
    <section class="detail-section"><span class="detail-label">${t.method}</span><div class="method-line"><span class="method-icon">${r.verification_method === "test" ? "⊙" : "⌕"}</span><b>${esc(r.verification_method || "not specified")}</b><small>${r.verification_case_ref ? `${esc(r.verification_case_ref.id)}@${esc(r.verification_case_ref.revision)}` : "no case linked"}</small></div></section>
    <section class="detail-section"><span class="detail-label">${t.unresolved} <i>${openItems.length.toString().padStart(2, "0")}</i></span>${openItems.length ? `<div class="open-item-list">${openItems.map((item) => `<article><span>${esc(item.id)}</span><p>${esc(item.description)}</p><small>OWNER · ${esc(item.owner || "TBD")}</small></article>`).join("")}</div>` : `<span class="empty-note">No open items are recorded for this requirement.</span>`}</section>
    <section class="detail-section"><span class="detail-label">${t.designParams} <i>${r.kdps.length.toString().padStart(2, "0")}</i></span>${r.kdps.length ? `<div class="kdp-list">${r.kdps.map((k) => `<details class="kdp-item"><summary><b>${esc(k.id)}</b><span>${esc(k.name || "Parameter")}</span><i>＋</i></summary><div><span>${esc(k.symbol || k.quantity || "")}</span><b>${esc(formatValue(k.value))} ${esc(k.unit || "")}</b><small>${esc(k.revision)}${k.uncertainty ? ` · uncertainty ${esc(formatValue(k.uncertainty))}` : ""}${k.role ? ` · ${esc(k.role)}` : ""}${k.origin ? ` · origin: ${esc(k.origin)}` : ""}</small></div></details>`).join("")}</div>` : `<span class="empty-note">No KDP link is recorded.</span>`}</section>
    <details class="detail-section trace-details"><summary><span class="detail-label">${t.links}</span><i>＋</i></summary>${renderLinks(r)}</details>
    <details class="detail-section trace-details"><summary><span class="detail-label">${t.case}</span><i>＋</i></summary>${r.verification_case_ref ? `<div class="case-summary"><b>${esc(r.verification_case?.name || r.verification_case_ref.id)}</b><pre>${esc(JSON.stringify(r.verification_case, null, 2))}</pre></div>` : `<span class="empty-note">No planned case linked.</span>`}</details>
    <details class="detail-section trace-details"><summary><span class="detail-label">${t.source}</span><i>＋</i></summary><div class="source-record"><b>${esc(r.source_record?.id || "Source not recorded")}@${esc(r.source_record?.revision || "")}</b><p>Statement status: ${esc(r.status)} · source statement status: ${esc(r.source_status || "not recorded")}</p><small>MODEL ${esc(DATA.balancing_cube.model.id)}@${esc(DATA.balancing_cube.model.revision)}</small></div></details>
    <button type="button" class="detail-propose" id="focus-review">${t.propose}<span>↗</span></button>`;
  $("#copy-id").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(r.id); showToast(`${r.id} copied`); }
    catch { showToast(r.id); }
  });
  $("#focus-review").addEventListener("click", () => {
    $("#proposal-text").focus();
    $("#review-panel").scrollIntoView({ behavior: "smooth", block: "center" });
  });
  $$('[data-architecture-node]', card).forEach((button) => button.addEventListener("click", () => showArchitectureObject(button.dataset.architectureNode)));
}

function selectRequirement(id) {
  selectedId = id;
  $$(".req-row").forEach((button) => button.classList.toggle("is-selected", button.dataset.requirement === id));
  renderRequirementDetail(requirement(id));
  loadDraftForSelection();
}

function loadDraftForSelection() {
  const r = requirement(selectedId);
  $("#review-selected").innerHTML = r ? `<b>${esc(r.id)}</b><span>${esc(r.name)}</span>` : `<span>Select a requirement above</span>`;
  const saved = drafts[selectedId] || {};
  $("#proposal-text").value = saved.proposed || r?.statement || "";
  $("#proposal-note").value = saved.note || "";
  $("#proposal-status-field").value = saved.proposedStateField || "";
  $("#proposal-status-value").value = saved.proposedStateValue || "";
  $("#draft-save-status").textContent = saved.updatedAt ? `Saved locally ${new Date(saved.updatedAt).toLocaleString()}` : "No saved proposal for this requirement";
}

function saveDraft() {
  const r = requirement(selectedId);
  if (!r) return showToast("Choose a requirement first");
  const proposed = $("#proposal-text").value.trim();
  const note = $("#proposal-note").value.trim();
  const proposedStateField = $("#proposal-status-field").value;
  const proposedStateValue = $("#proposal-status-value").value.trim();
  if (Boolean(proposedStateField) !== Boolean(proposedStateValue)) return showToast("Choose both a status field and a proposed value");
  if (proposed === r.statement && !note && !proposedStateField) {
    delete drafts[r.id];
  } else {
    drafts[r.id] = { proposed, note, proposedStateField, proposedStateValue, updatedAt: new Date().toISOString(), requirement: r.name, current: r.statement, revision: r.revision, currentStatus: r.status, currentApprovalState: r.approval_state, currentVerificationStatus: r.verification_status, currentPhysicalVerified: r.physical_verified };
  }
  localStorage.setItem(draftStorageKey, JSON.stringify(drafts));
  $("#draft-save-status").textContent = drafts[r.id]?.updatedAt ? `Saved locally ${new Date(drafts[r.id].updatedAt).toLocaleString()}` : "Proposal cleared";
  renderSavedDrafts();
  showToast(drafts[r.id] ? "Proposal saved in this browser" : "Proposal cleared");
}

function renderSavedDrafts() {
  const entries = Object.entries(drafts);
  const container = $("#saved-drafts");
  if (!entries.length) { container.innerHTML = `<span class="empty-note">No saved proposals yet.</span>`; return; }
  container.innerHTML = `<div class="saved-draft-heading"><b>${entries.length} SAVED ${entries.length === 1 ? "PROPOSAL" : "PROPOSALS"}</b><button type="button" id="clear-all-drafts" class="quiet-button">Clear all</button></div><div class="saved-draft-list">${entries.map(([id, draft]) => `<article><button type="button" data-open-draft="${esc(id)}"><b>${esc(id)}</b><span>${esc(draft.requirement || "Requirement")}${draft.proposedStateField ? ` · label proposal: ${esc(draft.proposedStateField)}` : ""}</span></button><button type="button" class="remove-draft" data-delete-draft="${esc(id)}" aria-label="Delete ${esc(id)} proposal">×</button></article>`).join("")}</div>`;
  $$('[data-open-draft]').forEach((button) => button.addEventListener("click", () => { setView("cube"); $("#group-filter").value = "all"; searchText = ""; $("#global-search").value = ""; renderRequirements(); selectRequirement(button.dataset.openDraft); $("#review-panel").scrollIntoView({ behavior: "smooth", block: "center" }); }));
  $$('[data-delete-draft]').forEach((button) => button.addEventListener("click", () => { delete drafts[button.dataset.deleteDraft]; localStorage.setItem(draftStorageKey, JSON.stringify(drafts)); renderSavedDrafts(); loadDraftForSelection(); }));
  $("#clear-all-drafts").addEventListener("click", () => { drafts = {}; localStorage.removeItem(draftStorageKey); renderSavedDrafts(); loadDraftForSelection(); showToast("Local proposals cleared"); });
}

function exportReview() {
  const entries = Object.entries(drafts);
  if (!entries.length) return showToast("Save a proposal before exporting");
  const body = [
    "# Requirements review packet",
    "",
    `Model: ${DATA.balancing_cube.model.id}@${DATA.balancing_cube.model.revision}`,
    `Model SHA-256: ${DATA.generated_from.model_sha256}`,
    `Snapshot: ${JSON.stringify(DATA.generated_from.snapshot_ref)}`,
    `Source records SHA-256: ${DATA.generated_from.record_set_sha256}`,
    "Source: One-Piece Balancing Cube versioned requirements; exported browser-local proposals are not canonical changes.",
    "",
    ...entries.flatMap(([id, draft]) => [
      `## ${id} — ${draft.requirement}`,
      `Current (${draft.revision}): ${draft.current}`,
      `Current labels: status=${draft.currentStatus || "not recorded"}; approval_state=${draft.currentApprovalState || "not recorded"}; verification_status=${draft.currentVerificationStatus || "not recorded"}; physical_verified=${draft.currentPhysicalVerified ?? "null"}`,
      `Proposed: ${draft.proposed || "(no wording change)"}`,
      `Proposed label change: ${draft.proposedStateField ? `${draft.proposedStateField} → ${draft.proposedStateValue}` : "(none)"}`,
      `Question / rationale: ${draft.note || "(none recorded)"}`,
      `Saved: ${draft.updatedAt}`,
      "",
    ]),
    "## Next step",
    "Discuss these items with Codex. Approval and canonical model updates remain human-controlled.",
  ].join("\n");
  const blob = new Blob([body], { type: "text/markdown;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `requirements-review-${new Date().toISOString().slice(0, 10)}.md`;
  a.click();
  URL.revokeObjectURL(a.href);
  showToast(`Exported ${entries.length} proposal${entries.length === 1 ? "" : "s"}`);
}

function renderEclss() {
  const config = DATA.eclss.scenario;
  const thresholds = config.thresholds || {};
  const thresholdRows = [
    ["CO₂", "co2_storage_high_kg", "High band · ARS trigger", "kg", "threshold-high"],
    ["CO₂", "co2_storage_critical_kg", "Critical band", "kg", "threshold-critical"],
    ["O₂", "o2_storage_low_kg", "Low band · OGS trigger", "kg", "threshold-low"],
    ["O₂", "o2_storage_critical_kg", "Critical band", "kg", "threshold-critical"],
    ["H₂O", "product_water_low_l", "Low band · WRS trigger", "L", "threshold-low"],
    ["H₂O", "product_water_critical_l", "Critical band", "L", "threshold-critical"],
  ];
  $("#eclss-source").textContent = DATA.eclss.source;
  $("#eclss-summary").innerHTML = [
    ["CREW SIZE", `${config.plant_sim.crew.size}`, "people"],
    ["RUN HORIZON", `${config.simulation.steps}`, "steps"],
    ["PRIMARY OBJECTIVE", humanize(config.design_constraints.objective.primary), "lexicographic"],
    ["ACCEPTANCE HORIZON", `${config.evaluation.tcl.reference_seconds / 3600}`, "hours · TCL reference"],
  ].map((x, i) => `<article class="stat-card ${["stat-amber", "stat-blue", "stat-green", "stat-coral"][i]}"><span class="stat-label">${esc(x[0])}</span><div><b>${esc(x[1])}</b><small>${esc(x[2])}</small></div><span class="stat-index">0${i + 1}</span></article>`).join("");
  $("#eclss-thresholds").innerHTML = thresholdRows.map(([resource, key, caption, unit, tone]) => `<article class="threshold-card ${tone}"><span>${esc(resource)}</span><b>${esc(thresholds[key])}<small>${esc(unit)}</small></b><p>${esc(caption)}</p><code>thresholds.${esc(key)}</code></article>`).join("");
  const survival = config.plant_sim.survival;
  $("#eclss-survival").innerHTML = `<div class="survival-note"><span class="survival-icon">♥</span><div><b>${survival.enabled ? "Survival model enabled" : "Survival model disabled"}</b><p>Survival objective is full crew retention. The configured crew is ${config.plant_sim.crew.size}; warning and critical band dwell rules below define the simulation's attrition behavior.</p></div></div><div class="rule-cards">${Object.entries(survival).filter(([k]) => k !== "enabled").map(([resource, rule]) => `<article><span>${esc(resource.toUpperCase())}</span>${Object.entries(rule).map(([key, value]) => `<small>${esc(humanize(key))}<b>${esc(formatValue(value))}</b></small>`).join("")}</article>`).join("")}</div>`;
  const design = config.design_constraints;
  const budgetCards = Object.entries(design.budgets).map(([key, value]) => `<div class="constraint-metric"><span>${esc(humanize(key))}</span><b>${esc(value)}<small>${esc(key.includes("mass") ? "kg" : key.includes("cost") ? "MUSD" : "m³")}</small></b><code>design_constraints.budgets.${esc(key)}</code></div>`).join("");
  const bounds = flattenLeaves(design.subsystem_bounds).map((leaf) => `<div class="constraint-leaf"><code>subsystem_bounds.${esc(leaf.path)}</code><b>${esc(Array.isArray(leaf.value) ? leaf.value.join(" → ") : leaf.value)}</b></div>`).join("");
  const policy = Object.entries(design.simulation_policy).map(([key, value]) => `<div class="policy-row"><span>${esc(humanize(key))}</span><b class="${value ? "policy-yes" : "policy-no"}">${esc(formatValue(value))}</b></div>`).join("");
  $("#eclss-design").innerHTML = `<div class="constraint-card"><span class="detail-label">BUDGETS · SOFT FEASIBILITY LABELS</span><div class="constraint-metrics">${budgetCards}</div><div class="constraint-subhead">Capacity envelope</div>${bounds}<div class="constraint-subhead">Candidate execution policy</div>${policy}</div><div class="objective-card"><span class="detail-label">LEXICOGRAPHIC OBJECTIVE</span><div class="objective-primary"><small>01 · FIRST</small><b>${esc(humanize(design.objective.primary))}</b><p>Keep the complete crew alive.</p></div><div class="objective-secondary"><small>02 · THEN</small><b>${esc(humanize(design.objective.secondary))}</b><p>Use the scorecard to compare survivors.</p></div><div class="objective-note">Out-of-budget results can still be simulated and reported. The human decides whether a provisional final design is acceptable.</div></div>`;
  const evalConfig = config.evaluation;
  const evalBlocks = Object.entries(evalConfig).map(([key, value], i) => {
    const leaves = flattenLeaves(value);
    return `<article class="evaluation-card"><div class="eval-head"><span>0${i + 1}</span><div><b>${esc(humanize(key))}</b><code>evaluation.${esc(key)}</code></div></div><div class="eval-values">${leaves.map((leaf) => `<div><span>${esc(leaf.path || key)}</span><b>${esc(formatValue(leaf.value))}</b></div>`).join("")}</div></article>`;
  }).join("");
  $("#eclss-evaluation").innerHTML = evalBlocks;
  $("#eclss-raw-tree").innerHTML = renderTree({ scenario: config, actors: DATA.eclss.agents }, "ECLSS configuration", 0);
}

function renderTree(value, key, depth = 0) {
  if (value === null || typeof value !== "object") return `<div class="tree-leaf"><code>${esc(key)}</code><span class="tree-value ${typeof value === "boolean" ? (value ? "is-true" : "is-false") : ""}">${esc(formatValue(value))}</span></div>`;
  if (Array.isArray(value)) {
    return `<details class="tree-node" ${depth === 0 ? "open" : ""}><summary><b>${esc(key)}</b><small>${value.length} items</small></summary><div class="tree-children">${value.map((v, i) => renderTree(v, `[${i}]`, depth + 1)).join("")}</div></details>`;
  }
  const entries = Object.entries(value);
  return `<details class="tree-node" ${depth < 1 ? "open" : ""}><summary><b>${esc(key)}</b><small>${entries.length} fields</small></summary><div class="tree-children">${entries.map(([childKey, childValue]) => renderTree(childValue, childKey, depth + 1)).join("")}</div></details>`;
}

function renderScrubber() {
  $("#scrubber-raw-tree").innerHTML = renderTree(DATA.scrubber.scenario, "scenario", 0);
  $("#scrubber-source").textContent = DATA.scrubber.source;
}

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.add("is-visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("is-visible"), 2400);
}

function setLanguage(lang) {
  language = lang;
  document.documentElement.lang = lang;
  $("#language-toggle").textContent = lang === "en" ? "JA" : "EN";
  $("#group-filter").options[0].textContent = COPY[lang].all;
  $("#status-filter").options[1].textContent = COPY[lang].open;
  $(".explorer-head h2").textContent = COPY[lang].requirements;
  $("#global-search").placeholder = lang === "ja" ? "ID、要求文、未解決項目を検索…" : "Search IDs, statements, questions…";
  renderRequirements();
  renderSystemGraph();
}

function wireControls() {
  $$(".model-link").forEach((button) => button.addEventListener("click", () => setView(button.dataset.view)));
  $("#group-filter").addEventListener("change", renderRequirements);
  $("#status-filter").addEventListener("change", renderRequirements);
  $("#clear-filters").addEventListener("click", () => { $("#group-filter").value = "all"; $("#status-filter").value = "all"; searchText = ""; $("#global-search").value = ""; renderRequirements(); });
  $("#global-search").addEventListener("input", (event) => { searchText = event.target.value; if (activeView !== "cube") setView("cube"); renderRequirements(); });
  $("#global-search").addEventListener("keydown", (event) => { if (event.key === "Escape") { event.target.value = ""; searchText = ""; renderRequirements(); event.target.blur(); } });
  document.addEventListener("keydown", (event) => { if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") { event.preventDefault(); $("#global-search").focus(); } });
  $("#language-toggle").addEventListener("click", () => setLanguage(language === "en" ? "ja" : "en"));
  $("#graph-home").addEventListener("click", () => openGraphNode("M-VERTEX"));
  $("#save-draft").addEventListener("click", saveDraft);
  $("#review-export-top").addEventListener("click", exportReview);
  $$("[data-jump]").forEach((button) => button.addEventListener("click", () => {
    const target = $(`#${button.dataset.jump}`);
    const ownerView = target?.closest(".view");
    if (ownerView && !ownerView.classList.contains("is-visible")) setView(ownerView.id.replace("view-", ""));
    target?.scrollIntoView({ behavior: "smooth", block: "center" });
  }));
  $("#proposal-text").addEventListener("input", () => { $("#draft-save-status").textContent = "Unsaved changes"; });
  $("#proposal-note").addEventListener("input", () => { $("#draft-save-status").textContent = "Unsaved changes"; });
  $("#proposal-status-field").addEventListener("change", () => { $("#draft-save-status").textContent = "Unsaved changes"; });
  $("#proposal-status-value").addEventListener("input", () => { $("#draft-save-status").textContent = "Unsaved changes"; });
}

function renderModelProvenance() {
  const model = DATA.balancing_cube.model;
  $("#model-status-pill").textContent = `${humanize(model.approval_state || "not recorded")} · ${model.revision}`;
  $("#model-status-title").textContent = `Requirement and allocation state: ${humanize(model.approval_state || "not recorded")}`;
  $("#model-status-copy").textContent = `This view pins ${model.id}@${model.revision}. Review, test execution and physical verification are separate states. Browser proposals do not change the canonical model.`;
  for (const view of ["eclss", "scrubber"]) {
    if (!DATA[view]) {
      $(`.model-link[data-view="${view}"]`).hidden = true;
      $(`#view-${view}`).hidden = true;
    }
  }
}

async function init() {
  const responses = await Promise.all([fetch("./data/models.json"), fetch("./data/cube-architecture-draft.json"), fetch("./data/design-claims.json")]);
  for (const response of responses) if (!response.ok) throw new Error(`Could not load model data (${response.status})`);
  const [model, architecture, designClaims] = await Promise.all(responses.map((r) => r.json()));
  DATA = model;
  draftStorageKey = `onepiece.review-drafts.v2.${DATA.generated_from.project_id}.${DATA.generated_from.model_sha256}`;
  try { drafts = JSON.parse(localStorage.getItem(draftStorageKey) || "{}"); } catch { drafts = {}; }
  if (!drafts || typeof drafts !== "object" || Array.isArray(drafts)) drafts = {};
  DATA.balancing_cube.architecture_draft = DATA.balancing_cube.reviewed_architecture || architecture;
  if (DATA.balancing_cube.reviewed_architecture || architecture.status === "unavailable") architectureMode = "recorded";
  DATA.balancing_cube.designs = designClaims.designs;
  DATA.balancing_cube.design_claims = designClaims;
  renderCubeStats();
  renderArchitecturePanel();
  renderDesignCoverage();
  renderSystemGraph();
  initGroupControls();
  renderModelProvenance();
  if (DATA.eclss) renderEclss();
  if (DATA.scrubber) renderScrubber();
  wireControls();
  selectedId = requirement("M-VERTEX") ? "M-VERTEX" : (DATA.balancing_cube.requirements[0]?.id || null);
  renderRequirements();
  renderSavedDrafts();
  loadDraftForSelection();
}

init().catch((error) => {
  console.error(error);
  document.body.innerHTML = `<main style="font:16px sans-serif;padding:4rem;color:#142132"><h1>Model data could not be loaded</h1><p>${esc(error.message)}</p></main>`;
});
