# 艺史长卷 · 对艺术史产生重大影响的 150 位艺术家

一个纯静态、可离线运行的两级检索数据库。列表页支持按**姓名、流派、时期、地区、媒介**的
关键词检索与多维组合筛选；详情页按统一六部分结构完整呈现每一位艺术家，代表作配馆藏高清图版。

---

## 一、快速开始

直接用浏览器打开 `index.html` 即可（无需服务器、无需构建、无需联网）。

> 站点通过 `<script src="data/db-*.js">` 载入数据，因此在 `file://` 协议下同样可用——
> 这是刻意为离线查阅设计的。

---

## 二、目录结构

```
artists-db/
├─ index.html                 列表页（检索 / 筛选 / 时期长卷）
├─ artist.html                详情页（?id=<艺术家id>）
├─ assets/
│  ├─ css/style.css           全站样式（纸张·墨色·硃砂）
│  ├─ js/app.js               列表页逻辑
│  ├─ js/detail.js            详情页逻辑
│  └─ img/<艺术家id>/         本地缓存的图版
│     ├─ portrait.jpg         艺术家肖像 / 头像
│     └─ w1.jpg … w5.jpg      代表作图版
├─ data/                      ★ 全部数据集中于此，均为独立结构化文件
│  ├─ roster.json             选目基线：150 位艺术家的分类元数据（唯一真源）
│  ├─ artists.json            150 位完整词条（六部分全文 + 图版信息）
│  ├─ index.json              轻量索引（列表页 / 筛选用）
│  ├─ images.json             图版清单（含来源、馆藏编号、高清原图链接）
│  ├─ taxonomy.json           检索词表（时期 / 地区 / 媒介 / 流派）
│  ├─ artists/part-NN-x.json  词条分片（写作批次产物，可直接编辑）
│  ├─ batches/                写作批次分配
│  └─ db-index.js             运行时数据包（由 build_db.py 生成，勿手改）
│  └─ db-entries.js
├─ docs/
│  ├─ ENTRY_SCHEMA.md         词条撰写规范
│  └─ EXAMPLE_ENTRY.json      合格样例（梵高，2451 字）
└─ scripts/
   ├─ validate_roster.py      校验选目
   ├─ make_batches.py         切分写作批次
   ├─ check_part.py           校验词条分片是否符合规范
   ├─ merge.py                合并分片 → artists.json / index.json
   ├─ fetch_images.py         抓取并核验馆藏图版
   └─ build_db.py             打包为 db-index.js / db-entries.js
```

---

## 三、统一词条结构

每位艺术家都写满六个部分，各部分以要点分述（不接受词条式简介）：

| 部分 | 字段 | 条数 | 要求 |
|---|---|---|---|
| 一、生平与时代语境 | `life` | 6–9 | 出生年代、人生转折（迁居/战争/变故）、创作关键节点、时代思潮与流派立场（顺应/反叛/开创）、师承交游与团体 |
| 二、创作风格与视觉标识 | `style` | 6–8 | 流派定位（开创者/核心/边缘）、题材、色彩笔触、标志符号、媒介技法、是否跨媒介 |
| 三、代表作品与艺术观念 | `works`（3–5 件）<br>`statement`<br>`motifs` | — | 每件写满创作背景／画面内容／艺术突破／历史地位，并给出英文通用名 `titleEn` 供馆藏检索；核心主张须含真实引文出处；贯穿母题 |
| 四、创作演变与分期 | `evolution.early/middle/late` | 3 段 | 各阶段风格特征与转向诱因（思潮、变故、材料技术） |
| 五、历史地位与影响力 | `legacy` | 5–7 | 艺术史贡献、对后世艺术家与流派的影响（点名）、顶级馆藏、奖项荣誉 |
| 六、争议与多元评价 | `controversy` | 4–6 | 当时批评、当代再解读（女性主义／后殖民／修复研究等）、个人经历如何作用于创作 |

全库正文合计约 **26.7 万字**，平均每条约 **1780 字**。

更多写作细则见 `docs/ENTRY_SCHEMA.md`，质量基准见 `docs/EXAMPLE_ENTRY.json`。

---

## 四、选目构成

- **150 位**艺术家，跨 1600 余年
- **11 个时期**：14世纪及以前 / 15世纪 / 16世纪 / 17世纪 / 18世纪 / 19世纪前期 / 19世纪后期 / 1900–1925 / 1925–1945 / 1945–1970 / 1970年以后
- **9 个地区**：南欧 / 西欧 / 中欧与北欧 / 北美 / 拉丁美洲 / 东亚 / 南亚 / 西亚·中东 / 非洲
- **16 类媒介**：油画 / 湿壁画 / 蛋彩 / 雕塑 / 版画 / 素描·手稿 / 水彩 / 摄影 / 建筑 / 设计·工艺 / 装置 / 行为 / 影像 / 拼贴 / 水墨·绢本 / 综合媒介
- 含中国艺术家 6 位（顾恺之、范宽、倪瓒、八大山人、齐白石、徐悲鸿）与日本浮世绘 2 位

---

## 五、图版来源与处理

`scripts/fetch_images.py` 按以下优先级解析并**逐幅下载核验**：

1. **大都会艺术博物馆开放获取 API** — 权威元数据 + 高清原图
   `collectionapi.metmuseum.org`
2. **克利夫兰艺术博物馆开放获取 API** — 权威元数据 + 高清原图
   `openaccess-api.clevelandart.org`
3. **WikiArt 视觉艺术百科** — 覆盖率保底（含近现代、非西方）

匹配策略：在**同一位艺术家名下**的候选中，用「标题词集相似度 + 年代一致性加权」评分择优，
并内置艺术史术语异名归一表（如 `Descent from the Cross` ↔ `Deposition`、`Madonna` ↔ `Virgin`）。
图版统一压缩至最长边 1100px、JPEG q82 后本地缓存，同时保留高清原图链接。

> **关于近现代作品的图版缺失**：1950 年代之后的作品多仍受版权保护，无合法开放图版可用。
> 这类作品以版式化的题名图版呈现，并提供馆藏检索入口——这是版权现实，而非数据缺漏。
> 每幅图版均在详情页与灯箱中标注来源机构、馆藏编号与 credit line。

---

## 六、如何补全 / 扩充词条

数据层与表现层完全解耦，新增艺术家**不需要改动任何页面代码**。

**方式 A：新增词条（补足至 150 位之后继续扩充）**

1. 在 `data/roster.json` 的 `artists` 数组末尾追加一条元数据：
   ```json
   {"id":"new-artist","name":"Full Name","zh":"中文名","birth":1900,"death":1980,
    "country":"法国","region":"西欧","period":"1925–1945","movement":"超现实主义",
    "mediums":["油画"],"wikiTitle":"Full Name"}
   ```
   > `period` / `region` 取值必须来自同文件 `taxonomy`；`mediums` 取值来自 `taxonomy.medium`。
2. 照 `docs/ENTRY_SCHEMA.md` 撰写词条，写成 `data/artists/part-99-a.json`（裸 JSON 数组即可）。
3. 依次运行：
   ```bash
   python scripts/check_part.py data/artists/part-99-a.json   # 结构校验
   python scripts/merge.py                                    # 合并（roster 元数据自动覆盖）
   python scripts/fetch_images.py                             # 抓取图版（自动跳过已完成）
   python scripts/build_db.py                                 # 打包运行时数据
   ```
   刷新页面即可看到新词条。

**方式 B：只修文字**

直接编辑 `data/artists/part-NN-x.json`（按原顺序的分片），然后重跑 `merge.py` + `build_db.py`。
`merge.py` 会以 `roster.json` 为准校正 `id/name/zh/birth/death/country/region/period/movement/mediums`
九个字段，因此分类字段永远不会有分歧。

**方式 C：只补图版**

往 `assets/img/<艺术家id>/w1.jpg … w5.jpg` 放入图片，并在 `data/images.json` 中对应位置填上
`{"img":"assets/img/<id>/w1.jpg","museum":"…","link":"…"}`，再跑 `build_db.py`。

---

## 七、检索能力

| 维度 | 说明 |
|---|---|
| 关键词 | 一次输入、多词与运算，命中姓名（中/英）、流派、时期、地区、媒介、国别、一句话定位、代表作名 |
| 时期 | 时期长卷可视化筛选，或在筛选条中多选 |
| 地区 | 9 大地区多选 |
| 流派 | 60+ 流派标签多选，默认展示高频项、可展开全部 |
| 媒介 | 16 类媒介多选 |
| 排序 | 年代升/降序、中文名、英文名、图版数量 |
| 链接 | 筛选状态实时写入 URL hash，可复制分享；从详情页返回会还原筛选状态 |

快捷键：`/` 聚焦搜索框，`Esc` 关闭灯箱。

---

## 八、依赖

站点本身**零依赖**（原生 HTML/CSS/JS）。

数据加工脚本需要 Python 3.9+；抓图与图像压缩需要 `requests`、`Pillow`：

```bash
python -m venv .venv
.venv/Scripts/pip install requests Pillow
```

---

## 九、说明

本库为研究与检索工具，史实以通行艺术史文献为准；当学界存在分歧时，在「争议与多元评价」
一部分并列呈现不同观点。图版用于研究与教育用途，版权归各馆藏机构或权利人所有。
