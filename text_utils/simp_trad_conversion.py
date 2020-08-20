# -*- coding: utf-8 -*-

import opencc
import argparse


def convert_file(input_file, output_file, config='t2s'):
    """
    简繁转换
    :param input_file: 输入文件路径
    :param output_file: 输出文件路径
    :param config: 配置文件, config in ['s2t', 't2s', 's2tw', 'tw2s', 's2hk',
     'hk2s', 's2twp', 'tw2sp', 't2tw', 't2hk'],
     参数详细解释见 'https://github.com/BYVoid/OpenCC'
    :return: None
    """
    if config not in ['s2t', 't2s', 's2tw', 'tw2s', 's2hk', 'hk2s', 's2twp',
                      'tw2sp', 't2tw', 't2hk']:
        raise ValueError("Unknown mode %s" % config)
    with open(input_file, 'r', encoding='utf-8') as f_in, \
            open(output_file, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            line = opencc.convert(line, f'{config}.json')
            f_out.write(line)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='path to input file')
    parser.add_argument('-o', '--output_file', type=str, default='output.txt',
                        help='path to output file')
    parser.add_argument('-c', '--config', type=str, default='t2s',
                        help=("config in ['s2t', 't2s', 's2tw', 'tw2s', 's2hk', "
                              "'hk2s', 's2twp', 'tw2sp', 't2tw', 't2hk']"))

    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file
    config = args.config
    convert_file(input_file, output_file, config)


if __name__ == '__main__':
    main()
