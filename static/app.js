const COLORS = ["#e2312f", "#1f6fe0", "#22a456", "#f2c418", "#8e44ad", "#e67e22"];
const SEAT_RADIUS = 215;
const NODE_SIZE = 38;
const svg = document.getElementById("table");
const toast = document.getElementById("toast");
let state = null;

function colorFor(name) {
  let hash = 0;
  for (const char of name) hash = (hash * 31 + char.charCodeAt(0)) >>> 0;
  return COLORS[hash % COLORS.length];
}

function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);
}

function polar(radius, degrees) {
  const rad = (degrees * Math.PI) / 180;
  return [radius * Math.cos(rad), radius * Math.sin(rad)];
}

function arcPath(radius, fromDeg, toDeg, clockwise) {
  const [x1, y1] = polar(radius, fromDeg);
  const [x2, y2] = polar(radius, toDeg);
  let span = clockwise ? toDeg - fromDeg : fromDeg - toDeg;
  span = ((span % 360) + 360) % 360;
  const largeArc = span > 180 ? 1 : 0;
  return `M ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} ${clockwise ? 1 : 0} ${x2} ${y2}`;
}

function showToast(message, isError = false) {
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.add("show");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.classList.remove("show"), 2600);
}

async function api(action, body = {}) {
  const data = await backend.request(action, body);
  if (data.error) showToast(data.error, true);
  render(data);
  return data;
}

function renderTable() {
  const players = state.players;
  const count = players.length;
  const step = 360 / Math.max(count, 1);
  const angleOf = (index) => -90 + index * step;
  const gap = Math.min(step / 2 - 2, (NODE_SIZE + 12) / SEAT_RADIUS * 57.3);

  let markup = `
    <defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M0,0 L10,5 L0,10 z" fill="#ffffffcc"/>
      </marker>
      <marker id="arrow-dim" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M0,0 L10,5 L0,10 z" fill="#ffffff66"/>
      </marker>
      <marker id="arrow-accent" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
        <path d="M0,0 L10,5 L0,10 z" fill="#f2c418"/>
      </marker>
    </defs>`;

  if (count === 0) {
    markup += `<text class="center-text" x="0" y="0">La mesa está vacía. ¡Agrega jugadores!</text>`;
    svg.innerHTML = markup;
    return;
  }

  // links: next (outer, solid) and prev (inner, dashed)
  if (count > 1) {
    players.forEach((_, index) => {
      const from = angleOf(index);
      const to = angleOf(index + 1);
      markup += `<path class="link-next" marker-end="url(#arrow)" d="${arcPath(SEAT_RADIUS + 52, from + gap, to - gap, true)}"/>`;
      markup += `<path class="link-prev" marker-end="url(#arrow-dim)" d="${arcPath(SEAT_RADIUS - 52, to - gap, from + gap, false)}"/>`;
    });
  }

  // direction arrow in the middle of the table
  const clockwise = state.clockwise;
  markup += `<path class="center-arrow" marker-end="url(#arrow-accent)"
      d="${clockwise ? arcPath(70, -150, 120, true) : arcPath(70, -30, 60, false)}"/>
    <text class="center-text" x="0" y="-6">${clockwise ? "Sentido horario" : "Sentido antihorario"}</text>
    <text class="center-text" x="0" y="14">sigue a <tspan font-weight="700">${clockwise ? "next →" : "← prev"}</tspan></text>`;

  // seats (nodes)
  players.forEach((player, index) => {
    const [x, y] = polar(SEAT_RADIUS, angleOf(index));
    const isCurrent = player.name === state.current;
    const labels = [];
    if (player.name === state.head) labels.push("PRIMERO");
    if (player.name === state.tail) labels.push("ÚLTIMO");
    markup += `
      <g class="seat ${isCurrent ? "current" : ""}" data-name="${escapeHtml(player.name)}" transform="translate(${x} ${y})">
        <title>Clic para sacar a ${escapeHtml(player.name)} de la mesa</title>
        <circle class="avatar" r="${NODE_SIZE}" fill="${colorFor(player.name)}"/>
        <text class="initial" y="-6">${escapeHtml(player.name[0].toUpperCase())}</text>
        <text class="count" y="16">🂠 ${player.cards}</text>
        <text class="name" y="${NODE_SIZE + 16}">${escapeHtml(player.name)}</text>
        ${labels.length ? `<text class="label" y="${-NODE_SIZE - 10}">${labels.join(" · ")}</text>` : ""}
      </g>`;
    if (isCurrent) {
      const [px, py] = polar(SEAT_RADIUS - NODE_SIZE - 30, angleOf(index));
      markup += `<circle class="pointer" cx="${px}" cy="${py}" r="7"/>`;
    }
  });

  svg.innerHTML = markup;
  svg.querySelectorAll(".seat").forEach((seat) => {
    seat.addEventListener("click", () => {
      const name = seat.dataset.name;
      if (confirm(`¿Sacar a ${name} de la mesa? Sus vecinos quedarán enlazados entre sí.`)) {
        api("eliminate", { name });
      }
    });
  });
}

function renderPanel() {
  const { players, current, clockwise, winners, log } = state;
  document.getElementById("current-name").textContent = current ?? "—";
  document.getElementById("direction").textContent = clockwise ? "↻ Horario" : "↺ Antihorario";

  const names = players.map((p) => escapeHtml(p.name));
  const loop = (list) => (list.length ? `${list.join(" → ")} → <i>${list[0]}…</i>` : "vacía");
  const reversed = names.length ? [names[0], ...names.slice(1).reverse()] : [];
  document.getElementById("trav-next").innerHTML = loop(names);
  document.getElementById("trav-prev").innerHTML = loop(reversed).replaceAll("→", "←");

  document.getElementById("pointers").innerHTML = players
    .map((p) => `<tr><td>${escapeHtml(p.prev)}</td><td><b>${escapeHtml(p.name)}</b></td><td>${escapeHtml(p.next)}</td><td>${p.cards}</td></tr>`)
    .join("");

  const select = document.getElementById("in-after");
  const chosen = select.value;
  const rawNames = players.map((p) => p.name);
  select.innerHTML = `<option value="">Al final (antes del primero)</option>` +
    rawNames.map((n) => `<option value="${escapeHtml(n)}">Después de ${escapeHtml(n)}</option>`).join("");
  if (rawNames.includes(chosen)) select.value = chosen;

  document.getElementById("winners").innerHTML = winners.length
    ? winners.map((w) => `<li>${escapeHtml(w)}</li>`).join("")
    : `<li class="muted">Nadie ha ganado todavía</li>`;
  document.getElementById("log").innerHTML = log.map((line) => `<li>${escapeHtml(line)}</li>`).join("");
}

function render(newState) {
  state = newState;
  renderTable();
  renderPanel();
}

document.querySelectorAll("[data-action]").forEach((button) => {
  button.addEventListener("click", () => api(button.dataset.action));
});

document.getElementById("btn-reset").addEventListener("click", () => {
  if (confirm("¿Vaciar la mesa por completo?")) api("reset");
});

document.getElementById("form-join").addEventListener("submit", async (event) => {
  event.preventDefault();
  const name = document.getElementById("in-name").value;
  const cards = document.getElementById("in-cards").value;
  const after = document.getElementById("in-after").value;
  const data = await api(after ? "join_after" : "join", { name, cards, after });
  if (!data.error) {
    document.getElementById("in-name").value = "";
    showToast(`${name} se sentó en la mesa`);
  }
});

backend.state().then(render);
