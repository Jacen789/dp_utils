import os
import glob
import re


def pinyin2phoneme(pinyin_str):
    """拼音转音素（声母和韵母）。所有轻声的声调都用5表示，儿化音标志是er0"""
    pinyin_str = pinyin_str.strip()
    pinyin_str = re.sub(r"([a-z]{2,})r(\d)", r"\1\2 er0", pinyin_str)
    pinyin_str = re.sub(r"([jqx])u", r"\1v", pinyin_str)
    pinyin_str = re.sub(r"yu", "v", pinyin_str)
    pinyin_str = re.sub(r"yi|y", "i", pinyin_str)
    pinyin_str = re.sub(r"wu|w", "u", pinyin_str)
    pinyin_str = re.sub(r"un", "uen", pinyin_str)
    pinyin_str = re.sub(r"iu", "iou", pinyin_str)
    pinyin_str = re.sub(r"ui", "uei", pinyin_str)
    pinyin_str = re.sub(r"([zcs])i", r"\1ii", pinyin_str)
    pinyin_str = re.sub(r"([zcs]h|r)i", r"\1iii", pinyin_str)
    pinyins = re.split(r"\s+", pinyin_str)
    pinyins_new = []
    for pinyin in pinyins:
        chunks = re.split(r"^(ng\d$|[zcs]h|[bpmfdtnlgkhjqxzcsr])(?!\d)", pinyin)
        chunks = [chunk for chunk in chunks if chunk is not None and len(chunk) > 0]
        pinyins_new.append(" ".join(chunks))
    pinyin_str_new = " ".join(pinyins_new)
    return pinyin_str_new


def main():
    pinyin_str = "xiao3 hair2 , ni2 hao3 ma5 , zi4 ji3 ren2 . hm4 ! hng4 ! h2 ! m2 ! n2 ! ng2 !"
    pinyin_str_new = pinyin2phoneme(pinyin_str)
    print("{}\n{}".format(pinyin_str, pinyin_str_new))


if __name__ == "__main__":
    main()
