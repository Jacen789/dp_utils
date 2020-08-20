# -*- coding: utf-8 -*-

import re
import argparse

from text_utils.tokenizer.tokenization import BasicTokenizer


class SentTokenizer(object):
    def __init__(self):
        self.sentence_boundary_pattern = re.compile(r'((?:[。；;！!？?…]|\.{3,}|\.{2,}\s)+[”’』」）］〕】》〉)\]}]*)')
        self.whitespace_or_punctuation_pattern = re.compile(r'[\s\W]+')
        self.basic_tokenizer = BasicTokenizer(do_lower_case=False)
        self.second_boundary_pattern = re.compile(r'([，,：:]+[”’』」）］〕】》〉)\]}]*)')
        self.third_boundary_pattern = re.compile(r'([^\w“‘『「（［〔【《〈(\[{]+)')

    def tokenize(self, text, boundary_pattern=None):
        """分句"""
        boundary_pattern = boundary_pattern or self.sentence_boundary_pattern
        text = convert_to_unicode(text)
        sentences = []
        for token in boundary_pattern.split(text):
            if token:
                if (boundary_pattern.fullmatch(token) or
                    self.whitespace_or_punctuation_pattern.fullmatch(token)) \
                        and sentences:
                    sentences[-1] += token
                else:
                    sentences.append(token)
        return sentences

    def tokenize_limited_length(self, text, max_len=50, force=True):
        """按照长度尽量切割字符串"""
        ss1 = self.tokenize(text)
        ss1_tokens = [(s1, self.len_of(s1)) for s1 in ss1]
        ss1_tokens = self.concat_tokens(ss1_tokens, max_len=max_len)
        for s1, s1_len in ss1_tokens:
            if s1_len <= max_len:
                yield s1
            else:
                ss2 = self.tokenize(s1, self.second_boundary_pattern)
                ss2_tokens = [(s2, self.len_of(s2)) for s2 in ss2]
                ss2_tokens = self.concat_tokens(ss2_tokens, max_len=max_len)
                for s2, s2_len in ss2_tokens:
                    if (not force) or (s2_len <= max_len):
                        yield s2
                    else:
                        ss3 = self.tokenize(s2, self.third_boundary_pattern)
                        ss3_tokens = [(s3, self.len_of(s3)) for s3 in ss3]
                        ss3_tokens = self.concat_tokens(ss3_tokens, max_len=max_len)
                        for s3, s3_len in ss3_tokens:
                            if s3_len <= max_len:
                                yield s3
                            else:
                                ss4 = self.basic_tokenizer.tokenize(s3)
                                ss4_tokens = [(s4, self.len_of(s4)) for s4 in ss4]
                                ss4_tokens = self.concat_tokens(ss4_tokens, max_len=max_len)
                                for s4, s4_len in ss4_tokens:
                                    yield s4

    def len_of(self, text, en_word_len=2.5, others_len=None):
        """专门设计的长度，例如一个英文单词相当于2.5的长度"""
        tokens = self.basic_tokenizer.tokenize(text)
        tokens_len = 0
        for token in tokens:
            if len(token) == 1:
                tokens_len += 1
            elif re.fullmatch(r'[A-Za-z]+', token):
                tokens_len += en_word_len
            else:
                if others_len is not None:
                    tokens_len += others_len
                else:
                    tokens_len += len(token)
        return tokens_len

    @staticmethod
    def concat_tokens(tokens, *, max_len=50):
        """拼接较短的token"""
        sum_len = sum([token_len for _, token_len in tokens])
        avg_len = sum_len // (sum_len // max_len + 1)
        new_tokens = []
        for token, token_len in tokens:
            if (not new_tokens) or (new_tokens and new_tokens[-1][1] >= avg_len):
                new_tokens.append((token, token_len))
            elif new_tokens[-1][1] + token_len <= max_len:
                new_tokens[-1] = (new_tokens[-1][0] + token, new_tokens[-1][1] + token_len)
            else:
                new_tokens.append((token, token_len))
        return new_tokens


def convert_to_unicode(text):
    """Converts `text` to Unicode (if it's not already), assuming utf-8 input."""
    if isinstance(text, str):
        return text
    elif isinstance(text, bytes):
        return text.decode("utf-8", "ignore")
    else:
        raise ValueError("Unsupported string type: %s" % (type(text)))


def sent_tokenize_file(input_file, output_file):
    """
    分句，用于文件
    :param input_file: 输入文件名
    :param output_file: 输出文件名
    :return: None
    """
    sent_tokenizer = SentTokenizer()
    with open(input_file, 'r', encoding='utf-8') as f_in, \
            open(output_file, 'w', encoding='utf-8') as f_out:
        for text in f_in:
            sentences = sent_tokenizer.tokenize_limited_length(text, max_len=50)
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    f_out.write(sentence)
                    f_out.write('\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='path to input file')
    parser.add_argument('-o', '--output_file', type=str, default='output.txt',
                        help='path to output file')

    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file
    sent_tokenize_file(input_file, output_file)


def main1():
    sent_tokenizer = SentTokenizer()
    while True:
        text = input('text:')
        print("{}(={}):{}".format(0, sent_tokenizer.len_of(text), text))
        sentences = sent_tokenizer.tokenize_limited_length(text, max_len=10)
        for i, sentence in enumerate(sentences, start=1):
            print("{}(={}):{}".format(i, sent_tokenizer.len_of(sentence), sentence))


if __name__ == '__main__':
    # main()
    main1()
