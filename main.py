# -*- coding: utf-8 -*-

import pygame
import sys
import os
import random
import pickle
import array
import math
import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path


if getattr(sys, 'frozen', False):
    # PyInstaller打包后：资源文件在临时解压目录（sys._MEIPASS），
    # 但存档要放在exe旁边，不能放临时目录——否则关闭程序就被清空，存档会丢
    _GAME_DIR = Path(sys._MEIPASS)
    _SAVE_DIR = Path(sys.executable).parent
else:
    _GAME_DIR = Path(__file__).parent
    _SAVE_DIR = Path(os.environ['ANDROID_PRIVATE']) if 'ANDROID_PRIVATE' in os.environ else _GAME_DIR
SAVE_FILE = _SAVE_DIR / 'floor23_save.pkl'



W, H     = 480, 854
TILE     = 52
MAP_COLS = 9
MAP_ROWS = 9
MAP_X0   = (W - MAP_COLS * TILE) // 2
MAP_Y0   = 95
LOG_Y0   = MAP_Y0 + MAP_ROWS * TILE
LOG_H    = H - LOG_Y0

C_BG     = (18,  18,  32)
C_WALL   = (55,  55,  80)
C_FLOOR  = (38,  38,  58)
C_PLAYER = (255, 220,  80)
C_ENEMY  = (220,  60,  60)
C_ITEM   = (100, 200, 100)
C_KEY_B  = ( 80, 140, 255)
C_KEY_R  = (255,  80,  80)
C_KEY_Y  = (255, 200,  50)
C_DOOR_B = ( 60, 100, 200)
C_DOOR_R = (180,  50,  50)
C_DOOR_Y = (200, 150,  30)
C_STAIRS = (180, 160, 255)
C_NPC    = (100, 220, 200)
C_SHOP   = (255, 165,   0)
C_TEXT   = (220, 220, 240)
C_GOLD   = (255, 200,  50)
C_HP     = (255,  80,  80)
C_ATK    = (255, 140,  60)
C_DEF    = ( 80, 180, 255)
C_PANEL  = ( 28,  28,  45)
C_LOG_BG = ( 22,  22,  38)
C_WARN   = (255, 100,  50)
C_BOSS   = (200,  50, 200)
C_RAGE   = (255,  60,  20)
C_SKILL  = (100, 240, 160)

ENEMIES = {
    1: ("本科困惑者",  50,   10,   2,   5, C_ENEMY),
    2: ("刁钻同学",   100,   18,   5,  15, C_ENEMY),
    3: ("嫉妒竞争者", 200,   30,  12,  30, (200, 80, 80)),
    4: ("苛刻审稿人", 400,   50,  18,  60, (210, 60, 60)),
    5: ("严格导师",   700,   75,  25, 120, (220, 50, 50)),
    6: ("论文委员",  1200,  100,  35, 200, (230, 40, 40)),
    7: ("资深教授",  2000,  130,  50, 350, (200, 30, 80)),
    8: ("主任委员",  3500,  180,  70, 600, (180, 20,100)),
    9: ("答辩主席",  8000,  250, 100,2000, C_BOSS),
}

ITEMS = {
    'c': ("咖啡",       "+100精力",  100,  0,  0,   0, C_ITEM),
    'e': ("能量饮料",   "+300精力",  300,  0,  0,   0, C_ITEM),
    'g': ("知识结晶",   "+50知识点",   0,  0,  0,  50, C_GOLD),
    'G': ("大量知识点", "+200知识点",  0,  0,  0, 200, C_GOLD),
    'w': ("学术武器",   "+10能力",     0, 10,  0,   0, C_ATK),
    'W': ("顶级武器",   "+25能力",     0, 25,  0,   0, C_ATK),
    's': ("防压盾",     "+8抗压",      0,  0,  8,   0, C_DEF),
    'S': ("顶级盾",     "+20抗压",     0,  0, 20,   0, C_DEF),
    'p': ("大补丸",     "+500精力",  500,  0,  0,   0, C_ITEM),
}

SHOP_ITEMS = [
    ("精力上限+200", "hp_max", 200, 200, 0),                                                   
    ("精力上限+500", "hp_max", 500, 500, 0),
    ("学术能力+5",   "atk",     5,  150, 5),
    ("抗压力+5",     "def",     5,  150, 5),
    ("学术能力+15",  "atk",    15,  400, 3),
    ("抗压力+15",    "def",    15,  400, 3),
]

NPC_DIALOGS = {
    'A': ["欢迎来到23层科研大厦！",
          "收集蓝钥匙、红钥匙、黄钥匙，用来开对应颜色的门。",
          "击败23层答辩主席即可通关！"],
    'B': ["前面的审稿人很强，建议先提升学术能力。", "加油！"],
    'C': ["你已到达高层，答辩主席就在23层。", "相信自己，你可以的！",
          "记得在商店升级精力上限，这很关键！"],
}

NPC_E_DIALOGS = {
    'kind':   ["导师把你叫到办公室，关上了门。",
               "「你这两年学得很好，进步很大。」",
               "「但我觉得你应该去更大的舞台——」",
               "「我已经帮你联系了几位外校的老师。」",
               "「去闯一闯吧，我支持你。」"],
    'pro':    ["导师放下论文，认真地看着你：",
               "「我一直在等一个合适的时机——」",
               "「我早就想把你培养成我的博士生。」",
               "「你是我带过最有潜力的学生之一。」"],
    'social': ["聚餐结束后，导师单独留下你。",
               "「你知道吗，我很少主动留学生读博。」",
               "「但你不一样——人脉好，又踏实。」",
               "「我希望你留下来，我会全力支持你。」"],
    'evil':   ["导师突然叫你到办公室，笑得让你不安。",
               "「最近表现还行，」他说，",
               "「你还有点利用价值——」",
               "「先把这个项目做完再说毕业的事。」",
               "心里某个东西，彻底碎掉了。"],
}

FLOOR_DIALOGS = {
    'kind': {
        2:  ["第一次组会——",
             "你发言时声音微微颤抖。",
             "导师在会上帮你圆场：",
             "「没关系，慢慢说，大家都这样过来的。」"],
        6:  ["投稿失败之夜。",
             "审稿人评语像一盆冷水浇下来。",
             "凌晨，导师发来消息：",
             "「来，我帮你分析问题。」",
             "那一夜，你没有那么孤单。"],
        12: ["通知：一区论文被接收！",
             "导师拍着你的肩膀：",
             "「走，今天去吃顿好的。」",
             "这是你来读研以来最轻松的一天。"],
        20: ["答辩前夜，导师发来消息：",
             "「这两年辛苦你了。」",
             "「其实我只是帮你挡了一下风，」",
             "「剩下的路，都是你自己走的。」",
             "明天，你将站在23层的门前。"],
    },
    'pro': {
        2:  ["第一次组会汇报文献。",
             "导师当场指出你PPT的三处逻辑错误。",
             "散会后私下找你：",
             "「回去想清楚，明天来找我。」"],
        6:  ["稿件被拒。",
             "导师发消息：「我知道了，来，一起分析。」",
             "两人对着审稿意见研究到深夜，",
             "「这不是失败，是下篇论文的起点。」"],
        12: ["项目重大突破。",
             "导师站在你身边，看完了全部数据。",
             "「这个成果，是你自己做出来的。」",
             "他说得很平静，但你知道这份认可有多重。"],
        20: ["导师罕见地找你谈心，关上了门。",
             "「你已经准备好了，」他说，",
             "「博士的路很长，但你能走完。」",
             "沉默了一会儿：",
             "「明天——证明给他们看。」"],
    },
    'social': {
        2:  ["第一次组会——",
             "师兄提前悄悄给你打了眼色，让你别紧张。",
             "导师笑着向大家介绍你：",
             "「好好带他/她，都是自己人。」"],
        6:  ["稿件被拒，你打电话给导师。",
             "「被拒很正常，」导师说，",
             "「我认识那本期刊的编委，我来协调。」",
             "挂掉电话，你感觉没那么崩溃了。"],
        12: ["论文录用！",
             "师兄师姐们一起跑来恭喜你，",
             "导师笑着说：",
             "「这就是团队的力量。」"],
        20: ["师兄师姐临时组了个小聚会为你送行。",
             "导师举起杯子：",
             "「不管你去哪，都是我们组的人。」",
             "「明天答辩，别紧张，我们都在。」"],
    },
    'evil': {
        2:  ["第一次组会。",
             "导师当着全组人的面说：",
             "「这个结果水平太差，怎么报出来的？」",
             "你在组内抬不起头。"],
        6:  ["稿件被拒，你鼓起勇气告诉导师。",
             "导师冷冷地说：",
             "「这种水平也敢投？重写，一周内给我。」",
             "你独自对着屏幕发呆到天亮。"],
        12: ["失眠第十三天。",
             "焦虑感压在胸口，快要无法呼吸。",
             "导师冷眼旁观：「软弱，太软弱了。」",
             "你想起了当初决定读研时的自己……"],
        20: ["答辩前夜。",
             "导师没有打来电话，没有任何祝福。",
             "只有一条消息：「明天别迟到。」",
             "你一个人坐在宿舍，翻着这几年的笔记。",
             "那些熬过来的每一个夜晚，",
             "都是你的铠甲。"],
    },
}

FLOOR_AMBIENT = {
    'kind': {
        0:  "新生报到——导师暗中观察着你的一举一动。",
        1:  "实验室走廊——师兄师姐友好地招呼你。",
        3:  "基础技能训练——导师低调地在背后帮了你一把。",
        4:  "开始熟悉节奏——导师不动声色地观察着你。",
        5:  "第一篇论文准备投稿——导师帮你一遍遍修改措辞。",
        7:  "大量阅读文献——导师指导你整理文献的方法。",
        8:  "小实验有了进展——导师给予肯定，让你继续做。",
        9:  "冲刺一区论文——导师全力配合你的进度安排。",
        10: "准备会议报告——导师帮你反复演练，直到自信为止。",
        11: "一区论文正在审稿——等待的日子最难熬。",
        13: "参与重要项目——导师把关键任务亲手交给了你。",
        14: "压力开始积累——导师主动问：「最近状态怎么样？」",
        15: "多项成果积累——导师认可你的进步。",
        16: "准备毕业材料——导师帮你认真整理每一份文件。",
        17: "导师认真撰写推荐信——一字一句，不马虎。",
        18: "导师主动帮你联系外校——发邮件、打电话，亲力亲为。",
        19: "导师的最后嘱托：「外面的路你要自己走，但我一直在。」",
        20: "顺利通过毕业答辩——温暖送别。",
        21: "去外校名校读博——圆满结局。",
    },
    'pro': {
        0:  "入学谈话——导师直接说：「我要求高，但我会全力培养你。」",
        1:  "熟悉实验室——没有多余的话，直接开始工作。",
        3:  "高压基础训练——导师陪你熬了第一个通宵。",
        4:  "初步获得认可——导师说：「你还算能吃苦。」",
        5:  "第一篇论文投稿——导师严格要求，改了七遍才点头。",
        7:  "重要项目启动——导师把核心任务交给你，没有多余客套。",
        8:  "项目和程序有进展——导师给出专业反馈，指出改进方向。",
        9:  "中期考核——通过。导师开始对你进行重点培养。",
        10: "项目重大突破——实验室里难得出现了笑声。",
        11: "论文投稿中——导师帮你精打细磨每一个细节。",
        13: "同时推进多个项目——导师给你更多资源和权限。",
        14: "高压导致倦怠——导师察觉，主动关心你的状态。",
        15: "多项成果爆发——导师表扬：「不错。」（这已经很难得了）",
        16: "毕业考核——导师全力支持你度过这一关。",
        17: "导师正式提出：「我可以给你更好的资源和平台。」",
        18: "留在导师身边读博——新的征程，熟悉的高压节奏。",
        19: "规划博士方向——导师给你画出了清晰的路线图。",
        20: "高压成长，导师认可结局。",
        21: "博士之路正式开启——未来很长，充满可能。",
    },
    'social': {
        0:  "导师宴请——在小聚会上，你认识了七八位业界前辈。",
        1:  "熟悉实验室——师兄师姐主动带你参观，氛围融洽。",
        3:  "获得资源支持——导师说：「需要什么资源，直接来找我。」",
        4:  "融入组内——师兄师姐帮你少走了很多弯路。",
        5:  "投稿第一篇论文——导师帮你联系期刊，走了绿色通道。",
        7:  "参加更多学术活动——导师带你认识了更多业界人士。",
        8:  "开始自我施压——导师说：「慢慢来，我帮你协调。」",
        9:  "小成果——导师肯定你的努力，师兄师姐一起鼓励你。",
        10: "新一轮论文投稿——导师帮你推荐给熟悉的编辑。",
        11: "会议报告——师兄师姐帮你反复准备，不让你一个人扛。",
        13: "参与重要项目——导师协调资源，让你专注做研究。",
        14: "压力增大——导师积极协调，帮你疏通各方关系。",
        15: "多项成果——组内互助氛围让你感到不孤单。",
        16: "毕业考核——导师和师兄师姐全力帮你度过这一关。",
        17: "导师正式提出留你读博：「我可以继续给你资源。」",
        18: "留在导师身边读博——熟悉的人，新的挑战。",
        19: "规划博士方向——导师温暖支持，师兄师姐送上祝福。",
        20: "顺利毕业——组内温暖送别。",
        21: "温暖现实结局，博士之路正式开启。",
    },
    'evil': {
        0:  "入学即PUA——导师说你很差、很笨。严重自卑从第一天开始。",
        1:  "你的第一个成果被导师署上了第一作者。「这是我的项目。」",
        3:  "要求每天工作到凌晨两三点——完全不关心你的身体和精神。",
        4:  "开始怀疑自己为什么选择读研。「别人都比你强。」",
        5:  "你的实验数据和想法被据为己有，完全不给你署名。",
        7:  "故意不让你发论文，卡你的毕业进度。你活在延毕的恐惧中。",
        8:  "导师偶尔给点小恩小惠——只是为了让你继续卖命。",
        9:  "你开始真正恨上这个导师。他完全不在乎你的感受。",
        10: "当着外校老师和学生的面羞辱你，完全不在乎你的尊严。",
        11: "你正在做的项目全部被抢走。「敢反抗就让你毕不了业。」",
        13: "你和导师彻底撕破脸。「敢闹就让你学术生涯完蛋。」",
        14: "人生最黑暗的时期——几乎想放弃读研。",
        15: "导师突然对你好一点——只是为了让你继续干活到毕业。",
        16: "继续压榨你做项目和论文，说「你还有利用价值」。",
        17: "毕业材料被导师故意卡住，你处于极度焦虑中。",
        18: "你开始收集证据，准备反击或举报。导师察觉到了变化。",
        19: "最终对决——导师露出最恶毒、最冷血的一面。",
        20: "「我从来没想过你能读博。」冷血宣告。",
        21: "没有体面，没有帮助——继续压榨或直接甩掉。",
    },
}

                                                           
WIN_ENDINGS = {
    'kind': {
        'title': "答辩通过！圆满结局",
        'color': (80, 255, 120),
        'story': [
            "「你通过了。」导师在台下轻声说。",
            "毕业典礼上，他握着你的手：",
            "「去外校读博，记得偶尔回来看看。」",
            "「我只是帮你挡了一下风——」",
            "「剩下的路，都是你走出来的。」",
        ],
        'epilogue': "去更大的舞台，带着这两年的一切。",
    },
    'pro': {
        'title': "答辩通过！高压成长结局",
        'color': (80, 160, 255),
        'story': [
            "答辩结束，导师走过来，只说了一句：",
            "「我没看错人。」",
            "你选择留在导师身边读博。",
            "「博士的路很长，」他说，",
            "「但我会陪你走完它。」",
        ],
        'epilogue': "熟悉的高压，真实的认可，新的征程。",
    },
    'social': {
        'title': "答辩通过！温暖现实结局",
        'color': (255, 180, 60),
        'story': [
            "答辩通过，师兄师姐们在门口等着你。",
            "「终于出来了！」「恭喜！」",
            "导师笑着说：",
            "「留下来读博，我们继续。」",
            "有人脉，有团队，未来并不孤单。",
        ],
        'epilogue': "温暖是真实的，路也是真实的。",
    },
    'evil': {
        'title': "答辩通过……磨难结局",
        'color': (255, 120, 50),
        'story_normal': [
            "你通过了答辩。",
            "导师例行签了字，没有任何祝贺。",
            "你拿到学位证，独自离开了实验室。",
            "没有读博，没有未来规划。",
            "但——你活下来了，你走出来了。",
        ],
        'story_yanbi': [
            "你通过了答辩——延毕之后。",
            "导师依然没有任何表示。",
            "你带着满身的伤，走出了这栋楼。",
            "这不是圆满，但这是你的胜利。",
            "没有人能替你承受这些，是你自己扛过来的。",
        ],
        'epilogue_normal': "没有读博，没有未来规划，但这已经足够。",
        'epilogue_yanbi': "延毕，但没有被打倒。这已经是最好的结局。",
    },
}

                                                            
BOSS_INTROS = {
    'kind':   ["答辩委员会严肃入场...",
               "但你的善良导师在台下向你微笑点头。",
               "多年来的悉心指导，都化为此刻的力量。加油！"],
    'pro':    ["答辩委员会入场。",
               "你感到学术积累已足以应对一切挑战。",
               "这是你证明自己研究价值的时刻，全力一战！"],
    'social': ["答辩委员会入场。",
               "你悄悄和其中两位委员点了个头——",
               "多年积累的人脉，在此刻或许能发挥作用。"],
    'evil':   ["答辩主席缓缓走入会场...",
               "PPT、快递、接孩子、项目书、Excel录入...",
               "那些年受过的委屈，今天全部化为力量！决战！"],
}

                                                                 
ROUTE_SKILLS = {
    'kind':   ("导师鼓励", "恢复30%精力上限，Q键每层一次"),
    'pro':    ("研究突破", "下次战斗学术+20，Q键每层一次"),
    'social': ("动用关系", "获得随机钥匙一把，Q键每层一次"),
    'evil':   ("摸鱼反击", "消耗50怒气跳过当前杂活，Q键每层一次"),
}

                                                                 
RANDOM_EVENTS = {
    'kind': [
        {'msg': "师兄分享了一篇珍稀文献！\n你熬夜读完，学术大涨。",           'hp':    0, 'atk': 5, 'def_': 0, 'gold':  0},
        {'msg': "组会气氛超好，导师当场夸你。\n信心大增，抗压+2，精力+80。",   'hp':   80, 'atk': 0, 'def_': 2, 'gold':  0},
        {'msg': "稿件返回——Minor Revision！\n意外惊喜，知识点+100。",         'hp':    0, 'atk': 0, 'def_': 0, 'gold':100},
        {'msg': "实验连失败三遍，原因不明。\n精力大损。",                          'hp': -200, 'atk': 0, 'def_': 0, 'gold':  0},
        {'msg': "导师推荐你去开学术会议！\n学术+3，知识点+60。",               'hp':    0, 'atk': 3, 'def_': 0, 'gold': 60},
    ],
    'pro': [
        {'msg': "导师凶信发来：「第三章全部重写。」\n精力严重损耗。",           'hp': -220, 'atk': 0, 'def_': 0, 'gold':  0},
        {'msg': "一个灵感爆发！思路全部打通。\n学术+8。",                          'hp':    0, 'atk': 8, 'def_': 0, 'gold':  0},
        {'msg': "代码跑三天终于出结果！\n知识点+120，成就感爆棚。",             'hp':    0, 'atk': 0, 'def_': 0, 'gold':120},
        {'msg': "导师让你跟进一个横向项目。\n精力-150，但涨了见识，学术+2。",   'hp': -150, 'atk': 2, 'def_': 0, 'gold':  0},
        {'msg': "你的方法被顶会引用了！\n抗压+4，知识点+60。",                  'hp':    0, 'atk': 0, 'def_': 4, 'gold': 60},
    ],
    'social': [
        {'msg': "师门聚餐大家很感激。\n抗压+3。",                   'hp':  -40, 'atk': 0, 'def_': 3, 'gold':  0},
        {'msg': "师兄悄悄把内部评审标准发给你！\n知识点+100。",                 'hp':    0, 'atk': 0, 'def_': 0, 'gold':100},
        {'msg': "师姐改格式，她引荐了外校大牛。\n学术+4。",                   'hp':    0, 'atk': 4, 'def_': 0, 'gold':  0},
        {'msg': "导师关系网帮你快速通过审核。\n精力+130。",                       'hp':  130, 'atk': 0, 'def_': 0, 'gold':  0},
        {'msg': "组内矛盾，你被卷进去了。\n精力-130，抗压-1。",                  'hp': -130, 'atk': 0, 'def_':-1, 'gold':  0},
    ],
    'evil': [
        {'msg': "导师把你成果挂自己PPT开大会。\n怒气+25。",                       'hp':    0, 'atk': 0, 'def_': 0, 'gold':  0, 'rage': 25},
        {'msg': "导师心情好，给三天自由研究时间！\n精力+200。",                    'hp':  200, 'atk': 0, 'def_': 0, 'gold':  0},
        {'msg': "臭导师不在，划水两小时视频……\n精力+70，怒气-10。",               'hp':   70, 'atk': 0, 'def_': 0, 'gold':  0, 'rage':-10},
        {'msg': "导师要你跟进绝对完不成的课题。\n精力-220，抗压-2。",            'hp': -220, 'atk': 0, 'def_':-2, 'gold':  0},
        {'msg': "新师弟来了，导师注意力转移！\n精力+100，怒气-15。",               'hp':  100, 'atk': 0, 'def_': 0, 'gold':  0, 'rage':-15},
    ],
}

                                                                    
TALENT_MILESTONES = {4, 9, 14, 19}                            

TALENTS = {
          
    'floor_heal':    {'name': '导师关怀', 'desc': '升层时恢复30%精力上限', 'route': 'kind'},
    'item_boost':    {'name': '珍惜扶持', 'desc': '所有道具回复效果×1.5', 'route': 'kind'},
    'calm_mind':     {'name': '心境平和', 'desc': '疲劳累积速度降低60%', 'route': 'kind'},
    'soft_def':      {'name': '以柔克刚', 'desc': '每次受伤，伤害的20%转化为防御', 'route': 'kind'},
    'lucky_key':     {'name': '贵人相助', 'desc': '每层35%概率获得随机钥匙', 'route': 'kind'},
    'kind_npc':      {'name': '人情温暖', 'desc': '进入好NPC的层恢复80精力', 'route': 'kind'},
         
    'battle_growth': {'name': '百炼成钢', 'desc': '每次战斗胜利学术永久+2', 'route': 'pro'},
    'iron_will':     {'name': '铁石意志', 'desc': '精力低于30%时攻击+20', 'route': 'pro'},
    'focus':         {'name': '专注研究', 'desc': '疲劳不影响攻击输出', 'route': 'pro'},
    'thesis_armor':  {'name': '论文铠甲', 'desc': '每层首次战斗额外防御+30', 'route': 'pro'},
    'deep_research': {'name': '深度钻研', 'desc': '知识点获取量+30%', 'route': 'pro'},
    'tough_skin':    {'name': '抗压成长', 'desc': '承受100+伤害后防御永久+1', 'route': 'pro'},
            
    'free_door':     {'name': '门路广阔', 'desc': '开门25%概率不消耗钥匙', 'route': 'social'},
    'vip_discount':  {'name': '人脉折扣', 'desc': '商店额外8折', 'route': 'social'},
    'network_gold':  {'name': '信息资源', 'desc': '每层进入获得20知识点', 'route': 'social'},
    'charm':         {'name': '亲和力', 'desc': '随机事件60%为正面效果', 'route': 'social'},
    'gift_key':      {'name': '礼尚往来', 'desc': '每5层免费获得随机钥匙', 'route': 'social'},
    'social_heal':   {'name': '精神支柱', 'desc': '进入好NPC的层恢复80精力', 'route': 'social'},
          
    'rage_cheap':    {'name': '摸鱼达人', 'desc': '技能怒气消耗降低20（原50）', 'route': 'evil'},
    'anger_power':   {'name': '以怒为力', 'desc': '每次完成杂活学术永久+3', 'route': 'evil'},
    'slacker':       {'name': '划水专家', 'desc': '疲劳累积速度降低60%', 'route': 'evil'},
    'cunning':       {'name': '狡兔三窟', 'desc': '战斗30%概率伤害减半', 'route': 'evil'},
    'exploit':       {'name': '利益最大化', 'desc': '知识点获取量+35%', 'route': 'evil'},
    'endurance':     {'name': '苦中作乐', 'desc': '杂活精力惩罚降低40%', 'route': 'evil'},
}

                                                                    
ACHIEVEMENTS = {
    'no_skill':  {'name': '禅定学者', 'desc': '全程未使用一次技能通关'},
    'gold_rich': {'name': '学术土豪', 'desc': '通关时知识点达到2000以上'},
    'full_hp':   {'name': '钢铁体魄', 'desc': '满精力状态击败最终boss'},
    'speed_run': {'name': '闪电毕业', 'desc': '总步数不超过180步通关'},
    'rage_full': {'name': '忍无可忍', 'desc': '怒气100时击败boss（恶导路线）'},
}


INTRO_PAGES = [
    [
        "★  序  章  ★",
        "",
        "公元某年，深秋。",
        "",
        "你坐在实验室里，盯着空白的文档。",
        "导师的话还在耳边回响：",
        "「数据不够。结论太弱。重做。」",
        "",
        "就在这时，桌上的台灯突然闪烁——",
        "一道光将你卷入了一个陌生的空间。",
        "",
        "眼前矗立着一座高塔，塔门上刻着：",
        "",
        "★  学  术  魔  塔  ★",
    ],
    [
        "★  塔  语  ★",
        "",
        "一个声音从四面八方传来：",
        "",
        "「欢迎。此塔共二十三层。」",
        "「每一层，都是无数学子走过或未曾走完的路。」",
        "「文献的迷宫、数据的荒漠，」",
        "「审稿人的诘问、答辩的深渊……」",
        "「皆在其中。」",
        "",
        "「能登顶者，方得学位，重返人间。」",
        "",
        "「当然——你也可以选择放弃。」",
        "「很多人都这么做了。」",
        "",
        "你握紧了手中的草稿纸。",
    ],
    [
        "★  操  作  说  明  ★",
        "",
        "方向键 / WASD    移动",
        "Enter / 空格     确认、对话",
        "数字键 1         确认选择",
        "数字键 0         放弃（慎重）",
        "",
        "【目标】",
        "探索二十三层，收集资源，",
        "击败每层的「怪物」，登顶魔塔。",
        "",
        "【提示】",
        "遇到NPC时多聊聊，",
        "他们都曾在这座塔里挣扎过。",
        "",
        "      准备好了吗？",
    ],
]


EVIL_CHORES = [
    ("导师：帮我做个PPT，明天开会用！\n你熬夜赶制到凌晨三点...",              -200,  0,  0, -50),
    ("导师：现在有个好项目，帮我写项目书，明天要！\n你觉得头发掉了一把...",      -300,  0,  0, -80),
    ("导师：楼下有个快递，帮我拿到我办公室来。\n顺便把上次那箱资料也搬过来。",    -80,  0,  0,   0),
    ("导师：去幼儿园接一下我孩子放学，我在开会。",                              -120,  0,  0,   0),
    ("导师：你来帮我写《XX领域前沿》第3章！\n写完了还不署名...",              -400,  0,  0,-100),
    ("通知：你的学术会议名额取消了，留下来做实验。\n学术视野白白错过...",          0, -3,  0,-100),
    ("导师：研究方向不对，推翻重来！\n三个月心血化为乌有...",                   -300, -5,  0, -50),
    ("紧急组会！今晚十点，准备15分钟汇报。\n睡眠严重不足...",                   -250,  0,  0,   0),
    ("导师：帮我审这篇投稿稿件，明天要回复编辑。",                             -150,  0,  0,   0),
    ("导师：把这500条实验数据录入Excel，今天要。\n你机械劳动到眼睛发酸...",     -200,  0,  0, -40),
    ("导师：下周我去外校做报告，帮我把PPT重新做一遍，风格改一改。",             -180,  0,  0,   0),
    ("导师：明天教育厅来检查，今晚把实验室整理了！",                           -220,  0,  0, -30),
    ("导师：帮我写个宣传视频脚本，学院要求的。",                               -160,  0,  0,   0),
    ("导师：我有个项目报销单据，你帮我整理一下。\n顺便跑一趟财务处。",           -130,  0,  0,   0),
    ("导师发消息：去给我买杯瑞幸，顺便打印十份文件。",                           -60,  0,  0, -20),
    ("导师：帮我写一封推荐信草稿（给别的同学的）。",                            -100,  0,  0,   0),
    ("导师：期末考试，你来帮我监考并批改卷子。\n整整两天...",                   -280,  0, -2, -30),
    ("导师：把这个实验仪器搬到另一个实验室，搬完再记录入库。",                  -150,  0,  0,   0),
    ("导师突发奇想：写个Python脚本帮我处理数据，今晚要！\n不是你的方向但也得写...", -200, 0, 0, -20),
    ("导师：帮我把这本英文书翻译成中文，就第2到第5章。",                        -350, -2,  0, -60),
]

                                                                   
EVIL_YANBI = [
    ("延毕通知！\n导师说你毕业论文需要大修，延期3个月！\n论文委员会：建议补充大量实验数据。",  -500, -5),
    ("再次延毕！\n答辩委员会要求补充实验，再等半年！\n导师：这都是为你好。",              -600,-10),
    ("三次延毕：\n导师突然换了研究方向，一年重来！\n答辩主席已进化为【延毕版答辩主席】！",   -800,-15),
]

                                                                    
ROUTES = {
    'kind': {
        'name':    '善良导师',
        'diff':    '简单',
        'stars':   1,
        'color':   (80, 200, 80),
        'key':     pygame.K_1,
        'desc':    ['温柔耐心，全力支持你。',
                    '敌人×0.7，每升一层回200精力，',
                    '技能：导师鼓励（回复30%精力上限）'],
        'start':   {'hp': 1500, 'hp_max': 1500, 'atk': 30, 'def_': 18, 'gold': 50,
                    'keys': {'b': 0, 'r': 0, 'y': 0}},
        'emult':   0.7,
        'heal':    200,
        'discount':1.0,
    },
    'pro': {
        'name':    '科研大佬',
        'diff':    '普通',
        'stars':   2,
        'color':   (80, 140, 255),
        'key':     pygame.K_2,
        'desc':    ['顶级学者，武器/盾效果×1.5。',
                    '击败敌人额外获得属性，',
                    '技能：研究突破（下次战斗学术+20）'],
        'start':   {'hp': 1100, 'hp_max': 1100, 'atk': 40, 'def_': 10, 'gold': 0,
                    'keys': {'b': 0, 'r': 0, 'y': 0}},
        'emult':   1.0,
        'heal':    0,
        'discount':1.0,
    },
    'social': {
        'name':    '人脉老师',
        'diff':    '普通',
        'stars':   2,
        'color':   (255, 165, 50),
        'key':     pygame.K_3,
        'desc':    ['关系广泛，初始多钥匙，商店7折。',
                    '敌人×0.9，知识点收益×1.5，',
                    '技能：动用关系（获得随机钥匙）'],
        'start':   {'hp': 1000, 'hp_max': 1000, 'atk': 25, 'def_': 12, 'gold': 200,
                    'keys': {'b': 2, 'r': 1, 'y': 0}},
        'emult':   0.9,
        'heal':    0,
        'discount':0.7,
    },
    'evil': {
        'name':    '邪恶导师',
        'diff':    '地狱',
        'stars':   4,
        'color':   (200, 40, 40),
        'key':     pygame.K_4,
        'desc':    ['PPT、项目书、取快递、接孩子...',
                    '随时杂活！敌人×1.2，累积怒气可反击。',
                    '技能：摸鱼反击（50怒气跳过杂活）'],
        'start':   {'hp': 1000, 'hp_max': 1000, 'atk': 20, 'def_': 10, 'gold': 0,
                    'keys': {'b': 0, 'r': 0, 'y': 0}},
        'emult':   1.2,
        'heal':    0,
        'discount':1.0,
    },
}

                                                                     
       
                                         
                                      
                                
                                                    
MAPS = [
        
    [".##.###.#",
     "k.1.#...#",
     ".##.#...#",
     ".#..###.#",
     ".........",
     ".#.K#####",
     ".##.....c",
     "..##.###1",
     "..#...#1U"],

        
    ["#DkA#.#.#",
     "##1##.#.#",
     "#.....#..",
     "#####.###",
     ".........",
     "####K####",
     ".#...e1#.",
     ".#.#.#1#.",
     "##.#.#U##"],

        
    ["Dk..#.#.#",
     "#1#.#.#..",
     "#.#.#.#.#",
     "#K#.#...#",
     "#.#####.#",
     "........#",
     "#.##.####",
     "#.....#1g",
     "#.###.1U#"],

        
    ["D#.#.#.#.",
     ".k.#...##",
     "K###.###.",
     "r......#.",
     ".#.#.....",
     ".#...####",
     ".###...w2",
     ".....#.#2",
     "..##.#.#U"],

        
    ["##D#.#.##",
     ".#r2.#...",
     "..R####.#",
     "##....#.#",
     "....#....",
     "#.#...#.#",
     "#.##2##.#",
     "#..p2...#",
     "####U####"],

        
    [".#D##.#.#",
     "##R...#.#",
     "...##....",
     ".#..#...#",
     "..#...#..",
     ".#..#...#",
     "...##....",
     ".#..#G###",
     "#.#..22U#"],

        
    ["##.#D#.##",
     "...#r#...",
     "####3####",
     "#..#.#..#",
     "...#R#...",
     "####W####",
     "....3....",
     "####3####",
     "#..#U#..#"],

        
    ["####D####",
     "#...r...#",
     "#.##3##.#",
     "#.#...#.#",
     "#.......#",
     "#.#...#.#",
     "#.##.##.#",
     "#...RB..#",
     "####U####"],

        
    ["Dy#$.#.#.",
     "k#.#.#...",
     "3.#..###.",
     "....#....",
     ".#.K..#.#",
     "#.#.#.#.#",
     ".#..#..S3",
     "....##.#3",
     ".#...#.#U"],

         
    ["..##D##..",
     "#.#.y.#.#",
     "#.#.4.#.#",
     "..##Y##..",
     "#.#...#.#",
     "..#...#..",
     ".###.###.",
     "..#.p4#..",
     "..#.4U#.."],

         
    ["D4YC#....",
     "y#.##.##.",
     "##.#...#.",
     ".....#.#.",
     "#.##.#...",
     ".........",
     ".#.#.###c",
     ".#....#.4",
     ".....##4U"],

         
    ["D###.###.",
     "k4.#.#...",
     "##K#.#.##",
     ".........",
     ".#.###.#.",
     "##..#..##",
     ".##.#e##.",
     "....#4...",
     "###.4U###"],

         
    ["D##.###.#",
     "k...#...#",
     "5##.#...#",
     ".#..###.#",
     ".........",
     ".#.K#####",
     ".##.....g",
     "..##.###5",
     "..#...#5U"],

         
    ["#Dk5#.#.#",
     "##r##.#.#",
     "#.....#..",
     "#####.###",
     ".........",
     "####K####",
     ".#...w5#.",
     ".#.#.#5#.",
     "##.#.#U##"],

         
    ["Dr..#.#.#",
     "#5#.#.#..",
     "#.#.#.#.#",
     "#R#.#...#",
     "#.#####.#",
     "........#",
     "#.##.####",
     "#.....#5p",
     "#.###.5U#"],

         
    ["D#.#.#.#.",
     ".y.#...##",
     "Y###.###.",
     ".......#.",
     ".#.#.....",
     ".#...####",
     ".###...G6",
     ".....#.#6",
     "..##.#.#U"],

         
    ["##D#E#.##",
     ".#y6.#...",
     "..Y####.#",
     "##....#.#",
     "....#....",
     "#.#...#.#",
     "#.##6##.#",
     "#..W6...#",
     "####U####"],

         
    [".#D##$#.#",
     "##.k..#.#",
     "..K##....",
     ".#..#...#",
     "..#...#..",
     ".#..#...#",
     "...##....",
     ".#..#s###",
     "#.#..66U#"],

         
    ["##.#D#.##",
     "...#y#...",
     "####y####",
     "#..#7#..#",
     "...#Y#...",
     "####S####",
     "....7....",
     "####7####",
     "#..#U#..#"],

         
    ["####D####",
     "#...y...#",
     "#.##7##.#",
     "#.#...#.#",
     "#.......#",
     "#.#...#.#",
     "#.##.##.#",
     "#...Y...#",
     "####U####"],

         
    ["D7#B.#.#.",
     "y#.#.#...",
     "..#..###.",
     "....#....",
     ".#.Y..#.#",
     "#.#.#.#.#",
     ".#..#..c7",
     "....##.#7",
     ".#...#.#U"],

         
    ["B.##D##..",
     "#.#.k.#.#",
     "#.#.8.#.#",
     "..##K##..",
     "#.#...#.#",
     "..#...#..",
     ".###.###.",
     "..#.e8#..",
     "..#.8U#.."],

         
    ["D888#8...",
     ".#.##.##.",
     "##.#...#.",
     ".....#.#.",
     "#.##9#...",
     ".........",
     ".#.#.###.",
     ".#....#..",
     ".....##.."],

]


@dataclass
class Player:
    hp: int = 1000
    hp_max: int = 1000
    atk: int = 25
    def_: int = 12
    gold: int = 0
    keys: Dict[str, int] = field(default_factory=lambda: {'b': 0, 'r': 0, 'y': 0})
    floor: int = 0
    x: int = 1
    y: int = 1
    won: bool = False
    dead: bool = False
    route: str = 'kind'
                
    step_count: int = 0
    next_chore_at: int = 0
    yanbi_count: int = 0
    rage: int = 0                           
           
    skill_used_floor: int = -1
    pro_bonus: int = 0                          
                                              
    shop_counts: Dict[int, int] = field(default_factory=dict)
                                                          
    visited_floors: set = field(default_factory=set)
                          
    total_steps: int = 0
    skill_use_count: int = 0
             
    fatigue: int = 0
    fatigue_step: int = 0                                      
             
    talents: List[str] = field(default_factory=list)
    talent_floor_used: Dict[str, int] = field(default_factory=dict)


                                                                                                           
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("学术魔塔 - 观云读研风云")
        self.clock = pygame.time.Clock()

        fonts = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'Arial']
        self.font_sm = self._load_font(fonts, 14)
        self.font_md = self._load_font(fonts, 18)
        self.font_lg = self._load_font(fonts, 22)
        self.font_xl = self._load_font(fonts, 30)

        cover_path = str(_GAME_DIR / 'fig' / 'begin.webp')
        try:
            raw = pygame.image.load(cover_path)
            iw, ih = raw.get_size()
            scale = max(W / iw, H / ih)
            nw, nh = int(iw * scale), int(ih * scale)
            scaled = pygame.transform.smoothscale(raw, (nw, nh))
            self.cover_img = pygame.Surface((W, H))
            self.cover_img.blit(scaled, ((W - nw) // 2, (H - nh) // 2))
        except Exception:
            self.cover_img = None

        _other_dir = _GAME_DIR / 'fig' / 'other'
        self.other_imgs = []
        for _i in range(1, 20):
            _p = str(_other_dir / f'{_i}.webp')
            try:
                _raw = pygame.image.load(_p).convert()
                _iw, _ih = _raw.get_size()
                _sc = max(W / _iw, H / _ih)
                _nw, _nh = int(_iw * _sc), int(_ih * _sc)
                _surf = pygame.Surface((W, H))
                _surf.blit(pygame.transform.smoothscale(_raw, (_nw, _nh)),
                           ((W - _nw) // 2, (H - _nh) // 2))
                self.other_imgs.append(_surf)
            except Exception:
                break
        self.intro_bg_imgs: list = []

        self.state = 'cover'
        self.intro_page = 0
        self._abandon_btn: Optional[pygame.Rect] = None
                
        self._touch_start: Optional[tuple] = None                
        self.player: Optional[Player] = None
        self.map_state: List[List[str]] = []
        self.floor_states: Dict[int, List[List[str]]] = {}
        self.log: List[str] = []
        self.npc_dialog: Optional[List[str]] = None
        self.npc_page = 0
        self.shop_open = False
        self.chore_popup: Optional[dict] = None
        self.tanping_msg: Optional[str] = None
        self.combat_preview: Optional[dict] = None
        self.random_event: Optional[dict] = None
        self.talent_select: Optional[List[str]] = None                  
        self.talent_pending: bool = False                                                 
        self.achievement_queue: List[str] = []
        self.achievement_timer: int = 0
        self.save_exists = SAVE_FILE.exists()

                                                                                                                                  
        self.npc_char: Optional[str] = None                         
        self.current_scene_key: Optional[str] = None              
        self.showing_end_cg: bool = False                       
        self._scene_cache: dict = {}                               

        _FIG = str(_GAME_DIR / 'fig')

                         
        self.portraits: dict = {}
        for _nm in ['你','善良导师','科研大佬','人脉老师','邪恶导师',
                    '刁钻同学','嫉妒竞争者','苛刻审稿人','严格导师',
                    '论文委员','资深教授','主任委员','答辩主席']:
            try:
                _img = pygame.image.load(f'{_FIG}/act/{_nm}.webp').convert()
                _iw, _ih = _img.get_size()
                _ph = 130
                _pw = int(_iw * _ph / _ih)
                self.portraits[_nm] = pygame.transform.smoothscale(_img, (_pw, _ph))
            except Exception:
                pass

                        
        self.end_cg: dict = {}
        for _route, _num in [('kind','1'),('pro','2'),('social','3'),('evil','4')]:
            try:
                _img = pygame.image.load(f'{_FIG}/{_num}end.webp').convert()
                self.end_cg[_route] = self._scale_fullscreen(_img)
            except Exception:
                pass

                                             
        self._npc_scene_map: dict = {
                                               
            ('kind',   'A'): '12', ('kind',   'B'): '14',
            ('kind',   'C'): '16', ('kind',   'E'): '17',
                                                  
            ('pro',    'A'): '23', ('pro',    'B'): '22',
            ('pro',    'C'): '27', ('pro',    'E'): '25',
                                                     
            ('social', 'A'): '37', ('social', 'B'): '33',
            ('social', 'C'): '36', ('social', 'E'): '34',
                                                  
            ('evil',   'A'): '43', ('evil',   'B'): '47',
            ('evil',   'C'): '45', ('evil',   'E'): '46',
        }

                                     
        self._boss_scene_map: dict = {
            'kind': '2', 'pro': '2', 'social': '2',
            'evil': '44',                 
        }

                        
        self._route_portrait: dict = {
            'kind': '善良导师', 'pro': '科研大佬',
            'social': '人脉老师', 'evil': '邪恶导师',
        }

                                                         
        _TS = TILE - 2        
                   
        _char_map = {
            '1': '本科困惑者', '2': '刁钻同学', '3': '嫉妒竞争者',
            '4': '苛刻审稿人', '5': '严格导师', '6': '论文委员',
            '7': '资深教授',   '8': '主任委员', '9': '答辩主席',
        }
                                  
        _item_map = {
            'c': '咖啡',     'e': '能量饮料', 'p': '大补丸',
            'g': '知识点',   'G': '知识点',
            'w': '学术武器', 'W': '学术武器',
            's': '扛压盾',   'S': '顶级扛压盾',
        }
        self.tile_imgs: dict = {}
        for _key, _nm in {**_char_map, **_item_map}.items():
            try:
                _img = pygame.image.load(f'{_FIG}/act/{_nm}.webp').convert()
                self.tile_imgs[_key] = pygame.transform.smoothscale(_img, (_TS, _TS))
            except Exception:
                pass
                  
        try:
            _img = pygame.image.load(f'{_FIG}/act/你.webp').convert()
            self.tile_imgs['P'] = pygame.transform.smoothscale(_img, (_TS, _TS))
        except Exception:
            pass
                                                 
        for _r, _nm in self._route_portrait.items():
            try:
                _img = pygame.image.load(f'{_FIG}/act/{_nm}.webp').convert()
                self.tile_imgs[f'npc_{_r}'] = pygame.transform.smoothscale(_img, (_TS, _TS))
            except Exception:
                pass

                                                                                                                  
        MUSIC_DIR = str(_GAME_DIR / 'music')
        self.music_route = {
            'kind': f'{MUSIC_DIR}/1.mp3',
            'pro':  f'{MUSIC_DIR}/2.mp3',
            'social': f'{MUSIC_DIR}/3.mp3',
            'evil': f'{MUSIC_DIR}/4.mp3',
        }
        self.music_begin  = f'{MUSIC_DIR}/begin.mp3'
        self.music_end    = f'{MUSIC_DIR}/end.mp3'
        self.music_hidden = f'{MUSIC_DIR}/music.mp3'
        self._current_bgm = None                
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            self.snd_step    = self._gen_sound(220, 0.04, 0.12)
            self.snd_door    = self._gen_sound(380, 0.09, 0.28)
            self.snd_floor   = self._gen_sweep(523, 1046, 0.22, 0.38)
            self.snd_win     = self._gen_sweep(440, 880, 0.28, 0.42)
            self.snd_dead    = self._gen_sweep(440, 220, 0.40, 0.32)
            self.snd_achieve = self._gen_sweep(659, 1318, 0.30, 0.50)
            self.sounds_ok   = True
        except Exception:
            self.sounds_ok = False
                       
        self._play_music(self.music_begin, loop=False)

                                                                                                                                   
    def _load_font(self, names, size):
        for name in names:
            try:
                return pygame.font.SysFont(name, size)
            except Exception:
                pass
        return pygame.font.Font(None, size)

                                                                                                                        
    def _gen_sound(self, freq, duration, volume=0.3):
        rate = 22050
        n = int(rate * duration)
        buf = array.array('h')
        for i in range(n):
            env = 1 - i / n
            buf.append(int(volume * 32767 * env * math.sin(2 * math.pi * freq * i / rate)))
        try:
            return pygame.mixer.Sound(buffer=buf)
        except Exception:
            return None

    def _gen_sweep(self, f0, f1, duration, volume=0.35):
        rate = 22050
        n = int(rate * duration)
        buf = array.array('h')
        phase = 0.0
        for i in range(n):
            freq = f0 + (f1 - f0) * (i / n)
            env = 1 - i / n
            buf.append(int(volume * 32767 * env * math.sin(phase)))
            phase += 2 * math.pi * freq / rate
        try:
            return pygame.mixer.Sound(buffer=buf)
        except Exception:
            return None

    def _play_music(self, path, loop=True):
        if not self.sounds_ok:
            return
        if self._current_bgm == path:
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1 if loop else 0)
            self._current_bgm = path
        except Exception:
            pass

    def _stop_music(self):
        try:
            pygame.mixer.music.stop()
            self._current_bgm = None
        except Exception:
            pass

    def _play(self, snd):
        if self.sounds_ok and snd:
            try:
                snd.play()
            except Exception:
                pass

                                                                                                                                 
    def _scale_fullscreen(self, img):
        iw, ih = img.get_size()
        scale = max(W / iw, H / ih)
        nw, nh = int(iw * scale), int(ih * scale)
        scaled = pygame.transform.smoothscale(img, (nw, nh))
        surf = pygame.Surface((W, H))
        surf.blit(scaled, ((W - nw) // 2, (H - nh) // 2))
        return surf

    def _get_scene_img(self, key):
        if key not in self._scene_cache:
            try:
                _FIG = str(_GAME_DIR / 'fig')
                img = pygame.image.load(f'{_FIG}/{key}.webp').convert()
                self._scene_cache[key] = self._scale_fullscreen(img)
            except Exception:
                self._scene_cache[key] = None
        return self._scene_cache[key]

                                                                                                                             
    def save_game(self):
        try:
            data = {
                'player': self.player,
                'floor_states': self.floor_states,
                'map_state': self.map_state,
                'log': self.log[-5:],
            }
            with open(SAVE_FILE, 'wb') as f:
                pickle.dump(data, f)
        except Exception:
            pass

    def load_game(self) -> bool:
        if not SAVE_FILE.exists():
            return False
        try:
            with open(SAVE_FILE, 'rb') as f:
                data = pickle.load(f)
            self.player = data['player']
            self.floor_states = data['floor_states']
            self.map_state = data['map_state']
            self.log = list(data['log']) + ["读档成功！继续加油！"]
            self.npc_dialog = None
            self.shop_open = False
            self.chore_popup = None
            self.tanping_msg = None
            self.combat_preview = None
            self.random_event = None
            self.talent_select = None
            self.talent_pending = False
            self.achievement_queue = []
            self.achievement_timer = 0
            self.state = 'playing'
            self._play_music(self.music_route.get(self.player.route, self.music_begin))
            return True
        except Exception:
            return False

    def delete_save(self):
        try:
            SAVE_FILE.unlink(missing_ok=True)
        except Exception:
            pass
        self.save_exists = False

                                                                                                                               
    def _start_game(self, route_key: str):
        rd = ROUTES[route_key]
        s = rd['start']
        p = Player(
            hp=s['hp'], hp_max=s['hp_max'],
            atk=s['atk'], def_=s['def_'],
            gold=s['gold'],
            keys=dict(s['keys']),
            route=route_key,
        )
        if route_key == 'evil':
            p.next_chore_at = random.randint(12, 20)
        self.player = p
        self.floor_states = {}
        self.map_state = [list(row) for row in MAPS[0]]
        self.log = [f"选择了【{rd['name']}】！",
                    "WASD/方向键移动，Q键技能，到达23层击败答辩主席！"]
        self.npc_dialog = None
        self.shop_open = False
        self.chore_popup = None
        self.tanping_msg = None
        self.combat_preview = None
        self.random_event = None
        self.talent_select = None
        self.talent_pending = False
        self.achievement_queue = []
        self.achievement_timer = 0
        self._find_player_start()
        self.state = 'playing'
        self._play_music(self.music_route.get(route_key, self.music_begin))
        self.delete_save()
                                                 
        p.visited_floors.add(0)
        ambient = FLOOR_AMBIENT.get(route_key, {}).get(0)
        if ambient:
            self._log(ambient)

    def _find_player_start(self):
        for r in range(MAP_ROWS):
            for c in range(MAP_COLS):
                if self.map_state[r][c] == 'P':
                    self.player.x, self.player.y = c, r
                    self.map_state[r][c] = '.'
                    return

    def _load_floor(self, floor_idx: int, from_up: bool):
        if self.player:
            self.floor_states[self.player.floor] = [row[:] for row in self.map_state]
        if floor_idx in self.floor_states:
            self.map_state = [row[:] for row in self.floor_states[floor_idx]]
        else:
            self.map_state = [list(row) for row in MAPS[floor_idx]]
        p = self.player
        p.floor = floor_idx
                           
        first_visit = floor_idx not in p.visited_floors
        if first_visit:
            p.visited_floors.add(floor_idx)
            route = p.route
            if floor_idx == 22:
                self.npc_dialog = BOSS_INTROS[route]
                self.npc_page = 0
                self.npc_char = 'BOSS'
                                                               
                _bsk = self._boss_scene_map.get(route)
                self.current_scene_key = _bsk
                if _bsk:
                    self._get_scene_img(_bsk)
            elif floor_idx in FLOOR_DIALOGS.get(route, {}):
                self.npc_dialog = FLOOR_DIALOGS[route][floor_idx]
                self.npc_page = 0
                self.npc_char = 'E'
                _sk = self._npc_scene_map.get((route, 'E'))
                self.current_scene_key = _sk
                if _sk:
                    self._get_scene_img(_sk)
            else:
                ambient = FLOOR_AMBIENT.get(route, {}).get(floor_idx)
                if ambient:
                    self._log(f"【剧情】{ambient}")
                                             
            if 1 <= floor_idx <= 21 and self.npc_dialog is None:
                if random.random() < 0.35:
                    evts = RANDOM_EVENTS.get(p.route, [])
                    if evts:
                        self.random_event = random.choice(evts)
        self._play(self.snd_floor if self.sounds_ok else None)

                                                                 
        has_npc = any(cell in ('A','B','C','E')
                      for row in self.map_state for cell in row)
        if 'floor_heal' in p.talents:
            p.hp = min(p.hp_max, p.hp + p.hp_max // 20)
        if 'lucky_key' in p.talents and random.random() < 0.35:
            kt = random.choice(['b','r','y']); p.keys[kt] += 1
            self._log(f"【贵人相助】随机获得一把钥匙！")
        if 'network_gold' in p.talents:
            p.gold += 20
        if 'gift_key' in p.talents and floor_idx > 0 and floor_idx % 5 == 0:
            kt = random.choice(['b','r','y']); p.keys[kt] += 1
            self._log(f"【礼尚往来】获得{floor_idx+1}层免费钥匙！")
        if has_npc and ('kind_npc' in p.talents or 'social_heal' in p.talents):
            p.hp = min(p.hp_max, p.hp + 80)
            self._log("【人情温暖】NPC在场，精力+80。")

                                                                                                                  
        if floor_idx in TALENT_MILESTONES and first_visit and len(p.talents) < 4:
                                         
            _milestone_scene = {
                'kind': '18', 'pro': '24', 'social': '35', 'evil': '49'
            }.get(p.route)
            if _milestone_scene and self.current_scene_key is None:
                self.current_scene_key = _milestone_scene
                self._get_scene_img(_milestone_scene)
            if self.npc_dialog is None and self.random_event is None:
                self._open_talent_select()
            else:
                self.talent_pending = True

        for r in range(MAP_ROWS):
            for c in range(MAP_COLS):
                cell = self.map_state[r][c]
                if cell == 'P':
                    self.map_state[r][c] = '.'
                if from_up and cell == 'U':
                    p.x, p.y = c, r
                    self.save_game()
                    return
                if not from_up and cell == 'D':
                    p.x, p.y = c, r
                    self.save_game()
                    return
        p.x, p.y = 1, 1
        self.save_game()

                                                                                                                                 
    def _log(self, msg: str):
        self.log.append(msg)
        if len(self.log) > 25:
            self.log = self.log[-25:]

                                                                                                                           
    def _route(self) -> dict:
        return ROUTES[self.player.route]

    def _enemy_stats(self, etype: int):
        name, hp, atk, def_, gold, color = ENEMIES[etype]
        if etype == 9 and self.player.route == 'evil':
            m = 1.0
            if self.player.yanbi_count >= 3:
                m = 2.0
        else:
            m = self._route()['emult']
        return name, int(hp * m), int(atk * m), int(def_ * m), gold, color

    def _item_bonuses(self, hp_b, atk_b, def_b, gold_b):
        route = self.player.route
        if route == 'pro':
            return hp_b, int(atk_b * 1.5), int(def_b * 1.5), gold_b
        if route == 'social':
            return hp_b, atk_b, def_b, int(gold_b * 1.5)
        return hp_b, atk_b, def_b, gold_b

    def _shop_cost(self, base_cost: int) -> int:
        cost = base_cost * self._route()['discount']
        if 'vip_discount' in self.player.talents:
            cost *= 0.8
        return int(cost)

                                                                                
    def _use_skill(self):
        p = self.player
        if p.skill_used_floor == p.floor:
            self._log("技能本层已使用，换层后冷却。")
            return
        p.skill_use_count += 1
        route = p.route
        if route == 'kind':
            heal = int(p.hp_max * 0.3)
            p.hp = min(p.hp_max, p.hp + heal)
            self._log(f"【导师鼓励】恢复{heal}精力！")
        elif route == 'pro':
            p.pro_bonus = 20
            self._log("【研究突破】下次战斗学术能力+20！")
        elif route == 'social':
            ktype = random.choice(['b', 'r', 'y'])
            p.keys[ktype] += 1
            kname = {'b': '蓝钥匙', 'r': '红钥匙', 'y': '黄钥匙'}
            self._log(f"【动用关系】获得{kname[ktype]}！")
        elif route == 'evil':
            if self.chore_popup:
                cost = 30 if 'rage_cheap' in p.talents else 50
                if p.rage >= cost:
                    p.rage -= cost
                    self.chore_popup = None
                    self._log(f"【摸鱼反击】消耗{cost}怒气，跳过了这次杂活！")
                    return
                else:
                    self._log(f"怒气不足！需要50，当前{p.rage}。")
                    return
            else:
                self._log("当前没有杂活可以跳过。")
                return
        p.skill_used_floor = p.floor

                                                                                                                 
    def _evil_step(self):
        p = self.player
        p.step_count += 1
        if p.step_count < p.next_chore_at:
            return
        p.step_count = 0
        p.next_chore_at = random.randint(12, 22)
        if p.yanbi_count < 3 and random.random() < 0.15:
            ev = EVIL_YANBI[p.yanbi_count]
            self.chore_popup = {'msg': ev[0], 'hp': ev[1], 'atk': ev[2],
                                'def': 0, 'gold': 0, 'yanbi': True}
            p.yanbi_count += 1
        else:
            ev = random.choice(EVIL_CHORES)
            self.chore_popup = {'msg': ev[0], 'hp': ev[1], 'atk': ev[2],
                                'def': ev[3], 'gold': ev[4], 'yanbi': False}

    def _apply_chore(self):
        ev = self.chore_popup
        p = self.player
        hp_delta = ev['hp']
        if 'endurance' in p.talents and hp_delta < 0:
            hp_delta = int(hp_delta * 0.6)
        p.hp    = max(1, p.hp + hp_delta)
        p.atk   = max(1, p.atk + ev['atk'])
        p.def_  = max(0, p.def_ + ev['def'])
        p.gold  = max(0, p.gold + ev['gold'])
        if 'anger_power' in p.talents:
            p.atk += 3
        p.rage  = min(100, p.rage + 20)
        self.chore_popup = None
        if p.rage == 100:
            self._log("怒气满了！下次战斗伤害翻倍！")
        if p.hp <= 1:
            self._log("精力几乎耗尽！快补给！")

                                                                                                                                  
    def _calc_combat(self, etype: int):
        """Returns (total_dmg, player_dmg_per_round, rounds, can_win, can_survive)"""
        name, ehp, eatk, edef, egold, _ = self._enemy_stats(etype)
        p = self.player
        atk_base = p.atk + (p.pro_bonus if p.route == 'pro' else 0)
        iron_bonus = 20 if ('iron_will' in p.talents and p.hp < p.hp_max * 0.3) else 0
        atk_eff = int(atk_base * self._fatigue_mult(ignore_for_atk=True)) + iron_bonus
        def_eff = max(0, int(p.def_ * self._fatigue_mult()))
        if 'thesis_armor' in p.talents and p.talent_floor_used.get('thesis_armor', -1) != p.floor:
            def_eff += 30
        pdmg = max(0, atk_eff - edef)
        if pdmg == 0:
            return 0, 0, 0, False, False
        rounds = -(-ehp // pdmg)
        if etype == 9:
            academic_bonus = p.atk // 2 + p.gold // 100
            edmg = max(0, eatk - def_eff - academic_bonus)
        else:
            edmg = max(0, eatk - def_eff - p.atk // 4)
                                          
        if p.route == 'evil' and p.rage >= 100:
            rounds = -(-ehp // (pdmg * 2))
            edmg = edmg // 2
        total = edmg * rounds
        return total, pdmg, rounds, True, total < p.hp

    def _show_combat_preview(self, r: int, c: int, etype: int):
        """设置战斗预判弹窗，等待玩家确认。"""
        name, ehp, eatk, edef, egold, _ = self._enemy_stats(etype)
        total, pdmg, rounds, can_win, can_survive = self._calc_combat(etype)
        rage_active = self.player.route == 'evil' and self.player.rage >= 100
        self.combat_preview = {
            'r': r, 'c': c, 'etype': etype,
            'name': name, 'ehp': ehp, 'eatk': eatk, 'edef': edef, 'egold': egold,
            'total_dmg': total, 'pdmg': pdmg, 'rounds': rounds,
            'can_win': can_win, 'can_survive': can_survive,
            'rage_active': rage_active,
        }

    def _confirm_combat(self):
        pv = self.combat_preview
        self.combat_preview = None
        r, c, etype = pv['r'], pv['c'], pv['etype']
        if not pv['can_win']:
            self._log(f"无法伤害{pv['name']}！先提升学术能力。")
            return
        if not pv['can_survive']:
            self._log(f"警告：与{pv['name']}战斗会倒下，取消！")
            return
        p = self.player
                             
        rage_burst = p.route == 'evil' and p.rage >= 100
        if rage_burst:
            p.rage = 0
            self._log("怒气爆发！伤害翻倍，承受减半！")
                          
        p.pro_bonus = 0
        actual_dmg = pv['total_dmg']
        if 'cunning' in p.talents and random.random() < 0.30:
            actual_dmg = actual_dmg // 2
            self._log("【狡兔三窟】伤害减半！")
        p.hp -= actual_dmg
                         
        if 'soft_def' in p.talents and actual_dmg > 0:
            p.def_ += max(1, actual_dmg // 5)
        egold = pv['egold']
        if 'deep_research' in p.talents: egold = int(egold * 1.30)
        if 'exploit'       in p.talents: egold = int(egold * 1.35)
        p.gold += egold
                
        if 'battle_growth' in p.talents:
            p.atk += 2
                
        if 'tough_skin' in p.talents and actual_dmg >= 100:
            p.def_ += 1
                            
        p.talent_floor_used['thesis_armor'] = p.floor
                         
        if p.route == 'pro' and etype >= 3:
            bonus_atk = max(1, etype - 2)
            bonus_def = max(0, etype - 4)
            p.atk += bonus_atk
            p.def_ += bonus_def
            extra = f"，攻击+{bonus_atk}" + (f"，抗压+{bonus_def}" if bonus_def else "")
        else:
            extra = ""
        name = pv['name']
        self._log(f"击败{name}！损耗{actual_dmg}精力！{egold}知识点{extra}。")
        self.map_state[r][c] = '.'
        p.x, p.y = c, r
        if etype == 9:
            p.won = True
            self.state = 'won'
            self.showing_end_cg = True           
            ab = p.atk // 2 + p.gold // 100
            self._log(f"综合实力（攻击加成{ab}）压制了答辩委员会！")
            if p.route == 'evil':
                yb = p.yanbi_count
                self._log(f"历经{yb}次延毕、无数杂活，你以钢铁意志通过了答辩！！")
            self._play(self.snd_win)
            self._stop_music()
            self._play_music(self.music_end, loop=False)
            self._check_achievements()
        else:
            self._play(self.snd_win)
        if p.hp <= 0:
            p.dead = True
            self.state = 'dead'
            self._play(self.snd_dead)
            self._stop_music()
            self._play_music(self.music_end, loop=False)
            self._log("精力耗尽！按R重新开始。")

    def _fatigue_mult(self, ignore_for_atk=False):
        """返回疲劳惩罚系数（1.0=无惩罚）"""
        p = self.player
        if ignore_for_atk and 'focus' in p.talents:
            return 1.0
        if p.fatigue >= 80:
            return 0.75
        if p.fatigue >= 60:
            return 0.88
        return 1.0

    def _open_talent_select(self):
        p = self.player
        if len(p.talents) >= 4:
            return
        available = [k for k, v in TALENTS.items()
                     if v['route'] == p.route and k not in p.talents]
        if available:
            self.talent_select = random.sample(available, min(3, len(available)))

    def _check_achievements(self):
        p = self.player
        unlocked = []
        if p.skill_use_count == 0:
            unlocked.append('no_skill')
        if p.gold >= 2000:
            unlocked.append('gold_rich')
        if p.hp >= p.hp_max:
            unlocked.append('full_hp')
        if p.total_steps <= 180:
            unlocked.append('speed_run')
        if p.route == 'evil' and p.rage >= 100:
            unlocked.append('rage_full')
        for key in unlocked:
            ac = ACHIEVEMENTS[key]
            self.achievement_queue.append(f"【隐藏成就解锁】{ac['name']}\n{ac['desc']}")
        if self.achievement_queue:
            self.achievement_timer = 150

    def _apply_random_event(self):
        ev = self.random_event
        self.random_event = None
        if not ev:
            return
        p = self.player
        p.hp    = max(1, p.hp + ev.get('hp', 0))
        p.atk   = max(1, p.atk + ev.get('atk', 0))
        p.def_  = max(0, p.def_ + ev.get('def_', 0))
        p.gold  = max(0, p.gold + ev.get('gold', 0))
        if p.route == 'evil':
            p.rage = max(0, min(100, p.rage + ev.get('rage', 0)))

                                                                                                                    
    def _use_item(self, r: int, c: int, itype: str):
        p = self.player
        name, desc, hp_b, atk_b, def_b, gold_b, _ = ITEMS[itype]
        hp_b, atk_b, def_b, gold_b = self._item_bonuses(hp_b, atk_b, def_b, gold_b)
        if 'item_boost' in p.talents:
            hp_b = int(hp_b * 1.5); atk_b = int(atk_b * 1.5); def_b = int(def_b * 1.5)
                             
        if hp_b > 0:
            p.fatigue = max(0, p.fatigue - 25)
        p.hp = min(p.hp_max, p.hp + hp_b)
        p.atk += atk_b; p.def_ += def_b; p.gold += gold_b
        self.map_state[r][c] = '.'
        p.x, p.y = c, r
        self._log(f"获得{name}：{desc}。")

    def _pick_key(self, r: int, c: int, ktype: str):
        slot  = {'k': 'b', 'r': 'r', 'y': 'y'}
        names = {'k': '蓝钥匙×2', 'r': '红钥匙×1', 'y': '黄钥匙×1'}
        self.player.keys[slot[ktype]] += 1
        self.map_state[r][c] = '.'
        self.player.x, self.player.y = c, r
        self._log(f"获得{names[ktype]}！")

    def _try_door(self, r: int, c: int):
        cell = self.map_state[r][c]
        kmap  = {'K': 'b', 'R': 'r', 'Y': 'y'}
        kname = {'b': '蓝钥匙', 'r': '红钥匙', 'y': '黄钥匙'}
        kt = kmap[cell]
        free = 'free_door' in self.player.talents and random.random() < 0.35
        if self.player.keys[kt] > 0 or free:
            if not free:
                self.player.keys[kt] -= 1
            self.map_state[r][c] = '.'
            self._log(f"用{kname[kt]}打开了门。" + ("（免费！）" if free else ""))
            self._play(self.snd_door)
        else:
            self._log(f"需要{kname[kt]}才能打开！")

                                                                                                                                
    def move(self, dx: int, dy: int):
        if any([self.chore_popup, self.npc_dialog, self.shop_open,
                self.combat_preview, self.tanping_msg, self.random_event,
                self.talent_select, self.player.won, self.player.dead]):
            return
        p = self.player
        nx, ny = p.x + dx, p.y + dy
        if not (0 <= nx < MAP_COLS and 0 <= ny < MAP_ROWS):
            return
        cell = self.map_state[ny][nx]
        moved = False

        if cell == '#':
            pass
        elif cell == '.':
            p.x, p.y = nx, ny; moved = True
        elif cell in '123456789':
            self._show_combat_preview(ny, nx, int(cell))
        elif cell in ITEMS:
            self._use_item(ny, nx, cell); moved = True
        elif cell in ('k', 'r', 'y'):
            self._pick_key(ny, nx, cell); moved = True
        elif cell in ('K', 'R', 'Y'):
            self._try_door(ny, nx)
        elif cell == 'U':
            if p.floor < 22:
                next_floor = p.floor + 1
                first_visit = next_floor not in p.visited_floors
                self._log(f"上至第{p.floor + 2}层。")
                self._load_floor(next_floor, from_up=False)
                if p.route == 'kind' and first_visit:
                    heal = self._route()['heal']
                    p.hp = min(p.hp_max, p.hp + heal)
                    self._log(f"导师关心问候，恢复{heal}精力。")
                moved = True
            else:
                self._log("已在最高层！")
        elif cell == 'D':
            if p.floor > 0:
                self._log(f"下至第{p.floor}层。")
                self._load_floor(p.floor - 1, from_up=True)
                moved = True
            else:
                self._log("已在底层！")
        elif cell in ('A', 'B', 'C', 'E'):
            self.npc_char = cell
            if cell == 'E':
                self.npc_dialog = NPC_E_DIALOGS.get(p.route, ["..."])
            else:
                self.npc_dialog = NPC_DIALOGS.get(cell, ["..."])
            self.npc_page = 0
            _sk = self._npc_scene_map.get((p.route, cell))
            self.current_scene_key = _sk
            if _sk:
                self._get_scene_img(_sk)          
        elif cell == '$':
            self.shop_open = True

        if moved:
            p.total_steps += 1
            self._play(self.snd_step)
                    
            step_threshold = 5
            if 'calm_mind' in p.talents or 'slacker' in p.talents:
                step_threshold = 13
            p.fatigue_step += 1
            if p.fatigue_step >= step_threshold:
                p.fatigue_step = 0
                old_f = p.fatigue
                p.fatigue = min(100, p.fatigue + 2)
                if old_f < 60 <= p.fatigue:
                    self._log("【疲劳警告】开始感到疲惫，学术和抗压下降10%！")
                elif old_f < 80 <= p.fatigue:
                    self._log("【严重疲劳】极度疲惫，学术和抗压下降25%！")
        if moved and p.route == 'evil' and self.state == 'playing':
            self._evil_step()

                                                                                                                          
    def _touch_to_key(self, dx, dy):
        """将滑动方向转成方向键事件"""
        if abs(dx) > abs(dy):
            key = pygame.K_RIGHT if dx > 0 else pygame.K_LEFT
        else:
            key = pygame.K_DOWN if dy > 0 else pygame.K_UP
        ev = pygame.event.Event(pygame.KEYDOWN, key=key, mod=0, unicode='')
        self.handle_event(ev)

    def handle_event(self, event):
                                                                                                                
        if event.type == pygame.FINGERDOWN:
            self._touch_start = (event.x * W, event.y * H)
                                         
            if self.state == 'cover':
                self.state = 'intro'
                self.intro_page = 0
                if self.other_imgs:
                    self.intro_bg_imgs = random.choices(self.other_imgs, k=len(INTRO_PAGES))
                return
            if self.state == 'intro':
                tx = event.x * W
                if tx < W // 2 and self.intro_page > 0:
                    self.intro_page -= 1
                else:
                    self.intro_page += 1
                    if self.intro_page >= len(INTRO_PAGES):
                        self.state = 'route_select'
                        self.intro_page = 0
                return
            if self.state == 'won' and self.showing_end_cg:
                self.showing_end_cg = False
                return
            return
        if event.type == pygame.FINGERUP:
            if self._touch_start is None:
                return
            x0, y0 = self._touch_start
            x1, y1 = event.x * W, event.y * H
            self._touch_start = None
            dx, dy = x1 - x0, y1 - y0
            dist = (dx**2 + dy**2) ** 0.5
            if dist < 18:
                                            
                ev = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, mod=0, unicode='')
                self.handle_event(ev)
            elif self.state == 'playing' and not any([
                    self.chore_popup, self.npc_dialog, self.shop_open,
                    self.combat_preview, self.tanping_msg]):
                                 
                self._touch_to_key(dx, dy)
            return

        if self.state == 'cover':
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.state = 'intro'
                self.intro_page = 0
                if self.other_imgs:
                    self.intro_bg_imgs = random.choices(self.other_imgs, k=len(INTRO_PAGES))
            return
        if self.state == 'intro':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = 'route_select'
                    self.intro_page = 0
                elif event.key in (pygame.K_LEFT, pygame.K_BACKSPACE):
                    if self.intro_page > 0:
                        self.intro_page -= 1
                else:
                    self.intro_page += 1
                    if self.intro_page >= len(INTRO_PAGES):
                        self.state = 'route_select'
                        self.intro_page = 0
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx = event.pos[0]
                if mx < W // 2 and self.intro_page > 0:
                    self.intro_page -= 1
                else:
                    self.intro_page += 1
                    if self.intro_page >= len(INTRO_PAGES):
                        self.state = 'route_select'
                        self.intro_page = 0
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            
            if self.state == 'won' and self.showing_end_cg:
                self.showing_end_cg = False
                return
            if (self.state == 'playing' and self.player
                    and not any([self.chore_popup, self.npc_dialog,
                                 self.shop_open, self.combat_preview, self.tanping_msg,
                                 self.player.won, self.player.dead])
                    and self._abandon_btn and self._abandon_btn.collidepoint(event.pos)):
                self.tanping_msg = "胜败不由己，大丈夫重头再来"
                self._play_music(self.music_hidden)
            return
        if event.type != pygame.KEYDOWN:
            return
        key = event.key

                                                                                                                     
        if self.state == 'route_select':
            for rk, rd in ROUTES.items():
                if key == rd['key']:
                    self._start_game(rk)
                    return
            if key == pygame.K_5 and self.save_exists:
                if not self.load_game():
                    self._log("读取失败！")
            return

                                                                                                                          
        if self.state in ('won', 'dead'):
            if self.showing_end_cg and self.state == 'won':
                self.showing_end_cg = False                  
                return
            if key == pygame.K_1:
                self.delete_save()
                self.state = 'route_select'
                self.save_exists = SAVE_FILE.exists()
                self._current_bgm = None             
            return

                                                                                                                     
        if self.combat_preview:
            pv = self.combat_preview
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                self._confirm_combat()
            elif key == pygame.K_ESCAPE:
                self.combat_preview = None
                self._log("鍙栨秷鎸戞垬銆")
            return

                                                                                                                          
        if self.chore_popup:
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                self._apply_chore()
            elif key == pygame.K_q:
                self._use_skill()
            elif key == pygame.K_t and self.player.route == 'evil':
                self.chore_popup = None
                self.tanping_msg = "胜败不由己，大丈夫重头再来"
                self._play_music(self.music_hidden)
            return

                                                                                                                     
        if self.random_event is not None:
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                self._apply_random_event()
                if self.talent_pending and self.npc_dialog is None:
                    self.talent_pending = False
                    self._open_talent_select()
            return

                                                                                                                          
        if self.talent_select is not None:
            idx = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2}.get(key, -1)
            if 0 <= idx < len(self.talent_select):
                chosen = self.talent_select[idx]
                self.player.talents.append(chosen)
                self.talent_select = None
                t = TALENTS[chosen]
                self._log(f"【天赋获得】{t['name']}：{t['desc']}")
                self._play(self.snd_achieve)
            return

                                                                                                                     
        if self.tanping_msg is not None:
            if key in (pygame.K_1, pygame.K_KP1, pygame.K_RETURN):
                self.tanping_msg = None
                self.delete_save()
                self.npc_dialog = None
                self.shop_open = False
                self.state = 'route_select'
                self.save_exists = SAVE_FILE.exists()
                self._current_bgm = None
                self._play_music(self.music_hidden)
            elif key in (pygame.K_2, pygame.K_KP2, pygame.K_ESCAPE):
                self.tanping_msg = None
            return

                                                                                                                            
        if self.npc_dialog is not None:
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                self.npc_page += 1
                if self.npc_page >= len(self.npc_dialog):
                    self.npc_dialog = None
                    self.npc_char = None
                    self.current_scene_key = None
                    if self.talent_pending:
                        self.talent_pending = False
                        self._open_talent_select()
            return

                                                                                                                               
        if self.shop_open:
            if key == pygame.K_ESCAPE:
                self.shop_open = False
            elif pygame.K_1 <= key <= pygame.K_6:
                idx = key - pygame.K_1
                if idx < len(SHOP_ITEMS):
                    name, stat, val, base_cost, max_buys = SHOP_ITEMS[idx]
                    cost = self._shop_cost(base_cost)
                    bought = self.player.shop_counts.get(idx, 0)
                    if max_buys > 0 and bought >= max_buys:
                        self._log(f"{name}已达购买上限（{max_buys}次）。")
                    elif self.player.gold < cost:
                        self._log(f"知识点不足！需要{cost}。")
                    else:
                        self.player.gold -= cost
                        p = self.player
                        if stat == 'hp':
                            p.hp = min(p.hp_max, p.hp + val)
                        elif stat == 'hp_max':
                            p.hp_max += val
                            p.hp = min(p.hp_max, p.hp + val)
                        elif stat == 'atk':
                            p.atk += val
                        elif stat == 'def':
                            p.def_ += val
                        p.shop_counts[idx] = bought + 1
                        remaining = f"（还可购买{max_buys - bought - 1}次）" if max_buys > 0 else ""
                        self._log(f"购买{name}（{cost}知识点）{remaining}。")
            return

                                                                                                                       
        if key == pygame.K_q:
            self._use_skill()
            return
        if key in (pygame.K_x, pygame.K_0):
            self.tanping_msg = "胜败不由己，大丈夫重头再来"
            return
        move_map = {
            pygame.K_UP:    (0,-1), pygame.K_w: (0,-1),
            pygame.K_DOWN:  (0, 1), pygame.K_s: (0, 1),
            pygame.K_LEFT:  (-1,0), pygame.K_a: (-1,0),
            pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
        }
        if key in move_map:
            self.move(*move_map[key])

                                                                                                         
         
                                                                                                         

    def _txt(self, text, font, color, x, y, center=False):
        try:
            img = font.render(str(text), True, color)
        except Exception:
            return
        r = img.get_rect()
        if center:
            r.centerx, r.y = x, y
        else:
            r.topleft = (x, y)
        self.screen.blit(img, r)

    def _txt_wrap(self, text, font, color, x, y, max_w):
        line, cy = '', y
        for ch in text:
            test = line + ch
            try:
                w = font.size(test)[0]
            except Exception:
                w = len(test) * 14
            if ch == '\n' or w > max_w:
                self._txt(line, font, color, x, cy)
                cy += font.get_height() + 2
                line = '' if ch == '\n' else ch
            else:
                line = test
        if line:
            self._txt(line, font, color, x, cy)
        return cy + font.get_height()

                                                                                                                            
    def _draw_intro(self):
        if self.intro_bg_imgs and self.intro_page < len(self.intro_bg_imgs):
            self.screen.blit(self.intro_bg_imgs[self.intro_page], (0, 0))
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((8, 6, 18, 185))
            self.screen.blit(overlay, (0, 0))
        else:
            self.screen.fill((10, 8, 20))
        page_lines = INTRO_PAGES[self.intro_page]
        is_last = self.intro_page == len(INTRO_PAGES) - 1

        pygame.draw.line(self.screen, (70, 60, 110), (30, 52), (W - 30, 52), 1)
        pygame.draw.line(self.screen, (70, 60, 110), (30, H - 62), (W - 30, H - 62), 1)

        y = 68
        for i, line in enumerate(page_lines):
            if line == "":
                y += 10
                continue
            if i == 0:
                color, font = (240, 210, 100), self.font_lg
                self._txt(line, font, color, W // 2, y, center=True)
            elif line.startswith("「"):
                color, font = (160, 205, 230), self.font_md
                self._txt(line, font, color, W // 2, y, center=True)
            elif line.startswith("【"):
                color, font = (160, 230, 160), self.font_md
                self._txt(line, font, color, W // 2, y, center=True)
            elif "★" in line:
                color, font = (240, 210, 100), self.font_lg
                self._txt(line, font, color, W // 2, y, center=True)
            elif "    " in line and not line.startswith(" "):
                parts = line.split("    ", 1)
                key_txt = parts[0].strip()
                val_txt = parts[1].strip()
                font = self.font_md
                try:
                    img_k = font.render(key_txt, True, (180, 210, 255))
                    img_v = font.render(val_txt, True, (220, 220, 200))
                    self.screen.blit(img_k, (W // 2 - 14 - img_k.get_width(), y))
                    self.screen.blit(img_v, (W // 2 + 14, y))
                except Exception:
                    self._txt(line, font, (200, 200, 215), W // 2, y, center=True)
            else:
                color, font = (200, 200, 215), self.font_md
                self._txt(line, font, color, W // 2, y, center=True)
            y += self.font_md.get_height() + 5

        total = len(INTRO_PAGES)
        for i in range(total):
            c = (210, 185, 90) if i == self.intro_page else (55, 55, 80)
            pygame.draw.circle(self.screen, c, (W // 2 - (total - 1) * 14 + i * 28, H - 52), 5)

        btn_y = H - 38
        prev_color = (160, 155, 120) if self.intro_page > 0 else (60, 58, 50)
        next_color = (230, 200, 80) if is_last else (160, 200, 160)
        next_label = "开始游戏 ▶" if is_last else "下一页 ▶"
        self._txt("◀ 上一页", self.font_md, prev_color, W // 4, btn_y, center=True)
        self._txt(next_label, self.font_md, next_color, W * 3 // 4, btn_y, center=True)
        pygame.display.flip()

    def _draw_route_select(self):
        self.screen.fill(C_BG)
        self._txt("选择你的导师", self.font_xl, C_TEXT, W//2, 14, center=True)

        # 主角介绍小卡
        pc_x, pc_y, pc_h = 20, 50, 48
        pygame.draw.rect(self.screen, (25, 30, 45), (pc_x, pc_y, W-40, pc_h), border_radius=6)
        pygame.draw.rect(self.screen, (100, 140, 200), (pc_x, pc_y, W-40, pc_h), 1, border_radius=6)
        if 'P' in self.tile_imgs:
            portrait = pygame.transform.smoothscale(self.tile_imgs['P'], (40, 40))
            self.screen.blit(portrait, (pc_x+4, pc_y+4))
            txt_x = pc_x + 50
        else:
            txt_x = pc_x + 10
        self._txt("主角：你", self.font_md, (200, 220, 255), txt_x, pc_y+5)
        self._txt("即将完成论文的研究生  身陷学术魔塔，登顶方可毕业", self.font_sm, (160, 170, 200), txt_x, pc_y+27)

        self._txt("这将决定你整个研究生涯的命运...", self.font_sm, (150,150,180), W//2, 106, center=True)

        card_w, card_h = W-40, 140
        order = ['kind', 'pro', 'social', 'evil']
        for i, rk in enumerate(order):
            rd = ROUTES[rk]
            x, y = 20, 120 + i * (card_h + 10)
            pygame.draw.rect(self.screen, (30,30,50), (x, y, card_w, card_h), border_radius=8)
            pygame.draw.rect(self.screen, rd['color'], (x, y, card_w, card_h), 2, border_radius=8)
            pygame.draw.rect(self.screen, rd['color'], (x+8, y+8, 32, 32), border_radius=6)
            self._txt(str(i+1), self.font_lg, (0,0,0), x+8+16, y+8+2, center=True)
            self._txt(rd['name'], self.font_lg, rd['color'], x+50, y+8)
            diff_color = {1:(80,220,80), 2:(255,200,50), 3:(255,130,50), 4:(255,50,50)}[rd['stars']]
            self._txt('★'*rd['stars']+'☆'*(4-rd['stars'])+' '+rd['diff'],
                      self.font_sm, diff_color, x+50, y+36)
            for j, line in enumerate(rd['desc']):
                self._txt(line, self.font_sm, C_TEXT, x+50, y+58 + j*22)

        if self.save_exists:
            pygame.draw.rect(self.screen, (40,40,60), (20, H-70, W-40, 44), border_radius=8)
            pygame.draw.rect(self.screen, C_SKILL, (20, H-70, W-40, 44), 2, border_radius=8)
            self._txt("5. 继续上次游戏", self.font_md, C_SKILL, W//2, H-60, center=True)
        self._txt("按 1-4 选择导师" + ("  /  5 继续" if self.save_exists else ""),
                  self.font_sm, (150,150,180), W//2, H-18, center=True)

                                                                                                                               
    def _draw_panel(self):
        p = self.player
        rd = self._route()
        pygame.draw.rect(self.screen, C_PANEL, (0, 0, W, MAP_Y0))
        pygame.draw.rect(self.screen, rd['color'], (0, 0, 4, MAP_Y0))

        self._txt(f"第{p.floor+1}层", self.font_md, C_STAIRS, 10, 4)
        self._txt(f"精力 {p.hp}/{p.hp_max}", self.font_md, C_HP, 90, 4)

                             
        if p.route == 'evil':
            yb_c = (255,80,80) if p.yanbi_count > 0 else (80,80,100)
            self._txt(f"延毕×{p.yanbi_count}", self.font_sm, yb_c, 310, 4)
            rage_c = C_RAGE if p.rage >= 100 else (180,80,40)
            self._txt(f"怒气{p.rage}", self.font_sm, rage_c, 370, 4)
                 
        skill_ready = p.skill_used_floor != p.floor
        sk_c = C_SKILL if skill_ready else (80,100,80)
        sname = ROUTE_SKILLS[p.route][0]
        self._txt(f"Q:{sname}" + ("✓" if skill_ready else "✗"),
                  self.font_sm, sk_c, 10, 28)

        self._txt(f"学术:{p.atk}", self.font_sm, C_ATK, 160, 28)
        self._txt(f"抗压:{p.def_}", self.font_sm, C_DEF, 240, 28)
        self._txt(f"知识:{p.gold}", self.font_sm, C_GOLD, 320, 28)

             
        knames = {'b':'蓝匙','r':'红匙','y':'黄匙'}
        kcolors = {'b':C_KEY_B,'r':C_KEY_R,'y':C_KEY_Y}
        x = 8
        for kt in ('b','r','y'):
            self._txt(f"{knames[kt]}×{p.keys[kt]}", self.font_sm, kcolors[kt], x, 52)
            x += 145
        ab = pygame.Rect(386, 46, 76, 22)
        pygame.draw.rect(self.screen, (80, 30, 30), ab, border_radius=4)
        pygame.draw.rect(self.screen, (160, 60, 60), ab, 1, border_radius=4)
        self._txt("0:放弃", self.font_sm, (220, 100, 100), ab.x+6, ab.y+3)
        self._abandon_btn = ab

                
        if p.talents:
            self._txt(f"天赋×{len(p.talents)}", self.font_sm, (200, 180, 80),
                      W - 10, 28, center=False)

               
        bw = W-12
        ratio = max(0.0, p.hp / p.hp_max)
        pygame.draw.rect(self.screen, (60,20,20), (6, 74, bw, 10))
        pygame.draw.rect(self.screen, C_HP, (6, 74, int(bw*ratio), 10))
               
        f_color = (220,60,60) if p.fatigue>=80 else (220,140,30) if p.fatigue>=60 else (60,120,180)
        pygame.draw.rect(self.screen, (30,30,50), (6, 86, bw, 6))
        pygame.draw.rect(self.screen, f_color, (6, 86, int(bw * p.fatigue / 100), 6))
        if p.fatigue >= 60:
            label = "严重疲劳" if p.fatigue >= 80 else "疲劳"
            self._txt(label, self.font_sm, f_color, 8, 87)
                     
        if p.route == 'evil':
            rage_w = int(bw * p.rage / 100)
            pygame.draw.rect(self.screen, (80,20,20), (6, 74, bw, 4))
            pygame.draw.rect(self.screen, C_RAGE, (6, 74, rage_w, 4))

                                                                                                                                     
    def _cell_color(self, cell):
        if cell == '#': return C_WALL
        if cell == '.': return C_FLOOR
        if cell in '123456789': return ENEMIES[int(cell)][5]
        if cell in ITEMS:       return ITEMS[cell][6]
        if cell == 'k': return C_KEY_B
        if cell == 'r': return C_KEY_R
        if cell == 'y': return C_KEY_Y
        if cell == 'K': return C_DOOR_B
        if cell == 'R': return C_DOOR_R
        if cell == 'Y': return C_DOOR_Y
        if cell in ('U','D'): return C_STAIRS
        if cell == '$': return C_SHOP
        if cell in ('A','B','C','E'): return C_NPC
        return C_FLOOR

    def _cell_label(self, cell):
        if cell in ('#','.'): return ''
        if cell in '123456789': return ENEMIES[int(cell)][0][:2]
        if cell in ITEMS:       return ITEMS[cell][0][:2]
        if cell == 'k': return '蓝匙'
        if cell == 'r': return '红匙'
        if cell == 'y': return '黄匙'
        if cell == 'K': return '蓝门'
        if cell == 'R': return '红门'
        if cell == 'Y': return '黄门'
        if cell == 'U': return '上楼'
        if cell == 'D': return '下楼'
        if cell == '$': return '售卖机'
        if cell in ('A','B','C','E'): return '导师'
        return ''

    def _draw_map(self):
        p = self.player
        _TS = TILE - 2             
        _npc_key = f'npc_{p.route}'             
        for r in range(MAP_ROWS):
            for c in range(MAP_COLS):
                cell = self.map_state[r][c]
                px = MAP_X0 + c * TILE
                py = MAP_Y0 + r * TILE
                                           
                pygame.draw.rect(self.screen, self._cell_color(cell), (px, py, TILE-1, TILE-1))

                          
                if cell in self.tile_imgs:
                    self.screen.blit(self.tile_imgs[cell], (px + 1, py + 1))
                                               
                elif cell in ('A', 'B', 'C', 'E') and _npc_key in self.tile_imgs:
                    self.screen.blit(self.tile_imgs[_npc_key], (px + 1, py + 1))
                                 
                else:
                    label = self._cell_label(cell)
                    if label:
                        self._txt(label, self.font_sm, C_TEXT,
                                  px + TILE//2, py + TILE//2 - 7, center=True)

             
        px = MAP_X0 + p.x * TILE
        py = MAP_Y0 + p.y * TILE
        rc = self._route()['color']
        t = pygame.time.get_ticks() / 1000.0
        pulse = (math.sin(t * 2.5) + 1) / 2  # 0.0~1.0，每秒~2.5周期

        # 向外扩散的呼吸光晕（3圈，从外到内透明度递增）
        for expand in (8, 5, 3):
            alpha = int(pulse * 110 * (1 - expand / 10))
            gs = pygame.Surface((TILE - 1 + expand * 2, TILE - 1 + expand * 2), pygame.SRCALPHA)
            pygame.draw.rect(gs, (*rc, alpha),
                             (0, 0, TILE - 1 + expand * 2, TILE - 1 + expand * 2),
                             expand, border_radius=5)
            self.screen.blit(gs, (px - expand, py - expand))

        # 格子填充与主边框
        fill = pygame.Surface((TILE - 1, TILE - 1), pygame.SRCALPHA)
        fill.fill((*rc, 40 + int(pulse * 40)))
        self.screen.blit(fill, (px, py))
        pygame.draw.rect(self.screen, rc, (px, py, TILE - 1, TILE - 1), 3)

        # 头像
        if 'P' in self.tile_imgs:
            self.screen.blit(self.tile_imgs['P'], (px + 1, py + 1))
        else:
            pygame.draw.rect(self.screen, rc, (px + 3, py + 3, TILE - 7, TILE - 7))
            self._txt("你", self.font_sm, (0, 0, 0), px + TILE // 2, py + TILE // 2 - 7, center=True)

        # 上方浮动小箭头（随脉冲上下轻微移动）
        arrow_cx = px + TILE // 2
        arrow_y  = py - 14 + int(pulse * 5)
        pts = [(arrow_cx - 7, arrow_y), (arrow_cx + 7, arrow_y), (arrow_cx, arrow_y + 9)]
        pygame.draw.polygon(self.screen, (30, 20, 20), pts)       # 深色描边
        pygame.draw.polygon(self.screen, (30, 20, 20), pts, 2)
        inner = [(arrow_cx - 5, arrow_y + 2), (arrow_cx + 5, arrow_y + 2), (arrow_cx, arrow_y + 8)]
        pygame.draw.polygon(self.screen, (255, 240, 180), inner)  # 暖白色填充

                                                                                                                                     
    def _draw_log(self):
        pygame.draw.rect(self.screen, C_LOG_BG, (0, LOG_Y0, W, LOG_H))
        pygame.draw.line(self.screen, (80,80,110), (0, LOG_Y0), (W, LOG_Y0), 2)
        y = LOG_Y0 + 6
        for line in self.log[-13:]:
            self._txt(line, self.font_sm, C_TEXT, 8, y)
            y += 21

                                                                                                                    
    def _draw_combat_preview(self):
        if not self.combat_preview:
            return
        pv = self.combat_preview
        rect = pygame.Rect(15, 130, W-30, 340)
        pygame.draw.rect(self.screen, (25,20,40), rect, border_radius=10)
        border_c = C_BOSS if pv['etype'] == 9 else C_ENEMY
        pygame.draw.rect(self.screen, border_c, rect, 2, border_radius=10)

        self._txt("⚔ 挑战确认", self.font_lg, border_c, W//2, rect.y+10, center=True)
        pygame.draw.line(self.screen, border_c, (rect.x+10, rect.y+42), (rect.right-10, rect.y+42), 1)

                
        name = pv['name']
        self._txt(f"对手：{name}", self.font_md, C_TEXT, rect.x+14, rect.y+52)
        self._txt(f"HP {pv['ehp']}  攻击{pv['eatk']}  防御{pv['edef']}",
                  self.font_sm, (180,180,200), rect.x+14, rect.y+80)

                
        self._txt("─── 战斗预测 ───", self.font_sm, (120,120,150), rect.x+14, rect.y+108)
        if not pv['can_win']:
            self._txt("无法造成伤害！需要提升学术能力。", self.font_md, C_WARN, rect.x+14, rect.y+130)
        else:
            dmg_c = (255,80,80) if not pv['can_survive'] else (100,220,100)
            rage_txt = "  【怒气爆发×2】" if pv['rage_active'] else ""
            self._txt(f"你每轮受伤：{pv['pdmg']}{rage_txt}", self.font_sm, C_ATK, rect.x+14, rect.y+130)
            self._txt(f"需要回合数：{pv['rounds']}", self.font_sm, C_TEXT, rect.x+14, rect.y+152)
            self._txt(f"预计损耗精力：{pv['total_dmg']}", self.font_md, dmg_c, rect.x+14, rect.y+176)
            self._txt(f"当前精力：{self.player.hp}", self.font_sm, C_HP, rect.x+14, rect.y+202)
            self._txt(f"获得知识点：+{pv['egold']}", self.font_sm, C_GOLD, rect.x+14, rect.y+226)
            if not pv['can_survive']:
                self._txt("警告：精力不足，此战必败！", self.font_md, C_WARN, rect.x+14, rect.y+252)

                
        if pv['can_win'] and pv['can_survive']:
            self._txt("回车/Z 确认挑战    ESC 取消", self.font_sm, (150,200,150), rect.x+14, rect.bottom-26)
        else:
            self._txt("ESC 取消", self.font_sm, (180,120,120), rect.x+14, rect.bottom-26)

                                                                                                                              
    def _draw_npc_dialog(self):
        if self.npc_dialog is None:
            return

                             
        if self.current_scene_key:
            scene = self._get_scene_img(self.current_scene_key)
            if scene:
                self.screen.blit(scene, (0, 0))
                dark = pygame.Surface((W, H), pygame.SRCALPHA)
                dark.fill((0, 0, 0, 140))
                self.screen.blit(dark, (0, 0))

                     
        box_h = 190
        rect = pygame.Rect(10, H - box_h - 8, W - 20, box_h)
        pygame.draw.rect(self.screen, (18, 18, 38, 230), rect, border_radius=10)
        pygame.draw.rect(self.screen, C_NPC, rect, 2, border_radius=10)

                   
        p = self.player
        if p and self.npc_char == 'BOSS':
            portrait_name = '答辩主席'
        elif p:
            portrait_name = self._route_portrait.get(p.route)
        else:
            portrait_name = None
        portrait = self.portraits.get(portrait_name) if portrait_name else None

        # NPC头像左侧
        if portrait:
            pw, ph = portrait.get_size()
            npc_py = rect.y + (box_h - ph) // 2
            self.screen.blit(portrait, (rect.x + 8, npc_py))
            text_x = rect.x + pw + 18
        else:
            text_x = rect.x + 12

        # 玩家小头像右侧（和NPC形成左右反差）
        player_portrait = self.portraits.get('你')
        if player_portrait:
            pp_h = 70
            pp_w = int(player_portrait.get_width() * pp_h / player_portrait.get_height())
            pp_surf = pygame.transform.smoothscale(player_portrait, (pp_w, pp_h))
            pp_x = rect.right - pp_w - 6
            pp_y = rect.bottom - pp_h - 6
            # 玩家头像背景（暖色调，与NPC冷色调对比）
            rc = self._route()['color'] if p else (100, 140, 200)
            bg = pygame.Surface((pp_w + 4, pp_h + 4), pygame.SRCALPHA)
            bg.fill((*rc, 50))
            self.screen.blit(bg, (pp_x - 2, pp_y - 2))
            pygame.draw.rect(self.screen, rc, (pp_x - 2, pp_y - 2, pp_w + 4, pp_h + 4), 2)
            self.screen.blit(pp_surf, (pp_x, pp_y))
            text_right = pp_x - 8
        else:
            text_right = rect.right - 10

        page = min(self.npc_page, len(self.npc_dialog) - 1)
        text_w = text_right - text_x
        self._txt_wrap(self.npc_dialog[page], self.font_md, C_TEXT, text_x, rect.y + 16, text_w)
        self._txt(f"({page+1}/{len(self.npc_dialog)})  回车/空格 继续",
                  self.font_sm, (150, 150, 180), rect.x + 10, rect.bottom - 24)

                                                                                                                                    
    def _draw_shop(self):
        if not self.shop_open:
            return
        rect = pygame.Rect(10, 120, W-20, 530)
        pygame.draw.rect(self.screen, (25,25,45), rect)
        pygame.draw.rect(self.screen, C_SHOP, rect, 2)
        self._txt("雷电售卖机", self.font_lg, C_SHOP, W//2, rect.y+10, center=True)
        disc = self._route()['discount']
        if disc < 1.0:
            self._txt(f"人脉折扣 {int(disc*100)}%", self.font_sm, (150,255,150), W//2, rect.y+40, center=True)
        p = self.player
        self._txt(f"知识点： {p.gold}    精力: {p.hp}/{p.hp_max}",
                  self.font_md, C_GOLD, rect.x+12, rect.y+46)
        for i, (name, stat, val, base, max_buys) in enumerate(SHOP_ITEMS):
            cost = self._shop_cost(base)
            bought = p.shop_counts.get(i, 0)
            at_limit = max_buys > 0 and bought >= max_buys
            y = rect.y + 82 + i * 70
            color = (80,80,100) if at_limit else (C_TEXT if p.gold >= cost else (100,100,120))
            limit_txt = f" [已购{bought}/{max_buys}]" if max_buys > 0 else ""
            if stat == 'hp_max':
                label = f"{i+1}. {name}  (当前{p.hp_max})"
            else:
                label = f"{i+1}. {name}{limit_txt}"
            self._txt(label, self.font_md, color, rect.x+12, y)
            cost_txt = "已达上限" if at_limit else f"花费 {cost} 知识点"
            self._txt(f"   {cost_txt}", self.font_sm, C_GOLD if not at_limit else (80,80,100),
                      rect.x+12, y+26)
        self._txt("ESC 关闭", self.font_sm, (150,150,150), rect.x+12, rect.bottom-24)

                                                                                                                        
    def _draw_chore_popup(self):
        if not self.chore_popup:
            return
        ev = self.chore_popup
        is_yanbi = ev.get('yanbi', False)
        border_c = (200,40,40) if is_yanbi else (220,120,30)
        rect = pygame.Rect(15, 110, W-30, 370)
        pygame.draw.rect(self.screen, (25,15,15), rect, border_radius=10)
        pygame.draw.rect(self.screen, border_c, rect, 3, border_radius=10)
        title = "延毕通知：" if is_yanbi else "导师来消息了..."
        self._txt(title, self.font_lg, border_c, W//2, rect.y+12, center=True)
        pygame.draw.line(self.screen, border_c, (rect.x+10, rect.y+44), (rect.right-10, rect.y+44), 1)
        bottom = self._txt_wrap(ev['msg'], self.font_sm, C_TEXT, rect.x+14, rect.y+54, rect.w-28)
        pen_y = max(bottom+10, rect.y+230)
        penalties = []
        if ev['hp']  < 0: penalties.append(f"精力{ev['hp']}")
        if ev['atk'] < 0: penalties.append(f"学术{ev['atk']}")
        if ev['def'] < 0: penalties.append(f"抗压{ev['def']}")
        if ev['gold']< 0: penalties.append(f"知识点{ev['gold']}")
        if penalties:
            self._txt("惩罚：" + "  ".join(penalties), self.font_sm, C_WARN, rect.x+14, pen_y)
        p = self.player
        rage_txt = f"  怒气+20（当前{min(100, p.rage+20)}）"
        self._txt(rage_txt, self.font_sm, C_RAGE, rect.x+14, pen_y+22)
        if p.rage >= 50:
            self._txt("Q键可消耗20怒气跳过此杂活！", self.font_sm, C_SKILL, rect.x+14, pen_y+44)
        self._txt("回车/空格 接受    Q 摸鱼反击    T 躺平认输", self.font_sm, (150,150,150), W//2, rect.bottom-26, center=True)

                                                                                                                           
    def _draw_talent_select(self):
        if self.talent_select is None:
            return
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        self._txt("天赋觉醒！选择一项能力", self.font_xl, (255, 220, 80), W//2, 30, center=True)
        self._txt("按 1 / 2 / 3 选择", self.font_sm, (160, 160, 200), W//2, 68, center=True)
        card_h = 160
        for i, key in enumerate(self.talent_select):
            t = TALENTS[key]
            cy = 100 + i * (card_h + 14)
            card = pygame.Rect(24, cy, W-48, card_h)
            pygame.draw.rect(self.screen, (28, 32, 55), card, border_radius=10)
            rd = self._route()
            pygame.draw.rect(self.screen, rd['color'], card, 2, border_radius=10)
            num_bg = pygame.Rect(card.x+10, card.y+10, 36, 36)
            pygame.draw.rect(self.screen, rd['color'], num_bg, border_radius=6)
            self._txt(str(i+1), self.font_lg, (0,0,0), num_bg.centerx, num_bg.y+4, center=True)
            self._txt(t['name'], self.font_lg, (255, 220, 100), card.x+58, card.y+12)
            self._txt_wrap(t['desc'], self.font_md, C_TEXT, card.x+58, card.y+46, card.w-70)

                                                                                                                      
    def _draw_random_event(self):
        ev = self.random_event
        if not ev:
            return
        rect = pygame.Rect(15, 120, W-30, 340)
        pygame.draw.rect(self.screen, (20, 25, 40), rect, border_radius=10)
        pygame.draw.rect(self.screen, (80, 120, 200), rect, 2, border_radius=10)
        self._txt("突发事件！", self.font_lg, (120, 180, 255), W//2, rect.y+12, center=True)
        pygame.draw.line(self.screen, (60, 90, 160), (rect.x+10, rect.y+42), (rect.right-10, rect.y+42), 1)
        bottom = self._txt_wrap(ev['msg'], self.font_md, C_TEXT, rect.x+16, rect.y+54, rect.w-32)
        pen_y = max(bottom+14, rect.y+230)
        effects = []
        if ev.get('hp',0) != 0:   effects.append(f"精力{'+'if ev['hp']>0 else ''}{ev['hp']}")
        if ev.get('atk',0) != 0:  effects.append(f"学术{'+'if ev['atk']>0 else ''}{ev['atk']}")
        if ev.get('def_',0) != 0: effects.append(f"抗压{'+'if ev['def_']>0 else ''}{ev['def_']}")
        if ev.get('gold',0) != 0: effects.append(f"知识点{'+' if ev['gold']>0 else ''}{ev['gold']}")
        if ev.get('rage',0) != 0: effects.append(f"怒气{'+'if ev['rage']>0 else ''}{ev['rage']}")
        if effects:
            ec = (100, 220, 100) if any(ev.get(k,0)>0 for k in('hp','atk','def_','gold')) else C_WARN
            self._txt("影响：" + "  ".join(effects), self.font_sm, ec, rect.x+16, pen_y)
        self._txt("回车/空格 确认", self.font_sm, (130,130,160), W//2, rect.bottom-26, center=True)

                                                                                                                       
    def _draw_achievement_popup(self):
        if not self.achievement_queue:
            return
        if self.achievement_timer <= 0:
            self.achievement_queue.pop(0)
            if self.achievement_queue:
                self.achievement_timer = 150
            return
        self.achievement_timer -= 1
        msg = self.achievement_queue[0]
        lines = msg.split('\n')
        bar_h = 16 + len(lines) * 22
        bar = pygame.Surface((W, bar_h), pygame.SRCALPHA)
        bar.fill((20, 60, 20, 210))
        self.screen.blit(bar, (0, MAP_Y0 + 4))
        for i, line in enumerate(lines):
            c = (120, 255, 120) if i == 0 else (180, 220, 180)
            self._txt(line, self.font_sm, c, W//2, MAP_Y0 + 10 + i*22, center=True)

                                                                                                                         
    def _draw_tanping_msg(self):
        if self.tanping_msg is None:
            return
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        rect = pygame.Rect(30, H//2-90, W-60, 180)
        pygame.draw.rect(self.screen, (30, 15, 15), rect, border_radius=12)
        pygame.draw.rect(self.screen, (200, 60, 60), rect, 2, border_radius=12)
        self._txt(self.tanping_msg, self.font_xl, (240, 200, 120), W//2, rect.y+28, center=True)
        pygame.draw.line(self.screen, (100, 50, 50), (rect.x+20, rect.y+76), (rect.right-20, rect.y+76), 1)
                  
        btn_y = pygame.Rect(rect.x+20, rect.y+90, (rect.w-60)//2, 52)
        pygame.draw.rect(self.screen, (160, 40, 40), btn_y, border_radius=8)
        self._txt("1  确认放弃", self.font_md, (255, 200, 200), btn_y.centerx, btn_y.y+8, center=True)
        self._txt("回车 也可确认", self.font_sm, (200, 140, 140), btn_y.centerx, btn_y.y+32, center=True)
                  
        btn_n = pygame.Rect(rect.right-20-(rect.w-60)//2, rect.y+90, (rect.w-60)//2, 52)
        pygame.draw.rect(self.screen, (40, 50, 70), btn_n, border_radius=8)
        self._txt("2  取消", self.font_md, (160, 180, 220), btn_n.centerx, btn_n.y+8, center=True)
        self._txt("ESC 也可取消", self.font_sm, (120, 140, 170), btn_n.centerx, btn_n.y+32, center=True)

                                                                                                                             
    def _draw_end_cg(self):
        p = self.player
        cg = self.end_cg.get(p.route) if p else None
        if cg:
            self.screen.blit(cg, (0, 0))
        else:
            self.screen.fill((10, 10, 30))
        hint_bar = pygame.Surface((W, 48), pygame.SRCALPHA)
        hint_bar.fill((0, 0, 0, 180))
        self.screen.blit(hint_bar, (0, H - 48))
        self._txt("按任意键继续...", self.font_md, (200, 210, 255), W // 2, H - 30, center=True)

                                                                                                                              
    def _draw_endscreen(self):
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        won = self.state == 'won'
        overlay.fill((0, 20, 0, 220) if won else (30, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))
        p = self.player

        if won:
            ed = WIN_ENDINGS[p.route]
            title_c = ed['color']

                                                                                                                   
            title = ed['title']
            if p.route == 'evil' and p.yanbi_count > 0:
                title = f"答辩通过！磨难结局（延毕{p.yanbi_count}次，"
            self._txt(title, self.font_lg, title_c, W//2, 50, center=True)
            pygame.draw.line(self.screen, title_c, (30, 82), (W-30, 82), 1)

                                                                                                            
            if p.route == 'evil':
                story = ed['story_yanbi'] if p.yanbi_count > 0 else ed['story_normal']
                epilogue = ed['epilogue_yanbi'] if p.yanbi_count > 0 else ed['epilogue_normal']
            else:
                story = ed['story']
                epilogue = ed['epilogue']

            sy = 100
            for line in story:
                self._txt(line, self.font_md, C_TEXT, W//2, sy, center=True)
                sy += 34
            sy += 10
            self._txt(epilogue, self.font_sm, title_c, W//2, sy, center=True)

                                                                                                      
            pygame.draw.line(self.screen, (80, 80, 100), (30, sy+28), (W-30, sy+28), 1)
            dy = sy + 40
            route_name = ROUTES[p.route]['name']
            self._txt(f"路线：{{{route_name}", self.font_sm, (160,160,200), W//2, dy, center=True)
            dy += 26
            self._txt(f"学术能力 {p.atk}    抗压力+{p.def_}    知识点+{p.gold}",
                      self.font_sm, (180, 220, 180), W//2, dy, center=True)
            dy += 26
            self._txt(f"精力上限 {p.hp_max}    探索 {len(p.visited_floors)}/23 层",
                      self.font_sm, (160, 180, 200), W//2, dy, center=True)
            if p.route == 'evil' and p.yanbi_count > 0:
                dy += 26
                self._txt(f"延毕 {p.yanbi_count} 次仍未放弃——这才是真正的坚韧",
                          self.font_sm, (255, 150, 80), W//2, dy, center=True)

        else:
                                                                            
            dead_lines = {
                'kind':   ["精力耗尽……", "导师还在等你回实验室。", "再准备一下，你可以的。"],
                'pro':    ["精力耗尽……", "导师：「实力还不够，回去练。」", "高压之路，再来一次。"],
                'social': ["精力耗尽……", "师兄师姐：「没事，我们陪你再来一次。」"],
                'evil':   ["精力耗尽……", "导师：「你还有三份PPT没做完。」",
                           "「而且明天还要接孩子。」", "爬起来，继续。"],
            }
            lines = dead_lines.get(p.route, ["精力耗尽……"])
            cy = H//2 - len(lines)*20
            self._txt("精力耗尽", self.font_xl, C_WARN, W//2, cy-50, center=True)
            for i, line in enumerate(lines):
                c = C_WARN if i == 0 else C_TEXT
                self._txt(line, self.font_md, c, W//2, cy + i*36, center=True)

                                                                              
        self._txt("按 1 返回主界面", self.font_md, (160, 160, 200), W//2, H-40, center=True)

                                                                                                                               
    def draw(self):
        if self.state == 'cover':
            if self.cover_img:
                self.screen.blit(self.cover_img, (0, 0))
            else:
                self.screen.fill((10, 10, 20))
                               
            title_bar = pygame.Surface((W, 80), pygame.SRCALPHA)
            title_bar.fill((0, 0, 0, 160))
            self.screen.blit(title_bar, (0, 0))
            self._txt("学术魔塔", self.font_xl, (240, 210, 120), W//2, 10, center=True)
            self._txt("观云读研风云", self.font_lg, (180, 200, 240), W//2, 46, center=True)
                       
            hint_bar = pygame.Surface((W, 36), pygame.SRCALPHA)
            hint_bar.fill((0, 0, 0, 140))
            self.screen.blit(hint_bar, (0, H-36))
            self._txt("点击或按任意键开始", self.font_md, (210, 210, 190), W//2, H-30, center=True)
            pygame.display.flip()
            return
        if self.state == 'intro':
            self._draw_intro()
            return
        if self.state == 'route_select':
            self._draw_route_select()
        else:
            self.screen.fill(C_BG)
            self._draw_panel()
            self._draw_map()
            self._draw_log()
            self._draw_shop()
            self._draw_npc_dialog()
            self._draw_combat_preview()
            self._draw_chore_popup()
            self._draw_random_event()
            self._draw_talent_select()
            self._draw_tanping_msg()
            self._draw_achievement_popup()
            if self.state in ('won', 'dead'):
                if self.showing_end_cg and self.state == 'won':
                    self._draw_end_cg()
                else:
                    self._draw_endscreen()
        pygame.display.flip()

    async def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.state == 'playing' and self.player:
                        self.save_game()
                    pygame.quit()
                    sys.exit()
                self.handle_event(event)
            self.draw()
            self.clock.tick(60)
            await asyncio.sleep(0)                    


async def main():
    await Game().run()


if __name__ == '__main__':
    asyncio.run(main())

