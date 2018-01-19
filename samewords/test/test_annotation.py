import pytest

from samewords import settings, cli
from samewords.annotate import *

no_proximity_match = r"""sw \edtext{so}{\lemma{so}\Bfootnote{foot content}}  and again sw it is all and something after."""

three_close_levels = r"""so \edtext{\edtext{\edtext{so}{\lemma{so}\Bfootnote{lev 3}}}{\lemma{so}\Bfootnote{lev 2}}}{\lemma{so}\Bfootnote{lev 1}}"""
three_close_levels_result = r"""\sameword{so} \edtext{\edtext{\edtext{\sameword[1,2,3]{so}}{\lemma{\sameword{so}}\Bfootnote{lev 3}}}{\lemma{\sameword{so}}\Bfootnote{lev 2}}}{\lemma{\sameword{so}}\Bfootnote{lev 1}}"""

flat_proximity_match = r"""so sw \edtext{so}{\lemma{so}\Bfootnote{foot content}}  and again sw it is all and something after."""
flat_proximity_match_result = r"\sameword{so} sw \edtext{\sameword[1]{so}}{\lemma{\sameword{so}}\Bfootnote{foot content}}  and again sw it is all and something after."

false_positives = r"\edtext{in}{\lemma{in}\Bfootnote{note content}} species intelligibilis imaginatur secundum Apostolum\index[persons]{}."

nested_1 = r"""sw \emph{so} \edtext{so}{\lemma{so}\Bfootnote{foot content}} \emph{so} \edtext{so}{\lemma{so}\Bfootnote{foot content}} \edtext{sw so \edtext{\edtext{sw}{\lemma{sw}\Bfootnote{B note here}} thing}{\lemma{sw thing}\Bfootnote{B footnote her}} and again sw it is all}{\lemma{sw \ldots all}\Afootnote{sw critical note}} and something after."""
nested_1_result = r"""sw \emph{\sameword{so}} \edtext{\sameword[1]{so}}{\lemma{\sameword{so}}\Bfootnote{foot content}} \emph{\sameword{so}} \edtext{\sameword[1]{so}}{\lemma{\sameword{so}}\Bfootnote{foot content}} \edtext{\sameword[1]{sw} \sameword{so} \edtext{\edtext{\sameword[2,3]{sw}}{\lemma{\sameword{sw}}\Bfootnote{B note here}} thing}{\lemma{\sameword{sw} WTF THIS IS NOT RIGHT"""

nested_ambiguity = r"""before and \edtext{first here \edtext{and another \edtext{and}{\lemma{and}\Afootnote{lvl 3}} that's it}{\lemma{and \dots{} it}\Afootnote{lvl 2}}}{\lemma{first \dots{} it}\Afootnote{note lvl 1}} after"""
nested_ambiguity_result = r"""before \sameword{and} \edtext{first here \edtext{\sameword[2]{and} another \edtext{\sameword[3]{and}}{\lemma{\sameword{and}}\Afootnote{lvl 3}} that's it}{\lemma{\sameword{and} \dots{} it}\Afootnote{lvl 2}}}{\lemma{first \dots{} it}\Afootnote{note lvl 1}} after"""

nested_ldots_lemma = r"""sw and \edtext{sw so \edtext{\edtext{sw}{\lemma{sw}\Bfootnote{lvl 3 note}} another thing \edtext{and more}{\lemma{and more}\Bfootnote{lvl 3 note}}}{\lemma{sw another thing and more}\Bfootnote{lvl 2 note}}}{\lemma{sw \ldots more}\Afootnote{lvl 1 note}} and a sw after and one more \edtext{flat}{\lemma{flat}\Bfootnote{note here}} entry."""
nested_ldots_lemma_result = r"""\sameword{sw} and \edtext{\sameword[1]{sw} so \edtext{\edtext{\sameword[3]{sw}}{\lemma{\sameword{sw}}\Bfootnote{lvl 3 note}} another thing \edtext{and \sameword[1]{more}}{\lemma{and more}\Bfootnote{lvl 3 note}}}{\lemma{sw another thing and more}\Bfootnote{lvl 2 note}}}{\lemma{\sameword{sw} \ldots \sameword{more}}\Afootnote{lvl 1 note}} and a \sameword{sw} after and one \sameword{more} \edtext{flat}{\lemma{flat}\Bfootnote{note here}} entry."""

nested_dots_lemma = r"""sw and \edtext{sw so \edtext{\edtext{sw}{\lemma{sw}\Bfootnote{B note here}} another thing}{\lemma{sw another thing}\Bfootnote{B footnote her}}}{\lemma{sw \dots thing}\Afootnote{ critical note}} and a sw after."""

flat_ldots_lemma = r"""sw and \edtext{sw so sw another thing}{\lemma{sw \ldots thing}\Afootnote{ critical note}} and a sw after."""
flat_ldots_lemma_result = r"""\sameword{sw} and \edtext{\sameword[1]{sw} so sw another thing}{\lemma{\sameword{sw} \ldots thing}\Afootnote{ critical note}} and a \sameword{sw} after."""

multiword_lemma = r"""per multa per causam tamen scire \edtext{causam}{\lemma{causam}\Bfootnote{fnote}} est \edtext{per causam}{\lemma{per causam}\Bfootnote{causam rei B}} cognoscere \edtext{causam}{\lemma{causam}\Bfootnote{fnote}}."""
multiword_lemma_result = r"""per multa \sameword{per \sameword{causam}} tamen scire \edtext{\sameword[1]{causam}}{\lemma{\sameword{causam}}\Bfootnote{fnote}} est \edtext{\sameword[1]{per \sameword{causam}}}{\lemma{\sameword{per causam}}\Bfootnote{causam rei B}} cognoscere \edtext{\sameword[1]{causam}}{\lemma{\sameword{causam}}\Bfootnote{fnote}}."""

long_proximate_before_after = r"""List comprehensions provide a concise a way to create lists. Common applications are to make new lists where each element is the result of some operations applied to each member of another sequence or iterable, or \edtext{to}{\lemma{to}\Bfootnote{note}} create a subsequence of those elements that satisfy a certain condition. List comprehensions provide a concise way to create lists. \edtext{Common}{\lemma{Common}\Bfootnote{note}} applications are to make new lists where each element is the result of some operations applied to each member of another sequence or iterable, or to create a subsequence of those elements that satisfy a certain condition. Start \edtext{a}{\lemma{a}\Bfootnote{lvl 1}} and another a List comprehensions provide a concise way to create lists. Common applications are to make new lists where each element is the result of some operations applied to each member of another sequence or iterable, or to create a subsequence \edtext{of}{\lemma{of}\Bfootnote{note}} those elements that satisfy a certain condition."""
long_proximate_before_after_result = r"""List comprehensions provide a concise a way \sameword{to} create lists. Common applications are \sameword{to} make new lists where each element is the result of some operations applied \sameword{to} each member of another sequence or iterable, or \edtext{\sameword[1]{to}}{\lemma{\sameword{to}}\Bfootnote{note}} create a subsequence of those elements that satisfy a certain condition. List comprehensions provide a concise way \sameword{to} create lists. \edtext{Common}{\lemma{Common}\Bfootnote{note}} applications are to make new lists where each element is the result of some operations applied to each member of another sequence or iterable, or to create \sameword{a} subsequence of those elements that satisfy \sameword{a} certain condition. Start \edtext{\sameword[1]{a}}{\lemma{\sameword{a}}\Bfootnote{lvl 1}} and another \sameword{a} List comprehensions provide \sameword{a} concise way to create lists. Common applications are to make new lists where each element is the result \sameword{of} some operations applied to each member \sameword{of} another sequence or iterable, or to create \sameword{a} subsequence \edtext{\sameword[1]{of}}{\lemma{\sameword{of}}\Bfootnote{note}} those elements that satisfy a certain condition."""

nested_2 = r"""Sed hic occurrunt arduae difficultates; et primo consideranda est descriptio fidei quam ponit \name{Apostolus\index[persons]{}}, scilicet, \edtext{\enquote{fides \edtext{est}{\lemma{est}\Bfootnote{\emph{om.} R}} substantia rerum sperandarum, argumentum non apparentium.}}{\lemma{}\Afootnote[nosep]{Hebrews 11:1}} Ubi secundum \edtext{\name{Altissiodorensis\index[persons]{}} \edtext{in}{\lemma{in}\Bfootnote{\emph{om.} R SV S}} principio suae \worktitle{Summae}\index[works]{}}{\lemma{}\Afootnote[nosep]{Guillelmus Auxerre \worktitle{Summa aurea}}} et \edtext{\name{\edtext{Guillelmum}{\lemma{Guillelmum}\Bfootnote{guillelmi R}} Parisiensis \index[persons]{}} tractatu suo \worktitle{De fide et legibus}\index[works]{}}{\lemma{}\Afootnote[nosep]{Guillelmus Parisiensis, \worktitle{de fide et legibus}}} sit una comparatio fidei, respectu credendorum, et caritatis, respectu amandorum; unde imaginatur quod sicut caritas dirigit hominem ad diligendum Deum propter se, ita proportionaliter fides inclinat intellectum ad credendum primae veritati propter se et \edtext{super}{\lemma{super}\Bfootnote{supra V}} omnia sine alia apparentia. Ideo fides est argumentum, et non est consequens nec conclusio. Ideo sicut inquit \name{\edtext{Guillelmus}{\lemma{Guillelmus}\Bfootnote{\emph{om.} V}} Altissiodorensis\index[persons]{}} \edtext{\enquote{a quodam bene dictum est quod apud Aristotelem\index[persons]{} argumentum est ratio rei dubiae faciens fidem, apud autem Christum est\edtext{}{\lemma{}\Bfootnote[nosep]{\emph{iter.} R SV; The double "est" in R and SV seems like a clear mistake, though good corroboration of the intimate relationship between these two witnesses.}} fides faciens rationem}}{\lemma{}\Afootnote[nosep]{Guillelmus Auxerre, \worktitle{Summa aurea}\index[works]{}, prologus.This formulation has been identified by Marie-dominique Chenu as originating with Simon de Tornai; Cf. Chenu, \worktitle{La théologie comme science au XIII siècle} (Paris: Vrin, 1942), p. 35; Cf. Simon de Tornai, \worktitle{Expositio in symbolium Quicumque}, "Propter hoc dictum est a quodam, quoniam apud Aristotelem argumentum est ratio rei dubiae faciens fidem, apud Christum autem argumentum est fides faciens rationem."}}. Et hoc videtur esse contra \edtext{\name{Aureolem\index[persons]{}} prima quaestione Prologi \edtext{articulo}{\lemma{articulo}\Bfootnote{capitulo V}} primo}{\lemma{}\Afootnote[nosep]{Aureoli, Prologue, article 1}}, qui tenet quod articuli fidei sunt conclusiones ex aliis deductae, ad quas \edtext{processus |\ledsidenote{S 2rb} theologicus et}{\lemma{processus theologicus et}\Bfootnote{\emph{om.} V; While this phrase appears a bit redundant and therefore somewhat understandable that it is omitted by V, we include because it does not hurt the sense and it is supported by R, SV, and S}} processus theologici principaliter nituntur concludendas; et non sunt tamquam principia ex quibus alia theologice \edtext{deducuntur}{\lemma{deducuntur}\Bfootnote{deducantur V; The choice of the subjunctive by V is unclear to us. Thus, follow the indicative reading supported by R, SV, and S}}."""
nested_2_result = r"""Sed hic occurrunt arduae difficultates; et primo consideranda \sameword{est} descriptio fidei quam ponit \name{Apostolus\index[persons]{}}, scilicet, \edtext{\enquote{fides \edtext{\sameword[2]{est}}{\lemma{\sameword{est}}\Bfootnote{\emph{om.} R}} substantia rerum sperandarum, argumentum non apparentium.}}{\lemma{}\Afootnote[nosep]{Hebrews 11:1}} Ubi secundum \edtext{\name{Altissiodorensis\index[persons]{}} \edtext{in}{\lemma{in}\Bfootnote{\emph{om.} R SV S}} principio suae \worktitle{Summae}\index[works]{}}{\lemma{}\Afootnote[nosep]{Guillelmus Auxerre \worktitle{Summa aurea}}} et \edtext{\name{\edtext{Guillelmum}{\lemma{Guillelmum}\Bfootnote{guillelmi R}} Parisiensis \index[persons]{}} tractatu suo \worktitle{De fide et legibus}\index[works]{}}{\lemma{}\Afootnote[nosep]{Guillelmus Parisiensis, \worktitle{de fide et legibus}}} sit una comparatio fidei, respectu credendorum, et caritatis, respectu amandorum; unde imaginatur quod sicut caritas dirigit hominem ad diligendum Deum propter se, ita proportionaliter fides inclinat intellectum ad credendum primae veritati propter se et \edtext{super}{\lemma{super}\Bfootnote{supra V}} omnia sine alia apparentia. Ideo fides est argumentum, et non est consequens nec conclusio. Ideo sicut inquit \name{\edtext{Guillelmus}{\lemma{Guillelmus}\Bfootnote{\emph{om.} V}} Altissiodorensis\index[persons]{}} \edtext{\enquote{a quodam bene dictum est quod apud Aristotelem\index[persons]{} argumentum est ratio rei dubiae faciens fidem, apud autem Christum est\edtext{}{\lemma{}\Bfootnote[nosep]{\emph{iter.} R SV; The double "est" in R and SV seems like a clear mistake, though good corroboration of the intimate relationship between these two witnesses.}} fides faciens rationem}}{\lemma{}\Afootnote[nosep]{Guillelmus Auxerre, \worktitle{Summa aurea}\index[works]{}, prologus.This formulation has been identified by Marie-dominique Chenu as originating with Simon de Tornai; Cf. Chenu, \worktitle{La théologie comme science au XIII siècle} (Paris: Vrin, 1942), p. 35; Cf. Simon de Tornai, \worktitle{Expositio in symbolium Quicumque}, "Propter hoc dictum est a quodam, quoniam apud Aristotelem argumentum est ratio rei dubiae faciens fidem, apud Christum autem argumentum est fides faciens rationem."}}. Et hoc videtur esse contra \edtext{\name{Aureolem\index[persons]{}} prima quaestione Prologi \edtext{articulo}{\lemma{articulo}\Bfootnote{capitulo V}} primo}{\lemma{}\Afootnote[nosep]{Aureoli, Prologue, article 1}}, qui tenet quod articuli fidei sunt conclusiones ex aliis deductae, ad quas \edtext{processus |\ledsidenote{S 2rb} theologicus et}{\lemma{processus theologicus et}\Bfootnote{\emph{om.} V; While this phrase appears a bit redundant and therefore somewhat understandable that it is omitted by V, we include because it does not hurt the sense and it is supported by R, SV, and S}} processus theologici principaliter nituntur concludendas; et non sunt tamquam principia ex quibus alia theologice \edtext{deducuntur}{\lemma{deducuntur}\Bfootnote{deducantur V; The choice of the subjunctive by V is unclear to us. Thus, follow the indicative reading supported by R, SV, and S}}."""

no_annotation_in_footnote = r"""Ad primum argumentum dicendum \edtext{quod minor est falsa}{\lemma{quod minor est falsa}\Bfootnote{per interemptionem minoris B}} \edtext{per}{\lemma{per}\Bfootnote{\emph{om.} O}} privationem. Per privationem sicut \edtext{dicitur per}{\lemma{dicitur per}\Bfootnote{per match}}."""
no_annotation_in_footnote_result = r"""Ad primum argumentum dicendum \edtext{quod minor est falsa}{\lemma{quod minor est falsa}\Bfootnote{per interemptionem minoris B}} \edtext{\sameword[1]{per}}{\lemma{\sameword{per}}\Bfootnote{\emph{om.} O}} privationem. Per privationem sicut \edtext{dicitur \sameword{per}}{\lemma{dicitur per}\Bfootnote{per match}}."""

class TestWordsObject:

    def test_space_macros(self):
        thinspace1 = r'A\,B'
        thinspace2 = r'A\thinspace B'
        enskip = r'A\enskip B'
        quad = r'A\quad B'
        qquad = r'A\qquad B'
        hskip = r'A\hskip{10pt}B'
        enspace = r'A\enspace B'
        negthinspace = r'A\negthinspace B'
        kern = r'A\kern{.5em}B'
        result = ['A', 'B']
        assert Words(thinspace1).list == result
        assert Words(thinspace2).list == result
        assert Words(enskip).list == result
        assert Words(quad).list == result
        assert Words(qquad).list == result
        assert Words(hskip).list == result
        assert Words(enspace).list == result
        assert Words(negthinspace).list == result
        assert Words(kern).list == result


class TestCritTextObject:

    def test_custom_ellipsis_dots_from_config(self):
        fname = './samewords/test/assets/sample_config.json'
        settings = cli.parse_config_file(fname)
        edtext = r'\edtext{A B C D E}{\lemma{A ... E}\Afootnote{A Vat.}}'
        assert CritText(edtext).search_words == ['A', 'E']

    def test_ellipsis_dashes(self):
        single_dash = r'\edtext{A B C D E}{\lemma{A - E}\Afootnote{A Vat.}}'
        double_dash = r'\edtext{A B C D E}{\lemma{A -- E}\Afootnote{A Vat.}}'
        triple_dash = r'\edtext{A B C D E}{\lemma{A --- E}\Afootnote{A Vat.}}'
        dash_without_space = r'\edtext{A B C D E}{\lemma{A-E}\Afootnote{A Vat.}}'
        endash = r'\edtext{A B C D E}{\lemma{A – E}\Afootnote{A Vat.}}'
        emdash = r'\edtext{A B C D E}{\lemma{A — E}\Afootnote{A Vat.}}'
        comma_string = r'\edtext{A B C D E}{\lemma{A ,-, E}\Afootnote{A Vat.}}'
        thin_space = r'\edtext{A B C D E}{\lemma{A\,--\,E}\Afootnote{A Vat.}}'
        result = ['A', 'E']
        assert CritText(single_dash).search_words == result
        assert CritText(double_dash).search_words == result
        assert CritText(triple_dash).search_words == result
        assert CritText(dash_without_space).search_words == result
        assert CritText(endash).search_words == result
        assert CritText(emdash).search_words == result
        assert CritText(comma_string).search_words == result
        assert CritText(thin_space).search_words == result

    def test_ellipsis_dots(self):
        dots = r'\edtext{A B C D E}{\lemma{A \dots E}\Afootnote{A Vat.}}'
        dots_brackets = r'\edtext{A B C D E}{\lemma{A \dots{} E}\Afootnote{A Vat.}}'
        ldots = r'\edtext{A B C D E}{\lemma{A \ldots E}\Afootnote{A Vat.}}'
        ldots_brackets = r'\edtext{A B C D E}{\lemma{A \ldots{} E}\Afootnote{A Vat.}}'
        result = ['A', 'E']
        assert CritText(dots).search_words == result
        assert CritText(dots_brackets).search_words == result
        assert CritText(ldots).search_words == result
        assert CritText(ldots_brackets).search_words == result




class TestLatexExpressionCapturing:
    long_string = """
    test of content \edtext{content \edtext{content2 \emph{test}}}{\lemma{content \edtext{content2 \emph{ 
    test}}}\Afootnote{Footnote content}} and some content afterwards! 
    """

    balanced_string = '{\lemma{\sw{content}}}'
    unbalanced_string = '{\lemma{\sw{content}}'
    escaped_latex_string = '{\\ \& \% \$ \# \_ \{ \} \~ \^}'

    def test_capture_balanced(self):
        assert Brackets(self.balanced_string).content == self.balanced_string[1:-1]

    def test_capture_escaped(self):
        assert Brackets(self.escaped_latex_string).content == self.escaped_latex_string[1:-1]

    def test_capture_unbalanced(self):
        with pytest.raises(ValueError):
            Brackets(self.unbalanced_string).content


class TestLatexListMaintextWords:

    def test_clean_nested_edtext_macros(self):
        edtext_string = r"""et \edtext{hic \edtext{et}{\Afootnote{÷ A}} hoc}{\Afootnote{ille et illud B}} et cetera """
        edtext_string_result = ['et', 'hic', 'et', 'hoc', 'et', 'cetera']
        assert Words(edtext_string).list == edtext_string_result


class TestProximityListing:
    simple_string = TextSegment("One major reason for \edtext{the}{\lemma{the}\Bfootnote{an}} "
                                "interest \edtext{in}{\lemma{in}\Bfootnote{an}} intentionality in "
                                "medieval philosophy is that it has been widely recognized that "
                                "Franz Brentano was reviving a scholastic notion when he "
                                "introduced intentionality as “the mark of the mental” (Brentano "
                                "1924). But Brentano never used \edtext{the}{\lemma{"
                                "the}\Bfootnote{an}} terminology of representation to explicate "
                                "intentionality. This was done much later, "
                                "in post-Wittgensteinian philosophy of mind. In later medieval "
                                "philosophy, it was, however, \edtext{standard}{\lemma{"
                                "standard}\Bfootnote{cont}} to explain the content of a thought "
                                "by referring to \edtext{the}{\lemma{the}\Bfootnote{or its}} "
                                "representational nature.")

    def test_proximity_listing_left(self):
        input_list = self.simple_string
        output_list = [' terminology of representation to explicate intentionality. This was done much later, in post-Wittgensteinian philosophy of mind. In later medieval philosophy, it was, however, ','\\edtext{standard}{\\lemma{standard}\\Bfootnote{cont}}',' to explain the content of a thought by referring to ', '\\edtext{the}{\\lemma{the}\\Bfootnote{or its}}', ' representational nature.']
        context = Context()
        context.update(raw_before=input_list, raw_after=[])
        assert context.before[0] == output_list

    def test_proximity_listing_right(self):
        output_list = ['One major reason for ', '\\edtext{the}{\\lemma{the}\\Bfootnote{an}}', ' interest ', '\\edtext{in}{\\lemma{in}\\Bfootnote{an}}', ' intentionality in medieval philosophy is that it has been widely recognized that Franz Brentano was reviving a scholastic notion when he introduced intentionality as “the mark of the mental” (Brentano 1924). But Brentano never used ']
        context = Context()
        context.update(raw_before=[], raw_after=self.simple_string)
        assert context.after[0] == output_list


class TestSamewordWrapping:
    def test_wrap_unwrapped_sameword(self):
        assert wrap_phrase('sw', lemma_level=1) == r'\sameword[1]{sw}'

    def test_wrap_wrapped_sameword_without_argument(self):
        wrap = Word(r'\sameword{so}')
        wrap.wrap_macro = r'\sameword'
        assert wrap_phrase('so', lemma_level=2, wrap=wrap) == r"\sameword[2]{so}"

    def test_wrap_wrapped_sameword_with_argument(self):
        w_item = Word(r'\sameword[2]{so}')
        w_item.wrap_macro = r'\sameword[2]'
        assert wrap_phrase('so', lemma_level=1, wrap=w_item) == r'\sameword[1,2]{so}'

    def test_wrap_no_lemma(self):
        assert wrap_phrase('so', lemma_level=0) == r"\sameword{so}"

    def test_no_proximity_match(self):
        assert critical_note_match_replace_samewords(no_proximity_match) == no_proximity_match


class TestWrapWordPhrase:
    def test_wrap_single_word(self):
        single_word = 'input'
        single_word_result = r'\sameword{input}'
        assert wrap_phrase(single_word) == single_word_result

    def test_wrap_wrapped_word(self):
        single_word = 'input'
        wrap = Word(r'\sameword{input}')
        wrap.wrap_macro = r'\sameword'
        single_word_result = r'\sameword{input}'
        assert wrap_phrase(single_word, wrap=wrap) == single_word_result


    def test_wrap_w_level(self):
        single_word = 'input'
        wrap = Word(r'\sameword[1]{input}')
        wrap.wrap_macro = r'\sameword[1]'
        single_word_result = r'\sameword[1]{input}'
        assert wrap_phrase(single_word, lemma_level=1, wrap=wrap) == single_word_result

    def test_wrap_wrapped_w_level(self):
        single_word = 'input'
        wrap = Word(r'\sameword[1]{input}')
        wrap.wrap_macro = r'\sameword[1]'
        single_word_result = r'\sameword[1]{input}'
        assert wrap_phrase(single_word, lemma_level=1, wrap=wrap) == single_word_result

    def test_wrap_multiword(self):
        multiword = 'input material'
        wrap = Word(r'\sameword{input material}')
        wrap.wrap_macro = r'\sameword'
        multiword_result = r'\sameword{input material}'
        assert wrap_phrase(multiword, wrap=wrap) == multiword_result

    def test_wrap_multi_partially_wrapped(self):
        multiword = r'input \sameword{material}'
        multiword_result = r'\sameword{input \sameword{material}}'
        assert wrap_phrase(multiword) == multiword_result

    def test_wrap_multi_both_wrapped(self):
        multiword = r'\sameword{input} \sameword{material}'
        multiword_result = r'\sameword{\sameword{input} \sameword{material}}'
        assert wrap_phrase(multiword) == multiword_result


class TestMainReplaceFunction:

    def test_match_word_boundary(self):
        text = r"""
test
thirtieth
twenty-ninth
twenty-eighth
twenty-seventh
twenty-sixth
twenty-fifth
twenty-fourth
twenty-third
twenty-second
twenty-first
twentieth
nineteenth
eighteenth
seventeenth
sixteenth
fifteenth
fourteenth
thirteenth
twelfth
eleventh
tenth
ninth
eighth
seventh
sixth
fifth
fourth
third
second
first
\edtext{test}{\Afootnote{check}}
first
second
third
fourth
fifth
sixth
seventh
eighth
ninth
tenth
eleventh
twelfth
thirteenth
fourteenth
fifteenth
sixteenth
seventeenth
eighteenth
nineteenth
twentieth
twenty-first
twenty-second
twenty-third
twenty-fourth
twenty-fifth
twenty-sixth
twenty-seventh
twenty-eighth
twenty-ninth
thirtieth
test
        """
        expectation = r"""
\sameword{test}
thirtieth
twenty-ninth
twenty-eighth
twenty-seventh
twenty-sixth
twenty-fifth
twenty-fourth
twenty-third
twenty-second
twenty-first
twentieth
nineteenth
eighteenth
seventeenth
sixteenth
fifteenth
fourteenth
thirteenth
twelfth
eleventh
tenth
ninth
eighth
seventh
sixth
fifth
fourth
third
second
first
\edtext{\sameword[1]{test}}{\Afootnote{check}}
first
second
third
fourth
fifth
sixth
seventh
eighth
ninth
tenth
eleventh
twelfth
thirteenth
fourteenth
fifteenth
sixteenth
seventeenth
eighteenth
nineteenth
twentieth
twenty-first
twenty-second
twenty-third
twenty-fourth
twenty-fifth
twenty-sixth
twenty-seventh
twenty-eighth
twenty-ninth
thirtieth
\sameword{test}        
        """
        print(critical_note_match_replace_samewords(text))

    def test_match_custom_singleword_exclude(self):
        settings.exclude_macros += ['\\somemacro']
        text = 'Han var sonr \edtext{Hákon\emph{ar}\somemacro{Håkon II}}{\Afootnote{k\emph{on}gſ hakon\emph{ar} Sk}}, sons Hákonar\somemacro{Håkon I}'
        result = 'Han var sonr \edtext{\sameword[1]{Hákon\emph{ar}\somemacro{Håkon II}}}{\Afootnote{k\emph{on}gſ hakon\emph{ar} Sk}}, sons \sameword{Hákonar\somemacro{Håkon I}}'
        assert critical_note_match_replace_samewords(text) == result

    def test_match_custom_multiword_exclude(self):
        settings.exclude_macros += ['\\somemacro']
        text = 'Han var sonr \edtext{Hákon\emph{ar}\somemacro{Håkon II} konungs}{\Afootnote{k\emph{on}gſ hakon\emph{ar} Sk}}, sons Hákonar\somemacro{Håkon I} konungs'
        result = 'Han var sonr \edtext{\sameword[1]{Hákon\emph{ar}\somemacro{Håkon II} konungs}}{\Afootnote{k\emph{on}gſ hakon\emph{ar} Sk}}, sons \sameword{Hákonar\somemacro{Håkon I} konungs}'
        assert critical_note_match_replace_samewords(text) == result

    def test_text_match_with_index_command(self):
        text_w_index = r"\edtext{Sortes\index[persons]{Sortes}}{\Afootnote{Socrates B}} dicit: Sortes\index[persons]{Sortes} probus"
        text_w_index_result = r"\edtext{\sameword[1]{Sortes\index[persons]{Sortes}}}{\Afootnote{Socrates B}} dicit: \sameword{Sortes\index[persons]{Sortes}} probus"
        assert critical_note_match_replace_samewords(text_w_index) == text_w_index_result

    def test_text_no_match_with_index_command(self):
        text_w_index = r"\edtext{Sortes\index[persons]{Socrates}}{\Afootnote{Socrates B}} dicit: Sortes\index[persons]{Sortes} probus"
        text_w_index_result = r"\edtext{Sortes\index[persons]{Socrates}}{\Afootnote{Socrates B}} dicit: Sortes\index[persons]{Sortes} probus"
        assert critical_note_match_replace_samewords(text_w_index) == text_w_index_result

    def test_ignoring_emph_macro(self):
        emph_conflict = r'\edtext{So\emph{cra}tes}{\Afootnote{Socrates B}} dicit: Socrates probus'
        emph_conflict_result = r'\edtext{\sameword[1]{So\emph{cra}tes}}{\Afootnote{Socrates B}} dicit: \sameword{Socrates} probus'
        assert critical_note_match_replace_samewords(emph_conflict) == emph_conflict_result

    def test_nested_no_lemma(self):
        nested_no_lemma = r"""et \edtext{hic \edtext{et}{\Afootnote{÷ A}} hoc}{\Afootnote{ille et
            illud B}} et cetera """
        nested_no_lemma_result = r"""\sameword{et} \edtext{hic \edtext{\sameword[2]{et}}{\Afootnote{÷ A}} hoc}{\Afootnote{ille et
            illud B}} \sameword{et} cetera """
        assert critical_note_match_replace_samewords(nested_no_lemma) == nested_no_lemma_result

    def test_wrap_without_lemma(self):
        no_lemma = r'non videtur sed \edtext{non}{\Bfootnote{sic B}}'
        no_lemma_result = r'\sameword{non} videtur sed \edtext{\sameword[1]{non}}{\Bfootnote{sic B}}'
        assert critical_note_match_replace_samewords(no_lemma) == no_lemma_result

    def test_wrap_text_with_macro(self):
        macro_wrap = r'\emph{non apparentium} quia \edtext{non}{\lemma{non}\Bfootnote{sed SV}}'
        macro_wrap_result = r'\emph{\sameword{non} apparentium} quia ' \
                            r'\edtext{\sameword[1]{non}}{\lemma{\sameword{non}}\Bfootnote{sed SV}}'
        assert critical_note_match_replace_samewords(macro_wrap) == macro_wrap_result

    def test_wrap_text_with_macro_with_optional_argument(self):
        macro_wrap = r'\macro[optional]{non apparentium} quia \edtext{non}{\lemma{non}\Bfootnote{sed SV}}'
        macro_wrap_result = r'\macro[optional]{\sameword{non} apparentium} quia ' \
                            r'\edtext{\sameword[1]{non}}{\lemma{\sameword{non}}\Bfootnote{sed SV}}'
        assert critical_note_match_replace_samewords(macro_wrap) == macro_wrap_result

    def test_wrap_multiword_with_macro(self):
        macro_wrap = r'sed \emph{non} \edtext{sed non}{\lemma{sed non}\Bfootnote{sed SV}}'
        macro_wrap_result = r'\sameword{sed \emph{non}} \edtext{\sameword[1]{sed non}}{\lemma{\sameword{sed non}}\Bfootnote{sed SV}}'
        assert critical_note_match_replace_samewords(macro_wrap) == macro_wrap_result


    def test_two_multi_words(self):
        double_multiword = r"\edtext{nobis apparentes}{\lemma{nobis apparentes}\Bfootnote{\emph{om.} B}} " \
                           r"\edtext{nobis apparentes}{\lemma{nobis apparentes}\Bfootnote{\emph{om.} B}}"
        double_multiword_result = r"\edtext{\sameword[1]{nobis apparentes}}{\lemma{\sameword{nobis " \
                                  r"apparentes}}\Bfootnote{\emph{om.} B}} \edtext{\sameword[1]{nobis apparentes}}{" \
                                  r"\lemma{\sameword{nobis apparentes}}\Bfootnote{\emph{om.} B}}"
        assert critical_note_match_replace_samewords(double_multiword) == double_multiword_result

    def test_multiword_lemma(self):
        assert critical_note_match_replace_samewords(multiword_lemma) == multiword_lemma_result

    @pytest.mark.skip('Not implemented yet!')
    def test_multiword_lemma_intervening_macro(self):
        test_string = r'per \sidenote{1rb O} causam scire est \edtext{per causam}{\lemma{per causam}\Bfootnote{causam rei B}} cognoscere'
        test_string_res = r'\sameword{per \sidenote{1rb O} causam} scire est \edtext{\sameword[1]{per causam}}{\lemma{\sameword{per causam}}\Bfootnote{causam rei B}} cognoscere'
        assert critical_note_match_replace_samewords(test_string) == test_string_res

    def test_nested_ambiguity(self):
        assert critical_note_match_replace_samewords(nested_ambiguity) == nested_ambiguity_result

    def test_false_positives(self):
        assert critical_note_match_replace_samewords(false_positives) == false_positives

    def test_flat_ldots_lemma(self):
        assert critical_note_match_replace_samewords(flat_ldots_lemma) == flat_ldots_lemma_result

    def test_no_proximity_match(self):
        assert critical_note_match_replace_samewords(no_proximity_match) == no_proximity_match

    def test_three_close_levels(self):
        assert critical_note_match_replace_samewords(three_close_levels) == three_close_levels_result

    def test_flat_proximity_match(self):
        assert critical_note_match_replace_samewords(flat_proximity_match) == flat_proximity_match_result

    def test_nested_ldots_lemma(self):
        assert critical_note_match_replace_samewords(nested_ldots_lemma) == nested_ldots_lemma_result

    def test_complex_real_example(self):
        assert critical_note_match_replace_samewords(nested_2) == nested_2_result

    def test_long_proximate_before_after(self):
        assert critical_note_match_replace_samewords(long_proximate_before_after) == long_proximate_before_after_result

    def test_wrapping_of_already_wrapped(self):
        identical_wrap_result = r"""Praeterea intellectus intelligit se: \edtext{\sameword[1]{aut}}{\lemma{\sameword{aut}}\Bfootnote{aliter Aguin.}} ergo per suam essentiam, \edtext{\sameword[1]{aut}}{\lemma{\sameword{aut}}\Bfootnote{aliter Aguin.}} per speciem, \edtext{\sameword[1]{aut}}{\lemma{\sameword{aut}}\Bfootnote{aliter Aguin.}} per suum actum; sed \edtext{\sameword[1]{nec}}{\lemma{\sameword{nec}}\Bfootnote{non Aguin.}} per speciem |\ledsidenote{B 174vb} \sameword{nec} per suum actum;"""
        identical_wrap = r"""Praeterea intellectus intelligit se: \edtext{aut}{\lemma{aut}\Bfootnote{aliter Aguin.}} ergo per suam essentiam, \edtext{aut}{\lemma{aut}\Bfootnote{aliter Aguin.}} per speciem, \edtext{aut}{\lemma{aut}\Bfootnote{aliter Aguin.}} per suum actum; sed \edtext{nec}{\lemma{nec}\Bfootnote{non Aguin.}} per speciem |\ledsidenote{B 174vb} nec per suum actum;"""
        assert (critical_note_match_replace_samewords(identical_wrap)) == identical_wrap_result

    def test_text_with_arbitrary_commands(self):
        text = r"""
        \edlabelS{da-49-l1q1-ysmgk1}%
        \no{1.1}
        Illud de quo est scientia est intelligibile, quia cum scientia sit habitus intellectus, de quo est scientia oportet esse intelligibile; sed anima non est intelligibile, quia omnis nostra cognitio ortum habet a sensu, \edtext{unde ipsum intelligere non est}{\lemma{unde \dots{} est}\Bfootnote{quia nihil intelligimus B}} sine phantasmate, sed anima sub sensu non cadit, nec phantasma facit; ergo et cetera. 
        \edlabelE{da-49-l1q1-ysmgk1}
        """
        result = r"""
        \edlabelS{da-49-l1q1-ysmgk1}%
        \no{1.1}
        Illud de quo \sameword{est} scientia \sameword{est} intelligibile, quia cum scientia sit habitus intellectus, de quo \sameword{est} scientia oportet esse intelligibile; sed anima non \sameword{est} intelligibile, quia omnis nostra cognitio ortum habet a sensu, \edtext{unde ipsum intelligere non \sameword[1]{est}}{\lemma{unde \dots{} \sameword{est}}\Bfootnote{quia nihil intelligimus B}} sine phantasmate, sed anima sub sensu non cadit, nec phantasma facit; ergo et cetera. 
        \edlabelE{da-49-l1q1-ysmgk1}
        """
        assert critical_note_match_replace_samewords(text) == result

    def test_no_annotation_in_footnote(self):
        assert critical_note_match_replace_samewords(no_annotation_in_footnote) == no_annotation_in_footnote_result


class TestReplaceInEdtext:
    edtext_unnested = CritText(r"\edtext{sw so sw another thing}{\lemma{sw \ldots thing"
                               r"}\Afootnote{critical note}} ")
    edtext_unnested_result = r"\edtext{\sameword[1]{sw} so sw another thing}{\lemma{sw \ldots thing}\Afootnote{critical note}}"

    def test_replace_in_edtext(self):
        assert self.edtext_unnested.replace_in_maintext_note(replace_word='sw') == \
               self.edtext_unnested_result
