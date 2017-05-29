from stemming.stemming import (apply_rule_1a, apply_rule_1b, apply_rule_1c,
                               apply_rule_2, apply_rule_3, apply_rule_4,
                               apply_rule_5a, apply_rule_5b, contains_vowel,
                               ends_cvc, ends_double_consonant, get_exceptions,
                               get_top_stems, is_consonant, measure, stem_word)

import pytest


class TestTopStems(object):

    def test_few_mappings(self):
        stem_mappings = {"stem1": [1, 2], "stem2": [4, 3, 2]}
        expected = ["stem2", "stem1"]

        actual = get_top_stems(stem_mappings)
        assert actual == expected

    def test_filter_mappings(self):
        stem_mappings = {"stem{i}".format(i=i): ["a"] * i for i in range(26)}
        expected = ["stem{i}".format(i=i) for i in range(25, 0, -1)]

        actual = get_top_stems(stem_mappings)
        assert actual == expected

    def test_keep_mappings(self):
        stem_mappings = {"stem{i}".format(i=i): ["a"] * i for i in range(26)}
        stem_mappings["stem0"] = ["a"]  # now tied for 25th place

        expected = ["stem{i}".format(i=i) for i in range(25, -1, -1)]

        actual = get_top_stems(stem_mappings)
        assert actual == expected


class TestStemWord(object):

    @staticmethod
    def _check_word_stem(word, stem):
        """
        Check that the word stemming output is independent of capitalization.

        Parameters
        ----------
        word : str
            The word to check.
        stem : str
            The expected stem to be generated.
        """

        assert stem_word(word) == stem
        assert stem_word(word.upper()) == stem
        assert stem_word(word.title()) == stem

    def test_small_word(self):
        word = "ai"
        stem = word.lower()
        self._check_word_stem(word, stem)

    @pytest.mark.parametrize("word,stem", get_exceptions().items())
    def test_exception(self, word, stem):
        self._check_word_stem(word, stem)

    @pytest.mark.parametrize("words,stem", [
        (["generate", "generator"], "gener"),
        (["succeed", "succeeding"], "succeed"),
        (["capricious"], "caprici"),
        (["doted", "doting"], "dote"),
        (["starring", "stars"], "star"),
        (["mischievous"], "mischiev"),
        (["asserted", "assertiveness"], "assert"),
        (["playings", "played"], "play"),
        (["unfortunately"], "unfortun"),
        (["quizzical"], "quizzic"),
        (["talk", "talks", "talked", "talking"], "talk")
    ])
    def test_general_vocab(self, words, stem):
        for word in words:
            self._check_word_stem(word, stem)


class TestIsConsonant(object):

    def test_is_vowel(self):
        word = "after"
        assert not is_consonant(word, 0)  # a
        assert not is_consonant(word, 3)  # e

        word = "unsocial"
        assert not is_consonant(word, 5)  # i
        assert not is_consonant(word, 3)  # o
        assert not is_consonant(word, 0)  # u

    def test_y_at_beginning(self):
        assert is_consonant("yak", 0)
        assert is_consonant("yonder", 0)

    def test_y_in_middle(self):
        assert is_consonant("away", 3)
        assert is_consonant("wayside", 2)

        assert not is_consonant("awry", 3)
        assert not is_consonant("wildly", 5)


class TestContainsVowel(object):

    def test_contains_vowel(self):
        assert contains_vowel("awry")
        assert contains_vowel("aside")
        assert contains_vowel("wildly")
        assert contains_vowel("invade")
        assert contains_vowel("underwear")
        assert contains_vowel("explicate")
        assert contains_vowel("openness")

    def test_contains_no_vowel(self):
        assert not contains_vowel("bbc")
        assert not contains_vowel("yz")


class TestEndsDoubleConsonant(object):

    def test_ends_double_consonant(self):
        assert ends_double_consonant("ill")
        assert ends_double_consonant("gatt")
        assert ends_double_consonant("profess")

    def test_no_ends_double_consonant(self):
        assert not ends_double_consonant("amputee")
        assert not ends_double_consonant("coffee")
        assert not ends_double_consonant("boo")


class TestEndsCVC(object):

    def test_ends_cvc(self):
        assert ends_cvc("al")
        assert ends_cvc("bal")
        assert ends_cvc("abel")

    def test_no_ends_cvc(self):
        assert not ends_cvc("yay")
        assert not ends_cvc("mouse")
        assert not ends_cvc("lovable")


class TestMeasure(object):

    def test_zero_measure(self):
        assert measure("tree") == 0
        assert measure("foo") == 0
        assert measure("bbc") == 0

    def test_positive_measure(self):
        assert measure("away") == 2
        assert measure("freed") == 1
        assert measure("monster") == 2


class TestApplyRule1A(object):

    def test_special_case(self):
        assert apply_rule_1a("dies") == "die"
        assert apply_rule_1a("lies") == "lie"

    def test_sess_es_case(self):
        assert apply_rule_1a("kisses") == "kiss"
        assert apply_rule_1a("misses") == "miss"

    def test_ies_i_case(self):
        assert apply_rule_1a("belies") == "beli"
        assert apply_rule_1a("mystifies") == "mystifi"

    def test_ss_ss_case(self):
        assert apply_rule_1a("caress") == "caress"
        assert apply_rule_1a("mistress") == "mistress"

    def test_s_none_case(self):
        assert apply_rule_1a("talks") == "talk"
        assert apply_rule_1a("monsters") == "monster"


class TestApplyRule1B(object):

    def test_special_case(self):
        assert apply_rule_1b("spied") == "spi"
        assert apply_rule_1b("died") == "die"

    def test_eed_ee_case(self):
        assert apply_rule_1b("freed") == "freed"
        assert apply_rule_1b("succeed") == "succee"

    def test_ed_ing_no_vowel(self):
        assert apply_rule_1b("bled") == "bled"
        assert apply_rule_1b("bing") == "bing"

    def test_ed_ing_vowel_special(self):
        assert apply_rule_1b("conflated") == "conflate"
        assert apply_rule_1b("troubled") == "trouble"
        assert apply_rule_1b("sized") == "size"

    def test_ed_ing_vowel_double_consonant(self):
        assert apply_rule_1b("hopping") == "hop"
        assert apply_rule_1b("tanned") == "tan"
        assert apply_rule_1b("sitting") == "sit"

    def test_ed_ing_vowel_cvc_ending(self):
        assert apply_rule_1b("smiled") == "smile"
        assert apply_rule_1b("filing") == "file"
        assert apply_rule_1b("lied") == "lie"

    def test_ed_ing_vowel_no_ending(self):
        assert apply_rule_1b("profiled") == "profil"
        assert apply_rule_1b("housed") == "hous"


class TestApplyRule1C(object):

    def test_y_consonant_precede(self):
        assert apply_rule_1c("happy") == "happi"
        assert apply_rule_1c("scrappy") == "scrappi"

    def test_y_no_has_vowel(self):
        assert apply_rule_1c("pay") == "pay"
        assert apply_rule_1c("buy") == "buy"


class TestApplyRule2(object):

    def test_recursive_call(self):
        assert apply_rule_2("relationalli") == "relate"
        assert apply_rule_2("conditionalli") == "condition"

    def test_suffix_replace(self):
        assert apply_rule_2("relational") == "relate"
        assert apply_rule_2("conditional") == "condition"
        assert apply_rule_2("valenci") == "valence"
        assert apply_rule_2("hesitanci") == "hesitance"
        assert apply_rule_2("digitizer") == "digitize"
        assert apply_rule_2("conformabli") == "conformable"
        assert apply_rule_2("radicalli") == "radical"
        assert apply_rule_2("differentli") == "different"
        assert apply_rule_2("vileli") == "vile"
        assert apply_rule_2("analogousli") == "analogous"
        assert apply_rule_2("vietnamization") == "vietnamize"
        assert apply_rule_2("predication") == "predicate"
        assert apply_rule_2("operator") == "operate"
        assert apply_rule_2("feudalism") == "feudal"
        assert apply_rule_2("decisiveness") == "decisive"
        assert apply_rule_2("hopefulness") == "hopeful"
        assert apply_rule_2("callousness") == "callous"
        assert apply_rule_2("formaliti") == "formal"
        assert apply_rule_2("sensitiviti") == "sensitive"
        assert apply_rule_2("sensibiliti") == "sensible"

    def test_logi_replace(self):
        assert apply_rule_2("geologi") == "geolog"
        assert apply_rule_2("theologi") == "theolog"
        assert apply_rule_2("archaeologi") == "archaeolog"


class TestApplyRule3(object):

    def test_suffix_replace(self):
        assert apply_rule_3("duplicate") == "duplic"
        assert apply_rule_3("formative") == "form"
        assert apply_rule_3("formalize") == "formal"
        assert apply_rule_3("electriciti") == "electric"
        assert apply_rule_3("electrical") == "electric"
        assert apply_rule_3("hopeful") == "hope"
        assert apply_rule_3("goodness") == "good"


class TestApplyRule4(object):

    def test_suffix_replace(self):
        assert apply_rule_4("revival") == "reviv"
        assert apply_rule_4("allowance") == "allow"
        assert apply_rule_4("inference") == "infer"
        assert apply_rule_4("airliner") == "airlin"
        assert apply_rule_4("gyroscopic") == "gyroscop"
        assert apply_rule_4("adjustable") == "adjust"
        assert apply_rule_4("defensible") == "defens"
        assert apply_rule_4("irritant") == "irrit"
        assert apply_rule_4("replacement") == "replac"
        assert apply_rule_4("adjustment") == "adjust"
        assert apply_rule_4("dependent") == "depend"
        assert apply_rule_4("homologou") == "homolog"
        assert apply_rule_4("communism") == "commun"
        assert apply_rule_4("activate") == "activ"
        assert apply_rule_4("angulariti") == "angular"
        assert apply_rule_4("homologous") == "homolog"
        assert apply_rule_4("effective") == "effect"
        assert apply_rule_4("bowdlerize") == "bowdler"

    def test_ion_replace(self):
        assert apply_rule_4("adoption") == "adopt"
        assert apply_rule_4("vision") == "vision"


class TestApplyRule5A(object):

    def test_replace_stem_greater_one(self):
        assert apply_rule_5a("retaliate") == "retaliat"
        assert apply_rule_5a("probate") == "probat"
        assert apply_rule_5a("rate") == "rate"

    def test_replace_stem_equal_one(self):
        assert apply_rule_5a("grease") == "greas"
        assert apply_rule_5a("cease") == "ceas"


class TestApplyRule5B(object):

    def test_replace_suffix(self):
        assert apply_rule_5b("controll") == "control"
        assert apply_rule_5b("compell") == "compel"
        assert apply_rule_5b("roll") == "roll"
        assert apply_rule_5b("mill") == "mill"
