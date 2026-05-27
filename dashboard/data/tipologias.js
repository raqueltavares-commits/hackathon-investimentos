// Tabelas de tipologias geradas pelo Claude (skill tabela-tipologias).
// A skill REESCREVE este arquivo a cada geração: adiciona/atualiza o Spot em `spots`
// e a entrada em `index`. Carregado como global pra abrir via file:// sem servidor.
window.TIPOLOGIAS = {
  colunas: ["TIPOLOGIA", "N DAS UNIDADES", "TERRAÇO", "TIPO", "QUANTIDADE",
            "CAPACIDADE (previsão)", "ÁREA ÚTIL (m²)", "ÁREA DA UNIDADE (m²)"],
  index: [
    {
      spot: "Natal Spot", codigo: "6953", slug: "natal-spot",
      gerado_em: "2026-05-26", total_tipologias: 5, total_unidades: 96, fonte: "analise",
      fontes: { pdf: true, analise: true, dwg: false },
      drive_url: "https://docs.google.com/spreadsheets/d/1Ffn359MFIgtERfKWiR-UfMFJVUOWDotSaSQLm8PxXQ8/edit"
    },
    {
      spot: "Bonito Spot", codigo: "5316", slug: "bonito-spot",
      gerado_em: "2026-05-26", total_tipologias: 4, total_unidades: 53, fonte: "pdf",
      fontes: { pdf: true, analise: false, dwg: false },
      drive_url: "https://docs.google.com/spreadsheets/d/1iq7gvHOmMwSrw0HwK8iT6Ssa0MRFyKIeAobpdZ7txNM/edit",
      rascunho: true
    }
  ],
  spots: {
    "natal-spot": {
      spot: "Natal Spot", codigo: "6953",
      drive_url: "https://docs.google.com/spreadsheets/d/1Ffn359MFIgtERfKWiR-UfMFJVUOWDotSaSQLm8PxXQ8/edit",
      tipologias: [
        { tipologia: "A", terraco: "Sem", tipo: "Padrão", quantidade: 74, capacidade: 2,
          area_util: "16,84–17,29", area_unidade: "16,84–17,29",
          unidades: ["101","102","103","104","105","106","107","201","202","203","204","205","206","207","301","302","303","304","305","306","307","401","402","403","404","405","406","501","502","503","504","505","506","601","602","603","604","605","606","701","702","703","704","705","706","801","802","803","804","805","806","901","902","903","904","905","906","1001","1002","1003","1004","1005","1006","1101","1102","1103","1104","1105","1106","1201","1202","1203","1204","1205"] },
        { tipologia: "B", terraco: "Sem", tipo: "Padrão", quantidade: 10, capacidade: 3,
          area_util: "18,16", area_unidade: "18,16",
          unidades: ["109","209","309","508","608","708","808","908","1008","1108"] },
        { tipologia: "C", terraco: "Sem", tipo: "Padrão", quantidade: 10, capacidade: 5,
          area_util: "23,46", area_unidade: "23,46",
          unidades: ["108","208","308","507","607","707","807","907","1007","1107"] },
        { tipologia: "D", terraco: "Sacada", tipo: "Padrão", quantidade: 1, capacidade: 3,
          area_util: "18,16", area_unidade: "27,41", unidades: ["408"] },
        { tipologia: "E", terraco: "Sacada", tipo: "Padrão", quantidade: 1, capacidade: 5,
          area_util: "23,46", area_unidade: "31,37", unidades: ["407"] }
      ]
    },
    "bonito-spot": {
      spot: "Bonito Spot", codigo: "5316",
      drive_url: "https://docs.google.com/spreadsheets/d/1iq7gvHOmMwSrw0HwK8iT6Ssa0MRFyKIeAobpdZ7txNM/edit",
      tipologias: [
        { tipologia: "A", terraco: "Sem sacada", tipo: "Padrão", quantidade: 40, capacidade: 2,
          area_util: "14,86–15,37", area_unidade: "14,86–15,37",
          unidades: ["201","202","203","204","205","206","207","208","209","210","211","212","213","214","215","216","301","302","303","304","305","306","307","308","309","310","311","312","313","314","315","316","401","402","403","404","405","406","407","408"] },
        { tipologia: "B", terraco: "Garden", tipo: "Padrão", quantidade: 10, capacidade: 2,
          area_util: "14,86–15,37", area_unidade: "14,86–15,37",
          unidades: ["101","102","103","107","108","109","110","111","112","113"] },
        { tipologia: "C", terraco: "Garden", tipo: "PCD", quantidade: 2, capacidade: 4,
          area_util: "22,91", area_unidade: "22,91", unidades: ["104","105"] },
        { tipologia: "D", terraco: "Garden", tipo: "Padrão", quantidade: 1, capacidade: 4,
          area_util: "19,20", area_unidade: "19,20", unidades: ["106"] }
      ]
    }
  }
};
