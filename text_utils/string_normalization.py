# -*- coding: utf-8 -*-

import argparse
import unicodedata


def string_normalize(text, form='NFKC'):
    """字符串规范化"""
    text = unicodedata.normalize(form, text)
    return text


def string_normalize_file(input_file, output_file, form='NFKC'):
    """
    字符串规范化，用于文件
    :param input_file: 输入文件路径
    :param output_file: 输出文件路径
    :param form: 规范化形式, form in ['NFC', 'NFKC', 'NFD', 'NFKD'],
     参数详细解释见 'http://www.unicode.org/reports/tr15/'
    :return: None
    """
    if form not in ['NFC', 'NFKC', 'NFD', 'NFKD']:
        raise ValueError("Unknown mode %s" % form)
    with open(input_file, 'r', encoding='utf-8') as f_in, \
            open(output_file, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            line = string_normalize(line, form)
            f_out.write(line)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='path to input file')
    parser.add_argument('-o', '--output_file', type=str, default='output.txt',
                        help='path to output file')
    parser.add_argument('-f', '--form', type=str, default='NFKC',
                        help="form in ['NFC', 'NFKC', 'NFD', 'NFKD']")

    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file
    form = args.form
    string_normalize_file(input_file, output_file, form)


if __name__ == '__main__':
    main()
