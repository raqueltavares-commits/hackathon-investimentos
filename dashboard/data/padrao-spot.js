// Padrão Spot — lógica de tipologias e regras de mobiliário.
// Fonte: projeto mapeamento-completo-de-mobilirio--unidade-spot (docs/mobiliario_spot.csv).
// Carregado como global pra a página abrir direto no navegador (file://), sem servidor.
window.PADRAO_SPOT = {
  classificacao: {
    intro:
      "Toda tipologia Spot nasce da combinação de três eixos. Junte os três e você " +
      "tem o código da unidade (ex.: Sem terraço · Padrão · Cap. 2).",
    eixos: [
      {
        nome: "Terraço / Área externa",
        opcoes: ["Sem", "Sacada", "Varanda", "Garden", "Terraço"],
        nota: "Garden e Terraço = área externa ampla. Sacada e Varanda = compacta."
      },
      {
        nome: "Tipo construtivo",
        opcoes: ["Padrão", "PCD", "Mezanino", "Único"],
        nota: "PCD muda banheiro e circulação. Mezanino divide o programa em 2 pisos."
      },
      {
        nome: "Capacidade (previsão)",
        opcoes: ["2", "3", "4", "5"],
        nota: "Quantas pessoas dormem. Definida pelo que cabe — confirmar no layout final."
      }
    ]
  },

  matriz: {
    intro:
      "A capacidade é uma previsão que sai do que cabe na unidade. A cama auxiliar e o " +
      "sofá-cama são as peças que destravam mais hóspedes.",
    colunas: ["Item", "Cap. 2", "Cap. 3", "Cap. 4", "Cap. 5"],
    linhas: [
      { item: "Cama Queen 1,60×2,00m", v: ["sim", "sim", "sim", "sim"] },
      { item: "Mesa de cabeceira", v: ["sim", "sim", "sim", "sim"] },
      { item: "Copa linear", v: ["sim", "sim", "sim", "sim"] },
      { item: "Arara + Vassoureiro", v: ["sim", "sim", "sim", "sim"] },
      { item: 'TV 43"', v: ["sim", "sim", "sim", "sim"] },
      { item: "Cama auxiliar 0,67×1,90m", v: ["não", "lado queen", "não", "lado queen"] },
      { item: "Sofá-cama (aberto = leito)", v: ["não", "não", "sim", "sim"] },
      { item: "Bancada (nº cadeiras)", v: ["2", "3", "3–4", "4–5"] },
      { item: "Mesa redonda externa", v: ["não", "não", "se varanda", "sim"] },
      { item: "Jacuzzi", v: ["se garden/terraço", "se garden/terraço", "se garden/terraço", "se garden/terraço"] }
    ]
  },

  programa: {
    intro: "13 itens, organizados por zona. O selo diz se é fixo ou condicional.",
    zonas: [
      {
        nome: "Zona Dormir",
        itens: [
          { nome: "Cama Queen", dim: "1,60 × 2,00m", status: "OBRIGATÓRIO",
            regra: "Cabeceira na parede interna, nunca de costas pra porta. 60cm de circulação lateral (mín. 1 lado). PCD: acesso bilateral." },
          { nome: "Mesa de cabeceira", dim: "~0,40 × 0,40m", status: "OBRIGATÓRIO",
            regra: "1 ou 2 conforme a cama. Sem espaço: cabeceira com 7cm de profundidade estrutural." },
          { nome: "Cama auxiliar", dim: "0,67 × 1,90m", status: "CAP. 3 e 5",
            regra: "Cabe ao lado da Queen. Não aparece na planta, mas define a capacidade." },
          { nome: "Sofá-cama", dim: "1,62 × 2,00m (aberto)", status: "CAP. 4 e 5",
            regra: "Fechado = estar, aberto = leito. Não existe sofá fixo." }
        ]
      },
      {
        nome: "Zona Copa",
        itens: [
          { nome: "Copa linear", dim: "1,55 × 0,55m (mín.)", status: "OBRIGATÓRIO",
            regra: "Pia + torneira + fogão 2 bocas + gaveteiro + armário inferior. Sempre linear e encostada na parede — nunca em L ou ilha." },
          { nome: "Bancada de refeição", dim: "1,10–1,50 × 0,40m", status: "OBRIGATÓRIO",
            regra: "De preferência em sequência à copa, mas pode ficar em outra parede. Nº de cadeiras pela capacidade. Pode integrar com a arara." }
        ]
      },
      {
        nome: "Zona Guardar",
        itens: [
          { nome: "Arara de roupas", dim: "0,60–0,80 × 0,55m", status: "OBRIGATÓRIO",
            regra: "Substitui o guarda-roupa. Posições: hall de entrada, lateral à cama ou rodapé." },
          { nome: "Vassoureiro", dim: "0,20–0,30 × 0,55m", status: "OBRIGATÓRIO",
            regra: "Posição flexível: onde couber sem atrapalhar a circulação. De preferência próximo à copa." }
        ]
      },
      {
        nome: "Tecnologia",
        itens: [
          { nome: 'TV 43"', dim: "43 polegadas", status: "OBRIGATÓRIO",
            regra: "Campo de visão do hóspede deitado. Suporte de parede; fachada de vidro = suporte de teto." }
        ]
      },
      {
        nome: "Área externa",
        itens: [
          { nome: "Jacuzzi circular", dim: "Ø 1,80–2,00m", status: "GARDEN / TERRAÇO",
            regra: "O ponto de instalação é obrigatório quando há garden ou terraço. A instalação da jacuzzi é responsabilidade do proprietário." },
          { nome: "Mesa externa + cadeiras", dim: "Ø 0,90m + 2–4 cadeiras", status: "VARANDA / COBERTURA",
            regra: "Mesa redonda preferencial. Sacadas compactas dispensam." }
        ]
      },
      {
        nome: "Banheiro",
        itens: [
          { nome: "Banheiro padrão", dim: "~2,30m²", status: "OBRIGATÓRIO",
            regra: "Chuveiro + vaso + pia. Módulo de marcenaria no inferior da bancada e espelho acima da bancada da pia." },
          { nome: "Banheiro PCD", dim: "≥ 4,00m²", status: "TIPO PCD",
            regra: "Raio de giro Ø 1,50m livre. Porta de correr ou de giro abrindo para fora. Barras de apoio." }
        ]
      }
    ]
  },

  regras: {
    intro: "As leis que valem em qualquer layout. Vermelho = proibido, azul = obrigatório.",
    grupos: [
      {
        nome: "Circulação",
        itens: [
          { texto: "60cm de circulação ao redor da cama (mín. 1 lateral; PCD em ambas).", tipo: "OBRIGATÓRIO" },
          { texto: "Nenhum móvel no caminho de abertura da porta de entrada.", tipo: "PROIBIDO" },
          { texto: "Porta do banheiro nunca obstruída (PCD: porta de correr ou de giro abrindo para fora, Ø 1,50m livre).", tipo: "OBRIGATÓRIO" }
        ]
      },
      {
        nome: "Janela",
        itens: [
          { texto: "20cm entre a cama e a parede da janela (para a cortina).", tipo: "OBRIGATÓRIO" },
          { texto: "Nenhum móvel alto na frente da janela principal.", tipo: "PROIBIDO" }
        ]
      },
      {
        nome: "Cama",
        itens: [
          { texto: "Cabeceira na parede interna; nunca de costas para a porta.", tipo: "OBRIGATÓRIO" },
          { texto: "Sempre orientada para a TV.", tipo: "OBRIGATÓRIO" },
          { texto: "Sem espaço para mesa de cabeceira: cabeceira com 7cm estrutural.", tipo: "EXCEÇÃO" }
        ]
      },
      {
        nome: "Copa",
        itens: [
          { texto: "Sempre linear e na parede; nunca em L, ilha ou deslocada.", tipo: "OBRIGATÓRIO" },
          { texto: "Sempre numa parede que divide tubulação: com a outra unidade (espelhada) ou com o banheiro.", tipo: "OBRIGATÓRIO" },
          { texto: "Bancada de preferência em sequência à copa; em algumas tipologias fica em outra parede.", tipo: "PERMITIDO" },
          { texto: "Arara + bancada-desk podem ser um módulo integrado.", tipo: "PERMITIDO" }
        ]
      },
      {
        nome: "Mezanino",
        itens: [
          { texto: "Piso 1 = sofá-cama + copa + bancada + banheiro.", tipo: "REGRA" },
          { texto: "Piso 2 = apenas cama + cabeceira + mesa, se couber.", tipo: "REGRA" }
        ]
      },
      {
        nome: "PCD",
        itens: [
          { texto: "Porta de correr ou de giro abrindo para fora + raio de giro Ø 1,50m + acesso bilateral à cama.", tipo: "OBRIGATÓRIO" }
        ]
      }
    ]
  },

  passos: {
    intro:
      "Rascunho do método, deduzido das regras. Raquel revisa e ajusta a ordem real.",
    nota: "⚠️ Capacidade é previsão até o layout final confirmar.",
    etapas: [
      { t: "Identifique a tipologia", d: "Terraço, tipo construtivo e capacidade prevista da unidade." },
      { t: "Posicione a Cama Queen", d: "Cabeceira na parede interna, nunca de costas pra porta, 20cm da janela, de frente pra TV, 60cm de circulação lateral." },
      { t: "Mesa(s) de cabeceira", d: "1 ou 2 conforme a cama. Sem espaço, use cabeceira de 7cm." },
      { t: "Defina a capacidade extra", d: "Cama auxiliar ao lado da Queen (cap. 3 e 5). Sofá-cama aberto = leito (cap. 4 e 5)." },
      { t: "Monte a Copa linear", d: "Encostada na parede, com pia, fogão 2 bocas e armários. Nunca em L ou ilha." },
      { t: "Bancada de refeição", d: "Em sequência à copa. Nº de cadeiras pela capacidade." },
      { t: "Arara e Vassoureiro", d: "Arara na entrada/lateral/rodapé; vassoureiro fixo na entrada." },
      { t: 'Fixe a TV 43"', d: "De frente para a cama. Suporte de parede; teto se a fachada for de vidro." },
      { t: "Resolva o banheiro", d: "Porta sempre desobstruída. Módulo de marcenaria no inferior da bancada e espelho acima da pia. PCD: porta de correr ou de giro abrindo para fora + Ø 1,50m." },
      { t: "Área externa (se houver)", d: "Jacuzzi em garden/terraço; mesa redonda em varanda/cobertura." },
      { t: "Confira as regras", d: "Circulação de 60cm, porta de entrada livre, nada alto na frente da janela." }
    ]
  }
};
