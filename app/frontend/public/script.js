// `value` debe coincidir exactamente con el nombre de equipo tal como aparece
// en el dataset histórico (data/processed/laliga_matches_clean.csv), que es
// contra lo que el backend valida el catálogo de equipos conocidos.
// `label` es solo el nombre comercial que ve el usuario.
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
  { label: "UD Las Palmas", value: "Las Palmas" },
  { label: "Deportivo Alavés", value: "Alaves" },
  { label: "Granada CF", value: "Granada" },
  { label: "Cádiz CF", value: "Cadiz" },
  { label: "UD Almería", value: "Almeria" },
  { label: "Girona FC", value: "Girona" },
];

const API_ORIGIN =
  window.location.port === "5173"
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : window.location.origin;
const API_URL = `${API_ORIGIN}/api/v1/predictions`;

const FACTORS = [
  { label: "Forma reciente local", weight: 0.22, icon: "🔥" },
  { label: "Rendimiento como visitante", weight: 0.18, icon: "🚌" },
  { label: "Historial de enfrentamientos", weight: 0.16, icon: "⚔️" },
  { label: "Lesiones y sanciones", weight: 0.14, icon: "🚑" },
  { label: "Motivación y posición", weight: 0.13, icon: "📊" },
  { label: "Descanso entre partidos", weight: 0.10, icon: "⏱️" },
  { label: "Clima y condiciones", weight: 0.07, icon: "🌤️" },
];

const homeSelect = document.getElementById("home-team");
const awaySelect = document.getElementById("away-team");
const dateInput = document.getElementById("match-date");
const form = document.getElementById("predict-form");
const resultSection = document.getElementById("result-section");
const historyList = document.getElementById("history-list");
const historyEmpty = document.getElementById("history-empty");
const clearHistoryBtn = document.getElementById("clear-history");

function populateSelects() {
  TEAMS.forEach((team) => {
    homeSelect.add(new Option(team.label, team.value));
    awaySelect.add(new Option(team.label, team.value));
  });
}

async function predict(home, away, date) {
  const response = await fetch(API_URL, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ home_team: home, away_team: away, match_date: date }),
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.message || "No se pudo obtener la predicción.");
  const labels = { H: "Victoria local", D: "Empate", A: "Victoria visitante" };
  const homeProb = payload.probabilities.H;
  const drawProb = payload.probabilities.D;
  const awayProb = payload.probabilities.A;
  return { home: Math.round(homeProb * 100), draw: Math.round(drawProb * 100), away: Math.round(awayProb * 100), outcome: labels[payload.prediction], confidence: Math.round(Math.max(homeProb, drawProb, awayProb) * 100) };
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

function addHistory(home, away, date, result) {
  const li = document.createElement("li");
  li.className = "history__item";
  li.innerHTML = `
    <div>
      <strong>${home}</strong> vs <strong>${away}</strong>
      <br><small>${formatDate(date)} · ${result.outcome}</small>
    </div>
    <span class="bar__value">${result.confidence}%</span>
  `;
  historyList.prepend(li);
  historyEmpty.hidden = true;
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
    addHistory(homeLabel, awayLabel, date, result);
  } catch (error) {
    alert(error.message);
  }
});

clearHistoryBtn.addEventListener("click", () => {
  historyList.innerHTML = "";
  historyEmpty.hidden = false;
});

homeSelect.addEventListener("change", () => {
  if (homeSelect.value === awaySelect.value) awaySelect.value = "";
});

awaySelect.addEventListener("change", () => {
  if (awaySelect.value === homeSelect.value) homeSelect.value = "";
});

// Default date to today
dateInput.valueAsDate = new Date();

populateSelects();
