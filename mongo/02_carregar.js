// ETL no mongosh: a extração já veio do MySQL; aqui transformamos e carregamos.
load(require('path').join(__dirname, '00_comum.js'));
var origem = N2.origem();
var fatos = origem.fornecedor.map(N2.fato);
var ids = new Set(fatos.map(f => f._id));
if (ids.size !== fatos.length) throw new Error('A origem contém IDs de fornecedor repetidos');

var paisPorId = new Map(origem.pais.map(p => [p._id, p]));
var regiaoPorId = new Map(origem.regiao.map(r => [r._id, r]));
fatos.forEach(f => {
  var p = paisPorId.get(f.geografia.paisId);
  var r = regiaoPorId.get(f.geografia.regiaoId);
  if (!p || !r || p.regiao.id !== r._id || p.nome !== f.geografia.pais || r.nome !== f.geografia.regiao) {
    throw new Error('Relacionamento inconsistente no fornecedor ' + f._id);
  }
});

var cargaId = new ObjectId().toString();
var colecoes = { fato_fornecedores: fatos, dim_pais: origem.pais, dim_regiao: origem.regiao };
var temporarias = {};
Object.keys(colecoes).forEach(nome => {
  var temporaria = nome + '_carga_' + cargaId;
  db.createCollection(temporaria);
  var dados = colecoes[nome];
  for (var i = 0; i < dados.length; i += 1000) {
    db.getCollection(temporaria).insertMany(dados.slice(i, i + 1000));
  }
  var gravados = db.getCollection(temporaria).find().sort({ _id: 1 }).toArray();
  var esperados = [...dados].sort((a, b) => a._id - b._id);
  if (N2.canonico(gravados) !== N2.canonico(esperados)) throw new Error('Staging divergente: ' + temporaria);
  temporarias[nome] = temporaria;
});
db.getCollection(temporarias.fato_fornecedores).createIndex(
  { 'geografia.regiaoId': 1, _id: 1 }, { name: 'ix_regiao_fornecedor' });
db.getCollection(temporarias.fato_fornecedores).createIndex(
  { 'geografia.paisId': 1 }, { name: 'ix_pais' });

// Publicação em janela sem leitores. As três trocas são sequenciais.
Object.keys(temporarias).forEach(nome => {
  if (db.getCollectionNames().includes(nome)) {
    db.getCollection(nome).renameCollection(nome + '_backup_' + cargaId);
  }
  db.getCollection(temporarias[nome]).renameCollection(nome);
});
var manifesto = { cargaId, origem: origem.controle[0], carregadoEm: new Date(),
  executor: 'mongosh / JavaScript', banco: db.getName(),
  fornecedores: fatos.length, paises: origem.pais.length, regioes: origem.regiao.length };
db.cargas.insertOne(manifesto);
N2.gravar('execucao_carga_mongosh.json', manifesto);
print('Carga concluída: ' + fatos.length + ' fornecedores. Execute 03_validar.js.');
