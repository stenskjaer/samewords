import pytest

from reledmac_samewords import *

no_proximity_match = r"""sw \edtext{so}{\lemma{so}\Bfootnote{foot content}}  and again sw it is all and something after."""

three_close_levels = r"""so \edtext{\edtext{\edtext{so}{\lemma{so}\Bfootnote{lev 3}}}{\lemma{so}\Bfootnote{lev 2}}}{\lemma{so}\Bfootnote{lev 1}}"""
three_close_levels_result = r"\sameword{so} \edtext{\edtext{\edtext{\sameword[1,2,3]{so}}{\lemma{\sameword{so}}\Bfootnote{lev 3}}}{\lemma{\sameword{so}}\Bfootnote{lev 2}}}{\lemma{\sameword{so}}\Bfootnote{lev 1}}"

flat_proximity_match = r"""so sw \edtext{so}{\lemma{so}\Bfootnote{foot content}}  and again sw it is all and something after."""
flat_proximity_match_result = r"\sameword{so} sw \edtext{\sameword[1]{so}}{\lemma{\sameword{so}}\Bfootnote{foot content}}  and again sw it is all and \sameword{so}mething after."

false_positives = r"\edtext{in}{\lemma{in}\Bfootnote{note content}} species intelligibilis imaginatur secundum Apostolum\index[persons]{}."

nested_1 = r"""sw \emph{so} \edtext{so}{\lemma{so}\Bfootnote{foot content}} \emph{so} \edtext{so}{\lemma{so}\Bfootnote{foot content}} \edtext{sw so \edtext{\edtext{sw}{\lemma{sw}\Bfootnote{B note here}} thing}{\lemma{sw thing}\Bfootnote{B footnote her}} and again sw it is all}{\lemma{sw \ldots all}\Afootnote{sw critical note}} and something after."""
nested_1_result = r"""sw \emph{\sameword{so}} \edtext{\sameword[1]{so}}{\lemma{\sameword{so}}\Bfootnote{foot content}} \emph{\sameword{so}} \edtext{\sameword[1]{so}}{\lemma{\sameword{so}}\Bfootnote{foot content}} \edtext{\sameword[1]{sw} \sameword{so} \edtext{\edtext{\sameword[2,3]{sw}}{\lemma{\sameword{sw}}\Bfootnote{B note here}} thing}{\lemma{\sameword{sw}"""

nested_ldots_lemma = r"""sw and \edtext{sw so \edtext{\edtext{sw}{\lemma{sw}\Bfootnote{B note here}} another thing \edtext{and more}{\lemma{and more}\Bfootnote{and more note}}}{\lemma{sw another thing and more}\Bfootnote{B footnote her}}}{\lemma{sw \ldots more}\Afootnote{sw critical note}} and a sw after and one more \edtext{flat}{\lemma{flat}\Bfootnote{note here}} entry."""
nested_ldots_lemma_result = r"""\sameword{sw} and \edtext{\sameword[1]{sw} so \edtext{\edtext{\sameword[1,3]{sw}}{\lemma{\sameword{sw}}\Bfootnote{B note here}} another thing \edtext{and \sameword[1]{more}}{\lemma{and more}\Bfootnote{and more note}}}{\lemma{sw another thing and more}\Bfootnote{B footnote her}}}{\lemma{\sameword{sw} \ldots \sameword{more}}\Afootnote{sw critical note}} and a \sameword{sw} after and one \sameword{more} \edtext{flat}{\lemma{flat}\Bfootnote{note here}} entry."""

nested_dots_lemma = r"""sw and \edtext{sw so \edtext{\edtext{sw}{\lemma{sw}\Bfootnote{B note here}} another thing}{\lemma{sw another thing}\Bfootnote{B footnote her}}}{\lemma{sw \dots thing}\Afootnote{ critical note}} and a sw after."""

flat_ldots_lemma = r"""sw and \edtext{sw so sw another thing}{\lemma{sw \ldots thing}\Afootnote{ critical note}} and a sw after."""
flat_ldots_lemma_result = r"""\sameword{sw} and \edtext{\sameword[1]{sw} so \sameword[1]{sw} another thing}{\lemma{\sameword{sw} \ldots thing}\Afootnote{ critical note}} and a \sameword{sw} after."""

nested_multiword_lemma = r"""sw so sw thing and \edtext{sw so \edtext{\edtext{sw}{\lemma{sw}\Bfootnote{B note here}} thing}{\lemma{sw thing}\Bfootnote{B footnote her}}}{\lemma{sw so sw thing}\Afootnote{ critical note}} and a sw after."""
nested_multiword_lemma_result = r"""sw so sw thing and \edtext{\sameword[1]{sw} so \edtext{\edtext{\sameword[2, 3]{sw}}{\lemma{\sameword{sw}}\Bfootnote{B note here}} thing}{\lemma{\sameword{sw} thing}\Bfootnote{B footnote her}}}{\lemma{\sameword{sw} so sw thing}\Afootnote{ critical note}} and a \sameword{sw} after."""

nested_2 = r"""Sed hic occurrunt arduae difficultates; et primo consideranda est descriptio fidei quam ponit \name{Apostolus\index[persons]{}}, scilicet, \edtext{\enquote{fides \edtext{est}{\lemma{est}\Bfootnote{\emph{om.} R}} substantia rerum sperandarum, argumentum non apparentium.}}{\lemma{}\Afootnote[nosep]{Hebrews 11:1}} Ubi secundum \edtext{\name{Altissiodorensis\index[persons]{}} \edtext{in}{\lemma{in}\Bfootnote{\emph{om.} R SV S}} principio suae \worktitle{Summae}\index[works]{}}{\lemma{}\Afootnote[nosep]{Guillelmus Auxerre \worktitle{Summa aurea}}} et \edtext{\name{\edtext{Guillelmum}{\lemma{Guillelmum}\Bfootnote{guillelmi R}} Parisiensis \index[persons]{}} tractatu suo \worktitle{De fide et legibus}\index[works]{}}{\lemma{}\Afootnote[nosep]{Guillelmus Parisiensis, \worktitle{de fide et legibus}}} sit una comparatio fidei, respectu credendorum, et caritatis, respectu amandorum; unde imaginatur quod sicut caritas dirigit hominem ad diligendum Deum propter se, ita proportionaliter fides inclinat intellectum ad credendum primae veritati propter se et \edtext{super}{\lemma{super}\Bfootnote{supra V}} omnia sine alia apparentia. Ideo fides est argumentum, et non est consequens nec conclusio. Ideo sicut inquit \name{\edtext{Guillelmus}{\lemma{Guillelmus}\Bfootnote{\emph{om.} V}} Altissiodorensis\index[persons]{}} \edtext{\enquote{a quodam bene dictum est quod apud Aristotelem\index[persons]{} argumentum est ratio rei dubiae faciens fidem, apud autem Christum est\edtext{}{\lemma{}\Bfootnote[nosep]{\emph{iter.} R SV; The double "est" in R and SV seems like a clear mistake, though good corroboration of the intimate relationship between these two witnesses.}} fides faciens rationem}}{\lemma{}\Afootnote[nosep]{Guillelmus Auxerre, \worktitle{Summa aurea}\index[works]{}, prologus.This formulation has been identified by Marie-dominique Chenu as originating with Simon de Tornai; Cf. Chenu, \worktitle{La théologie comme science au XIII siècle} (Paris: Vrin, 1942), p. 35; Cf. Simon de Tornai, \worktitle{Expositio in symbolium Quicumque}, "Propter hoc dictum est a quodam, quoniam apud Aristotelem argumentum est ratio rei dubiae faciens fidem, apud Christum autem argumentum est fides faciens rationem."}}. Et hoc videtur esse contra \edtext{\name{Aureolem\index[persons]{}} prima quaestione Prologi \edtext{articulo}{\lemma{articulo}\Bfootnote{capitulo V}} primo}{\lemma{}\Afootnote[nosep]{Aureoli, Prologue, article 1}}, qui tenet quod articuli fidei sunt conclusiones ex aliis deductae, ad quas \edtext{processus |\ledsidenote{S 2rb} theologicus et}{\lemma{processus theologicus et}\Bfootnote{\emph{om.} V; While this phrase appears a bit redundant and therefore somewhat understandable that it is omitted by V, we include because it does not hurt the sense and it is supported by R, SV, and S}} processus theologici principaliter nituntur concludendas; et non sunt tamquam principia ex quibus alia theologice \edtext{deducuntur}{\lemma{deducuntur}\Bfootnote{deducantur V; The choice of the subjunctive by V is unclear to us. Thus, follow the indicative reading supported by R, SV, and S}}."""
nested_2_result = r"""Sed hic occurrunt arduae difficultates; et primo consideranda \sameword{est} descriptio fidei quam ponit \name{Apostolus\index[persons]{}}, scilicet, \edtext{\enquote{fides \edtext{\sameword[2]{est}}{\lemma{\sameword{est}}\Bfootnote{\emph{om.} R}} substantia rerum sperandarum, argumentum non apparentium.}}{\lemma{}\Afootnote[nosep]{Hebrews 11:1}} Ubi secundum \edtext{\name{Altissiodorensis\index[persons]{}} \edtext{in}{\lemma{in}\Bfootnote{\emph{om.} R SV S}} principio suae \worktitle{Summae}\index[works]{}}{\lemma{}\Afootnote[nosep]{Guillelmus Auxerre \worktitle{Summa aurea}}} et \edtext{\name{\edtext{Guillelmum}{\lemma{Guillelmum}\Bfootnote{guillelmi R}} Parisiensis \index[persons]{}} tractatu suo \worktitle{De fide et legibus}\index[works]{}}{\lemma{}\Afootnote[nosep]{Guillelmus Parisiensis, \worktitle{de fide et legibus}}} sit una comparatio fidei, respectu credendorum, et caritatis, respectu amandorum; unde imaginatur quod sicut caritas dirigit hominem ad diligendum Deum propter se, ita proportionaliter fides inclinat intellectum ad credendum primae veritati propter se et \edtext{super}{\lemma{super}\Bfootnote{supra V}} omnia sine alia apparentia. Ideo fides est argumentum, et non est consequens nec conclusio. Ideo sicut inquit \name{\edtext{Guillelmus}{\lemma{Guillelmus}\Bfootnote{\emph{om.} V}} Altissiodorensis\index[persons]{}} \edtext{\enquote{a quodam bene dictum est quod apud Aristotelem\index[persons]{} argumentum est ratio rei dubiae faciens fidem, apud autem Christum est\edtext{}{\lemma{}\Bfootnote[nosep]{\emph{iter.} R SV; The double "est" in R and SV seems like a clear mistake, though good corroboration of the intimate relationship between these two witnesses.}} fides faciens rationem}}{\lemma{}\Afootnote[nosep]{Guillelmus Auxerre, \worktitle{Summa aurea}\index[works]{}, prologus.This formulation has been identified by Marie-dominique Chenu as originating with Simon de Tornai; Cf. Chenu, \worktitle{La théologie comme science au XIII siècle} (Paris: Vrin, 1942), p. 35; Cf. Simon de Tornai, \worktitle{Expositio in symbolium Quicumque}, "Propter hoc dictum est a quodam, quoniam apud Aristotelem argumentum est ratio rei dubiae faciens fidem, apud Christum autem argumentum est fides faciens rationem."}}. Et hoc videtur esse contra \edtext{\name{Aureolem\index[persons]{}} prima quaestione Prologi \edtext{articulo}{\lemma{articulo}\Bfootnote{capitulo V}} primo}{\lemma{}\Afootnote[nosep]{Aureoli, Prologue, article 1}}, qui tenet quod articuli fidei sunt conclusiones ex aliis deductae, ad quas \edtext{processus |\ledsidenote{S 2rb} theologicus et}{\lemma{processus theologicus et}\Bfootnote{\emph{om.} V; While this phrase appears a bit redundant and therefore somewhat understandable that it is omitted by V, we include because it does not hurt the sense and it is supported by R, SV, and S}} processus theologici principaliter nituntur concludendas; et non sunt tamquam principia ex quibus alia theologice \edtext{deducuntur}{\lemma{deducuntur}\Bfootnote{deducantur V; The choice of the subjunctive by V is unclear to us. Thus, follow the indicative reading supported by R, SV, and S}}."""

class TestLatexExpressionCapturing:
    long_string = """
    test of content \edtext{content \edtext{content2 \emph{test}}}{\lemma{content \edtext{content2 \emph{ 
    test}}}\Afootnote{Footnote content}} and some content afterwards! 
    """

    balanced_string = '{\lemma{\sw{content}}}'
    unbalanced_string = '{\lemma{\sw{content}}'
    escaped_latex_string = '{\\ \& \% \$ \# \_ \{ \} \~ \^}'

    def test_capture_balanced(self):
        assert macro_expression_content(self.balanced_string) == self.balanced_string[1:-1]

    def test_capture_balanced_with_wrap(self):
        assert macro_expression_content(self.balanced_string, capture_wrap=True) == self.balanced_string

    def test_capture_escaped(self):
        assert macro_expression_content(self.escaped_latex_string) == self.escaped_latex_string[1:-1]

    def test_capture_unbalanced(self):
        with pytest.raises(ValueError):
            macro_expression_content(self.unbalanced_string)

    def test_capture_unbalanced_with_wrap(self):
        with pytest.raises(ValueError):
            macro_expression_content(self.unbalanced_string, capture_wrap=True)


class TestSamewordWrapping:
    def test_wrap_unwrapped_sameword(self):
        assert wrap_in_sameword('sw', 'so sw ', lemma_level=1) == r'so \sameword[1]{sw} '

    def test_wrap_wrapped_sameword_without_argument(self):
        assert wrap_in_sameword('so', '\sameword{so} sw ', lemma_level=2) == r"\sameword[2]{so} sw "

    def test_wrap_wrapped_sameword_with_argument(self):
        assert wrap_in_sameword('so', '\sameword[2]{so} sw ', lemma_level=1) == r'\sameword[1,2]{so} sw '

    def test_wrap_no_lemma(self):
        assert wrap_in_sameword('so', 'so sw', lemma_level=0) ==  r"\sameword{so} sw"

    def test_no_proximity_match(self):
        assert critical_note_match_replace_samewords(no_proximity_match) == no_proximity_match


class TestProximityListing():
    simple_string = "One major reason for \edtext{the}{\lemma{the}\Bfootnote{an}} interest \edtext{in}{\lemma{in}\Bfootnote{an}} intentionality in medieval philosophy is that it has been widely recognized that Franz Brentano was reviving a scholastic notion when he introduced intentionality as “the mark of the mental” (Brentano 1924). But Brentano never used \edtext{the}{\lemma{the}\Bfootnote{an}} terminology of representation to explicate intentionality. This was done much later, in post-Wittgensteinian philosophy of mind. In later medieval philosophy, it was, however, \edtext{standard}{\lemma{standard}\Bfootnote{cont}} to explain the content of a thought by referring to \edtext{the}{\lemma{the}\Bfootnote{or its}} representational nature."

    def test_proximity_listing_left(self):
        assert list(iter_proximate_words(edtext_split(self.simple_string), pivot=7, index=6, side='left')) \
               == [' intentionality in medieval philosophy is that it has been widely recognized that Franz Brentano was reviving a scholastic notion when he introduced intentionality as “the mark of the mental” (Brentano 1924). But Brentano never used ', '\\edtext{the}{\\lemma{the}\\Bfootnote{an}}', ' terminology of representation to explicate intentionality. This was done much later, in post-Wittgensteinian philosophy of mind. In later medieval philosophy, it was, however, ']

    def test_proximity_listing_right(self):
        assert list(iter_proximate_words(edtext_split(self.simple_string), pivot=7, index=8, side='right')) == [' to explain the content of a thought by referring to ', '\\edtext{the}{\\lemma{the}\\Bfootnote{or its}}', ' representational nature.']


class TestMainReplaceFunction:

    def test_false_positives(self):
        assert critical_note_match_replace_samewords(edtext_split(false_positives)) == false_positives

    def test_flat_ldots_lemma(self):
        assert critical_note_match_replace_samewords(edtext_split(flat_ldots_lemma)) == flat_ldots_lemma_result

    def test_no_proximity_match(self):
        assert critical_note_match_replace_samewords(edtext_split(no_proximity_match)) == no_proximity_match

    def test_three_close_levels(self):
        assert critical_note_match_replace_samewords(edtext_split(three_close_levels)) == three_close_levels_result

    def test_flat_proximity_match(self):
        assert critical_note_match_replace_samewords(edtext_split(flat_proximity_match)) == flat_proximity_match_result

    def test_nested_ldots_lemma(self):
        assert critical_note_match_replace_samewords(edtext_split(nested_ldots_lemma)) == nested_ldots_lemma_result

    def test_complex_real_example(self):
        assert critical_note_match_replace_samewords(edtext_split(nested_2)) == nested_2_result


class TestReplaceInEdtext:
    edtext_unnested = r"\edtext{sw so sw another thing}{\lemma{sw \ldots thing}\Afootnote{ critical note}}"
    edtext_unnested_result = r"\edtext{\sameword[1]{sw} so \sameword[1]{sw} another thing}{\lemma{sw \ldots " \
                             r"thing}\Afootnote{ critical note}}"

    edtext_nested = r"\edtext{sw so \edtext{\edtext{sw}{\lemma{sw}\Bfootnote{B note here}} another sw}{\lemma{sw " \
                    "another thing}\Bfootnote{B footnote her}}}{\lemma{sw \ldots thing}\Afootnote{ critical note}} "
    edtext_nested_result = r"\edtext{\sameword[1]{sw} so \edtext{\edtext{\sameword[1]{sw}}{\lemma{sw}\Bfootnote{B " \
                           r"note here}} another \sameword[1]{sw}}{\lemma{sw another thing}\Bfootnote{B footnote her}}}{\lemma{" \
                           r"sw \ldots thing}\Afootnote{ critical note}} "

    def test_replace_in_edtext(self):
        assert replace_in_critical_note(self.edtext_unnested, replace_word='sw') == self.edtext_unnested_result

    def test_replace_in_nested_edtext(self):
        assert replace_in_critical_note(self.edtext_nested, replace_word='sw') == self.edtext_nested_result

