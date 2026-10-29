// Funções de leitura, transformação e validação da ETL.
var N2 = {};
N2.fs = require('fs');
N2.path = require('path');
N2.raiz = process.env.PROJETO_DIR || N2.path.resolve(__dirname, '..');
N2.banco = db.getName();
if (!N2.banco.startsWith('n2_')) throw new Error('Conecte a um banco dedicado n2_...');

N2.ler = function (arquivo) {
  return JSON.parse(N2.fs.readFileSync(N2.path.join(N2.raiz, arquivo), 'utf8'));
};
N2.gravar = function (arquivo, objeto) {
  var destino = N2.path.join(N2.raiz, 'evidencias', arquivo);
  N2.fs.mkdirSync(N2.path.dirname(destino), { recursive: true });
  N2.fs.writeFileSync(destino, EJSON.stringify(objeto, null, 2, { relaxed: true }), 'utf8');
};
N2.canonico = function (valor) {
  var simples = JSON.parse(EJSON.stringify(valor, { relaxed: true }));
  function ordenar(x) {
    if (Array.isArray(x)) return x.map(ordenar);
    if (x && typeof x === 'object') {
      var out = {};
      Object.keys(x).sort().forEach(k => out[k] = ordenar(x[k]));
      return out;
    }
    return x;
  }
  return JSON.stringify(ordenar(simples));
};
N2.fato = function (r) {
  if (!Number.isSafeInteger(r.id) || !r.nome || !r.nome.trim() ||
      !Number.isSafeInteger(r.paisId) || !Number.isSafeInteger(r.regiaoId) ||
      !r.pais || !r.regiao) throw new Error('Fornecedor inválido ou sem geografia: ' + r.id);
  return {
    _id: r.id,
    fornecedor: { id: r.id, nome: r.nome.trim() },
    geografia: { paisId: r.paisId, pais: r.pais.trim(), regiaoId: r.regiaoId, regiao: r.regiao.trim() },
    quantidadeFornecedores: 1
  };
};
N2.origem = function () {
  var arquivo = N2.path.join(N2.raiz, 'dados', 'extracao.ndjson');
  var linhas = N2.fs.readFileSync(arquivo, 'utf8').replace(/^\uFEFF/, '').split(/\r?\n/).filter(x => x.trim());
  var grupos = { fornecedor: [], pais: [], regiao: [], indicador_regiao: [], indicador_pais: [], controle: [] };
  linhas.forEach((linha, i) => {
    var r = JSON.parse(linha);
    if (!(r.tipo in grupos)) throw new Error('Tipo de registro inesperado na linha ' + (i + 1));
    grupos[r.tipo].push(r.dados);
  });
  if (grupos.controle.length !== 1) throw new Error('A extração deve conter exatamente um controle SQL');
  var c = grupos.controle[0];
  if (!c.fornecedores || c.fornecedores !== grupos.fornecedor.length ||
      c.paises !== grupos.pais.length || c.regioes !== grupos.regiao.length ||
      c.fornecedores_sem_pais !== 0 || c.paises_sem_regiao !== 0) {
    throw new Error('Fonte vazia, incompleta ou com referências órfãs. Refazer a extração SQL.');
  }
  return grupos;
};
N2.indicadores = function () {
  var nomes = ['01_participacao_regiao', '02_distribuicao_pais'];
  var resultado = {};
  nomes.forEach(nome => {
    var pipeline = N2.ler('consultas/mongodb/' + nome + '.json');
    resultado[nome] = db.fato_fornecedores.aggregate(pipeline, { allowDiskUse: true }).toArray();
  });
  return resultado;
};
