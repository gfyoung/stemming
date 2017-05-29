"""
Main stemming functionality.
"""


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
        stems = [stem for stem in stems if stem_counts[stem] >= bottom_count]

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
        stem_mappings[stem] = stem_mappings[stem] + [word]

    return stem_mappings


def stem_word(word):
    """
    Stem a word and return the produced stem.

    Parameters
    ----------
    word : str
        The word that we are to stem.

    Returns
    -------
    word_stem : str
        The stem produced from parsing this word.
    """

    return word
