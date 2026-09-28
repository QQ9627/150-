# -*- coding: utf-8 -*-
import json

ROOT = "C:/Users/JNPYY/WorkBuddy/2026-09-27-19-27-34/artists-db/data/artists/"
FILES = ["part-01-a.json", "part-01-b.json", "part-01-c.json"]

# 元数据修正（必须照抄 batch-01.json）
MOVE_FIX = {
    "pieter-bruegel-the-elder": "北方文艺复兴",
    "leonardo-da-vinci": "盛期文艺复兴",
}

# works 子字段追加（仅 background/innovation/significance，皆以「」中文引号）
WORK_ADD = {
    "masaccio": {
        "The Tribute Money": {
            "background": "此画位于布兰卡奇礼拜堂右墙，与《洗礼》等同壁组画，自然光统一取自画面左上方，令群像体积连贯。",
            "innovation": "他参照多纳泰罗浮雕的单点透视，使税吏身影退入远景，人物如雕塑般立于地面而非漂浮。",
            "significance": "被视为壁画从哥特平面转向『亲眼所见的真实』的转折点，直接影响利皮、吉兰达约与达·芬奇。",
        },
        "The Expulsion from the Garden of Eden": {
            "background": "绘于布兰卡奇礼拜堂入口上方，与《亚当夏娃被造》相对，是早期文艺复兴极少以裸体情绪著称的壁画。",
            "innovation": "他舍弃装饰，用斜射光与肌肉转折表现羞耻与痛苦，夏娃掩面张口的姿态异常真实而克制。",
            "significance": "米开朗基罗曾临摹此作，其人体悲怆感预示了西斯廷天顶中『堕落后』的绝望情绪。",
        },
        "Holy Trinity": {
            "background": "为佛罗伦萨新圣母大殿的丧葬礼拜堂而作，画面嵌于建筑壁龛，借真实拱顶错觉向纵深延伸。",
            "innovation": "以布鲁内莱斯基式单点透视构筑『可见的神圣剧场』，骨灰瓮上的骷髅题字警示尘世生命无常。",
            "significance": "是西方艺术首件完整运用数学透视的壁画代表作，成为阿尔贝蒂《论绘画》的视觉范本。",
        },
    },
    "rogier-van-der-weyden": {
        "The Descent from the Cross": {
            "background": "约1435年为鲁汶弩手行会所作，后入西班牙，今藏马德里普拉多，是尼德兰祭坛画的标杆。",
            "innovation": "他以浅浮雕式压缩空间与极度拉长的人体，把哀恸凝成近乎装饰性的情感图案。",
            "significance": "其下垂基督的S形体态深远影响德国与西班牙绘画，成为全欧模仿的『下十字架』范式。",
        },
        "The Last Judgment": {
            "background": "为勃艮第博讷济贫院（主宫医院）议事厅所作翼板，与中板《最后审判》共同陈设。",
            "innovation": "他以金底分隔善恶两界，将米开朗基罗式体量预演于北方细密笔法之中。",
            "significance": "把道德说教化为可触的视觉剧场，确立北方『审判』题材的构图与色彩传统。",
        },
        "The Magdalen Reading": {
            "background": "属其晚年私密性单幅板画，描绘抹大拉的马利亚于静室读经，背景以绿帘与器物界定。",
            "innovation": "他以日常器物与侧光营造冥想氛围，使宗教人物获得市民生活的温度。",
            "significance": "体现凡·德·维登将大型祭坛语汇转为私人 devotion 图像的转型，启发布料斯等后继。",
        },
    },
    "sandro-botticelli": {
        "The Birth of Venus": {
            "background": "约1485年为美第奇圈层所作，以蛋彩绘于布面，今藏乌菲齐，题材取自波利齐亚诺的诗。",
            "innovation": "他以线条而非体积塑形，维纳斯立于贝壳随风飘至，发丝与衣袂皆作装饰性韵律。",
            "significance": "是新柏拉图主义『神圣之爱』的视觉宣言，也是西方艺术首幅大幅异教神话题材布面画。",
        },
        "Primavera": {
            "background": "约1480年为美第奇别墅所作，人物逾九，以橙树丛为背景，布满可辨识的花卉近百种。",
            "innovation": "他以平面化群像取代透视深度，用舞姿般的重复线条组织神话叙事。",
            "significance": "被视为文艺复兴最复杂的寓言画之一，串联奥维德与新柏拉图主义的爱之谱系。",
        },
        "The Mystic Nativity": {
            "background": "约1500年绘于佛罗伦萨动荡之年，是唯一有他亲笔希腊文题记的板画，今藏伦敦国家美术馆。",
            "innovation": "他以火焰般金色漩涡表现天使环舞，把末世欢庆压缩进温柔的乡土场景。",
            "significance": "反映萨伏那洛拉布道后他的精神转向，是其晚期风格由优雅转神秘的见证。",
        },
    },
    "hieronymus-bosch": {
        "The Garden of Earthly Delights": {
            "background": "约1490至1510年间为某贵族所作三联画，今藏马德里普拉多，是其最庞大也最费解之作。",
            "innovation": "他以玻璃微缩般的奇想生物与透明球体构筑不存在的乐园，透视服从梦境而非理性。",
            "significance": "被视为中世纪末与文艺复兴交界最奇特的想象档案，至今无人能确解其全部象征。",
        },
        "The Temptation of St. Anthony": {
            "background": "约1505年为葡萄牙国王曼努埃尔一世所作，三联画碎片今分藏里斯本与美国数馆。",
            "innovation": "他把诱惑化为机械与有机杂交的怪物，火光与冰面并置以凸显圣者的孤立。",
            "significance": "其妖异意象深刻影响勃鲁盖尔与勃鲁盖尔之后的佛兰德斯怪诞传统。",
        },
        "The Haywain Triptych": {
            "background": "约1490至1510年所作，左翼伊甸、中翼干草车、右翼地狱，构图对应俗语『干草 Massacre』。",
            "innovation": "他以满载干草的大车象征世人对虚荣的争夺，群像如蚁附于虚妄之上。",
            "significance": "把道德讽喻推向全景式荒诞，是北方『人间愚行』母题的奠基性图像。",
        },
    },
    "raphael": {
        "The School of Athens": {
            "background": "1509至1511年为教皇尤利乌斯二世的书斋（署名厅）所作湿壁画，今藏梵蒂冈使徒宫。",
            "innovation": "他以拱券透视统合数十哲人，柏拉图与亚里士多德居中，以手势分示理念与经验。",
            "significance": "被誉为盛期文艺复兴空间与人文理想的集大成，至今是『哲学』的视觉代名词。",
        },
        "Sistine Madonna": {
            "background": "约1512年为皮亚琴察圣西斯托修道院所作，今藏德累斯顿历代大师画廊。",
            "innovation": "他以帷幕拉开般的构图把圣母自云端迎入人间，帷幕下两个小天使成为后世图标。",
            "significance": "将神圣庄严与温柔母性结合，是北方与南方均奉为范本的圣母像。",
        },
        "The Marriage of the Virgin": {
            "background": "1504年为卡斯特洛城圣济安略堂所作，直接回应佩鲁吉诺的同题构图。",
            "innovation": "他以更严谨的集中式透视与圆庙背景压过老师，确立个人空间语言。",
            "significance": "标志其脱离佩鲁吉诺工坊、形成盛期清晰典雅风格的公开宣言。",
        },
        "The Transfiguration": {
            "background": "1516至1520年为其最后一作，未竟而殁，今藏梵蒂冈博物馆，分上下两景。",
            "innovation": "他以上景基督升空、下景门徒慌乱的对角动势，把神迹与人间疾苦并置。",
            "significance": "其未完成状态由门徒续完，被视为连接盛期文艺复兴与样式主义的桥梁。",
        },
    },
    "titian": {
        "Assumption of the Virgin": {
            "background": "1516至1518年为威尼斯弗拉里教堂主祭坛所作，置于高坛，观者需仰视其升腾。",
            "innovation": "他以暖色垂直光柱把祭坛变为『上升的剧场』，红蓝对比强化圣母的视觉中心。",
            "significance": "威尼斯画派里程碑，证明色彩可独自承担宗教巨制的庄严，无需雕塑式素描。",
        },
        "Bacchus and Ariadne": {
            "background": "1522至1523年为费拉拉公爵阿方索一世『诗性神话』系列所作，今藏伦敦国家美术馆。",
            "innovation": "他以『跃动瞬间』与高饱和蓝红对置，把神话变为可触的肉体狂欢。",
            "significance": "文艺复兴神话画的色彩巅峰，其群青被伦敦国家美术馆专门保护以维持原貌。",
        },
        "Venus of Urbino": {
            "background": "1534年为乌尔比诺公爵圭多巴尔多二世所作，今藏佛罗伦萨乌菲齐美术馆。",
            "innovation": "他把『神性维纳斯』移入世俗卧房，并以正视眼神打破观者与图像的界限。",
            "significance": "西方卧姿维纳斯的原型，引发数世纪关于『神圣还是情色』的争论与仿作。",
        },
    },
    "parmigianino": {
        "Madonna of the Long Neck": {
            "background": "1534至1540年未竟之作，今藏乌菲齐，其狭长比例与 vacated 右下方空间显刻意留白。",
            "innovation": "他以不合解剖的修长颈与指，把优雅推至『反自然』的样式主义极致。",
            "significance": "样式主义圣母像的宣言式作品，其未完成感反成刻意的美学姿态。",
        },
        "Self-Portrait in a Convex Mirror": {
            "background": "1524年作于凸面镜自照，今藏维也纳艺术史博物馆，是早期自画像的奇品。",
            "innovation": "他据镜面变形拉长右手与背景，使写实服从于镜中真实的几何。",
            "significance": "被曼努埃尔·巴尔加斯·略萨等文人反复书写，是西方自画像传统的转折点。",
        },
        "Cupid Making His Bow": {
            "background": "约1530年代所作，以拉长的肢体与冷调光泽描绘小爱神制弓，今藏伦敦国家美术馆。",
            "innovation": "他以蛇形线条与光滑釉感皮肤，把神话题材转化为纯粹的形式优雅。",
            "significance": "体现样式主义『以美为美』的自律倾向，预示后来枫丹白露派的装饰趣味。",
        },
    },
    "pieter-bruegel-the-elder": {
        "The Tower of Babel": {
            "background": "1563年作，今藏维也纳艺术史博物馆，其螺旋巨塔据罗马斗兽场想象而绘。",
            "innovation": "他以巨石错位与工匠蚁群表现人类骄傲的徒劳，透视故意失调以显混乱。",
            "significance": "是北方最著名的圣经寓意画，把『巴别』化为对权欲与语言分裂的讽喻。",
        },
        "The Hunters in the Snow": {
            "background": "1565年属『月度』系列之一，今藏维也纳，描绘冬日归猎的村落远景。",
            "innovation": "他以高视点对角线统领雪原，点景人物与冰面嬉戏填满辽阔的冷峻空间。",
            "significance": "西方风景画中最早以季节与日常劳作为题的杰作，启发布雷哲尔风景传统。",
        },
        "The Peasant Wedding": {
            "background": "约1567年作，今藏维也纳，以板凳宴席与搬运汤盆的仆人定格乡村婚宴。",
            "innovation": "他以平视群像与无中心叙事，把农民视作值得郑重描绘的主体而非笑料。",
            "significance": "奠定佛兰德斯风俗画传统，使其超越宗教题材成为独立的视觉类型。",
        },
        "The Triumph of Death": {
            "background": "约1562年所作巨幅板画，今藏马德里普拉多，以骷髅大军横扫众生。",
            "innovation": "他以全景式屠杀与骨碾磨坊，把死亡表现为无差别的自然法则而非惩罚。",
            "significance": "在尼德兰战乱阴影下，是北方最阴郁的末世图景，承继博斯又更世俗化。",
        },
    },
    "el-greco": {
        "The Burial of the Count of Orgaz": {
            "background": "1586年为托莱多圣多默堂所作，描绘1288年善人伯爵下葬时圣徒自天而降。",
            "innovation": "他以上下两界分割：下界写实黑衣群像、上界扭曲天界，空间被信仰而非透视统合。",
            "significance": "是其西班牙成熟期代表作，把威尼斯色彩、样式主义形体与神秘主义熔于一炉。",
        },
        "View of Toledo": {
            "background": "约1596至1600年所作，今藏纽约大都会，是西方最早以天气与光为母题的城景之一。",
            "innovation": "他以翻卷乌云与绿金对比把托莱多绘成被风暴洗礼的灵性之地，地形故意移位。",
            "significance": "被视为风景作为情绪载体的先驱，直接影响19世纪浪漫派与表现派。",
        },
        "The Nobleman with his Hand on his Chest": {
            "background": "约1580年代所作，今藏马德里普拉多，人物身份未明，以手势示诚。",
            "innovation": "他以拉长身形与暗底侧光，把肖像化为『灵魂姿态』而非身份记录。",
            "significance": "确立西班牙『手势肖像』范式，深远影响委拉斯开兹早期的肃穆基调。",
        },
        "The Disrobing of Christ": {
            "background": "约1577至1579年为托莱多主教座堂圣衣室所作，描绘基督被剥衣前的对峙。",
            "innovation": "他以放射红衣的基督为唯一亮源，周遭凶徒面目灰暗，光即神学。",
            "significance": "是其宗教戏剧性的极致，把样式主义拉长形体用于集体情绪的聚焦。",
        },
    },
}

EVO_ADD = {
    "masaccio": {
        "early": "他早年受乔托与多纳泰罗启蒙，在佛罗伦萨习得以体块与光影塑形，摒弃国际哥特的纤巧。",
        "middle": "1420年代他与马索利诺合作布兰卡奇礼拜堂，独立承担主要场景，确立单点透视的壁画语言。",
        "late": "他短暂赴罗马参与圣克莱门特教堂湿壁画，把托斯卡纳体量法带入教廷，惜27岁早逝未竟其业。",
    },
    "rogier-van-der-weyden": {
        "early": "他师承坎平，在图尔奈习得精确细密与室内光，后于布鲁塞尔获匠师资格并任市画师。",
        "middle": "1430至1450年代他以《下十字架》成名，受勃艮第宫廷委托，声誉远播法、意、西。",
        "late": "晚年他经营大型工坊，向全欧输出样稿，其哀婉风格被视作北方『情感国际式』的轴心。",
    },
    "sandro-botticelli": {
        "early": "他师从利皮，习得柔润线条，又受波提切利家族与美第奇文人圈熏陶，偏重诗性题材。",
        "middle": "1480年代他以《春》与《维纳斯的诞生》达于优雅巅峰，成为新柏拉图主义视觉代言。",
        "late": "1490年代后萨伏那洛拉布道使其转向虔修，《神秘的诞生》显出其风格由甜美转向内省。",
    },
    "hieronymus-bosch": {
        "early": "他生于斯海尔托亨博斯，承佛兰德斯细密传统，在家族工坊习得怪诞生物与象征语汇。",
        "middle": "1490至1510年代他作《人间乐园》等三联画，以私人委托避开行会束缚，想象无拘。",
        "late": "晚年他受托为葡萄牙王室作画，其噩梦式图像在北方广为传摹，身后声望不坠。",
    },
    "raphael": {
        "early": "他出于翁布里亚佩鲁吉诺工坊，习得以柔和透视与清明构图，早期圣母已显个人温润。",
        "middle": "1508年应召罗马后入教廷，以署名厅系列征服尤利乌斯二世，成为盛期核心。",
        "late": "1510年代他掌巨型工坊并兼圣彼得工程，风格转雄健，未竟的《变容》预示样式主义。",
    },
    "titian": {
        "early": "他少年入贝利尼工坊，又与乔尔乔内共事，习威尼斯色彩法，早年平滑而诗性。",
        "middle": "1520至1545年他以神话与肖像称雄，受封伯爵并服务查理五世，声名跨出意大利。",
        "late": "1545年后赴罗马受封，晚年笔触松放、色层直接，成为19世纪画家追摹的『现代性』先声。",
    },
    "parmigianino": {
        "early": "他出于帕尔马，幼年习柯雷乔的柔光与晕染，早作已显修长优雅的偏好。",
        "middle": "1524年罗马之行亲见拉斐尔与米开朗基罗，翌年作凸面镜自画像震动艺坛。",
        "late": "1530年代定居博洛尼亚与帕尔马，专攻样式主义圣母与神话题材，未及四十而卒。",
    },
    "pieter-bruegel-the-elder": {
        "early": "他疑师彼得·库克，1550年代游意大利临摹阿尔卑斯景，归后转向佛兰德斯乡村母题。",
        "middle": "1560年代作《巴别塔》《雪中猎人》，以全景风景与农民风俗确立独立绘画类型。",
        "late": "晚年他作《盲人的寓言》《死神之凯旋》，讽喻愈发尖锐，把北方风俗推向思想深度。",
    },
    "el-greco": {
        "early": "他生于克里特，习拜占庭圣像，约1567年赴威尼斯入提香圈，转向色彩性绘画。",
        "middle": "1570年赴罗马接触样式主义，1577年定居托莱多，获教会委托步入成熟。",
        "late": "1590年代后其形体愈拉长、光愈主观，以《奥尔加斯伯爵的葬礼》成就西班牙式神秘主义。",
    },
}

STMT_ADD = {
    "masaccio": "他强调绘画应如雕塑般『可环绕的真实』，把科学透视与人体研究奉为再现信仰的基石。",
    "rogier-van-der-weyden": "他主张情感须经精确形式传达，以克制而高昂的哀恸使宗教图像兼具戏剧与神圣。",
    "sandro-botticelli": "他在与菲奇诺等新柏拉图主义者交往中，视美为通向上帝的阶梯，线即理念之迹。",
    "hieronymus-bosch": "他以图像为道德镜鉴，借不可名状的幻象警示欲望与愚行，拒绝给观众廉价安慰。",
    "raphael": "他承认为『集众长于一身』，把达·芬奇的柔和与米开朗基罗的力统一于清明秩序。",
    "titian": "他与阿里奥斯托等文人交往，主张绘画应以色彩（colorito）先于素描（disegno）取胜。",
    "parmigianino": "他把优雅奉为最高德性，刻意偏离自然比例以逼近『观念中的美』而非眼见的真。",
    "pieter-bruegel-the-elder": "他以农民与风景为正经题材，拒绝神话架空，使佛兰德斯日常获得史诗般的重量。",
    "el-greco": "他视绘画为灵性经验的载体，形体拉长非为怪异，而是为显现肉眼未见的天界真实。",
}

MOTIFS_ADD = {
    "masaccio": "母题含税吏、逐出伊甸、圣三位一体与透视拱顶，皆围绕『真实空间中的神圣在场』。",
    "rogier-van-der-weyden": "母题含下十字架、审判、读经抹大拉，统一于哀恸、虔诚与精确的北方细密。",
    "sandro-botticelli": "母题含维纳斯、春之群像、星座花卉与诵读天使，皆服务新柏拉图的爱与美。",
    "hieronymus-bosch": "母题含玻璃球体、杂交怪物、干草车与火焰，构成欲望、愚行与末日的象征辞典。",
    "raphael": "母题含哲人手势、帷幕圣母、圆庙婚礼，统一于人文理性、优雅与建筑式秩序。",
    "titian": "母题含圣母升天、酒神、卧姿维纳斯与君主肖像，皆以色彩与肉体感为共同语言。",
    "parmigianino": "母题含长颈圣母、凸镜自照、制弓小爱神，皆凸显拉长形体与冷釉般的样式主义美。",
    "pieter-bruegel-the-elder": "母题含巴别塔、雪原猎人、婚宴与骷髅大军，把圣经与民俗并置为人生讽喻。",
    "el-greco": "母题含自天而降的圣徒、风暴城景、手势贵族，统一于拉长形体与主观之光的神秘。",
}

# el-greco 过短的 style[4] 修正（原 27 字）
ELGRECO_STYLE4 = "光的处理：他以主观冷光令基督红衣成唯一亮源，周遭灰暗，使光本身承担神学叙事。"

for fn in FILES:
    path = ROOT + fn
    d = json.load(open(path, encoding="utf-8"))
    for e in d:
        aid = e["id"]
        if aid in MOVE_FIX:
            e["movement"] = MOVE_FIX[aid]
        if aid in WORK_ADD:
            wa = WORK_ADD[aid]
            for w in e["works"]:
                if w["titleEn"] in wa:
                    add = wa[w["titleEn"]]
                    for fld in ("background", "innovation", "significance"):
                        if fld in add:
                            w[fld] = w[fld].rstrip("。") + add[fld]
        if aid in EVO_ADD:
            for kk, txt in EVO_ADD[aid].items():
                if isinstance(e.get("evolution"), dict) and kk in e["evolution"]:
                    e["evolution"][kk] = e["evolution"][kk].rstrip("。") + txt
        if aid in STMT_ADD:
            e["statement"] = e["statement"].rstrip("。") + STMT_ADD[aid]
        if aid in MOTIFS_ADD:
            e["motifs"] = e["motifs"].rstrip("。") + MOTIFS_ADD[aid]
        if aid == "el-greco" and isinstance(e.get("style"), list) and len(e["style"]) > 4:
            e["style"][4] = ELGRECO_STYLE4
    json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("written", fn)
print("OK")
