from collections import defaultdict
import re
import sys
from stop_words import STOP_WORD_SET
from collections import Counter

PUNCTUATION_RE = re.compile("[%s]" % re.escape(
    """!"&()*+,-\.\/:;<=>?\[\\\]^`\{|\}~]+"""))
DISCARD_RE = re.compile("^('{|`|git@|@|https?:)")

def remove_stop_words(word_seq, stop_words):
    """Sanitize using intersection and list.remove()"""
    return [w for w in word_seq if w and w not in stop_words]

def remove_punctuation(word_seq):
    def remove_punc_inner(word):
        return PUNCTUATION_RE.sub("", word)
    removed = map(remove_punc_inner, word_seq)
    # Remove emptry strings
    return [w for w in removed if w]

def filter_discards(word_seq):
    def discard(word):
        return not DISCARD_RE.match(word)
    return filter(discard, word_seq)

def count_words_from_seq(word_seq):
    word_count = defaultdict(int)
    for word in word_seq:
        word_count[word] += 1
    return word_count

def keep_top_n_words(word_counts, n):
    return dict(Counter(word_counts).most_common(n))


def count_words(text_blob):
    word_seq = re.split('[=|\s]+', text_blob.lower())
    print '     Splitting blob'
    word_seq = filter_discards(word_seq)
    print '     Filtering discards'
    word_seq = remove_punctuation(word_seq)
    print '     Removing punctuation'
    word_seq = remove_stop_words(word_seq, STOP_WORD_SET)
    print '     Removing stop words'
    word_counts = count_words_from_seq(word_seq)
    print '     Counting words'
    top_n = keep_top_n_words(word_counts, 100)
    print '     Filtering to top 100 words'
    return top_n

if __name__ == '__main__':
    print count_words(sys.stdin.read())
