import os
import glob
import re


class PinyinConverter(object):
    def __init__(self):
        # 正则表达式替换命令元组和内部标志
        self.PATTERN, self.SUBST = 0, 1   # 匹配段和替换段
        # 创建正则表达式替换命令元组的默认设置表（固定集合对象）
        defaultPrefSet = frozenset([
            # 以下各行字符串，凡行首用#号注释者均表示无效；
            # 凡行首未用#号注释者均有效，效用如后面注释所述：
            # "NUMBER_2_BY_AR4",                      # 数字“二”有大开口度韵腹
            # "AI_INC_NEAR_OPEN_FRONT",               # ai/uai韵腹为舌面前次开元音
            # "AIR_ANR_INC_NEAR_OPEN_CENTRAL",        # air/anr韵腹为舌面央次低元音
            # "CENTRAL_A_BY_SMALLCAPS_A",             # “央a”采用小型大写[A]标明
            # "IE_YUE_INC_SMALLCAPS_E",               # ie/yue采用小型大写[E]标明
            # "IE_YUE_INC_E",                         # ie/yue采用[e]标明（覆盖上一条）
            # "IAN_YUAN_AS_AN",                       # ian/yuan韵腹和an一样
            # "ONLY_YUAN_AS_AN",                      # 仅yuan韵腹和an一样（覆盖上一条）
            # "OU_INC_SCHWA",                         # ou/iou采用舌面央中元音韵腹
            # "IONG_BY_IUNG",                         # iong韵母采用i韵头u韵腹
            "ASPIRATE_BY_TURNED_COMMA",             # 采用反逗号弱送气符号
            # "RHOTICITY_BY_RHOTIC_HOOK",             # 儿化韵卷舌动作采用卷舌小钩
            # "ONLY_ER_BY_RHOTIC_HOOK",               # 只有er音节卷舌动作采用卷舌小钩
            "INITIAL_R_BY_VED_RETRO_FRIC",          # 声母r为卷舌浊擦音而非卷舌通音
            # "R_TURNED_WITH_HOOK",                   # 严格采用卷舌通音符号
            # "TRANSITIONAL_SCHWA_IN_ING",            # ing有舌面央中元音韵腹
            "TRANSITIONAL_SCHWA_IN_UEN",            # 合口un有舌面央中元音韵腹
            "NO_TRANSITIONAL_U",                    # bo/po/mo/fo没有[u]韵头
            # "SYLLABLE_JUNCTURE_BY_PLUS",            # 音节间断采用开音渡+号而非.号
            # "HTML_SUP_TAG_FOR_TONE_VALUE",          # 调值采用HTML上标标签格式
            # "HIDE_ALL_TONE_VALUE",                  # 隐藏所有声调转换
            # 以下选项仅存设想，目前尚未实现：
            # "RETROFLEX_INITIAL_STANDALONE",         # 卷舌声母可成音节而无需舌尖元音
            # "ZERO_INITIAL_HAS_CONSONANT",           # 零声母有辅音
        ])
        # 正则表达式替换命令元组一揽子创建设置方案（元组，[0]位为说明）
        # recipeLinWang1992 = (
        #     "林焘、王理嘉《语音学教程》",
        #     "NO_TRANSITIONAL_U", "ASPIRATE_BY_TURNED_COMMA", "AI_INC_NEAR_OPEN_FRONT"
        # )
        # recipeBeidaCN2004 = (
        #     "北京大学中文系《现代汉语》（重排本）",
        #     "NO_TRANSITIONAL_U", "ASPIRATE_BY_TURNED_COMMA", "INITIAL_R_BY_VED_RETRO_FRIC",
        #     "TRANSITIONAL_SCHWA_IN_UEN", "IONG_BY_IUNG", "IAN_YUAN_AS_AN"
        # )
        # recipeHuangLiao2002 = (
        #     "黄伯荣、廖序东《现代汉语》（增订三版）",
        #     "NO_TRANSITIONAL_U", "ASPIRATE_BY_TURNED_COMMA", "CENTRAL_A_BY_SMALLCAPS_A",
        #     "TRANSITIONAL_SCHWA_IN_UEN", "ONLY_YUAN_AS_AN", "ONLY_ER_BY_RHOTIC_HOOK",
        #     "INITIAL_R_BY_VED_RETRO_FRIC"
        # )
        # recipeYangZhou1995 = (
        #     "杨润陆、周一民《现代汉语》（北师大文学院教材）",
        #     "NO_TRANSITIONAL_U", "ASPIRATE_BY_TURNED_COMMA", "TRANSITIONAL_SCHWA_IN_UEN",
        #     "INITIAL_R_BY_VED_RETRO_FRIC"
        # )
        # recipeYuan2001 = (
        #     "袁家骅等《汉语方言概要》（第二版重排）",
        #     "NO_TRANSITIONAL_U", "ASPIRATE_BY_TURNED_COMMA", "INITIAL_R_BY_VED_RETRO_FRIC",
        #     "ONLY_ER_BY_RHOTIC_HOOK", "IAN_YUAN_AS_AN", "TRANSITIONAL_SCHWA_IN_UEN",
        #     "IE_YUE_INC_E"
        # )
        # recipeTang2002 = (
        #     "唐作藩《音韵学教程》（第三版）",
        #     "NO_TRANSITIONAL_U", "ASPIRATE_BY_TURNED_COMMA", "INITIAL_R_BY_VED_RETRO_FRIC",
        #     "ONLY_ER_BY_RHOTIC_HOOK", "IAN_YUAN_AS_AN", "TRANSITIONAL_SCHWA_IN_UEN",
        #     "IE_YUE_INC_E", "OU_INC_SCHWA"
        # )

        prefSet = set(defaultPrefSet)           # 先换为可变集合副本，以防固定类型参数
        if "IE_YUE_INC_E" in prefSet and "IE_YUE_INC_SMALLCAPS_E" in prefSet:
            prefSet.remove("IE_YUE_INC_SMALLCAPS_E")
        if "ONLY_YUAN_AS_AN" in prefSet and "IAN_YUAN_AS_AN" in prefSet:
            prefSet.remove("IAN_YUAN_AS_AN")
        self.cmdPairTuple = (
            # 转换声母前的预处理
            # 音节间断与隔音符号
            (r"([aoeiuvüê][1-5]?)([yw])",   # a/o/e前有元音时必须写隔音符号
             r"\1'\2"),      # 标明不必写出隔音符号的音节间断
            (r"'",        (r"+" if "SYLLABLE_JUNCTURE_BY_PLUS" in prefSet else
                           r".")),         # 音节间断（开音渡）标记
            # 兼容正规的印刷体字母ɡ/ɑ->g/a
            (r"ɡ",         r"g"),
            (r"ɑ",         r"a"),
            # 特殊的ê韵母，只能搭配零声母（“诶”字等）
            (r"(ê|ea)",    r"ɛ"),          # ea是ê的GF 3006表示
            # 消除因可以紧邻韵腹充当声母或韵尾的辅音的歧义
            (r"r([aoeiu])",   r"R\1"),     # 声母r暂改为R，以免与卷舌标志r混淆
            (r"n([aoeiuvü])", r"N\1"),     # 声母n暂改为N，以免与韵尾n/ng混淆
            # 需要排除式匹配转换的韵母
            (r"ng(?![aeu])",  r"ŋ"),       # 双字母ng，后鼻音韵尾或自成音节
            (r"(?<![ieuyüv])e(?![inŋr])",
             r"ɤ"),       # 单韵母e，此前已转换ea和声母r/n
            (r"(?<![bpmfdtNlgkhjqxzcsRiywuüv])er4",
             (r"ar4" if "NUMBER_2_BY_AR4" in prefSet else
              r"er4")),    # 数字“二”是否有大开口度韵腹
            (r"(?<![bpmfdtNlgkhjqxzcsRiywuüv])ar4",
             (r"a˞4" if "ONLY_ER_BY_RHOTIC_HOOK" in prefSet else
              r"ar4")),    # 数字“二”也属于er音节，可特别选用小钩
            (r"a(?![ionŋ])", (r"ᴀ" if "CENTRAL_A_BY_SMALLCAPS_A" in prefSet else
                              r"a")),      # “央a”是否用小型大写[A]标明，已转换“二”
            (r"(?<![bpmfdtNlgkhjqxzcsRiywuüv])er",
             (r"ə˞" if "ONLY_ER_BY_RHOTIC_HOOK" in prefSet else
              r"ər")),    # 一般的卷舌单韵母er，此前已排除“二”
            (r"(?<![iuüv])er", r"ər"),     # 构成单韵母e的儿化韵的er
            (r"(?<=[bpmf])o(?![uŋ])",
             (r"o" if "NO_TRANSITIONAL_U" in prefSet else
              r"uo")),     # bo/po/mo/fo是否有韵头u
            # 声母——无需转换m/f/n/l/s/r(但r可根据设置执行转换)
            # 送气清辅音声母
            (r"([ptk])",   r"\1ʰ"),
            (r"q",         r"tɕʰ"),
            (r"(ch|ĉ)",    r"tʂʰ"),        # 后者是ch的注音变体
            (r"c",         r"tsʰ"),        # 此前已排除ch
            # 不送气清辅音声母
            (r"b",         r"p"),          # 此前已排除送气的p/t/k
            (r"d",         r"t"),
            (r"g",         r"k"),          # 此前已排除后鼻音双字母中的g，注意隔音
            (r"j",         r"tɕ"),
            (r"(zh|ẑ)",    r"tʂ"),         # 后者是zh的注音变体
            (r"z",         r"ts"),         # 此前已排除zh
            # 擦音声母
            (r"(sh|ŝ)",    r"ʂ"),          # 后者是sh的注音变体
            (r"x",         r"ɕ"),          # 声母x，排除后再转换h
            (r"h",         r"x"),          # 声母h，此前已排除zh/ch/sh
            # 韵母
            # 舌尖元音韵母
            (r"(sʰ?)i",    r"\1ɿ"),        # zi/ci/si
            (r"([ʂR]ʰ?)i", r"\1ʅ"),        # zhi/chi/shi/ri
            # 部分韵腹省略表示的韵母+隔音符号和韵头w/y
            (r"iu",        r"iou"),        # 无需转换iou
            (r"ui",        r"uei"),        # 无需转换uei
            (r"wu?",       r"u"),
            (r"yi?",       r"i"),          # 此前已排除iu
            # 韵头[i]/[y]的韵母
            (r"iu|[üv]",   r"y"),          # 转换ü/v，恢复yu/yue，准备yuan/yun
            (r"ian",      (r"ian" if "IAN_YUAN_AS_AN" in prefSet else
                           r"iɛn")),       # 是否认为ian韵腹和an一样
            (r"yan",      (r"yan" if ("ONLY_YUAN_AS_AN" in prefSet)
                           or ("IAN_YUAN_AS_AN" in prefSet) else
                           r"yɛn")),       # 是否认为yuan韵腹和an一样（覆盖上一选项）
            (r"(ɕʰ?)uan", (r"\1yan" if ("ONLY_YUAN_AS_AN" in prefSet)
                           or ("IAN_YUAN_AS_AN" in prefSet) else
                           r"\1yɛn")),     # {j/q/x}uan，是否认为和an一样
            (r"(ɕʰ?)u",    r"\1y"),        # {j/q/x}u{e/n}韵头，此前已排除{j/q/x}uan
            (r"([iy])e(?!n)",  (r"\1ᴇ" if "IE_YUE_INC_SMALLCAPS_E" in prefSet else
                                r"\1e")),  # ie/yue/üe/ve，此前已转换{j/q/x}u
            (r"([iy])e(?!n)",  (r"\1e" if "IE_YUE_INC_E" in prefSet else
                                r"\1ɛ")),  # ie/yue是否采用[e]标明，此前已判断[E]
            # 舌面央中元音轻微过渡韵腹
            (r"iŋ",       (r"iəŋ" if "TRANSITIONAL_SCHWA_IN_ING" in prefSet else
                           r"iŋ")),        # ing是否有舌面央中元音韵腹
            (r"(un|uen)", (r"uən" if "TRANSITIONAL_SCHWA_IN_UEN" in prefSet else
                           r"un")),        # 合口un/uen过渡，此前已排除撮口[j/q/x]un
            # 后移的a
            (r"ao",        r"ɑu"),         # 包括ao/iao，o改为u
            (r"aŋ",        r"ɑŋ"),         # 包括ang/iang/uang
            # 韵母en/eng韵腹是舌面央中元音
            (r"e([nŋ])",   r"ə\1"),
            # ong类韵母
            (r"ioŋ",      (r"iuŋ" if "IONG_BY_IUNG" in prefSet else
                           r"yŋ")),        # iong的两种转换，此前yong已转换为iong
            (r"oŋ",        r"uŋ"),         # ong，此前已排除iong
            # 儿化音变——无需转换ar/ir/ur/aur/our/yur
            # 舌尖元音韵母
            (r"[ɿʅ]r",     r"ər"),         # {zh/ch/sh/r/z/c/s}ir
            # 鼻韵尾脱落和相应的韵腹元音替换
            (r"[aɛ][in]r", (r"ɐr" if "AIR_ANR_INC_NEAR_OPEN_CENTRAL" in prefSet else
                            r"ar")),        # air/anr韵尾脱落后的韵腹替换
            (r"eir|ənr",   r"ər"),         # eir韵腹央化，韵尾脱落；enr韵尾脱落
            (r"([iy])r",   r"\1ər"),       # ir/yr增加央化韵腹
            (r"([iuy])nr", r"\1ər"),       # inr/ynr/unr韵尾脱落后增加央化韵腹
            (r"iuŋr",      r"iũr"),        # iungr(iongr的可选变换)
            (r"([iuy])ŋr", r"\1ə̃r"),      # ingr/yngr/ungr韵尾脱落后增加央化鼻化韵腹
            (r"ŋr",        r"̃r"),         # ang/eng韵尾儿化脱落后韵腹鼻化
            # 声母、韵母转换的善后扫尾工作
            # 处理儿化韵卷舌动作
            (r"r",        (r"˞" if "RHOTICITY_BY_RHOTIC_HOOK" in prefSet else
                           r"r")),         # 是否先把儿化韵卷舌动作改为卷舌小钩
            (r"R",        (r"ʐ" if "INITIAL_R_BY_VED_RETRO_FRIC" in prefSet else
                           r"r")),         # 恢复声母r，是否采用卷舌浊擦音表示声母r
            # 此前已处理完卷舌动作和声母，现在处理剩下的r字符的可选转换
            (r"r",        (r"ɻ" if "R_TURNED_WITH_HOOK" in prefSet else
                           r"r")),         # 是否严格采用卷舌通音符号[ɻ]
            # 恢复声母n
            (r"N",         r"n"),          # 此前已处理完单元音韵母e和ie/yue
            # 其他选项
            (r"ʰ",        (r"ʻ" if "ASPIRATE_BY_TURNED_COMMA" in prefSet else
                           r"ʰ")),         # 是否采用反逗号送气符号
            (r"ai",       (r"æi" if "AI_INC_NEAR_OPEN_FRONT" in prefSet else
                           r"ai")),        # （非儿化的）ai/uai韵腹为舌面前次开元音
            (r"ou",       (r"əu" if "OU_INC_SCHWA" in prefSet else
                           r"ou")),        # ou/iou是否采用舌面央中元音韵腹
            # 声调
            # 先期处理
            ((r"[1-5]" if "HIDE_ALL_TONE_VALUE" in prefSet else
              r"5"),       r""),           # 只隐藏轻声还是隐藏所有的声调转换
            (r"([1-4])",
             (r"<sup>\1</sup>" if "HTML_SUP_TAG_FOR_TONE_VALUE" in prefSet else
              r"(\1)")),      # 隔离单个数字调号
            # 标出普通话调值
            ("([(>])1([)<])", r"\1 55\2"),  # 阴平（第一声）
            ("([(>])2([)<])", r"\1 35\2"),  # 阳平（第二声）
            ("([(>])3([)<])", r"\1 214\2"),  # 上声（第三声）
            ("([(>])4([)<])", r"\1 51\2"),  # 去声（第四声）
            ("([(>]) ([235])", r"\1\2")      # 去掉此前标调值时加上的空格
        )
        # 以上，替换命令元组创建完成！
        # 编译正则表达式对象，以便反复使用
        reList = map(re.compile, [pair[self.PATTERN] for pair in self.cmdPairTuple])
        self.reList = list(reList)

    def convert_pinyin(self, pinyin):
        pinyin = pinyin.lower()
        for eachRe, eachCmdPair in zip(self.reList, self.cmdPairTuple):
            pinyin = eachRe.sub(eachCmdPair[self.SUBST], pinyin)
        return pinyin


def main():
    pinyin_converter = PinyinConverter()
    pinyins = ["zhun1", "zhong4", "ke1", "xue2", "gui1", "lv4", "de5", "yao1", "qiu2"]
    for pinyin in pinyins:
        pinyin_new = pinyin_converter.convert_pinyin(pinyin)
        print(pinyin, pinyin_new)


if __name__ == "__main__":
    main()
