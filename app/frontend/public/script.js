// `value` debe coincidir exactamente con el nombre de equipo tal como aparece
// en el dataset histórico (data/processed/laliga_matches_clean.csv), que es
// contra lo que el backend valida el catálogo de equipos conocidos.
// `label` es el nombre real/oficial que ve el usuario. Lista = los 20 equipos
// que disputaron LaLiga en la temporada 2025-26 (la más reciente en los
// datos); equipos descendidos en temporadas previas (Las Palmas, Granada,
// Cádiz, Almería...) ya no aparecen aquí para no ofrecer partidos irreales.
const TEAMS = [
  { label: "Real Madrid", value: "Real Madrid" },
  { label: "FC Barcelona", value: "Barcelona" },
  { label: "Atlético de Madrid", value: "Ath Madrid" },
  { label: "Sevilla FC", value: "Sevilla" },
  { label: "Real Betis", value: "Betis" },
  { label: "Real Sociedad", value: "Sociedad" },
  { label: "Athletic Club", value: "Ath Bilbao" },
  { label: "Villarreal CF", value: "Villarreal" },
  { label: "Valencia CF", value: "Valencia" },
  { label: "RC Celta", value: "Celta" },
  { label: "Getafe CF", value: "Getafe" },
  { label: "CA Osasuna", value: "Osasuna" },
  { label: "Rayo Vallecano", value: "Vallecano" },
  { label: "RCD Mallorca", value: "Mallorca" },
  { label: "Deportivo Alavés", value: "Alaves" },
  { label: "Girona FC", value: "Girona" },
  { label: "RCD Espanyol", value: "Espanol" },
  { label: "Elche CF", value: "Elche" },
  { label: "Levante UD", value: "Levante" },
  { label: "Real Oviedo", value: "Oviedo" },
];

const API_ORIGIN =
  window.location.port === "5173"
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : window.location.origin;

// Pesos calculados de verdad con permutation importance sobre el Champion
// (scripts/run_permutation_importance.py, medido en validation, nunca en
// train ni test). Cada peso agrupa las features de MODEL_FEATURES afines
// (ver src/data/historical_features.py) y está normalizado para sumar 1.
// Fuente completa por feature individual:
// reports/experiments/champion_permutation_importance.json
// El modelo NO usa lesiones, clima ni enfrentamientos directos: solo
// estadísticas históricas de resultados/goles/Elo/descanso/identidad de
// equipo, calculadas aparte para cada equipo.
const FACTORS = [
  { label: "Fortaleza histórica (Elo)", weight: 0.3458, icon: "📈" },
  { label: "Forma reciente (últimos 5 partidos)", weight: 0.2191, icon: "🔥" },
  { label: "Partidos disputados en la temporada", weight: 0.1385, icon: "📅" },
  { label: "Identidad del equipo", weight: 0.1060, icon: "🏟️" },
  { label: "Ataque reciente (goles a favor)", weight: 0.0974, icon: "⚽" },
  { label: "Defensa reciente (goles en contra)", weight: 0.0687, icon: "🛡️" },
  { label: "Descanso entre partidos", weight: 0.0245, icon: "⏱️" },
];

const TOKEN_KEY = "laliga_predictor_token";
const EMAIL_KEY = "laliga_predictor_email";

// --- Elementos ---
const authSection = document.getElementById("auth-section");
const appContent = document.getElementById("app-content");
const userBar = document.getElementById("user-bar");
const userEmailEl = document.getElementById("user-email");
const logoutBtn = document.getElementById("logout-btn");

const tabLogin = document.getElementById("tab-login");
const tabRegister = document.getElementById("tab-register");
const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const loginError = document.getElementById("login-error");
const registerError = document.getElementById("register-error");

const homeSelect = document.getElementById("home-team");
const awaySelect = document.getElementById("away-team");
const dateInput = document.getElementById("match-date");
const form = document.getElementById("predict-form");
const resultSection = document.getElementById("result-section");
const historyList = document.getElementById("history-list");
const historyEmpty = document.getElementById("history-empty");
const refreshHistoryBtn = document.getElementById("refresh-history");

// --- Sesión ---
function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setSession(token, email) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(EMAIL_KEY, email);
}

function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(EMAIL_KEY);
}

function showApp(email) {
  authSection.hidden = true;
  appContent.hidden = false;
  userBar.hidden = false;
  userEmailEl.textContent = email;
}

function showAuth() {
  clearSession();
  authSection.hidden = false;
  appContent.hidden = true;
  userBar.hidden = true;
  resultSection.hidden = true;
}

// --- Llamadas a la API ---
async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${API_ORIGIN}${path}`, { ...options, headers });
  if (response.status === 401 && path !== "/api/v1/auth/login" && path !== "/api/v1/auth/register") {
    showAuth();
    throw new Error("Tu sesión expiró. Inicia sesión de nuevo.");
  }
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.message || "Ocurrió un error inesperado.");
  return payload;
}

async function predict(home, away, date) {
  const payload = await apiFetch("/api/v1/predictions", {
    method: "POST",
    body: JSON.stringify({ home_team: home, away_team: away, match_date: date }),
  });
  const labels = { H: "Victoria local", D: "Empate", A: "Victoria visitante" };
  const homeProb = payload.probabilities.H;
  const drawProb = payload.probabilities.D;
  const awayProb = payload.probabilities.A;
  return { home: Math.round(homeProb * 100), draw: Math.round(drawProb * 100), away: Math.round(awayProb * 100), outcome: labels[payload.prediction], confidence: Math.round(Math.max(homeProb, drawProb, awayProb) * 100) };
}

// --- UI: selects, gauge, factores ---
function populateSelects() {
  TEAMS.forEach((team) => {
    homeSelect.add(new Option(team.label, team.value));
    awaySelect.add(new Option(team.label, team.value));
  });
}

function setGauge(value) {
  const arc = document.getElementById("gauge-arc");
  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (value / 100) * circumference;
  arc.style.strokeDashoffset = offset;
}

function renderFactors() {
  const list = document.getElementById("factors-list");
  list.innerHTML = "";
  FACTORS.forEach((factor) => {
    const li = document.createElement("li");
    li.className = "factor";
    li.innerHTML = `
      <span class="factor__icon">${factor.icon}</span>
      <span class="factor__label">${factor.label}</span>
      <div class="factor__weight"><span style="width: 0%"></span></div>
    `;
    list.appendChild(li);
    setTimeout(() => {
      li.querySelector(".factor__weight span").style.width = `${factor.weight * 100}%`;
    }, 50);
  });
}

function formatDate(dateStr) {
  const [y, m, d] = dateStr.split("-");
  return `${d}/${m}/${y}`;
}

// --- Historial (persistido en el backend, por usuario) ---
function renderHistory(items) {
  historyList.innerHTML = "";
  if (!items.length) {
    historyEmpty.hidden = false;
    return;
  }
  historyEmpty.hidden = true;
  const labels = { H: "Victoria local", D: "Empate", A: "Victoria visitante" };
  items.forEach((item) => {
    const confidence = Math.round(Math.max(item.probabilities.H, item.probabilities.D, item.probabilities.A) * 100);
    const li = document.createElement("li");
    li.className = "history__item";
    li.innerHTML = `
      <div>
        <strong>${item.home_team}</strong> vs <strong>${item.away_team}</strong>
        <br><small>${formatDate(item.match_date)} · ${labels[item.prediction]}</small>
      </div>
      <span class="bar__value">${confidence}%</span>
    `;
    historyList.appendChild(li);
  });
}

async function loadHistory() {
  try {
    const payload = await apiFetch("/api/v1/history");
    renderHistory(payload.items);
  } catch (error) {
    // Sesión ya manejada por apiFetch (redirige a login si expiró).
  }
}

function showResult(home, away, result) {
  document.getElementById("result-home").textContent = home;
  document.getElementById("result-away").textContent = away;
  document.getElementById("result-prediction").textContent = result.outcome;

  document.getElementById("prob-home").textContent = `${result.home}%`;
  document.getElementById("prob-draw").textContent = `${result.draw}%`;
  document.getElementById("prob-away").textContent = `${result.away}%`;

  document.getElementById("confidence-value").textContent = `${result.confidence}%`;
  setGauge(result.confidence);

  document.getElementById("bar-home").style.width = `${result.home}%`;
  document.getElementById("bar-draw").style.width = `${result.draw}%`;
  document.getElementById("bar-away").style.width = `${result.away}%`;

  renderFactors();
  resultSection.hidden = false;
  resultSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// --- Auth: tabs, login, registro, logout ---
function switchTab(target) {
  const showLogin = target === "login";
  tabLogin.classList.toggle("auth__tab--active", showLogin);
  tabRegister.classList.toggle("auth__tab--active", !showLogin);
  tabLogin.setAttribute("aria-selected", String(showLogin));
  tabRegister.setAttribute("aria-selected", String(!showLogin));
  loginForm.hidden = !showLogin;
  registerForm.hidden = showLogin;
  loginError.hidden = true;
  registerError.hidden = true;
}

tabLogin.addEventListener("click", () => switchTab("login"));
tabRegister.addEventListener("click", () => switchTab("register"));

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  loginError.hidden = true;
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;
  try {
    const payload = await apiFetch("/api/v1/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
    setSession(payload.access_token, payload.user.email);
    showApp(payload.user.email);
    loadHistory();
  } catch (error) {
    loginError.textContent = error.message;
    loginError.hidden = false;
  }
});

registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  registerError.hidden = true;
  const email = document.getElementById("register-email").value.trim();
  const password = document.getElementById("register-password").value;
  try {
    const payload = await apiFetch("/api/v1/auth/register", { method: "POST", body: JSON.stringify({ email, password }) });
    setSession(payload.access_token, payload.user.email);
    showApp(payload.user.email);
    loadHistory();
  } catch (error) {
    registerError.textContent = error.message;
    registerError.hidden = false;
  }
});

logoutBtn.addEventListener("click", () => {
  showAuth();
  switchTab("login");
  loginForm.reset();
});

// --- Predicción ---
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const home = homeSelect.value;
  const away = awaySelect.value;
  const homeLabel = homeSelect.selectedOptions[0]?.text ?? home;
  const awayLabel = awaySelect.selectedOptions[0]?.text ?? away;
  const date = dateInput.value;

  if (!home || !away || !date) return;
  if (home === away) {
    alert("El equipo local y visitante deben ser diferentes.");
    return;
  }

  try {
    const result = await predict(home, away, date);
    showResult(homeLabel, awayLabel, result);
    loadHistory();
  } catch (error) {
    alert(error.message);
  }
});

refreshHistoryBtn.addEventListener("click", loadHistory);

homeSelect.addEventListener("change", () => {
  if (homeSelect.value === awaySelect.value) awaySelect.value = "";
});

awaySelect.addEventListener("change", () => {
  if (awaySelect.value === homeSelect.value) homeSelect.value = "";
});

// --- Arranque ---
dateInput.valueAsDate = new Date();
populateSelects();

const storedToken = getToken();
const storedEmail = localStorage.getItem(EMAIL_KEY);
if (storedToken && storedEmail) {
  showApp(storedEmail);
  loadHistory();
} else {
  showAuth();
}
