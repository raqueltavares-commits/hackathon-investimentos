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
