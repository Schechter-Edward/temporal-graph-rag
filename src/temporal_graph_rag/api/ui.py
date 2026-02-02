UI_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Temporal Graph RAG</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Fraunces:wght@400;600;700&family=Space+Grotesk:wght@400;500;600&display=swap"
      rel="stylesheet"
    />
    <style>
      :root {
        --bg-0: #0b1a2b;
        --bg-1: #0f2a3f;
        --bg-2: #122f3a;
        --ink-0: #f5f1e8;
        --ink-1: #d7e1ec;
        --ink-2: #9bb1c7;
        --accent: #f29f3f;
        --accent-2: #3fd0b4;
        --card: rgba(16, 34, 52, 0.9);
        --border: rgba(255, 255, 255, 0.08);
      }

      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        min-height: 100vh;
        color: var(--ink-0);
        font-family: "Space Grotesk", sans-serif;
        background:
          radial-gradient(circle at 10% 10%, rgba(242, 159, 63, 0.25), transparent 50%),
          radial-gradient(circle at 90% 20%, rgba(63, 208, 180, 0.18), transparent 55%),
          linear-gradient(160deg, var(--bg-0), var(--bg-1) 50%, var(--bg-2));
      }

      .wrap {
        max-width: 1100px;
        margin: 0 auto;
        padding: 48px 24px 80px;
      }

      header {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 24px;
        margin-bottom: 32px;
        align-items: center;
      }

      h1 {
        font-family: "Fraunces", serif;
        font-size: clamp(2.4rem, 4vw, 3.6rem);
        margin: 0 0 12px;
      }

      .lede {
        color: var(--ink-1);
        font-size: 1.05rem;
        line-height: 1.6;
        margin: 0 0 16px;
      }

      .pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
      }

      .pill {
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid var(--border);
        font-size: 0.85rem;
        color: var(--ink-1);
      }

      .panel {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
        position: relative;
        overflow: hidden;
      }

      .panel ul {
        margin: 12px 0 0 18px;
        color: var(--ink-1);
        line-height: 1.6;
      }

      .panel:before {
        content: "";
        position: absolute;
        inset: -80px auto auto -80px;
        width: 180px;
        height: 180px;
        background: rgba(242, 159, 63, 0.14);
        filter: blur(8px);
        border-radius: 50%;
      }

      .grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 18px;
        margin-top: 18px;
      }

      label {
        display: block;
        font-size: 0.85rem;
        color: var(--ink-2);
        margin-bottom: 6px;
      }

      textarea,
      input {
        width: 100%;
        border-radius: 12px;
        border: 1px solid var(--border);
        background: rgba(9, 18, 28, 0.6);
        color: var(--ink-0);
        padding: 12px 14px;
        font-size: 0.95rem;
        outline: none;
      }

      textarea {
        min-height: 120px;
        resize: vertical;
      }

      button {
        border: none;
        border-radius: 12px;
        background: linear-gradient(135deg, var(--accent), #f7c45a);
        color: #221c13;
        font-weight: 600;
        padding: 12px 18px;
        cursor: pointer;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
      }

      button:hover {
        transform: translateY(-1px);
        box-shadow: 0 12px 30px rgba(242, 159, 63, 0.25);
      }

      .examples {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 14px;
      }

      .example {
        padding: 8px 12px;
        border-radius: 10px;
        background: rgba(63, 208, 180, 0.12);
        color: var(--ink-1);
        border: 1px solid rgba(63, 208, 180, 0.25);
        font-size: 0.85rem;
        cursor: pointer;
      }

      .status {
        margin-top: 12px;
        color: var(--ink-2);
        font-size: 0.85rem;
      }

      .result {
        margin-top: 18px;
        border-radius: 16px;
        border: 1px solid var(--border);
        background: rgba(10, 20, 32, 0.65);
        padding: 16px;
        opacity: 0;
        transform: translateY(8px);
        transition: opacity 0.3s ease, transform 0.3s ease;
      }

      .result.visible {
        opacity: 1;
        transform: translateY(0);
      }

      .result pre {
        white-space: pre-wrap;
        margin: 0;
        font-family: "Space Grotesk", sans-serif;
        color: var(--ink-0);
      }

      .sources {
        margin-top: 12px;
        display: grid;
        gap: 10px;
      }

      .source {
        padding: 10px 12px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid var(--border);
        font-size: 0.85rem;
        color: var(--ink-1);
      }

      .meta {
        margin-top: 10px;
        font-size: 0.8rem;
        color: var(--ink-2);
      }

      @media (max-width: 720px) {
        .wrap {
          padding: 32px 18px 64px;
        }
      }
    </style>
  </head>
  <body>
    <div class="wrap">
      <header>
        <div>
          <h1>Temporal Graph RAG</h1>
          <p class="lede">
            Time-aware retrieval that respects validity windows, detects contradictions,
            and fuses graph, dense, and sparse signals.
          </p>
          <div class="pill-row">
            <span class="pill">Temporal parsing</span>
            <span class="pill">Hybrid retrieval</span>
            <span class="pill">Consistency checks</span>
          </div>
        </div>
        <div class="panel">
          <strong>What recruiters should notice</strong>
          <ul>
            <li>End-to-end system: API, CLI, UI demo</li>
            <li>Deterministic temporal reasoning core</li>
            <li>Benchmarks + tests to validate behavior</li>
          </ul>
        </div>
      </header>

      <section class="panel">
        <form id="query-form">
          <div class="grid">
            <div>
              <label for="query">Temporal query</label>
              <textarea
                id="query"
                placeholder="Who owned Project Orion before the March 2024 reorg?"
              ></textarea>
            </div>
            <div>
              <label for="reference-time">Reference time (optional)</label>
              <input id="reference-time" type="datetime-local" />
              <div class="examples">
                <span class="example" data-query="Who led Project Orion before 2024?">Before 2024</span>
                <span class="example" data-query="What changed during March 2024?">During March 2024</span>
                <span class="example" data-query="Who owned infra after the reorg?">After reorg</span>
              </div>
              <button type="submit">Run temporal query</button>
              <div class="status" id="status">Awaiting query.</div>
            </div>
          </div>
        </form>

        <div class="result" id="result">
          <pre id="answer"></pre>
          <div class="meta" id="context"></div>
          <div class="sources" id="sources"></div>
        </div>
      </section>
    </div>

    <script>
      const form = document.getElementById("query-form");
      const status = document.getElementById("status");
      const result = document.getElementById("result");
      const answer = document.getElementById("answer");
      const sources = document.getElementById("sources");
      const context = document.getElementById("context");
      const queryEl = document.getElementById("query");
      const refEl = document.getElementById("reference-time");

      document.querySelectorAll(".example").forEach((chip) => {
        chip.addEventListener("click", () => {
          queryEl.value = chip.dataset.query;
          queryEl.focus();
        });
      });

      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const query = queryEl.value.trim();
        if (!query) {
          status.textContent = "Add a query to run.";
          return;
        }

        status.textContent = "Querying temporal index...";
        result.classList.remove("visible");
        answer.textContent = "";
        sources.innerHTML = "";
        context.textContent = "";

        const referenceTime = refEl.value ? new Date(refEl.value).toISOString() : null;

        try {
          const res = await fetch("/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query, reference_time: referenceTime }),
          });
          const data = await res.json();
          if (!res.ok) {
            throw new Error(data.detail || "Request failed");
          }

          answer.textContent = data.answer;
          context.textContent = `Operators: ${data.temporal_context.operators.join(", ") || "None"} | Window: ${data.temporal_context.time_start || "n/a"} -> ${data.temporal_context.time_end || "n/a"}`;

          data.sources.forEach((item) => {
            const div = document.createElement("div");
            div.className = "source";
            div.textContent = `${item.content} | ${item.sources.join(",")} | fused=${item.fused_score.toFixed(3)}`;
            sources.appendChild(div);
          });

          status.textContent = "Done.";
          result.classList.add("visible");
        } catch (err) {
          status.textContent = `Error: ${err.message}`;
        }
      });
    </script>
  </body>
</html>
""".strip()
