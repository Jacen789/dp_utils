# -*- coding: utf-8 -*-

import string
import argparse

# Some dictionaries for converting half-angle characters to full-angle characters
space_half2full = {chr(0x20): chr(0x3000)}
letter_half2full = {
    letter: chr(ord(letter) + 0xfee0) for letter in string.ascii_letters
}
digit_half2full = {
    digit: chr(ord(digit) + 0xfee0) for digit in string.digits
}
punctuation_half2full = {
    punct: chr(ord(punct) + 0xfee0) for punct in string.punctuation
}

# Dictionaries for conversion of space, letters and numbers
space_letter_digit_half2full = {
    **space_half2full, **letter_half2full, **digit_half2full
}
space_letter_digit_full2half = {
    v: k for k, v in space_letter_digit_half2full.items()
}

# Dictionaries for conversion of space, letters, numbers and punctuation marks
half2full = {
    **space_half2full, **letter_half2full,
    **digit_half2full, **punctuation_half2full
}
full2half = {
    v: k for k, v in half2full.items()
}


def punctuation_half_to_full(text):
    """半角转全角，只转标点符号"""
    return ''.join([punctuation_half2full.get(i, i) for i in text])


def space_letter_digit_full_to_half(text):
    """全角转半角，只转空格、字母和数字"""
    return ''.join([space_letter_digit_full2half.get(i, i) for i in text])


def half_to_full(text):
    """半角转全角，对于空格、字母、数字和标点符号"""
    return ''.join([half2full.get(i, i) for i in text])


def full_to_half(text):
    """全角转半角，对于空格、字母、数字和标点符号"""
    return ''.join([full2half.get(i, i) for i in text])


def conversion_text(text, function):
    """按照函数转换文本"""
    return function(text)


def full_half_conversion(input_file, output_file, mode='sld-f2h'):
    """
    全角半角转换，用于文件
    :param input_file: 输入文件路径
    :param output_file: 输出文件路径
    :param mode: 转换的模式
    :return: None
    """
    if mode in ['h2f', 'half2full']:
        function = half_to_full
    elif mode in ['f2h', 'full2half']:
        function = full_to_half
    elif mode in ['p-h2f', 'punctuation-half2full']:
        function = punctuation_half_to_full
    elif mode in ['sld-f2h', 'space-letter-digit-full2half']:
        function = space_letter_digit_full_to_half
    else:
        raise ValueError("Unknown mode %s" % mode)
    with open(input_file, 'r', encoding='utf-8') as f_in, \
            open(output_file, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            line = conversion_text(line, function)
            f_out.write(line)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='path to input file')
    parser.add_argument('-o', '--output_file', type=str, default='output.txt',
                        help='path to output file')
    parser.add_argument('-m', '--mode', type=str, default='sld-f2h',
                        help="mode in ['h2f', 'f2h', 'p-h2f', 'sld-f2h']")

    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file
    mode = args.mode
    full_half_conversion(input_file, output_file, mode)


if __name__ == '__main__':
    main()
