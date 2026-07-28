// ============================================================
// NAVEGACIÓN ENTRE SECCIONES (one-pager, sin recarga de página)
// ============================================================
const sections = ["inicio", "modelo", "historico", "login", "admin"];
let isLoggedIn = false;

function showSection(name, scrollToId) {
  if (name === "admin" && !isLoggedIn) name = "login";

  sections.forEach((s) => {
    document.getElementById("page-" + s).classList.toggle("is-hidden", s !== name);
  });

  document.querySelectorAll(".nav-link").forEach((a) => {
    const linkTarget = a.dataset.scroll ? "inicio" : a.dataset.section;
    a.classList.toggle("is-active", linkTarget === name || (name === "admin" && a.dataset.section === "login"));
  });

  document.getElementById("loginNavLink").textContent = isLoggedIn ? "Admin" : "Login";
  document.getElementById("loginNavLink").dataset.section = isLoggedIn ? "admin" : "login";

  if (scrollToId) {
    // Espera a que la sección esté visible antes de medir su posición
    requestAnimationFrame(() => {
      document.getElementById(scrollToId).scrollIntoView({ behavior: "smooth", block: "start" });
    });
  } else {
    window.scrollTo(0, 0);
  }
  document.getElementById("navLinks").classList.remove("is-open");
}

document.querySelectorAll(".nav-link").forEach((a) => {
  a.addEventListener("click", (e) => {
    e.preventDefault();
    showSection(a.dataset.section, a.dataset.scroll);
  });
});
document.querySelectorAll("[data-scroll]:not(.nav-link)").forEach((el) => {
  el.addEventListener("click", () => {
    document.getElementById(el.dataset.scroll).scrollIntoView({ behavior: "smooth", block: "start" });
  });
});
document.getElementById("navToggle").addEventListener("click", () => {
  document.getElementById("navLinks").classList.toggle("is-open");
});

// ============================================================
// INICIO — fixtures ilustrativos de la temporada 2026/27
// ============================================================
// ============================================================
// MARQUESINA — próxima fecha, horizontal, clicable para precargar el predictor
// ============================================================
function renderMarquee() {
  const nextJornada = FIXTURES_2026_27[0].jornada;
  const items = FIXTURES_2026_27.filter((f) => f.jornada === nextJornada);

  const chip = (f) => `
    <button type="button" class="marquee__chip" data-home="${f.home}" data-away="${f.away}" data-date="${f.date}">
      <span class="marquee__chip-date">${formatDate(f.date)}</span>
      <span class="marquee__chip-teams">${f.home} <span class="marquee__chip-vs">vs</span> ${f.away}</span>
    </button>`;

  // Se duplica la lista para que la animación de scroll infinito no muestre un salto/corte.
  const html = items.map(chip).join("") + items.map(chip).join("");
  const track = document.getElementById("marqueeTrack");
  track.innerHTML = html;

  track.querySelectorAll(".marquee__chip").forEach((chipEl) => {
    chipEl.addEventListener("click", () => {
      homeSelect.value = chipEl.dataset.home;
      awaySelect.value = chipEl.dataset.away;
      dateInput.value = chipEl.dataset.date;
      updatePredictBtn();
      document.getElementById("predictor-section").scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
}

function formatDate(iso) {
  const [y, m, d] = iso.split("-");
  const dias = ["dom", "lun", "mar", "mié", "jue", "vie", "sáb"];
  const dt = new Date(Number(y), Number(m) - 1, Number(d));
  return `${dias[dt.getDay()]} ${d}/${m}/${y}`;
}

// ============================================================
// PREDICCIÓN — mismo mock de antes, con equipos reales
// ============================================================
const FACTOR_DEFS = [
  { label: "Forma reciente (últimos 5 partidos)", icon: "🔥" },
  { label: "Rendimiento como visitante", icon: "🚌" },
  { label: "Historial directo (H2H)", icon: "⚔️" },
  { label: "Bajas y sanciones", icon: "🚑" },
  { label: "Motivación y posición en tabla", icon: "📊" },
  { label: "Descanso entre partidos", icon: "⏱️" },
];

function mockFactors() {
  const raw = FACTOR_DEFS.map(() => Math.random());
  const total = raw.reduce((a, b) => a + b, 0);
  const normalized = raw.map((v) => Math.round((v / total) * 100));
  return FACTOR_DEFS.map((def, i) => ({ ...def, weight: normalized[i] })).sort((a, b) => b.weight - a.weight);
}

const homeSelect = document.getElementById("home-team");
const awaySelect = document.getElementById("away-team");
const dateInput = document.getElementById("match-date");
const predictForm = document.getElementById("predict-form");
const predictBtn = document.getElementById("predict-btn");
const spinner = document.getElementById("spinner");
const resultOk = document.getElementById("result-ok");
const resultError = document.getElementById("result-error");

LALIGA_TEAMS.forEach((t) => {
  homeSelect.add(new Option(t, t));
  awaySelect.add(new Option(t, t));
});
dateInput.value = new Date().toISOString().slice(0, 10);

function updatePredictBtn() {
  predictBtn.disabled = !(homeSelect.value && awaySelect.value && dateInput.value);
}
function handleHomeChange() {
  if (homeSelect.value === awaySelect.value) awaySelect.value = "";
  updatePredictBtn();
}
function handleAwayChange() {
  if (awaySelect.value === homeSelect.value) homeSelect.value = "";
  updatePredictBtn();
}
homeSelect.addEventListener("change", handleHomeChange);
awaySelect.addEventListener("change", handleAwayChange);
dateInput.addEventListener("change", updatePredictBtn);

let history = [];

function mockPredict(home, away) {
  return new Promise((resolve) => {
    setTimeout(() => {
      const probH = Math.round(Math.random() * 60 + 20) / 100;
      const probD = Math.round(Math.random() * (100 - probH * 100) * 0.4) / 100;
      const probA = Math.round((1 - probH - probD) * 100) / 100;
      const probs = { H: probH, D: probD, A: probA };
      const prediction = Object.keys(probs).reduce((a, b) => (probs[a] > probs[b] ? a : b));
      resolve({
        status: "ok", prediction, probabilities: probs,
        model_version: CHAMPION.modelVersion, data_version: "laliga_matches_1995_96_to_2025_26_v1",
        latency_ms: 400,
      });
    }, 500);
  });
}

const OUTCOME_LABELS = { H: "Victoria local", D: "Empate", A: "Victoria visitante" };
const RESULT_COLORS = { H: "home", D: "draw", A: "away" };
const RADIUS = 54, CIRC = 2 * Math.PI * RADIUS;

function renderResult(result, home, away) {
  resultError.style.display = "none";
  resultOk.style.display = "block";

  document.getElementById("result-teams").innerHTML =
    `<span style="color:var(--green)">${home}</span> <span style="color:var(--gold);font-size:0.85em;">VS</span> <span style="color:var(--sky)">${away}</span>`;
  document.getElementById("result-prediction").textContent = OUTCOME_LABELS[result.prediction];

  const pct = Math.round(result.probabilities[result.prediction] * 100);
  document.getElementById("gaugeValue").textContent = pct + "%";
  const offset = CIRC - (pct / 100) * CIRC;
  document.getElementById("gaugeArc").style.strokeDasharray = CIRC;
  document.getElementById("gaugeArc").style.strokeDashoffset = offset;

  const barsEl = document.getElementById("probBars");
  barsEl.innerHTML = ["H", "D", "A"].map((k) => {
    const p = Math.round(result.probabilities[k] * 100);
    const label = k === "H" ? "Local" : k === "D" ? "Empate" : "Visitante";
    return `<div class="bar">
      <span class="bar__label">${label}</span>
      <div class="bar__track"><div class="bar__fill bar__fill--${RESULT_COLORS[k]}" style="width:${p}%"></div></div>
      <span class="bar__value">${p}%</span>
    </div>`;
  }).join("");

  const factors = mockFactors();
  document.getElementById("factorsList").innerHTML = factors.map((f) => `
    <li class="factor">
      <span class="factor__icon">${f.icon}</span>
      <span class="factor__label">${f.label}</span>
      <div class="factor__weight"><span style="width:${f.weight}%"></span></div>
    </li>
  `).join("");

  document.getElementById("result-meta").textContent =
    `Modelo: ${result.model_version} · Datos: ${result.data_version} · ${result.latency_ms} ms`;
}

function renderHistory() {
  const listEl = document.getElementById("historyList");
  const emptyEl = document.getElementById("historyEmpty");
  const clearBtn = document.getElementById("clearHistoryBtn");
  emptyEl.style.display = history.length ? "none" : "block";
  clearBtn.style.display = history.length ? "inline-flex" : "none";
  listEl.innerHTML = history.map((h) => `
    <li class="history__item">
      <div><strong>${h.home}</strong> vs <strong>${h.away}</strong><br><small>${formatDate(h.date)} · ${h.status === "error" ? "Error de validación" : OUTCOME_LABELS[h.prediction]}</small></div>
      <span class="bar__value">${h.status === "error" ? "—" : h.confidencePct + "%"}</span>
    </li>
  `).join("");
}
document.getElementById("clearHistoryBtn").addEventListener("click", () => { history = []; renderHistory(); });

// ---- Parámetros de búsqueda + resultados recientes (se llenan tras predecir) ----
function renderParamsSummary(home, away, date, result) {
  document.getElementById("paramHome").textContent = home;
  document.getElementById("paramAway").textContent = away;
  document.getElementById("paramDate").textContent = formatDate(date);
  document.getElementById("paramResult").textContent =
    result && result.status === "ok" ? OUTCOME_LABELS[result.prediction] : "Error de validación";
}

function renderRecentResults(home, away) {
  const grid = document.getElementById("recentResultsGrid");
  document.getElementById("recentResultsNote").style.display = "none";

  function column(team) {
    const matches = (HISTORICAL_RESULTS[team] || []).slice(0, 3);
    const items = matches.map((m) => `
      <li class="history__item">
        <div><strong>${m.home}</strong> ${m.home_goals} - ${m.away_goals} <strong>${m.away}</strong><br><small>${formatDate(m.date)}</small></div>
      </li>
    `).join("");
    return `<div class="recent-results-col">
      <h4 class="recent-results-col__title">${team}</h4>
      <ul class="history__list">${items || '<li class="history__empty">Sin datos recientes.</li>'}</ul>
    </div>`;
  }

  grid.innerHTML = column(home) + column(away);
}

predictForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const home = homeSelect.value, away = awaySelect.value, date = dateInput.value;

  resultOk.style.display = "none";
  resultError.style.display = "none";
  spinner.style.display = "block";
  predictBtn.disabled = true;

  if (home.toLowerCase() === away.toLowerCase()) {
    spinner.style.display = "none";
    resultError.style.display = "block";
    document.getElementById("error-code").textContent = "INVALID_INPUT";
    document.getElementById("error-message").textContent = "El equipo local y el visitante deben ser distintos.";
    history.unshift({ home, away, date, status: "error" });
    renderHistory();
    renderParamsSummary(home, away, date, { status: "error" });
    updatePredictBtn();
    return;
  }

  const result = await mockPredict(home, away);
  spinner.style.display = "none";
  updatePredictBtn();
  renderResult(result, home, away);
  renderParamsSummary(home, away, date, result);
  renderRecentResults(home, away);

  history.unshift({
    home, away, date, status: "ok", prediction: result.prediction,
    confidencePct: Math.round(result.probabilities[result.prediction] * 100),
  });
  renderHistory();
});

// ============================================================
// MODELO — tabla de candidatos + champion (vista pública)
// ============================================================
function renderCandidatesTable(targetId, detailed) {
  const rows = MODEL_CANDIDATES.map((c) => `
    <tr>
      <td><span class="pill">${c.id}</span></td>
      <td>${c.algorithm}</td>
      <td>${c.member}</td>
      <td>${c.valF1.toFixed(3)}</td>
      <td>${c.gap.toFixed(3)}</td>
      <td><span class="status-badge status-badge--${c.status}">${c.status}</span></td>
      ${detailed ? `<td>${c.trainF1.toFixed(3)}</td>` : ""}
    </tr>
  `).join("");
  const header = `<tr>
    <th>Modelo</th><th>Algoritmo</th><th>Responsable</th><th>macro-F1 val.</th><th>Gap</th><th>Estado</th>
    ${detailed ? "<th>macro-F1 train</th>" : ""}
  </tr>`;
  document.getElementById(targetId).innerHTML = `<thead>${header}</thead><tbody>${rows}</tbody>`;
}

function renderChampionGrid() {
  const items = [
    ["Algoritmo", CHAMPION.algorithm.split("(")[0]],
    ["macro-F1 validación", CHAMPION.valMacroF1.toFixed(3)],
    ["Gap de overfitting", CHAMPION.gap.toFixed(3)],
    ["macro-F1 test (evaluación única)", CHAMPION.testMacroF1.toFixed(3)],
  ];
  document.getElementById("championGrid").innerHTML = items.map(([l, v]) => `
    <div><span class="objective-label">${l}</span><span class="objective-value">${v}</span></div>
  `).join("");
}

function renderTargetBar() {
  const d = DATASET_INFO.targetDistribution;
  const bar = document.getElementById("targetBar");
  bar.innerHTML = `
    <span style="width:${d.H * 100}%;background:var(--green)">${Math.round(d.H * 100)}% H</span>
    <span style="width:${d.D * 100}%;background:var(--gold)">${Math.round(d.D * 100)}% D</span>
    <span style="width:${d.A * 100}%;background:var(--sky)">${Math.round(d.A * 100)}% A</span>
  `;
  document.getElementById("targetNote").textContent =
    `${DATASET_INFO.totalMatches.toLocaleString("es-ES")} partidos, temporadas ${DATASET_INFO.seasons}. Ratio de desbalance mayoritaria/minoritaria: ${DATASET_INFO.imbalanceRatio}.`;
}

// ============================================================
// HISTÓRICO — resultados reales del dataset
// ============================================================
const historicoSelect = document.getElementById("historico-team");
LALIGA_TEAMS.forEach((t) => historicoSelect.add(new Option(t, t)));
historicoSelect.addEventListener("change", () => {
  const list = document.getElementById("historicoList");
  const matches = HISTORICAL_RESULTS[historicoSelect.value] || [];
  if (!matches.length) { list.innerHTML = ""; return; }
  list.innerHTML = matches.map((m) => `
    <li class="history__item">
      <div><strong>${m.home}</strong> ${m.home_goals} - ${m.away_goals} <strong>${m.away}</strong><br><small>${formatDate(m.date)} · Temporada ${m.season}</small></div>
    </li>
  `).join("");
});

// ============================================================
// LOGIN SIMULADO + ADMIN
// ============================================================
document.getElementById("loginForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const user = document.getElementById("login-user").value.trim();
  const pass = document.getElementById("login-pass").value.trim();
  if (!user || !pass) return; // simulado: solo exige que no estén vacíos
  isLoggedIn = true;
  renderAdmin();
  showSection("admin");
});
document.getElementById("logoutBtn").addEventListener("click", () => {
  isLoggedIn = false;
  document.getElementById("login-user").value = "";
  document.getElementById("login-pass").value = "";
  showSection("login");
});

function renderAdmin() {
  document.getElementById("datasetGrid").innerHTML = `
    <div><span class="objective-label">Partidos totales</span><span class="objective-value">${DATASET_INFO.totalMatches.toLocaleString("es-ES")}</span></div>
    <div><span class="objective-label">Temporadas</span><span class="objective-value">${DATASET_INFO.seasons}</span></div>
    <div><span class="objective-label">Métrica</span><span class="objective-value">${DATASET_INFO.metric}</span></div>
    <div><span class="objective-label">Límite de gap</span><span class="objective-value">&lt; ${DATASET_INFO.gapLimit}</span></div>
  `;
  renderCandidatesTable("adminCandidatesTable", true);

  document.getElementById("championHyperparams").textContent =
    JSON.stringify(CHAMPION.hyperparameters, null, 2) +
    `\n\nfinal_fit_rows: ${CHAMPION.finalFitRows}\ntest_rows: ${CHAMPION.testRows}\nselection_rule: "${CHAMPION.selectionRule}"`;

  document.getElementById("trainingTimeline").innerHTML = TRAINING_LOG.map((t) => `
    <li>
      <span class="t-date">${t.date}</span>
      <div>${t.event}<span class="t-actor">${t.actor}</span></div>
    </li>
  `).join("");
}

// ============================================================
// INIT
// ============================================================
renderMarquee();
renderCandidatesTable("candidatesTable", false);
renderChampionGrid();
renderTargetBar();
showSection("inicio");
