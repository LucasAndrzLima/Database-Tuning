// Execute no mongosh para mostrar os mesmos indicadores usados no Redash.
load(require('path').join(__dirname, '00_comum.js'));
var indicadores = N2.indicadores();
Object.keys(indicadores).forEach(nome => {
  print('\n' + nome);
  printjson(indicadores[nome]);
});
N2.gravar('execucao_indicadores_mongosh.json', indicadores);
