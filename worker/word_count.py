from collections import defaultdict
import re
import sys
from stop_words import STOP_WORD_SET

PUNCTUATION_RE = re.compile("[%s]" % re.escape(
    """!"&()*+,-\.\/:;<=>?\[\\\]^`\{|\}~]+"""))
DISCARD_RE = re.compile("^('{|`|git@|@|https?:)")

def remove_stop_words(word_seq, stop_words):
    """Sanitize using intersection and list.remove()"""
    stop_words = set(stop_words)
    for sw in stop_words.intersection(word_seq):
        while sw in word_seq:
            word_seq.remove(sw)

    return word_seq

def remove_punctuation(word_seq):
    def remove_punc_inner(word):
        return PUNCTUATION_RE.sub("", word)
    return map(remove_punc_inner, word_seq)

def filter_discards(word_seq):
    def discard(word):
        return not DISCARD_RE.match(word)
    return filter(discard, word_seq)

def count_words_from_seq(word_seq):
    word_count = defaultdict(int)
    for word in word_seq:
        word_count[word] += 1
    return word_count

def count_words(text_blob):
    word_seq = re.split('[=|\s]+', text_blob.lower())
    word_seq = filter_discards(word_seq)
    word_seq = remove_punctuation(word_seq)
    word_seq = [w for w in word_seq if w]
    word_seq = remove_stop_words(word_seq, STOP_WORD_SET)
    return count_words_from_seq(word_seq)

if __name__ == '__main__':
    print count_words(sys.stdin.read())
