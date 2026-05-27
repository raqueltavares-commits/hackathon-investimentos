(function () {
  const D = window.PADRAO_SPOT;
  if (!D) return;

  const $ = (sel) => document.querySelector(sel);
  const el = (tag, cls, html) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  };

  // Intros
  document.querySelectorAll("[data-intro]").forEach((p) => {
    const sec = D[p.dataset.intro];
    if (sec && sec.intro) p.textContent = sec.intro;
  });

  // 01 — Eixos da classificação
  const eixos = $("#eixos");
  D.classificacao.eixos.forEach((e, i) => {
    const card = el("div", "eixo");
    card.dataset.i = i + 1;
    card.appendChild(el("h3", null, e.nome));
    const chips = el("div", "chips");
    e.opcoes.forEach((o) => chips.appendChild(el("span", "chip", o)));
    card.appendChild(chips);
    card.appendChild(el("p", "nota", e.nota));
    eixos.appendChild(card);
  });

  // 02 — Matriz de capacidade
  const m = D.matriz;
  const table = $("#matriz");
  const thead = el("thead");
  const trh = el("tr");
  m.colunas.forEach((c) => trh.appendChild(el("th", null, c)));
  thead.appendChild(trh);
  table.appendChild(thead);
  const tbody = el("tbody");
  m.linhas.forEach((row) => {
    const tr = el("tr");
    tr.appendChild(el("td", null, row.item));
    row.v.forEach((v) => {
      let cls = "cell-cond", txt = v;
      if (v === "sim") { cls = "cell-yes"; txt = "●"; }
      else if (v === "não") { cls = "cell-no"; txt = "—"; }
      tr.appendChild(el("td", cls, txt));
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);

  // 03 — Programa por zona
  const prog = $("#programa");
  D.programa.zonas.forEach((z) => {
    const wrap = el("div", "zona");
    wrap.appendChild(el("div", "zona-title", z.nome));
    const cards = el("div", "cards");
    z.itens.forEach((it) => {
      const ob = it.status === "OBRIGATÓRIO";
      const card = el("div", "card");
      const top = el("div", "card-top");
      top.appendChild(el("h4", null, it.nome));
      top.appendChild(el("span", "badge " + (ob ? "ob" : "cond"), it.status));
      card.appendChild(top);
      card.appendChild(el("p", "dim", it.dim));
      card.appendChild(el("p", "regra", it.regra));
      cards.appendChild(card);
    });
    wrap.appendChild(cards);
    prog.appendChild(wrap);
  });

  // 04 — Regras de posicionamento
  const tagCls = {
    "OBRIGATÓRIO": "tag-ob", "PROIBIDO": "tag-no", "EXCEÇÃO": "tag-ex",
    "PERMITIDO": "tag-pe", "REGRA": "tag-re"
  };
  const tagTxt = { "OBRIGATÓRIO": "OBRIG.", "PROIBIDO": "PROIB.", "EXCEÇÃO": "EXCEÇÃO", "PERMITIDO": "OK", "REGRA": "REGRA" };
  const regras = $("#regras");
  D.regras.grupos.forEach((g) => {
    const card = el("div", "regra-card");
    card.appendChild(el("h3", null, g.nome));
    g.itens.forEach((it) => {
      const row = el("div", "regra-item");
      row.appendChild(el("span", "tag " + (tagCls[it.tipo] || "tag-re"), tagTxt[it.tipo] || it.tipo));
      row.appendChild(el("span", null, it.texto));
      card.appendChild(row);
    });
    regras.appendChild(card);
  });

  // 05 — Passo a passo
  $("#passos-nota").textContent = D.passos.nota;
  const passos = $("#passos");
  D.passos.etapas.forEach((s) => {
    const li = el("li", "passo");
    const body = el("div");
    body.appendChild(el("h4", null, s.t));
    body.appendChild(el("p", null, s.d));
    li.appendChild(body);
    passos.appendChild(li);
  });
})();

// ---------- Navegação por abas ----------
(function () {
  const tabs = document.querySelectorAll(".tab[data-tab]");
  const panels = {
    logica: document.getElementById("panel-logica"),
    tipologias: document.getElementById("panel-tipologias"),
    orcamento: document.getElementById("panel-orcamento"),
  };
  tabs.forEach((t) => {
    t.addEventListener("click", () => {
      tabs.forEach((x) => x.classList.remove("is-active"));
      t.classList.add("is-active");
      Object.entries(panels).forEach(([k, p]) => { if (p) p.hidden = k !== t.dataset.tab; });
      window.scrollTo(0, 0);
    });
  });
})();

// ---------- Aba: Tipologias por Spot (vitrine) ----------
(function () {
  const T = window.TIPOLOGIAS;
  if (!T) return;
  const $ = (s) => document.querySelector(s);
  const el = (tag, cls, html) => { const n = document.createElement(tag); if (cls) n.className = cls; if (html != null) n.innerHTML = html; return n; };

  const list = $("#spot-list");
  const empty = $("#spot-empty");
  const input = $("#spot-search");

  function tabelaHTML(spot) {
    const rows = spot.tipologias.map((t) => `
      <tr>
        <td class="t-tip">${t.tipologia}</td>
        <td class="t-unids">${t.unidades.join(", ")}${t.obs ? ` <em>(${t.obs})</em>` : ""}</td>
        <td>${t.terraco}</td>
        <td>${t.tipo}</td>
        <td>${t.quantidade}</td>
        <td>${t.capacidade}</td>
        <td>${t.area_util}</td>
        <td>${t.area_unidade}</td>
      </tr>`).join("");
    const head = T.colunas.map((c) => `<th>${c}</th>`).join("");
    return `<div class="table-wrap"><table class="matriz tabela-tip"><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table></div>`;
  }

  function card(item) {
    const c = el("div", "spot-card");
    const f = item.fontes || { pdf: item.fonte !== "analise", analise: item.fonte === "analise", dwg: false };
    const tag = (label, on, titulo) =>
      `<span class="fonte-tag ${on ? "on" : "off"}" title="${titulo}">${label}</span>`;
    const fontes = `<div class="fontes">
      ${tag("PDF", f.pdf, f.pdf ? "Áreas e números vieram do anteprojeto PDF." : "Sem PDF.")}
      ${tag("Análise", f.analise, f.analise ? "Áreas confirmadas pela planilha de análise (ÁREA UNDS)." : "Sem planilha de análise — áreas só do PDF.")}
      ${tag("DWG", f.dwg, f.dwg ? "Agrupamento conferido no DWG (esquadrias por unidade)." : "Sem DWG — agrupamento por layout a revisar na planta.")}
    </div>`;
    c.innerHTML = `
      <div class="spot-card-top">
        <div>
          <h3>${item.spot} <span class="spot-cod">${item.codigo}</span></h3>
          <p class="spot-meta">${item.total_tipologias} tipologias · ${item.total_unidades} unidades · gerado em ${item.gerado_em}</p>
        </div>
        ${fontes}
      </div>
      <div class="spot-actions">
        <button class="btn btn-primary" data-ver="${item.slug}">Ver tabela</button>
        <a class="btn btn-ghost" href="${item.drive_url}" target="_blank" rel="noopener">Abrir no Drive ↗</a>
      </div>
      <div class="spot-tabela" hidden></div>`;
    c.querySelector("[data-ver]").addEventListener("click", (e) => {
      const box = c.querySelector(".spot-tabela");
      const btn = e.currentTarget;
      if (box.hidden) {
        if (!box.dataset.loaded) { box.innerHTML = tabelaHTML(T.spots[item.slug]); box.dataset.loaded = "1"; }
        box.hidden = false; btn.textContent = "Ocultar tabela";
      } else { box.hidden = true; btn.textContent = "Ver tabela"; }
    });
    return c;
  }

  function semMatch(termo) {
    empty.hidden = false;
    list.innerHTML = "";
    const cmd = `gera a tabela de tipologias do ${termo || "<empreendimento>"}`;
    empty.innerHTML = `
      <p class="empty-title">Nenhuma tabela gerada para "<strong>${termo}</strong>".</p>
      <p class="empty-sub">As tabelas são geradas pelo Claude a partir do anteprojeto. Copie o comando e cole no Claude:</p>
      <div class="cmd-row"><code id="cmd">${cmd}</code><button class="btn btn-primary" id="copy-cmd">Pedir geração ao Claude</button></div>`;
    empty.querySelector("#copy-cmd").addEventListener("click", () => {
      navigator.clipboard && navigator.clipboard.writeText(cmd);
      empty.querySelector("#copy-cmd").textContent = "Comando copiado ✓";
    });
  }

  function render(termo) {
    const q = (termo || "").trim().toLowerCase();
    const itens = T.index.filter((i) =>
      !q || i.spot.toLowerCase().includes(q) || String(i.codigo).toLowerCase().includes(q));
    if (!T.index.length) { semMatch(termo); empty.querySelector(".empty-title").innerHTML = "Nenhuma tabela gerada ainda."; return; }
    if (!itens.length) { semMatch(termo); return; }
    empty.hidden = true;
    list.innerHTML = "";
    itens.forEach((i) => list.appendChild(card(i)));
  }

  input.addEventListener("input", (e) => render(e.target.value));
  render("");

  // Botão "Copiar comando" do bloco "Gerar uma tabela nova"
  const howtoCopy = $("#howto-copy");
  if (howtoCopy) {
    howtoCopy.addEventListener("click", () => {
      const txt = ($("#howto-cmd") || {}).textContent || "";
      navigator.clipboard && navigator.clipboard.writeText(txt);
      howtoCopy.textContent = "Comando copiado ✓";
      setTimeout(() => { howtoCopy.textContent = "Copiar comando"; }, 2000);
    });
  }
})();

// ---------- Aba: Orçamento por Spot (vitrine) ----------
(function () {
  const O = window.ORCAMENTOS;
  if (!O) return;
  const $ = (s) => document.querySelector(s);
  const el = (tag, cls, html) => { const n = document.createElement(tag); if (cls) n.className = cls; if (html != null) n.innerHTML = html; return n; };

  const list = $("#orc-list");
  const empty = $("#orc-empty");
  const input = $("#orc-search");

  const brl = (v) => "R$ " + Number(v).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  function tabelaHTML(spot) {
    const rows = spot.tipologias.map((t) => {
      const link = t.memorial_url && t.memorial_url !== "#"
        ? `<a class="memorial-link" href="${t.memorial_url}" target="_blank" rel="noopener">Memorial ↗</a>`
        : `<span class="memorial-link off">—</span>`;
      return `
      <tr>
        <td class="t-tip">${t.tipologia}</td>
        <td class="t-desc">${t.descricao}</td>
        <td class="t-custo">${brl(t.custo)}</td>
        <td>${link}</td>
      </tr>`;
    }).join("");
    return `<div class="table-wrap"><table class="matriz tabela-orc">
      <thead><tr><th>Tipologia</th><th>Descrição</th><th>Custo estimado</th><th>Memorial</th></tr></thead>
      <tbody>${rows}</tbody></table></div>`;
  }

  function card(item) {
    const c = el("div", "spot-card");
    const chip = `<div class="fontes"><span class="estilo-chip">${item.estilo} · ${item.pacote}</span></div>`;
    const cons = item.consolidado_url && item.consolidado_url !== "#"
      ? `<a class="btn btn-ghost" href="${item.consolidado_url}" target="_blank" rel="noopener">Abrir consolidado no Drive ↗</a>`
      : "";
    c.innerHTML = `
      <div class="spot-card-top">
        <div>
          <h3>${item.spot} <span class="spot-cod">${item.codigo}</span></h3>
          <p class="spot-meta">${item.total_tipologias} tipologias · gerado em ${item.gerado_em}</p>
        </div>
        ${chip}
      </div>
      <div class="spot-actions">
        <button class="btn btn-primary" data-ver="${item.slug}">Ver custos</button>
        ${cons}
      </div>
      <div class="spot-tabela" hidden></div>`;
    c.querySelector("[data-ver]").addEventListener("click", (e) => {
      const box = c.querySelector(".spot-tabela");
      const btn = e.currentTarget;
      if (box.hidden) {
        if (!box.dataset.loaded) { box.innerHTML = tabelaHTML(O.spots[item.slug]); box.dataset.loaded = "1"; }
        box.hidden = false; btn.textContent = "Ocultar custos";
      } else { box.hidden = true; btn.textContent = "Ver custos"; }
    });
    return c;
  }

  function semMatch(termo) {
    empty.hidden = false;
    list.innerHTML = "";
    const cmd = `gera o orçamento do ${termo || "<empreendimento>"}`;
    empty.innerHTML = `
      <p class="empty-title">Nenhum orçamento gerado para "<strong>${termo}</strong>".</p>
      <p class="empty-sub">Os orçamentos são gerados pelo Claude a partir do catálogo. Copie o comando e cole no Claude:</p>
      <div class="cmd-row"><code>${cmd}</code><button class="btn btn-primary" id="orc-copy-cmd">Pedir geração ao Claude</button></div>`;
    empty.querySelector("#orc-copy-cmd").addEventListener("click", () => {
      navigator.clipboard && navigator.clipboard.writeText(cmd);
      empty.querySelector("#orc-copy-cmd").textContent = "Comando copiado ✓";
    });
  }

  function render(termo) {
    const q = (termo || "").trim().toLowerCase();
    const itens = (O.index || []).filter((i) =>
      !q || i.spot.toLowerCase().includes(q) || String(i.codigo).toLowerCase().includes(q));
    if (!(O.index || []).length) { semMatch(termo); empty.querySelector(".empty-title").innerHTML = "Nenhum orçamento gerado ainda."; return; }
    if (!itens.length) { semMatch(termo); return; }
    empty.hidden = true;
    list.innerHTML = "";
    itens.forEach((i) => list.appendChild(card(i)));
  }

  input.addEventListener("input", (e) => render(e.target.value));
  render("");

  const howtoCopy = $("#orc-howto-copy");
  if (howtoCopy) {
    howtoCopy.addEventListener("click", () => {
      const txt = ($("#orc-howto-cmd") || {}).textContent || "";
      navigator.clipboard && navigator.clipboard.writeText(txt);
      howtoCopy.textContent = "Comando copiado ✓";
      setTimeout(() => { howtoCopy.textContent = "Copiar comando"; }, 2000);
    });
  }
})();
