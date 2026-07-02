const form = document.getElementById("researchForm");
const questionInput = document.getElementById("questionInput");
const wikiToggle = document.getElementById("wikiToggle");
const submitButton = document.getElementById("submitButton");
const progressBar = document.getElementById("progressBar");
const logPanel = document.getElementById("logPanel");
const runMeta = document.getElementById("runMeta");
const answerPanel = document.getElementById("answerPanel");
const sourcesPanel = document.getElementById("sourcesPanel");
const historyPanel = document.getElementById("historyPanel");

const agentDescriptions = {
  CoordinatorAgent: "Clarified the question and mapped the workflow.",
  SearchAgent: "Collected external sources for the question.",
  ReaderAgent: "Fetched the top links and summarized them.",
  WriterAgent: "Synthesized the final answer and source list."
};

let activeSocket = null;

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function setRunState(state) {
  runMeta.textContent = state;
}

function resetAgentTiles() {
  document.querySelectorAll(".agent-tile").forEach((tile) => {
    tile.classList.remove("active", "complete");
    tile.querySelector("strong").textContent = "Waiting";
  });
}

function updateAgentTile(agent, status, message) {
  const tile = document.querySelector(`.agent-tile[data-agent="${agent}"]`);
  if (!tile) {
    return;
  }

  tile.classList.remove("active", "complete");
  if (status === "completed" || status.endsWith("_complete")) {
    tile.classList.add("complete");
    tile.querySelector("strong").textContent = "Complete";
  } else if (status === "error") {
    tile.querySelector("strong").textContent = "Error";
  } else {
    tile.classList.add("active");
    tile.querySelector("strong").textContent = "Working";
  }

  tile.querySelector("p").textContent = message || agentDescriptions[agent] || "Working...";
}

function appendLog(update) {
  if (logPanel.querySelector(".empty-note")) {
    logPanel.innerHTML = "";
  }

  const item = document.createElement("article");
  item.className = "log-item";
  item.innerHTML = `
    <strong>${escapeHtml(update.agent || "System")}</strong>
    <p>${escapeHtml(update.message || "Update received")}</p>
    <small>${escapeHtml(update.timestamp || new Date().toISOString())}</small>
  `;
  logPanel.prepend(item);
}

function renderAnswer(text) {
  if (!text) {
    answerPanel.innerHTML = '<p class="empty-note">No answer returned yet.</p>';
    return;
  }

  const blocks = text.split(/\n\s*\n/).map((block) => block.trim()).filter(Boolean);
  const html = blocks.map((block) => {
    if (block.startsWith("- ") || block.startsWith("* ")) {
      const items = block.split("\n").map((line) => line.replace(/^[-*]\s*/, "").trim()).filter(Boolean);
      return `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
    }

    return `<p>${escapeHtml(block).replaceAll("\n", "<br>")}</p>`;
  }).join("");

  answerPanel.innerHTML = html;
}

function renderSources(sources) {
  if (!sources || !sources.length) {
    sourcesPanel.innerHTML = "";
    return;
  }

  sourcesPanel.innerHTML = sources.map((source) => `
    <article class="source-item">
      <strong>${escapeHtml(source.title || "Source")}</strong>
      <a href="${escapeHtml(source.url || "#")}" target="_blank" rel="noreferrer">${escapeHtml(source.url || "")}</a>
    </article>
  `).join("");
}

async function loadHistory() {
  try {
    const response = await fetch("/research/history?limit=6&offset=0");
    const history = await response.json();

    if (!Array.isArray(history) || history.length === 0) {
      historyPanel.innerHTML = '<p class="empty-note">No saved research yet. Your first run will show up here.</p>';
      return;
    }

    historyPanel.innerHTML = history.map((item) => `
      <article class="history-item">
        <strong>${escapeHtml(item.query)}</strong>
        <p>${escapeHtml((item.final_answer || "").slice(0, 180))}${item.final_answer && item.final_answer.length > 180 ? "..." : ""}</p>
        <div class="history-meta">Status: ${escapeHtml(item.status)} • Cost: $${Number(item.cost || 0).toFixed(4)} • Duration: ${Number(item.duration_seconds || 0).toFixed(1)}s</div>
        <button type="button" data-id="${escapeHtml(item.id)}">Open result</button>
      </article>
    `).join("");

    historyPanel.querySelectorAll("button[data-id]").forEach((button) => {
      button.addEventListener("click", async () => {
        const result = await fetch(`/research/${button.dataset.id}`).then((res) => res.json());
        renderAnswer(result.final_answer);
        renderSources(result.sources);
        setRunState("Showing saved result");
      });
    });
  } catch (error) {
    historyPanel.innerHTML = '<p class="empty-note">Could not load research history.</p>';
  }
}

function startSocket(researchId) {
  if (activeSocket) {
    activeSocket.close();
  }

  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  activeSocket = new WebSocket(`${protocol}://${window.location.host}/ws/${researchId}`);

  activeSocket.onopen = () => {
    activeSocket.send("ready");
    setRunState("Running");
  };

  activeSocket.onmessage = async (event) => {
    const update = JSON.parse(event.data);
    progressBar.style.width = `${Math.round((update.progress || 0) * 100)}%`;
    updateAgentTile(update.agent, update.status || "", update.message || "");
    appendLog(update);

    if (update.status === "completed") {
      setRunState("Completed");
      submitButton.disabled = false;
      submitButton.textContent = "Start research";

      const result = await fetch(`/research/${researchId}`).then((res) => res.json());
      renderAnswer(result.final_answer);
      renderSources(result.sources);
      loadHistory();
    }

    if (update.status === "error") {
      setRunState("Error");
      submitButton.disabled = false;
      submitButton.textContent = "Start research";
      answerPanel.innerHTML = `<p class="empty-note">${escapeHtml(update.message || "Something went wrong during research.")}</p>`;
    }
  };

  activeSocket.onerror = () => {
    setRunState("Connection issue");
  };
}

function resetRunUi() {
  progressBar.style.width = "0%";
  logPanel.innerHTML = '<p class="empty-note">Connecting to the workflow...</p>';
  answerPanel.innerHTML = '<p class="empty-note">The final answer will appear here when the writer agent finishes.</p>';
  sourcesPanel.innerHTML = "";
  resetAgentTiles();
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) {
    questionInput.focus();
    return;
  }

  submitButton.disabled = true;
  submitButton.textContent = "Researching...";
  setRunState("Starting");
  resetRunUi();

  const response = await fetch("/research", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      use_wikipedia: wikiToggle.checked
    })
  });

  const payload = await response.json();
  startSocket(payload.id);
});

document.getElementById("samplePrompts").querySelectorAll("button").forEach((button) => {
  button.addEventListener("click", () => {
    questionInput.value = button.dataset.prompt;
    questionInput.focus();
  });
});

loadHistory();
