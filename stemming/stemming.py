"""
Main stemming functionality.
"""

import os
import sys


def memoize(f):
    """
    Memoize a function.

    Parameters
    ----------
    f : callable
        The function that we are to memoize.

    Returns
    -------
    memo_f : callable
        The memoized version of `f`.
    """

    cache = {}

    def wrapper(*args, **kwargs):
        key = args + tuple(kwargs.keys()) + tuple(kwargs)

        if key not in cache:
            cache[key] = f(*args, **kwargs)

        return cache[key]

    return wrapper


def get_top_stems(stem_mappings):
    """
    Get the top 25 stems or words found in a document.

    Parameters
    ----------
    stem_mappings : dict
        The stem mappings from which
    """

    stems = list(stem_mappings.keys())
    stem_counts = {stem: len(stem_mappings[stem]) for stem in stem_mappings}

    stems.sort(key=lambda k: (stem_counts[k], k), reverse=True)

    if len(stems) > 25:
        bottom_count = len(stem_mappings[stems[24]])
        stems = [(stem, stem_counts[stem]) for stem in stems
                 if stem_counts[stem] >= bottom_count]
    else:
        stems = [(stem, stem_counts[stem]) for stem in stems]

    return stems


def stem_document(document):
    """
    Stem the words in a document and return mappings from stem to words.

    Parameters
    ----------
    document : str
        Document whose words we are parsing.

    Returns
    -------
    stem_mappings : dict
        A mapping from stem to list of words whose stem was the same.
    """

    stem_mappings = {}
    words = document.split()

    for word in words:
        stem = stem_word(word)
        stem_mappings[stem] = stem_mappings.get(stem, []) + [word]

    return stem_mappings


@memoize
def load_dictionary():
    """
    Load the dictionary of English words that we use to check strings.

    Returns
    -------
    english_dict : set
        The set of valid English words.
    """

    try:
        file_path = __file__
    except NameError:
        file_path = os.path.join(os.getcwd(), sys.argv[0])

    directory = os.path.dirname(file_path)
    dictionary = os.path.join(directory, "dictionary.txt")

    with open(dictionary, "r") as f:
        return {word.strip() for word in f}


@memoize
def get_exceptions():
    """
    Get exceptions that are independent of the rules we use to stem words.

    Returns
    -------
    exceptions_mappings : dict
        A list of exceptions mapping a word to its appropriate stem.
    """

    exceptions_reversed = {
        "sky": ["sky", "skies"],
        "die": ["dying"],
        "lie": ["lying"],
        "tie": ["tying"],
        "news": ["news"],
        "inning": ["innings", "inning"],
        "outing": ["outings", "outing"],
        "canning": ["cannings", "canning"],
        "howe": ["howe"],
        "proceed": ["proceed"],
        "exceed": ["exceed"],
        "succeed": ["succeed"],
    }

    exception_mappings = {}

    for stem, exceptions in exceptions_reversed.items():
        for exception in exceptions:
            exception_mappings[exception] = stem

    return exception_mappings


def stem_word(word):
    """
    Stem a word and return the produced stem. Based on Porter (1980).

    The major difference between our implementation and that in Porter (1980)
    and subsequent work that has built on top of his algorithm is that we are
    returning valid English words if possible, not stems, which can often be
    non-English words.

    Parameters
    ----------
    word : str
        The word that we are to stem.

    Returns
    -------
    word_stem : str
        The stem produced from parsing this word.
    """

    word = normalize_word(word)
    if not is_valid_word(word):
        return word

    exception_mappings = get_exceptions()
    if word in exception_mappings:
        return exception_mappings[word]

    # Words like these are too small
    if len(word) <= 2:
        return word

    # We want to return an actual word
    # as the stem, so we need to keep
    # track of our last known valid word.
    current_word = word

    word = apply_rule_1a(word)
    current_word = word if is_valid_word(word) else current_word

    word = apply_rule_1b(word)
    current_word = word if is_valid_word(word) else current_word

    word = apply_rule_1c(word)
    current_word = word if is_valid_word(word) else current_word

    word = apply_rule_2(word)
    current_word = word if is_valid_word(word) else current_word

    word = apply_rule_3(word)
    current_word = word if is_valid_word(word) else current_word

    word = apply_rule_4(word)
    current_word = word if is_valid_word(word) else current_word

    word = apply_rule_5a(word)
    current_word = word if is_valid_word(word) else current_word

    word = apply_rule_5b(word)
    current_word = word if is_valid_word(word) else current_word

    return current_word


def get_extraneous_chars():
    """
    Return a string of extraneous characters that we can strip from words.

    Returns
    -------
    extraneous_chars : str
        A string containing all extraneous characters we can remove.
    """

    return " \t\n\r!?.,()@#&*^\"\'"


def normalize_word(word):
    """
    Normalize word by lower-casing all letters and stripping punctuation.

    Parameters
    ----------
    word : str
        The word to normalize.

    Returns
    -------
    normalized_word : str
        The normalized version of the word.
    """

    word = word.lower()
    word = word.strip(get_extraneous_chars())

    return word


def is_valid_word(word):
    """
    Check if the word provided is a valid US English word.

    Parameters
    ----------
    word : str
        The word to check.

    Returns
    -------
    valid_word : bool
        Whether or not the word is a valid US English word.
    """

    word_dict = load_dictionary()
    return word in word_dict


def is_consonant(word, i):
    """
    Check if the letter at index `i` of `word` is a consonant.

    Per Porter (1980), a consonant is a letter not in {'a', 'e',
    'i', 'o', 'u'} and is not a 'y' preceded by a consonant.

    Letters that are not consonants are thereby vowels. Note that
    we implement consonant checking because there are more cases
    where we want consonants than vowels in other stemming checks.

    Parameters
    ----------
    word : str
        The word whose letter we are checking. Assumed lowercase.
    i : int
        The index corresponding to the letter we are checking.

    Returns
    -------
    is_consonant : bool
        Whether or not the letter at the index in the word is a consonant.
    """

    vowels = {"a", "e", "i", "o", "u"}

    if word[i] in vowels:
        return False

    if word[i] == "y":
        if i == 0:
            return True
        else:
            return not (is_consonant(word, i - 1))

    return True


def contains_vowel(stem):
    """
    Check whether a stem contains a vowel.

    Parameters
    ----------
    stem : str
        The stem that we are checking. We assume all letters are lowercase.

    Returns
    -------
    contains_vowel : bool
        Whether or not the stem contains a vowel.
    """

    for i in range(len(stem)):
        if not is_consonant(stem, i):
            return True

    return False


def ends_double_consonant(word):
    """
    Check whether a word ends with a double consonant.

    Parameters
    ----------
    word : str
        The word to check. We assume all letters are lowercase.

    Returns
    -------
    ends_with_double_consonant : bool
        Whether or not the word ends with a double consonant.
    """

    if len(word) >= 2:
        if word[-1] == word[-2]:
            return is_consonant(word, len(word) - 1)

    return False


def ends_cvc(word):
    """
    Check whether a word ends with a CVC pattern.

    C means a consonant, and V means a vowel per Porter (1980). The second C
    must not be one of "w", "x" or "y".

    Subsequent implementations have included an additional check for words of
    length-2 in that they must contain the VC portion, without the restriction
    on the "second" C since it is now the first C. We implement that check too.

    Parameters
    ----------
    word : str
        The word to check. We assume all letters are lowercase.

    Returns
    -------
    ends_with_cvc : bool
        Whether or not the word ends with a CVC pattern.
    """

    if len(word) == 2:
        return not is_consonant(word, 0) and is_consonant(word, 1)

    elif len(word) >= 3:
        return (is_consonant(word, len(word) - 3) and
                not is_consonant(word, len(word) - 2) and
                is_consonant(word, len(word) - 1) and
                word[-1] not in {"w", "x", "y"})

    return False


def measure(stem):
    """
    Return the measure of a stem.

    Per Porter (1980), the measurement is the count of number of pairs
    consecutive vowel-consonant pairs.

    For example, the word "tree" has no consecutive vowel-consonant pairs,
    so its measure is zero. However, the word "monster" has two vowel-
    consonant pairs ("on" and "er"), so its measure is two.

    Parameters
    ----------
    stem : str
        The stem that we are to measure. We assume all letters are lowercase.
    """

    cv_sequence = ""

    for i in range(len(stem)):
        consonant = is_consonant(stem, i)
        cv_sequence += "c" if consonant else "v"

    return cv_sequence.count("vc")


def apply_rule_1a(word):
    """
    Apply Rule 1a from Porter (1980).

    SSES -> SS                         caresses  ->  caress
    IES  -> I                          ponies    ->  poni
                                       ties      ->  ti
    SS   -> SS                         caress    ->  caress
    S    ->                            cats      ->  cat

    Parameters
    ----------
    word : str
        The word to process. We assume all letters are lowercase.

    Returns
    -------
    processed_word : str
        The word processed with Rule 1a.
    """

    # "dies" --> "die" but not "flies" --> "flie"
    #
    # "ies" --> "ie" suffix change special case
    if word.endswith("ies") and len(word) == 4:
        return word[:-1]

    # "sess" --> "ss"
    # "ies"  --> "i"
    if word.endswith("sses") or word.endswith("ies"):
        word = word[:-2]

    # "ss"   --> "ss"
    # "s"    --> ""
    elif not word.endswith("ss") and word.endswith("s"):
        word = word[:-1]

    return word


def apply_rule_1b(word):
    """
    Apply Rule 1b from Porter (1980).

    (m>0) EED -> EE                    feed      ->  feed
                                       agreed    ->  agree
    (*v*) ED  ->                       plastered ->  plaster
                                       bled      ->  bled
    (*v*) ING ->                       motoring  ->  motor
                                       sing      ->  sing


    If the second or third of the rules in Step 1b is successful,
    the following is done:

    AT -> ATE                       conflat(ed)  ->  conflate
    BL -> BLE                       troubl(ed)   ->  trouble
    IZ -> IZE                       siz(ed)      ->  size
    (*d and not (*L or *S or *Z))
       -> single letter
                                    hopp(ing)    ->  hop
                                    tann(ed)     ->  tan
                                    fall(ing)    ->  fall
                                    hiss(ing)    ->  hiss
                                    fizz(ed)     ->  fizz
    (m=1 and *o) -> E               fail(ing)    ->  fail
                                    fil(ing)     ->  file

    The rule to map to a single letter causes the removal of one of the
    double letter pair. The -E is put back on -AT, -BL and -IZ, so that
    the suffixes -ATE, -BLE and -IZE can be recognised later. This E may
    be removed in step 4.

    Parameters
    ----------
    word : str
        The word to process. We assume all letters are lowercase.

    Returns
    -------
    processed_word : str
        The word processed with Rule 1b.
    """

    # We want words like "spied" to be stemmed as "spi" and words like
    # "died" to be stemmed as "died" for subsequent analysis.
    if word.endswith("ied"):
        if len(word) == 4:
            # "ied" --> "ie"
            return word[:-1]
        else:
            # "ied" --> "i"
            return word[:-2]

    # "eed" --> "ee" if measure > 0, else return original word
    if word.endswith("eed"):
        stem = word[:-3]
        return stem + "ee" if measure(stem) > 0 else word

    # "ed" --> "" if stem contains vowel, else return original word
    # "ing" --> "" if stem contains vowel, else return original word
    stem = None

    for suffix in ["ed", "ing"]:
        if word.endswith(suffix):
            test_stem = word[:-len(suffix)]

            if contains_vowel(test_stem):
                stem = test_stem
                break

    if not stem:
        return word

    # "at" --> "ate"
    # "bl" --> "ble"
    # "iz" --> "ize"
    if stem.endswith("at") or stem.endswith("bl") or stem.endswith("iz"):
        return stem + "e"

    # double-consonant --> single consonant if not "l", "s", or "z"
    if ends_double_consonant(stem) and stem[-1] not in {"l", "s", "z"}:
        return stem[:-1]

    # add "e" to end of word if stem measure is 1 and ends with CVC
    if measure(stem) == 1 and ends_cvc(stem):
        return stem + "e"

    return stem


def apply_rule_1c(word):
    """
    Apply Rule 1c from Porter (1980).

    (*v*) Y -> I                    happy        ->  happi
                                    sky          ->  sky

    We don't follow this rule strictly though. Some inconsistencies were
    found with this rule (e.g. "enjoy" vs. "enjoyment"). In this case, the
    condition for this rule will be that the "y" must be preceded with a
    consonant for this change to occur.

    As a result, "sky" actually becomes "ski" in our case (that's why it's
    included as one of the exceptions in `get_exceptions`).

    Parameters
    ----------
    word : str
        The word to process. We assume all letters are lowercase.

    Returns
    -------
    processed_word : str
        The word processed with Rule 1c.
    """

    if word.endswith("y"):
        stem = word[:-1]

        if len(stem) > 1 and is_consonant(stem, len(stem) - 1):
            return stem + "i"

    return word


def apply_rule_2(word):
    """
    Apply Rule 2 from Porter (1980).

    (m>0) ATIONAL ->  ATE           relational     ->  relate
    (m>0) TIONAL  ->  TION          conditional    ->  condition
                                    rational       ->  rational
    (m>0) ENCI    ->  ENCE          valenci        ->  valence
    (m>0) ANCI    ->  ANCE          hesitanci      ->  hesitance
    (m>0) IZER    ->  IZE           digitizer      ->  digitize
    (m>0) ABLI    ->  ABLE          conformabli    ->  conformable
    (m>0) ALLI    ->  AL            radicalli      ->  radical
    (m>0) ENTLI   ->  ENT           differentli    ->  different
    (m>0) ELI     ->  E             vileli        - >  vile
    (m>0) OUSLI   ->  OUS           analogousli    ->  analogous
    (m>0) IZATION ->  IZE           vietnamization ->  vietnamize
    (m>0) ATION   ->  ATE           predication    ->  predicate
    (m>0) ATOR    ->  ATE           operator       ->  operate
    (m>0) ALISM   ->  AL            feudalism      ->  feudal
    (m>0) IVENESS ->  IVE           decisiveness   ->  decisive
    (m>0) FULNESS ->  FUL           hopefulness    ->  hopeful
    (m>0) OUSNESS ->  OUS           callousness    ->  callous
    (m>0) ALITI   ->  AL            formaliti      ->  formal
    (m>0) IVITI   ->  IVE           sensitiviti    ->  sensitive
    (m>0) BILITI  ->  BLE           sensibiliti    ->  sensible

    Parameters
    ----------
    word : str
        The word to process. We assume all letters are lowercase.

    Returns
    -------
    processed_word : str
        The word processed with Rule 2.
    """

    # "alli" --> "al" and then re-apply Rule 2.
    if word.endswith("alli") and measure(word[:-4]) > 0:
        return apply_rule_2(word[:-2])

    for suffix, replacement in [
        ("ational", "ate"),
        ("tional", "tion"),
        ("enci", "ence"),
        ("anci", "ance"),
        ("izer", "ize"),
        ("bli", "ble"),
        ("alli", "al"),
        ("entli", "ent"),
        ("eli", "e"),
        ("ousli", "ous"),
        ("ization", "ize"),
        ("ation", "ate"),
        ("ator", "ate"),
        ("alism", "al"),
        ("iveness", "ive"),
        ("fulness", "ful"),
        ("ousness", "ous"),
        ("aliti", "al"),
        ("iviti", "ive"),
        ("biliti", "ble"),
        ("fulli", "ful"),
    ]:
        if word.endswith(suffix) and measure(word[:-len(suffix)]) > 0:
            return word[:-len(suffix)] + replacement

    # "logi" --> "log" (include "l" in stem for consistency between
    # shorter stems like "geo" and longer ones like "philo").
    if word.endswith("logi") and measure(word[:-3]) > 0:
        return word[:-1]

    return word


def apply_rule_3(word):
    """
    Apply Rule 3 from Porter (1980).

    (m>0) ICATE ->  IC              triplicate     ->  triplic
    (m>0) ATIVE ->                  formative      ->  form
    (m>0) ALIZE ->  AL              formalize      ->  formal
    (m>0) ICITI ->  IC              electriciti    ->  electric
    (m>0) ICAL  ->  IC              electrical     ->  electric
    (m>0) FUL   ->                  hopeful        ->  hope
    (m>0) NESS  ->                  goodness       ->  good

    Parameters
    ----------
    word : str
        The word to process. We assume all letters are lowercase.

    Returns
    -------
    processed_word : str
        The word processed with Rule 3.
    """

    for suffix, replacement in [
        ("icate", "ic"),
        ("ative", ""),
        ("alize", "al"),
        ("iciti", "ic"),
        ("ical", "ic"),
        ("ful", ""),
        ("ness", ""),
    ]:
        if word.endswith(suffix) and measure(word[:-len(suffix)]) > 0:
            return word[:-len(suffix)] + replacement

    return word


def apply_rule_4(word):
    """
    Apply Rule 4 from Porter (1980).

    (m>1) AL    ->                  revival        ->  reviv
    (m>1) ANCE  ->                  allowance      ->  allow
    (m>1) ENCE  ->                  inference      ->  infer
    (m>1) ER    ->                  airliner       ->  airlin
    (m>1) IC    ->                  gyroscopic     ->  gyroscop
    (m>1) ABLE  ->                  adjustable     ->  adjust
    (m>1) IBLE  ->                  defensible     ->  defens
    (m>1) ANT   ->                  irritant       ->  irrit
    (m>1) EMENT ->                  replacement    ->  replac
    (m>1) MENT  ->                  adjustment     ->  adjust
    (m>1) ENT   ->                  dependent      ->  depend
    (m>1 and (*S or *T)) ION ->     adoption       ->  adopt
    (m>1) OU    ->                  homologou      ->  homolog
    (m>1) ISM   ->                  communism      ->  commun
    (m>1) ATE   ->                  activate       ->  activ
    (m>1) ITI   ->                  angulariti     ->  angular
    (m>1) OUS   ->                  homologous     ->  homolog
    (m>1) IVE   ->                  effective      ->  effect
    (m>1) IZE   ->                  bowdlerize     ->  bowdler

    Parameters
    ----------
    word : str
        The word to process. We assume all letters are lowercase.

    Returns
    -------
    processed_word : str
        The word processed with Rule 4.
    """

    for suffix in ["al", "ance", "ence", "er", "ic", "able",
                   "ible", "ant", "ement", "ment", "ent"]:
        if word.endswith(suffix) and measure(word[:-len(suffix)]) > 1:
            return word[:-len(suffix)]

    if word.endswith("ion"):
        stem = word[:-3]

        if measure(stem) > 1 and stem[-1] in {"s", "t"}:
            return stem

    for suffix in ["ou", "ism", "ate", "iti", "ous", "ive", "ize"]:
        if word.endswith(suffix) and measure(word[:-len(suffix)]) > 1:
            return word[:-len(suffix)]

    return word


def apply_rule_5a(word):
    """
    Apply Rule 5a from Porter (1980).

    (m>1) AL    ->                  revival        ->  reviv
    (m>1) ANCE  ->                  allowance      ->  allow
    (m>1) ENCE  ->                  inference      ->  infer
    (m>1) ER    ->                  airliner       ->  airlin
    (m>1) IC    ->                  gyroscopic     ->  gyroscop
    (m>1) ABLE  ->                  adjustable     ->  adjust
    (m>1) IBLE  ->                  defensible     ->  defens
    (m>1) ANT   ->                  irritant       ->  irrit
    (m>1) EMENT ->                  replacement    ->  replac
    (m>1) MENT  ->                  adjustment     ->  adjust
    (m>1) ENT   ->                  dependent      ->  depend
    (m>1 and (*S or *T)) ION ->     adoption       ->  adopt
    (m>1) OU    ->                  homologou      ->  homolog
    (m>1) ISM   ->                  communism      ->  commun
    (m>1) ATE   ->                  activate       ->  activ
    (m>1) ITI   ->                  angulariti     ->  angular
    (m>1) OUS   ->                  homologous     ->  homolog
    (m>1) IVE   ->                  effective      ->  effect
    (m>1) IZE   ->                  bowdlerize     ->  bowdler

    Parameters
    ----------
    word : str
        The word to process. We assume all letters are lowercase.

    Returns
    -------
    processed_word : str
        The word processed with Rule 5a.
    """

    # "e" --> ""
    if word.endswith("e"):
        stem = word[:-1]

        if measure(stem) > 1:
            return stem

        if measure(stem) == 1 and not ends_cvc(stem):
            return stem

    return word


def apply_rule_5b(word):
    """
    Apply Rule 5b from Porter (1980).

    (m > 1 and *d and *L) -> single letter
                                    controll       ->  control
                                    roll           ->  roll

    Parameters
    ----------
    word : str
        The word to process. We assume all letters are lowercase.

    Returns
    -------
    processed_word : str
        The word processed with Rule 5b.
    """

    # "ll" --> "l"
    if word.endswith("ll") and measure(word[:-1]) > 1:
        return word[:-1]

    return word
