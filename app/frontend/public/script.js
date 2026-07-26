const TEAMS = [
  "Real Madrid",
  "FC Barcelona",
  "Atlético de Madrid",
  "Sevilla FC",
  "Real Betis",
  "Real Sociedad",
  "Athletic Club",
  "Villarreal CF",
  "Valencia CF",
  "RC Celta",
  "Getafe CF",
  "CA Osasuna",
  "Rayo Vallecano",
  "RCD Mallorca",
  "UD Las Palmas",
  "Deportivo Alavés",
  "Granada CF",
  "Cádiz CF",
  "UD Almería",
  "Girona FC",
];

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
    homeSelect.add(new Option(team, team));
    awaySelect.add(new Option(team, team));
  });
}

function seededRandom(seed) {
  let s = seed % 2147483647;
  if (s <= 0) s += 2147483646;
  return function () {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
}

function hashString(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

function predict(home, away, date) {
  const seed = hashString(`${home}|${away}|${date}`);
  const rng = seededRandom(seed + 12345);

  const homeIndex = TEAMS.indexOf(home);
  const awayIndex = TEAMS.indexOf(away);
  const baseHome = 0.45 + (TEAMS.length - homeIndex) * 0.005;
  const baseAway = 0.30 + (TEAMS.length - awayIndex) * 0.005;

  let homeProb = baseHome + rng() * 0.18;
  let awayProb = baseAway + rng() * 0.18;
  let drawProb = 1 - homeProb - awayProb;

  if (drawProb < 0.05) {
    drawProb = 0.05;
    const scale = 1 - drawProb;
    homeProb = (homeProb / (homeProb + awayProb)) * scale;
    awayProb = scale - homeProb;
  }

  const total = homeProb + drawProb + awayProb;
  homeProb /= total;
  drawProb /= total;
  awayProb /= total;

  let outcome;
  if (homeProb > awayProb && homeProb > drawProb) outcome = "Victoria local";
  else if (awayProb > homeProb && awayProb > drawProb) outcome = "Victoria visitante";
  else outcome = "Empate";

  const confidence = Math.round(Math.max(homeProb, drawProb, awayProb) * 100);

  return {
    home: Math.round(homeProb * 100),
    draw: Math.round(drawProb * 100),
    away: Math.round(awayProb * 100),
    outcome,
    confidence,
  };
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

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const home = homeSelect.value;
  const away = awaySelect.value;
  const date = dateInput.value;

  if (!home || !away || !date) return;
  if (home === away) {
    alert("El equipo local y visitante deben ser diferentes.");
    return;
  }

  const result = predict(home, away, date);
  showResult(home, away, result);
  addHistory(home, away, date, result);
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
