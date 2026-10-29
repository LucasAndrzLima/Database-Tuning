// Compara a carga MongoDB com registros e indicadores independentes do MySQL.
load(require('path').join(__dirname, '00_comum.js'));
var origem = N2.origem();
var esperados = origem.fornecedor.map(N2.fato).sort((a, b) => a._id - b._id);
var destino = db.fato_fornecedores.find().sort({ _id: 1 }).toArray();
var destinoPorId = new Map(destino.map(d => [Number(d._id), d]));
var idsEsperados = new Set(esperados.map(d => d._id));
var divergentes = esperados.filter(d => N2.canonico(d) !== N2.canonico(destinoPorId.get(d._id) || {})).map(d => d._id);
var extras = destino.filter(d => !idsEsperados.has(Number(d._id))).map(d => Number(d._id));
var ind = N2.indicadores();

function compararIndicadores(sql, mongo, chave) {
  var a = [...sql].sort((x, y) => x[chave] - y[chave]);
  var b = [...mongo].sort((x, y) => x[chave] - y[chave]);
  if (a.length !== b.length) return false;
  return a.every((r, i) => Object.keys(r).sort().join() === Object.keys(b[i]).sort().join() &&
    Object.keys(r).every(k => k === 'participacao_pct'
      ? r[k] !== null && b[i][k] !== null && Math.abs(Number(r[k]) - Number(b[i][k])) <= 0.000051
      : N2.canonico(r[k]) === N2.canonico(b[i][k])));
}
var regioesOk = compararIndicadores(origem.indicador_regiao, ind['01_participacao_regiao'], 'regiao_id');
var paisesOk = compararIndicadores(origem.indicador_pais, ind['02_distribuicao_pais'], 'pais_id');
var dimensoesOk = N2.canonico([...origem.pais].sort((a, b) => a._id - b._id)) ===
    N2.canonico(db.dim_pais.find().sort({ _id: 1 }).toArray()) &&
  N2.canonico([...origem.regiao].sort((a, b) => a._id - b._id)) ===
    N2.canonico(db.dim_regiao.find().sort({ _id: 1 }).toArray());
var evidencia = {
  aprovado: esperados.length > 0 && esperados.length === destino.length && !divergentes.length && !extras.length && regioesOk && paisesOk && dimensoesOk,
  executor: 'mongosh / JavaScript', instante: new Date(),
  mysql: origem.controle[0],
  mongodb: { fornecedores: destino.length, paises: db.dim_pais.countDocuments(), regioes: db.dim_regiao.countDocuments() },
  fornecedoresDivergentes: divergentes, idsExtras: extras,
  regioesEquivalentes: regioesOk, paisesEquivalentes: paisesOk, dimensoesEquivalentes: dimensoesOk,
  comparacaoRegioes: { mysql: origem.indicador_regiao, mongodb: ind['01_participacao_regiao'] },
  comparacaoPaises: { mysql: origem.indicador_pais, mongodb: ind['02_distribuicao_pais'] }
};
N2.gravar('execucao_validacao_mongosh.json', evidencia);
N2.gravar('execucao_indicadores_mongosh.json', ind);
if (!evidencia.aprovado) throw new Error('Validação REPROVADA. Consulte a evidência.');
print('Validação APROVADA. MySQL e MongoDB: ' + destino.length + ' fornecedores; indicadores correspondentes.');
printjson(ind['01_participacao_regiao']);
