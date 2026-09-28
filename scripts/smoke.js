// 在 Node 里模拟浏览器环境，验证运行时数据包与筛选逻辑
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..');
global.window = {};
const load = (f) => eval(fs.readFileSync(path.join(ROOT, f), 'utf8'));
load('data/db-index.js');
load('data/db-entries.js');
const DB = global.window.ARTDB;

const ok = [], bad = [];
const A = (c, m) => (c ? ok : bad).push(m);

A(!!DB, 'window.ARTDB 已定义');
A(DB.index && DB.index.length === 150, `索引条目数 = ${DB.index && DB.index.length}（应为 150）`);
A(DB.entries && Object.keys(DB.entries).length === 150, `词条数 = ${DB.entries && Object.keys(DB.entries).length}`);
A(DB.taxonomy && DB.taxonomy.period.length === 11, `时期词表 = ${DB.taxonomy && DB.taxonomy.period.length}`);
A(DB.taxonomy.region.length === 9, `地区词表 = ${DB.taxonomy.region.length}`);
A(DB.movements.length === 64, `流派词表 = ${DB.movements.length}（受控值）`);
A(DB.meta.words > 200000, `正文总字数 = ${DB.meta.words}`);

// 六部分完整性
let miss = { life: 0, style: 0, works: 0, legacy: 0, controversy: 0, statement: 0, motifs: 0 };
let shortWork = 0, noImg = 0, totImg = 0, totW = 0;
for (const id of Object.keys(DB.entries)) {
  const e = DB.entries[id];
  for (const k of Object.keys(miss)) {
    const v = e[k];
    if (!v || (Array.isArray(v) && !v.length) || (typeof v === 'object' && !Array.isArray(v) && !Object.keys(v).length)) miss[k]++;
  }
  if (!(e.evolution && e.evolution.early && e.evolution.middle && e.evolution.late)) miss.evo++;
  totW += (e.works || []).length;
  for (const w of (e.works || [])) {
    if (!(w.background && w.scene && w.innovation && w.significance)) shortWork++;
    if (w.image) totImg++; else noImg++;
  }
}
for (const [k, v] of Object.entries(miss)) A(v === 0, `缺失「${k}」的词条数 = ${v}（应为 0）`);
A(shortWork === 0, `作品四要素不全的件数 = ${shortWork}`);

// 索引/筛选一致性
const byId = Object.fromEntries(DB.index.map(a => [a.id, a]));
A(DB.index.every(a => !!DB.entries[a.id]), '索引与词条一一对应');
const hit = (q) => DB.index.filter(a => {
  const hay = [a.zh, a.name, a.movement, a.period, a.region, (a.mediums||[]).join(' '),
               (a.movementTags||[]).join(' '), a.tagline, (a.works||[]).join(' '), a.country]
    .join(' ').toLowerCase();
  return hay.includes(q.toLowerCase());
}).length;
A(hit('印象派') >= 5, `关键词「印象派」命中 = ${hit('印象派')}`);
A(hit('油画') > 100, `媒介「油画」命中 = ${hit('油画')}`);
A(hit('日本') >= 2, `地区/国别「日本」命中 = ${hit('日本')}`);
A(hit('梵高') === 1, `姓名「梵高」命中 = ${hit('梵高')}`);
A(hit('水墨') >= 6, `媒介「水墨」命中 = ${hit('水墨')}`);

// 图版
const portrait = DB.index.filter(a => a.thumb).length;
A(portrait >= 140, `有头像缩略图的艺术家 = ${portrait}`);

console.log('【通过】');
ok.forEach(m => console.log('  ✓ ' + m));
if (bad.length) { console.log('\n【失败】'); bad.forEach(m => console.log('  ✗ ' + m)); }
console.log(`\n作品总数 ${totW}｜已配图 ${totImg}（${(totImg/totW*100).toFixed(0)}%）｜无图 ${noImg}`);
console.log(bad.length ? `\n结果：${bad.length} 项未通过` : '\n结果：全部通过');
process.exit(bad.length ? 1 : 0);
