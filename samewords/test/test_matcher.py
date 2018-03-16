from samewords.matcher import Matcher
from samewords.tokenize import Tokenizer
from samewords.settings import settings


class TestAnnotate:

    def run_annotation(self, input_text):
        tokenization = Tokenizer(input_text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        words = matcher.annotate()
        return words.write()

    def run_cleanup(self, input_text):
        tokenization = Tokenizer(input_text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        words = matcher.cleanup()
        return words.write()

    def test_annotation_thinspace_shorthand_in_word(self):
        text = r"""5\,000 or \edtext{5\,000}{\Afootnote{6\,000}}"""
        expect = (r'\sameword{5\,000} or \edtext{\sameword[1]{5\,000}}{'
                  r'\Afootnote{6\,000}}')
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

    def test_annotation_thinspace_in_word(self):
        text = r"""5\thinspace{}000 or \edtext{5\,000}{\Afootnote{6\,000}}"""
        expect = (r'\sameword{5\thinspace{}000} or \edtext{\sameword[1]{5\,'
                  r'000}}{\Afootnote{6\,000}}')
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

    def test_last_ellipsis_word_not_last_index(self):
        text = ("B \edtext{F and some B %\n}{\lemma{F--B}}")
        expect = ("\sameword{B} \edtext{F and some "
                  "\sameword[1]{B} %\n}{\lemma{F--\sameword{B}}}")
        assert self.run_annotation(text) == expect

    def test_first_ellipsis_word_not_first_index(self):
        text = ("F \edtext{ % \nF and B}{\lemma{F--B}}")
        expect = ("\sameword{F} \edtext{ % \n"
                  "\sameword[1]{F} and B}{\lemma{\sameword{F}--B}}")
        assert self.run_annotation(text) == expect

    def test_first_and_last_ellipsis_word_not_first_and_last_index(self):
        text = ("B F \edtext{ % \nF and B %\n}{\lemma{F--B}}")
        expect = ("\sameword{B} \sameword{F} \edtext{ % \n\sameword[1]{F} and "
                  "\sameword[1]{B} %\n}{\lemma{\sameword{F}--\sameword{B}}}")
        assert self.run_annotation(text) == expect

    def test_ellipsis_lemma_word_not_first_or_last_index(self):
        text = ("F B \edtext{ F and B}{\lemma{ % \n F--B % \n}\Afootnote{test}}")
        expect = ("\sameword{F} \sameword{B} \edtext{ \sameword[1]{F} and "
                  "\sameword[1]{B}}{\lemma{ % \n \sameword{F}--\sameword{B}"
                  " % \n}\Afootnote{test}}")
        assert self.run_annotation(text) == expect

    def test_edtext_with_editorial_brackets_1(self):
        text = ('B, F \edtext{(F and B)}{\lemma{F--B}\Afootnote{test}}')
        expect = ('\sameword{B}, \sameword{F} \edtext{(\sameword[1]{F} and '
                  '\sameword[1]{B})}{\lemma{\sameword{F}--\sameword{B}}'
                  '\Afootnote{test}}')
        assert self.run_annotation(text) == expect

    def test_edtext_with_editorial_brackets_2(self):
        text = ('B, F, \edtext{⟨F and B⟩}{\lemma{F--B}\Afootnote{test}}')
        expect = ('\sameword{B}, \sameword{F}, \edtext{⟨\sameword[1]{F} and '
                  '\sameword[1]{B}⟩}{\lemma{\sameword{F}--\sameword{B}}'
                  '\Afootnote{test}}')
        assert self.run_annotation(text) == expect

    def test_edtext_with_editorial_brackets_3(self):
        text = ('B, F, \edtext{{{}F and B{}}}{\lemma{F--B}\Afootnote{test}}')
        expect = ('\sameword{B}, \sameword{F}, \edtext{{{}\sameword[1]{F} and '
                  '\sameword[1]{B}{}}}{\lemma{\sameword{F}--\sameword{B}}'
                  '\Afootnote{test}}')
        assert self.run_annotation(text) == expect

    def test_edtext_with_editorial_brackets_custom_macro(self):
        text = ('F \edtext{\supplied{F} and B}{\lemma{F--B}}')
        expect = ('\sameword{F} \edtext{\supplied{\sameword[1]{F}} and '
                  'B}{\lemma{\sameword{F}--B}}')
        assert self.run_annotation(text) == expect


    def test_edtext_with_custom_punctuation(self):
        text = ('B˧ \edtext{B}{}')
        expect = ('\sameword{B}˧ \edtext{\sameword[1]{B}}{}')
        old = settings['punctuation']
        settings['punctuation'] += '˧'
        assert self.run_annotation(text) == expect
        settings['punctuation'] = old


    def test_edtext_with_exotic_punctuation(self):
        text = ('o “o ⸀o o. o \edtext{o}{}')
        expect = ('\sameword{o} “\sameword{o} ⸀\sameword{o} \sameword{o}. '
                  '\sameword{o} \edtext{\sameword[1]{o}}{}')
        assert self.run_annotation(text) == expect

    def test_macro_update_copies_to_closing_attribute(self):
        """If the sameword annotation of edtext entries as context samewords
        does not copy the to_closing property during updating, we will get
        nested sameword annotations. """
        text = r"""
            \edtext{my phrase}{\Afootnote{}}
            \edtext{my phrase}{\Afootnote{}}
            \edtext{my phrase}{\Afootnote{}}
        """
        expect = r"""
            \edtext{\sameword[1]{my phrase}}{\Afootnote{}}
            \edtext{\sameword[1]{my phrase}}{\Afootnote{}}
            \edtext{\sameword[1]{my phrase}}{\Afootnote{}}
        """
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

    def test_custom_ellipses_without_space(self):
        double_dash = r'A E \edtext{A B C D E}{\lemma{A--E}\Afootnote{}}'
        expect = (r'\sameword{A} \sameword{E} \edtext{\sameword[1]{A} B C '
                  r'D \sameword[1]{E}}{\lemma{\sameword{A}--\sameword{E}}'
                  r'\Afootnote{}}')
        assert self.run_annotation(double_dash) == expect
        assert self.run_cleanup(expect) == double_dash

    def test_consequtive_context_matches_are_annotated(self):
        text = (r'word word word word \edtext{word}{\Afootnote{statement}} '
                r'word word word \edtext{word}{\Afootnote{statement}} word '
                r'word')
        expect = (r'\sameword{word} \sameword{word} \sameword{word} '
                  r'\sameword{word} \edtext{\sameword[1]{word}}{\Afootnote{'
                  r'statement}} \sameword{word} \sameword{word} \sameword{'
                  r'word} \edtext{\sameword[1]{word}}{\Afootnote{statement}} '
                  r'\sameword{word} \sameword{word}')
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

    def test_no_match_single_level(self):
        text = r'text \edtext{emphasis}{\Bfootnote{fnote}} is nice'
        assert self.run_annotation(text) == text

    def test_no_match_empty_edtext(self):
        text = (r'Christum est\edtext{}{\lemma{}\Bfootnote[nosep]{'
                r'\emph{iter.} R SV; The double "est" in R and SV seems like '
                r'a clear mistake, though good corroboration of the intimate '
                r'relationship between these two witnesses.}} fides faciens')
        assert self.run_annotation(text) == text

    def test_match_single_level_single_item(self):
        text = (r'emphasis \edtext{emphasis}{\Bfootnote{fnote}} is emphasis')
        expect = (r'\sameword{emphasis} \edtext{\sameword[1]{emphasis}}{'
                  r'\Bfootnote{fnote}} is \sameword{emphasis}')
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

    def test_match_single_level_multiple_context_matches(self):
        text = (r'emphasis a emphasis \edtext{emphasis}{\Bfootnote{fnote}} '
                r'and emphasis')
        expect = (r'\sameword{emphasis} a \sameword{emphasis} \edtext{'
                  r'\sameword[1]{emphasis}}{\Bfootnote{fnote}} and \sameword{'
                  r'emphasis}')
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

    def test_match_single_level_multiword(self):
        text = (r'\sameword{a b} and a b \edtext{a b}{\Bfootnote{fnote}} a b '
                r'and a b')
        expect = (r'\sameword{a b} and \sameword{a b} \edtext{\sameword[1]{a '
                  r'b}}{\Bfootnote{fnote}} \sameword{a b} and \sameword{a b}')
        clean = (r'a b and a b \edtext{a b}{\Bfootnote{fnote}} a b and a b')
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == clean

    def test_match_single_level_multiword_lemma(self):
        text = (r'\sameword{a b} and a b \edtext{a b}{\lemma{a b}\Bfootnote{'
                r'fnote}} a b and a b')
        expect = (r'\sameword{a b} and \sameword{a b} \edtext{\sameword[1]{a '
                  r'b}}{\lemma{\sameword{a b}}\Bfootnote{fnote}} \sameword{a b}'
                  r' and \sameword{a b}')
        clean = (r'a b and a b \edtext{a b}{\lemma{a b}\Bfootnote{fnote}} a b '
                 r'and a b')
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == clean

    def test_match_single_level_multiword_lemma_ellipsis(self):
        text = (r'\sameword{a} b and c \edtext{a and c}{\lemma{a \dots{} '
                r'c}\Bfootnote{fnote}} and c and c')
        expect = (r'\sameword{a} b and \sameword{c} \edtext{\sameword[1]{a} '
                  r'and \sameword[1]{c}}{\lemma{\sameword{a} \dots{} '
                  r'\sameword{c}}\Bfootnote{fnote}} and \sameword{c} and '
                  r'\sameword{c}')
        clean = (r'a b and c \edtext{a and c}{\lemma{a \dots{} c}\Bfootnote{'
                 r'fnote}} and c and c')
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == clean

    def test_three_close_nested_levels(self):
        text = (r"so \edtext{\edtext{\edtext{so}{\lemma{so}\Bfootnote{lev "
                r"3}}}{\lemma{so}\Bfootnote{lev 2}}}{\lemma{so}\Bfootnote{lev"
                r" 1}}")
        expect = (r"\sameword{so} \edtext{\edtext{\edtext{\sameword[1,2,"
                  r"3]{so}}{\lemma{\sameword{so}}\Bfootnote{lev 3}}}{\lemma{"
                  r"\sameword{so}}\Bfootnote{lev 2}}}{\lemma{\sameword{so}}"
                  r"\Bfootnote{lev 1}}")
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

    def test_flat_proximity_match(self):
        text = (r"so sw \edtext{so}{\lemma{so}\Bfootnote{foot content}}  and "
                r"again sw it is all and something after.")
        expect = (r"\sameword{so} sw \edtext{\sameword[1]{so}}{\lemma{"
                  r"\sameword{so}}\Bfootnote{foot content}}  and again sw it is "
                  r"all and something after.")
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

    def test_false_positives(self):
        text = (r"\edtext{in}{\lemma{in}\Bfootnote{note content}} species "
                r"intelligibilis imaginatur secundum Apostolum\index["
                r"persons]{}.")
        assert self.run_annotation(text) == text

    def test_nested_ambiguity(self):
        text = (r"before and \edtext{first here \edtext{and another \edtext{"
                r"and}{\lemma{and}\Afootnote{lvl 3}} that's it}{\lemma{and "
                r"\dots{} it}\Afootnote{lvl 2}}}{\lemma{first \dots{} "
                r"it}\Afootnote{note lvl 1}} after")
        expect = ("before \sameword{and} \edtext{first here \edtext{"
                  "\sameword[2]{and} another \edtext{\sameword[3]{and}}{"
                  "\lemma{\sameword{and}}\Afootnote{lvl 3}} that's it}{\lemma{"
                  "\sameword{and} \dots{} it}\Afootnote{lvl 2}}}{\lemma{first "
                  "\dots{} it}\Afootnote{note lvl 1}} after")
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

    def test_nested_ldots_lemma(self):
        text = (r"sw and \edtext{sw so \edtext{\edtext{sw}{\lemma{"
                "sw}\Bfootnote{lvl 3 note}} another thing \edtext{and more}{"
                "\lemma{and more}\Bfootnote{lvl 3 note}}}{\lemma{sw another "
                "thing and more}\Bfootnote{lvl 2 note}}}{\lemma{sw \ldots "
                "more}\Afootnote{lvl 1 note}} and a sw after and one more "
                "\edtext{flat}{\lemma{flat}\Bfootnote{note here}} entry.")
        expect = (r"\sameword{sw} and \edtext{\sameword[1]{sw} so \edtext{"
                  r"\edtext{\sameword[3]{sw}}{\lemma{\sameword{"
                  r"sw}}\Bfootnote{lvl 3 note}} another thing \edtext{and "
                  r"\sameword[1]{more}}{\lemma{and more}\Bfootnote{lvl 3 "
                  r"note}}}{\lemma{sw another thing and more}\Bfootnote{lvl 2 "
                  r"note}}}{\lemma{\sameword{sw} \ldots \sameword{more}}"
                  r"\Afootnote{lvl 1 note}} and a \sameword{sw} after and one "
                  r"\sameword{more} \edtext{flat}{\lemma{flat}\Bfootnote{note "
                  r"here}} entry.")
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

    def test_multiword_lemma(self):
        text = (r"per multa per causam tamen scire \edtext{causam}{\lemma{"
                r"causam}\Bfootnote{fnote}} est \edtext{per causam}{\lemma{"
                r"per causam}\Bfootnote{causam rei B}} cognoscere \edtext{"
                r"causam}{\lemma{causam}\Bfootnote{fnote}}.")
        expect = (r"per multa \sameword{per \sameword{causam}} tamen scire "
                  r"\edtext{\sameword[1]{causam}}{\lemma{\sameword{causam}}"
                  r"\Bfootnote{fnote}} est \edtext{\sameword[1]{per "
                  r"\sameword{causam}}}{\lemma{\sameword{per causam}}"
                  r"\Bfootnote{causam rei B}} cognoscere \edtext{\sameword[1]"
                  r"{causam}}{\lemma{\sameword{causam}}\Bfootnote{fnote}}.")
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

    def test_long_proximate_before_after(self):
        text = (r"List comprehensions provide a concise a way to create "
                r"lists. Common applications are to make new lists where each "
                r"element is the result of some operations applied to each "
                r"member of another sequence or iterable, or \edtext{to}{"
                r"\lemma{to}\Bfootnote{note}} create a subsequence of those "
                r"elements that satisfy a certain condition. List "
                r"comprehensions provide a concise way to create lists. "
                r"\edtext{Common}{\lemma{Common}\Bfootnote{note}} "
                r"applications are to make new lists where each element is "
                r"the result of some operations applied to each member of "
                r"another sequence or iterable, or to create a subsequence of "
                r"those elements that satisfy a certain condition. Start "
                r"\edtext{a}{\lemma{a}\Bfootnote{lvl 1}} and another a List "
                r"comprehensions provide a concise way to create lists. "
                r"Common applications are to make new lists where each "
                r"element is the result of some operations applied to each "
                r"member of another sequence or iterable, or to create a "
                r"subsequence \edtext{of}{\lemma{of}\Bfootnote{note}} those "
                r"elements that satisfy a certain condition.")
        expect = (r"List comprehensions provide a concise a way to create "
                  r"lists. Common applications are to make new lists where "
                  r"each element is the result of some operations applied "
                  r"\sameword{to} each member of another sequence or "
                  r"iterable, or \edtext{\sameword[1]{to}}{\lemma{\sameword{"
                  r"to}}\Bfootnote{note}} create a subsequence of those "
                  r"elements that satisfy a certain "
                  r"condition. List comprehensions provide a concise way "
                  r"\sameword{to} create lists. \edtext{Common}{\lemma{"
                  r"Common}\Bfootnote{note}} applications are to "
                  r"make new lists where each element is the result of some "
                  r"operations applied to each member of another sequence or "
                  r"iterable, or to create \sameword{a} subsequence of those "
                  r"elements that satisfy \sameword{a} certain condition. Start"
                  r" \edtext{\sameword[1]{a}}{\lemma{\sameword{a}}\Bfootnote{"
                  r"lvl 1}} and another \sameword{a} List comprehensions "
                  r"provide \sameword{a} concise way to create lists. Common "
                  r"applications are to make new lists where each element is "
                  r"the result \sameword{of} some operations applied to each "
                  r"member \sameword{of} another sequence or iterable, "
                  r"or to create a subsequence \edtext{\sameword[1]{of}}{"
                  r"\lemma{\sameword{of}}\Bfootnote{note}} those elements that "
                  r"satisfy a certain condition.")
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

    def test_long_nested_real_world_example(self):
        text = (r'Sed hic occurrunt arduae difficultates; et primo '
                r'consideranda est descriptio fidei quam ponit \name{'
                r'Apostolus\index[persons]{}}, scilicet, \edtext{\enquote{'
                r'fides \edtext{est}{\lemma{est}\Bfootnote{\emph{om.} R}} '
                r'substantia rerum sperandarum, argumentum non '
                r'apparentium.}}{\lemma{}\Afootnote[nosep]{Hebrews 11:1}} Ubi '
                r'secundum \edtext{\name{Altissiodorensis\index[persons]{}} '
                r'\edtext{in}{\lemma{in}\Bfootnote{\emph{om.} R SV S}} '
                r'principio suae \worktitle{Summae}\index[works]{}}{\lemma{'
                r'}\Afootnote[nosep]{Guillelmus Auxerre \worktitle{Summa '
                r'aurea}}} et \edtext{\name{\edtext{Guillelmum}{\lemma{'
                r'Guillelmum}\Bfootnote{guillelmi R}} Parisiensis \index['
                r'persons]{}} tractatu suo \worktitle{De fide et '
                r'legibus}\index[works]{}}{\lemma{}\Afootnote[nosep]{'
                r'Guillelmus Parisiensis, \worktitle{de fide et legibus}}} '
                r'sit una comparatio fidei, respectu credendorum, '
                r'et caritatis, respectu amandorum; unde imaginatur quod '
                r'sicut caritas dirigit hominem ad diligendum Deum propter '
                r'se, ita proportionaliter fides inclinat intellectum ad '
                r'credendum primae veritati propter se et \edtext{super}{'
                r'\lemma{super}\Bfootnote{supra V}} omnia sine alia '
                r'apparentia. Ideo fides est argumentum, et non est '
                r'consequens nec conclusio. Ideo sicut inquit \name{\edtext{'
                r'Guillelmus}{\lemma{Guillelmus}\Bfootnote{\emph{om.} V}} '
                r'Altissiodorensis\index[persons]{}} \edtext{\enquote{a '
                r'quodam bene dictum est quod apud Aristotelem\index['
                r'persons]{} argumentum est ratio rei dubiae faciens fidem, '
                r'apud autem Christum est\edtext{}{\lemma{}\Bfootnote[nosep]{'
                r'\emph{iter.} R SV; The double "est" in R and SV seems like '
                r'a clear mistake, though good corroboration of the intimate '
                r'relationship between these two witnesses.}} fides faciens '
                r'rationem}}{\lemma{}\Afootnote[nosep]{Guillelmus Auxerre, '
                r'\worktitle{Summa aurea}\index[works]{}, prologus.This '
                r'formulation has been identified by Marie-dominique Chenu as '
                r'originating with Simon de Tornai; Cf. Chenu, \worktitle{La '
                r'théologie comme science au XIII siècle} (Paris: Vrin, '
                r'1942), p. 35; Cf. Simon de Tornai, \worktitle{Expositio in '
                r'symbolium Quicumque}, "Propter hoc dictum est a quodam, '
                r'quoniam apud Aristotelem argumentum est ratio rei dubiae '
                r'faciens fidem, apud Christum autem argumentum est fides '
                r'faciens rationem."}}. Et hoc videtur esse contra \edtext{'
                r'\name{Aureolem\index[persons]{}} prima quaestione Prologi '
                r'\edtext{articulo}{\lemma{articulo}\Bfootnote{capitulo V}} '
                r'primo}{\lemma{}\Afootnote[nosep]{Aureoli, Prologue, article '
                r'1}}, qui tenet quod articuli fidei sunt conclusiones ex '
                r'aliis deductae, ad quas \edtext{processus |\ledsidenote{S '
                r'2rb} theologicus et}{\lemma{processus theologicus '
                r'et}\Bfootnote{\emph{om.} V; While this phrase appears a bit '
                r'redundant and therefore somewhat understandable that it is '
                r'omitted by V, we include because it does not hurt the sense '
                r'and it is supported by R, SV, and S}} processus theologici '
                r'principaliter nituntur concludendas; et non sunt tamquam '
                r'principia ex quibus alia theologice \edtext{deducuntur}{'
                r'\lemma{deducuntur}\Bfootnote{deducantur V; The choice of '
                r'the subjunctive by V is unclear to us. Thus, follow the '
                r'indicative reading supported by R, SV, and S}}.')
        expect = (r'Sed hic occurrunt arduae difficultates; et primo '
                  r'consideranda \sameword{est} descriptio fidei quam ponit '
                  r'\name{Apostolus\index[persons]{}}, scilicet, \edtext{'
                  r'\enquote{fides \edtext{\sameword[2]{est}}{\lemma{\sameword{'
                  r'est}}\Bfootnote{\emph{om.} R}} substantia rerum '
                  r'sperandarum, argumentum non apparentium.}}{\lemma{'
                  r'}\Afootnote[nosep]{Hebrews 11:1}} Ubi secundum \edtext{'
                  r'\name{Altissiodorensis\index[persons]{}} \edtext{in}{'
                  r'\lemma{in}\Bfootnote{\emph{om.} R SV S}} principio suae '
                  r'\worktitle{Summae}\index[works]{}}{\lemma{}\Afootnote['
                  r'nosep]{Guillelmus Auxerre \worktitle{Summa aurea}}} et '
                  r'\edtext{\name{\edtext{Guillelmum}{\lemma{'
                  r'Guillelmum}\Bfootnote{guillelmi R}} Parisiensis \index['
                  r'persons]{}} tractatu suo \worktitle{De fide et '
                  r'legibus}\index[works]{}}{\lemma{}\Afootnote[nosep]{'
                  r'Guillelmus Parisiensis, \worktitle{de fide et legibus}}} '
                  r'sit una comparatio fidei, respectu credendorum, '
                  r'et caritatis, respectu amandorum; unde imaginatur quod '
                  r'sicut caritas dirigit hominem ad diligendum Deum propter '
                  r'se, ita proportionaliter fides inclinat intellectum ad '
                  r'credendum primae veritati propter se et \edtext{super}{'
                  r'\lemma{super}\Bfootnote{supra V}} omnia sine alia '
                  r'apparentia. Ideo fides est argumentum, et non est '
                  r'consequens nec conclusio. Ideo sicut inquit \name{'
                  r'\edtext{Guillelmus}{\lemma{Guillelmus}\Bfootnote{\emph{'
                  r'om.} V}} Altissiodorensis\index[persons]{}} \edtext{'
                  r'\enquote{a quodam bene dictum est quod apud '
                  r'Aristotelem\index[persons]{} argumentum est ratio rei '
                  r'dubiae faciens fidem, apud autem Christum est\edtext{}{'
                  r'\lemma{}\Bfootnote[nosep]{\emph{iter.} R SV; The double '
                  r'"est" in R and SV seems like a clear mistake, though good '
                  r'corroboration of the intimate relationship between these '
                  r'two witnesses.}} fides faciens rationem}}{\lemma{'
                  r'}\Afootnote[nosep]{Guillelmus Auxerre, \worktitle{Summa '
                  r'aurea}\index[works]{}, prologus.This formulation has been '
                  r'identified by Marie-dominique Chenu as originating with '
                  r'Simon de Tornai; Cf. Chenu, \worktitle{La théologie comme '
                  r'science au XIII siècle} (Paris: Vrin, 1942), p. 35; Cf. '
                  r'Simon de Tornai, \worktitle{Expositio in symbolium '
                  r'Quicumque}, "Propter hoc dictum est a quodam, quoniam '
                  r'apud Aristotelem argumentum est ratio rei dubiae faciens '
                  r'fidem, apud Christum autem argumentum est fides faciens '
                  r'rationem."}}. Et hoc videtur esse contra \edtext{\name{'
                  r'Aureolem\index[persons]{}} prima quaestione Prologi '
                  r'\edtext{articulo}{\lemma{articulo}\Bfootnote{capitulo V}} '
                  r'primo}{\lemma{}\Afootnote[nosep]{Aureoli, Prologue, '
                  r'article 1}}, qui tenet quod articuli fidei sunt '
                  r'conclusiones ex aliis deductae, ad quas \edtext{processus '
                  r'|\ledsidenote{S 2rb} theologicus et}{\lemma{processus '
                  r'theologicus et}\Bfootnote{\emph{om.} V; While this phrase '
                  r'appears a bit redundant and therefore somewhat '
                  r'understandable that it is omitted by V, we include '
                  r'because it does not hurt the sense and it is supported by '
                  r'R, SV, and S}} processus theologici principaliter '
                  r'nituntur concludendas; et non sunt tamquam principia ex '
                  r'quibus alia theologice \edtext{deducuntur}{\lemma{'
                  r'deducuntur}\Bfootnote{deducantur V; The choice of the '
                  r'subjunctive by V is unclear to us. Thus, follow the '
                  r'indicative reading supported by R, SV, and S}}.')
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

    def test_custom_macros(self):
        """Macro `\exclude` is explicitly excluded, so what is compared is
        'Sortes' and 'Sortes' which is then matched and annotated. """
        old_exclude = settings['exclude_macros']
        settings['exclude_macros'] += [r'\exclude']
        text = (r'Han var sonr \edtext{Hákon\emph{ar}\exclude{Håkon II}}{'
                r'\Afootnote{k\emph{on}gſ hakon\emph{ar} Sk}}, '
                r'sons Hákonar\exclude{Håkon I}')
        expect = (r'Han var sonr \edtext{\sameword[1]{Hákon\emph{'
                  r'ar}}\exclude{Håkon II}}{\Afootnote{k\emph{on}gſ '
                  r'hakon\emph{ar} Sk}}, sons \sameword{Hákonar}\exclude{'
                  r'Håkon I}')
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text
        settings['exclude_macros'] = old_exclude

    def test_custom_multiword(self):
        """Macro `\exclude` is explicitly excluded, so what is compared is
        'Hákonar' and 'Hákonar' which is then matched and annotated. """
        old_exclude = settings['exclude_macros']
        settings['exclude_macros'] += [r'\exclude']
        text = (r'Han var sonr \edtext{Hákon\emph{ar}\exclude{Håkon II} '
                r'konungs}{\Afootnote{k\emph{on}gſ hakon\emph{ar} Sk}}, '
                r'sons Hákonar\exclude{Håkon I} konungs')
        expect = (r'Han var sonr \edtext{\sameword[1]{Hákon\emph{'
                  r'ar}\exclude{Håkon II} konungs}}{\Afootnote{k\emph{on}gſ '
                  r'hakon\emph{ar} Sk}}, sons \sameword{Hákonar\exclude{'
                  r'Håkon I} konungs}')
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text
        settings['exclude_macros'] = old_exclude

    def test_custom_not_excluded_macro_with_match(self):
        """Macro is not explicitly excluded, which means that the
        search-words are 'Sortes1' and 'Sortes1', which matche"""
        text = (r'\edtext{Sortes\test{1}}{\Afootnote{Socrates B}} dicit: '
                r'Sortes\test{1} probus')
        expect = (r'\edtext{\sameword[1]{Sortes\test{1}}}{\Afootnote{Socrates '
                  r'B}} dicit: \sameword{Sortes\test{1}} probus')
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

    def test_custom_not_excluded_macro_without_match(self):
        """Macro is not explicitly excluded, which means that the
        search-words are 'Sortes1' and 'Sortes2', which don't match"""
        text = (r'\edtext{Sortes\test{1}}{\Afootnote{Socrates B}} dicit: '
                r'Sortes\test{2} probus')
        assert self.run_annotation(text) == text

    def test_multiword_with_interveening_macro(self):
        text = (r'per \sidenote{1rb O} causam scire est \edtext{per causam}{'
                r'\lemma{per causam}\Bfootnote{causam rei B}} cognoscere')
        expect = (r'\sameword{per \sidenote{1rb O} causam} scire est \edtext{'
                  r'\sameword[1]{per causam}}{\lemma{\sameword{per causam}}'
                  r'\Bfootnote{causam rei B}} cognoscere')
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

    def test_two_multi_words(self):
        text = (r"\edtext{nobis apparentes}{\lemma{nobis "
                r"apparentes}\Bfootnote{\emph{om.} B}} \edtext{nobis "
                r"apparentes}{\lemma{nobis apparentes}\Bfootnote{\emph{om.} "
                r"B}}")
        expect = (r"\edtext{\sameword[1]{nobis apparentes}}{\lemma{\sameword{"
                  r"nobis apparentes}}\Bfootnote{\emph{om.} B}} "
                  r"\edtext{\sameword[1]{nobis apparentes}}{\lemma{\sameword{"
                  r"nobis apparentes}}\Bfootnote{\emph{om.} B}}")
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

    def test_neutrality_on_already_wrapped(self):
        text = (r"Praeterea intellectus intelligit se: \edtext{\sameword[1]{"
                r"aut}}{\lemma{\sameword{aut}}\Bfootnote{aliter Aguin.}} ergo "
                r"per suam essentiam, \edtext{\sameword[1]{aut}}{\lemma{"
                r"\sameword{aut}}\Bfootnote{aliter Aguin.}} per speciem, "
                r"\edtext{\sameword[1]{aut}}{\lemma{\sameword{aut}}}\Bfootnote{"
                r"aliter Aguin.}} per suum actum; sed \edtext{\sameword[1]{nec}"
                r"}{\lemma{\sameword{nec}}}\Bfootnote{non Aguin.}} per speciem "
                r"|\ledsidenote{B 174vb} \sameword{nec} per suum actum;")
        assert self.run_annotation(text) == text

    def test_text_with_arbitrary_commands(self):
        text = ("\\edlabelS{da-49-l1q1-ysmgk1}% \n\\no{1.1} Illud de quo est "
                r"scientia est intelligibile, quia cum scientia sit habitus "
                r"intellectus, de quo est scientia oportet esse "
                r"intelligibile; sed anima non est intelligibile, quia omnis "
                r"nostra cognitio ortum habet a sensu, \edtext{unde ipsum "
                r"intelligere non est}{\lemma{unde \dots{} est}\Bfootnote{"
                r"quia nihil intelligimus B}} sine phantasmate, sed anima sub "
                r"sensu non cadit, nec phantasma facit; ergo et "
                r"cetera.\edlabelE{da-49-l1q1-ysmgk1}")
        expect = ("\\edlabelS{da-49-l1q1-ysmgk1}% \n\\no{1.1} Illud de quo "
                  r"est scientia est intelligibile, quia cum scientia sit "
                  r"habitus intellectus, de quo "
                  r"\sameword{est} scientia oportet esse intelligibile; sed "
                  r"anima non \sameword{est} intelligibile, quia omnis nostra "
                  r"cognitio ortum habet a sensu, \edtext{unde ipsum "
                  r"intelligere non \sameword[1]{est}}{\lemma{unde \dots{} "
                  r"\sameword{est}}\Bfootnote{quia nihil intelligimus B}} sine "
                  r"phantasmate, sed anima sub sensu non cadit, nec phantasma "
                  r"facit; ergo et cetera.\edlabelE{da-49-l1q1-ysmgk1}")
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

    def test_match_word_boundary_match_outside_both_ends(self):
        text = (r"test thirtieth twenty-ninth twenty-eighth twenty-seventh "
                r"twenty-sixth twenty-fifth twenty-fourth twenty-third "
                r"twenty-second twenty-first twentieth nineteenth eighteenth "
                r"seventeenth sixteenth fifteenth fourteenth thirteenth "
                r"twelfth eleventh tenth ninth eighth seventh sixth fifth "
                r"fourth third second first \edtext{test}{\Afootnote{check}} "
                r"first second third fourth fifth sixth seventh eighth ninth "
                r"tenth eleventh twelfth thirteenth fourteenth fifteenth "
                r"sixteenth seventeenth eighteenth nineteenth twentieth "
                r"twenty-first twenty-second twenty-third twenty-fourth "
                r"twenty-fifth twenty-sixth twenty-seventh twenty-eighth "
                r"twenty-ninth thirtieth test")
        assert self.run_annotation(text) == text

    def test_match_word_boundary_match_inside_at_start(self):
        text = (r"test nineteenth eighteenth "
                r"seventeenth sixteenth fifteenth fourteenth thirteenth "
                r"twelfth eleventh tenth ninth eighth seventh sixth fifth "
                r"fourth third second first \edtext{test}{\Afootnote{check}} "
                r"first second third fourth fifth sixth seventh eighth ninth "
                r"tenth eleventh twelfth thirteenth fourteenth fifteenth "
                r"sixteenth seventeenth eighteenth nineteenth twentieth "
                r"test")
        expect = (r"\sameword{test} nineteenth "
                  r"eighteenth seventeenth sixteenth fifteenth fourteenth "
                  r"thirteenth twelfth eleventh tenth ninth eighth seventh "
                  r"sixth fifth fourth third second first \edtext{\sameword["
                  r"1]{test}}{\Afootnote{check}} first second third fourth "
                  r"fifth sixth seventh eighth ninth tenth eleventh twelfth "
                  r"thirteenth fourteenth fifteenth sixteenth seventeenth "
                  r"eighteenth nineteenth twentieth test")
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

    def test_match_word_boundary_match_inside_at_end(self):
        text = (r"test twentieth nineteenth eighteenth "
                r"seventeenth sixteenth fifteenth fourteenth thirteenth "
                r"twelfth eleventh tenth ninth eighth seventh sixth fifth "
                r"fourth third second first \edtext{test}{\Afootnote{check}} "
                r"first second third fourth fifth sixth seventh eighth ninth "
                r"tenth eleventh twelfth thirteenth fourteenth fifteenth "
                r"sixteenth seventeenth eighteenth nineteenth test")
        expect = (r"test twentieth nineteenth "
                  r"eighteenth seventeenth sixteenth fifteenth fourteenth "
                  r"thirteenth twelfth eleventh tenth ninth eighth seventh "
                  r"sixth fifth fourth third second first \edtext{\sameword["
                  r"1]{test}}{\Afootnote{check}} first second third fourth "
                  r"fifth sixth seventh eighth ninth tenth eleventh twelfth "
                  r"thirteenth fourteenth fifteenth sixteenth seventeenth "
                  r"eighteenth nineteenth \sameword{test}")
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

    def test_match_word_boundary_match_both_ends(self):
        text = (r"test nineteenth eighteenth "
                r"seventeenth sixteenth fifteenth fourteenth thirteenth "
                r"twelfth eleventh tenth ninth eighth seventh sixth fifth "
                r"fourth third second first \edtext{test}{\Afootnote{check}} "
                r"first second third fourth fifth sixth seventh eighth ninth "
                r"tenth eleventh twelfth thirteenth fourteenth fifteenth "
                r"sixteenth seventeenth eighteenth nineteenth test")
        expect = (r"\sameword{test} nineteenth "
                  r"eighteenth seventeenth sixteenth fifteenth fourteenth "
                  r"thirteenth twelfth eleventh tenth ninth eighth seventh "
                  r"sixth fifth fourth third second first \edtext{\sameword["
                  r"1]{test}}{\Afootnote{check}} first second third fourth "
                  r"fifth sixth seventh eighth ninth tenth eleventh twelfth "
                  r"thirteenth fourteenth fifteenth sixteenth seventeenth "
                  r"eighteenth nineteenth \sameword{test}")
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

    def test_spaced_index_command(self):
        text = r'\edtext{A}{\Afootnote{a}}\index{A, A}'
        assert self.run_annotation(text) == text

    def test_on_comments(self):
        text = r'\edtext{A}{\Afootnote{a}}     %A'
        assert self.run_annotation(text) == text

    def test_annotation_around_comments(self):
        text = """
word % some word commented out
word
w%
%something commented out
%something else commented out
o% some letter commented out
r% another word just to see what will happen
d
word wo% check whether "o" or "ø"
rd
\edtext{w%
%
ord}{\Afootnote{statement}} %A
w% "W" or "w"?
ord
word
"""
        expect = """
\sameword{word} % some word commented out
\sameword{word}
\sameword{w%
%something commented out
%something else commented out
o% some letter commented out
r% another word just to see what will happen
d}
\sameword{word} \sameword{wo% check whether "o" or "ø"
rd}
\edtext{\sameword[1]{w%
%
ord}}{\Afootnote{statement}} %A
\sameword{w% "W" or "w"?
ord}
\sameword{word}
"""
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

    def test_case_insensitive_context_no_match_lemma(self):
        settings['sensitive_context_match'] = False
        text = r'\edtext{A}{\lemma{A}\Afootnote{x}} a'
        expect = (r'\edtext{\sameword[1]{A}}{\lemma{\sameword{A}}\Afootnote{x}} '
                  r'\sameword{a}')
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text
        settings['sensitive_context_match'] = True

    def test_case_insensitive_context_no_match_edtext(self):
        settings['sensitive_context_match'] = False
        text = r'\edtext{A}{\Afootnote{x}} a'
        expect = r'\edtext{\sameword[1]{A}}{\Afootnote{x}} \sameword{a}'
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text
        settings['sensitive_context_match'] = True

    def test_case_sensitive_context_match_lemma(self):
        text = r'\edtext{A}{\lemma{A}\Afootnote{x}} a'
        assert self.run_annotation(text) == text

    def test_case_sensitive_context_match_edtext(self):
        text = r'\edtext{A}{\Afootnote{x}} a'
        assert self.run_annotation(text) == text

    def test_latex_expression_escaping(self):
        text = r'\\ \& \% \$ \# \_ \{ \} \~ \^'
        assert self.run_annotation(text) == text

    def test_latex_expression_escaped_not_matching(self):
        text = r'\edtext{a and b}{\Afootnote{x}} a \& b'
        assert self.run_annotation(text) == text

    def test_latex_expression_escaped_matching(self):
        text = r'\edtext{a \& b}{\Afootnote{x}} a \& b'
        expect = (r'\edtext{\sameword[1]{a \& b}}{\Afootnote{x}} \sameword{a '
                  r'\& b}')
        assert self.run_annotation(text) == expect
        assert self.run_cleanup(expect) == text

class TestUpdate:

    def run_update(self, input_text):
        tokenization = Tokenizer(input_text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        words = matcher.update()
        return words.write()

    def test_update_single_no_change(self):
        text = (r'\sameword{emphasis} \edtext{\sameword[1]{emphasis}}{'
                  r'\Bfootnote{fnote}} is \sameword{emphasis}')
        assert self.run_update(text) == text

    def test_update_with_change(self):
        text = (r'\sameword{emphasis} a emph \edtext{'
                r'\sameword[1]{emph}}{\Bfootnote{fnote}} and emph '
                r'\sameword{emphasis}')
        expect = (r'emphasis a \sameword{emph} \edtext{'
                  r'\sameword[1]{emph}}{\Bfootnote{fnote}} and \sameword{emph} '
                  r'emphasis')
        assert self.run_update(text) == expect

    def test_update_single_level_multiword_lemma(self):
        text = (r'a c and \sameword{a b} \edtext{\sameword[1]{a '
                  r'c}}{\lemma{\sameword{a c}}\Bfootnote{fnote}} \sameword{a b}'
                  r' and a c')
        expect = (r'\sameword{a c} and a b \edtext{\sameword[1]{a c}}{\lemma{'
                  r'\sameword{a c}}\Bfootnote{fnote}} a b and \sameword{a c}')
        assert self.run_update(text) == expect

    def test_update_single_level_multiword_lemma_ellipsis(self):
        text = (r'\sameword{a} b and \sameword{c} \edtext{\sameword[1]{a} '
                  r'and \sameword[1]{b}}{\lemma{\sameword{a} \dots{} '
                  r'\sameword{b}}\Bfootnote{fnote}} and \sameword{c} and '
                  r'\sameword{c} and b and b')
        expect = (r'\sameword{a} \sameword{b} and c \edtext{\sameword[1]{a} '
                  r'and \sameword[1]{b}}{\lemma{\sameword{a} \dots{} '
                  r'\sameword{b}}\Bfootnote{fnote}} and c and c and '
                  r'\sameword{b} and \sameword{b}')
        assert self.run_update(text) == expect

    def test_three_close_nested_levels(self):
        text = (r"sw \sameword{so} \edtext{\edtext{\edtext{\sameword[1,2,"
                  r"3]{sw}}{\lemma{\sameword{sw}}\Bfootnote{lev 3}}}{\lemma{"
                  r"\sameword{sw}}\Bfootnote{lev 2}}}{\lemma{\sameword{sw}}"
                  r"\Bfootnote{lev 1}} sw")
        expect = (r"\sameword{sw} so \edtext{\edtext{\edtext{\sameword[1,2,"
                r"3]{sw}}{\lemma{\sameword{sw}}\Bfootnote{lev 3}}}{\lemma{"
                r"\sameword{sw}}\Bfootnote{lev 2}}}{\lemma{\sameword{sw}}"
                r"\Bfootnote{lev 1}} \sameword{sw}")
        assert self.run_update(text) == expect

    def test_flat_proximity_match(self):
        text = (r"\sameword{so} sw \edtext{\sameword[1]{sw}}{\lemma{"
                  r"\sameword{sw}}\Bfootnote{foot content}}  and again sw it is"
                  r" all and something after.")
        expect = (r"so \sameword{sw} \edtext{\sameword[1]{sw}}{\lemma{"
                r"\sameword{sw}}\Bfootnote{foot content}}  and again "
                r"\sameword{sw} it is all and something after.")
        assert self.run_update(text) == expect


    def test_nested_ambiguity(self):
        text = ("but \sameword{and} \edtext{first here \edtext{"
                  "\sameword[2]{but} another \edtext{\sameword[3]{but}}{"
                  "\lemma{\sameword{but}}\Afootnote{lvl 3}} that's it}{\lemma{"
                  "\sameword{but} \dots{} it}\Afootnote{lvl 2}}}{\lemma{first "
                  "\dots{} it}\Afootnote{note lvl 1}} after")
        expect = ("\sameword{but} and \edtext{first here \edtext{"
                "\sameword[2]{but} another \edtext{\sameword[3]{but}}{"
                "\lemma{\sameword{but}}\Afootnote{lvl 3}} that's it}{\lemma{"
                "\sameword{but} \dots{} it}\Afootnote{lvl 2}}}{\lemma{first "
                "\dots{} it}\Afootnote{note lvl 1}} after")
        assert self.run_update(text) == expect


class TestGetContext:

    def run_get_context_after(self, input_text: str, boundary: int):
        tokenization = Tokenizer(input_text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        return matcher._get_context_after(tokenization.wordlist, boundary)

    def run_get_context_before(self, input_text: str, boundary: int):
        tokenization = Tokenizer(input_text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        return matcher._get_context_before(tokenization.wordlist, boundary)

    def test_get_from_long_context_after_without_empty(self):
        text = (r"List comprehensions provide a concise a way to create "
                r"lists. Common applications are to make new lists where each "
                r"element is the result of some operations applied to each "
                r"member of another sequence or iterable, or \edtext{to}{"
                r"\lemma{to}\Bfootnote{note}} create a subsequence of those "
                r"elements that satisfy a certain condition. List "
                r"comprehensions provide a concise way to create lists. "
                r"\edtext{Common}{\lemma{Common}\Bfootnote{note}} "
                r"applications are to make new lists where each element is "
                r"the result of some operations applied to each member of "
                r"another sequence or iterable, or to create a subsequence of "
                r"those elements that satisfy a certain condition. Start ")
        expect = ['Common', 'applications', 'are', 'to', 'make', 'new',
                  'lists', 'where', 'each', 'element', 'is', 'the', 'result',
                  'of', 'some', 'operations', 'applied', 'to', 'each',
                  'member']
        assert self.run_get_context_after(text, 10) == expect

    def test_get_from_long_context_after_with_empty(self):
        text = (r"List comprehensions provide a concise a way to create "
                r"lists. Common  ... applications \emph{} are to make new "
                r"element is the result of some operations applied to each "
                r"member of another sequence or iterable, or \edtext{to}{"
                r"\lemma{to}\Bfootnote{note}} \emph{} , a subsequence of those "
                r"element s that satisfy \index{} a certain condition. "
                r"comprehensions provide a concise way to create lists. "
                r"\edtext{Common}{\lemma{Common}\Bfootnote{note}} "
                r"applications are to make new lists where each element is "
                r"the result of some operations applied to each member of "
                r"another sequence or iterable, or to create a subsequence of "
                r"those elements that satisfy a certain condition. Start ")
        expect = ['Common', '', 'applications', '', 'are', 'to', 'make',
                  'new', 'element', 'is', 'the', 'result', 'of', 'some',
                  'operations', 'applied', 'to', 'each', 'member', 'of',
                  'another', 'sequence']
        assert self.run_get_context_after(text, 10) == expect

    def test_get_from_short_context_after_without_empty(self):
        text = (r"another sequence or iterable, or to create a subsequence of "
                r"those elements that satisfy a certain condition. Start ")
        expect = ['those', 'elements', 'that', 'satisfy', 'a', 'certain',
                  'condition', 'Start']
        assert self.run_get_context_after(text, 10) == expect

    def test_get_from_long_context_before_without_empty(self):
        text = (r"List comprehensions provide a concise a way to create "
                r"lists. Common applications are to make new lists where each "
                r"element is the result of some operations applied to each "
                r"member of another sequence or iterable, or \edtext{to}{"
                r"\lemma{to}\Bfootnote{note}} create a subsequence of those "
                r"elements that satisfy a certain condition. List "
                r"comprehensions provide a concise way to create lists. "
                r"\edtext{Common}{\lemma{Common}\Bfootnote{note}} "
                r"applications are to make new lists where each element is "
                r"the result of some operations applied to each member of "
                r"another sequence or iterable, or to create a subsequence of "
                r"those elements that satisfy a certain condition. Start ")
        expect = ['operations', 'applied', 'to', 'each', 'member', 'of',
                  'another', 'sequence', 'or', 'iterable', 'or', 'to',
                  'create', 'a', 'subsequence', 'of', 'those', 'elements',
                  'that', 'satisfy']
        assert self.run_get_context_before(text, 45) == expect

    def test_get_from_long_context_before_with_empty(self):
        text = (r"List comprehensions provide a concise a way to create "
                r"lists. Common  ... applications \emph{} are to make new "
                r"element is the result of some operations applied to each "
                r"member of another sequence or iterable, or \edtext{to}{"
                r"\lemma{to}\Bfootnote{note}} \emph{} , a subsequence of those "
                r"elements that satisfy \index{} a certain condition. "
                r"comprehensions provide a concise way to create lists. "
                r"\edtext{Common}{\lemma{Common}\Bfootnote{note}} "
                r"applications are to make new lists where each element is "
                r"the result of some operations applied to each member of "
                r"another sequence or iterable, or to create a subsequence of "
                r"those elements that satisfy a certain condition. Start ")
        expect = ['of', 'some', 'operations', 'applied', 'to',
                  'each', 'member', 'of', 'another', 'sequence', 'or',
                  'iterable', 'or', 'to', '', '', 'a', 'subsequence',
                  'of', 'those', 'elements', 'that', 'satisfy']
        assert self.run_get_context_before(text, 45) == expect

    def test_get_from_short_context_before_without_empty(self):
        text = (r"another sequence or iterable, or to create a subsequence of "
                r"those elements that satisfy a certain condition. Start ")
        expect = ['another', 'sequence', 'or', 'iterable', 'or', 'to',
                  'create', 'a', 'subsequence', 'of']
        assert self.run_get_context_before(text, 10) == expect

    def test_get_from_end(self):
        text = (r"another sequence or iterable, or to create a subsequence of "
                r"those elements that satisfy a certain condition. Start ")
        assert self.run_get_context_after(text, 18) == []

    def test_get_backward_from_start(self):
        text = (r"another sequence or iterable, or to create a subsequence of "
                r"those elements that satisfy a certain condition. Start ")
        assert self.run_get_context_before(text, 0) == []

    def test_get_context_modified_range(self):
        text = (r"List comprehensions provide a concise a way to create "
                r"lists. Common applications are to make new lists where each "
                r"element is the result of some operations applied to each "
                r"member of another sequence or iterable, or \edtext{to}{"
                r"\lemma{to}\Bfootnote{note}} create a subsequence of those "
                r"elements that satisfy a certain condition.")
        expect = ['List', 'comprehensions', 'provide', 'a', 'concise', 'a',
                  'way', 'to', 'create', 'lists']
        old_dist = settings['context_distance']
        settings['context_distance'] = 10
        assert self.run_get_context_after(text, 0) == expect
        assert len(self.run_get_context_after(text, 0)) == 10
        settings['context_distance'] = old_dist

    def test_get_context_before_modified_range(self):
        text = (r"List comprehensions provide a concise a way to create "
                r"lists. Common applications are to make new lists where each "
                r"element is the result of some operations applied to each "
                r"member of another sequence or iterable, or \edtext{to}{"
                r"\lemma{to}\Bfootnote{note}} create a subsequence of those "
                r"elements that satisfy a certain condition.")
        expect = ['Common', 'applications', 'are', 'to', 'make', 'new',
                  'lists', 'where', 'each', 'element']
        old_dist = settings['context_distance']
        settings['context_distance'] = 10
        assert self.run_get_context_before(text, 20) == expect
        assert len(self.run_get_context_before(text, 20)) == 10
        settings['context_distance'] = old_dist


class TestSamewordWrapper:

    def test_wrap_unwrapped_sameword(self):
        text = r'sw'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=1)
        assert matcher.words.write() == r'\sameword[1]{sw}'

    def test_wrap_multiword(self):
        text = r'\sameword{one word and another}'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=0)
        assert matcher.words.write() == r'\sameword{one word and another}'

    def test_wrap_wrapped_sameword_without_argument(self):
        text = r'\sameword{sw}'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=2)
        assert matcher.words.write() == r'\sameword[2]{sw}'

    def test_wrap_wrapped_multiword_without_argument(self):
        text = r'\sameword{one word and another}'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=2)
        assert matcher.words.write() == r'\sameword[2]{one word and another}'

    def test_wrap_wrapped_sameword_with_argument(self):
        text = r'\sameword[2]{sw}'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=1)
        assert matcher.words.write() == r'\sameword[1,2]{sw}'

    def test_wrap_wrapped_multiword_with_argument(self):
        text = r'\sameword[2]{one word and another}'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=1)
        assert matcher.words.write() == r'\sameword[1,2]{one word and another}'

    def test_wrap_wrapped_in_edtext(self):
        text = r'\edtext{\sameword[1]{sw} with more}'
        expect = r'\edtext{\sameword[2]{\sameword[1]{sw} with more}}'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=2)
        assert matcher.words.write() == expect

    def test_wrap_no_lemma(self):
        text = r'sw'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=0)
        assert matcher.words.write() == r'\sameword{sw}'

    def test_wrap_multiword_no_lemma(self):
        text = r'one word and another'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=0)
        assert matcher.words.write() == r'\sameword{one word and another}'

    def test_wrap_multi_partially_wrapped(self):
        text = r'input \sameword{material}'
        expect = r'\sameword{input \sameword{material}}'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=0)
        assert matcher.words.write() == expect

    def test_wrap_multi_both_wrapped(self):
        text = r'\sameword{input} \sameword{material}'
        expect = r'\sameword[1]{\sameword{input} \sameword{material}}'
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=1)
        assert matcher.words.write() == expect

    def test_reg(self):
        text = "per causam,"
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        matcher._add_sameword(matcher.words, level=1)
        assert matcher.words.write() == r"\sameword[1]{per causam},"


class TestDefineSearchWords:

    def run_wordlist(self, input_text):
        tokenization = Tokenizer(input_text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        cont, _ = matcher._define_search_words(tokenization.wordlist)
        return cont

    def test_single_lemma_word(self):
        text = '\edtext{item}{\lemma{item}\Bfootnote{fnote}}'
        assert self.run_wordlist(text) == ['item']

    def test_multiword_lemma_first(self):
        text = '\edtext{item and more}{\lemma{item and more}\Bfootnote{fnote}}'
        assert self.run_wordlist(text) == ['item', 'and', 'more']

    def test_ellipsis_lemma_first(self):
        text = '\edtext{one a b c more}{\lemma{one ... more}\Bfootnote{fnote}}'
        assert self.run_wordlist(text) == ['one', 'more']

    def test_single_no_lemma(self):
        text = '\edtext{item}{\Bfootnote{fnote}}'
        assert self.run_wordlist(text) == ['item']

    def test_multiword_no_lemma(self):
        text = '\edtext{item and more}{\Bfootnote{fnote}}'
        assert self.run_wordlist(text) == ['item', 'and', 'more']

    def test_nested_multiwords_no_lemma(self):
        """Simulate the annotation procedure by getting the search word
        results for each nested level """
        text = r"""
            \edtext{lvl1 \edtext{lvl2 \edtext{lvl3-1}{\Bfootnote{n3}} inter
            \edtext{lvl3-2}{\Bfootnote{n4}}}{\Bfootnote{n2}}}{\Bfootnote{n1}}
            """
        expect = [['lvl1', 'lvl2', 'lvl3-1', 'inter', 'lvl3-2'],
                  ['lvl2', 'lvl3-1', 'inter', 'lvl3-2'],
                  ['lvl3-1'], ['lvl3-2']]
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        search_words = []
        for entry in matcher.registry:
            edtext_start = entry['data'][0]
            edtext_end = entry['data'][1]
            edtext_lvl = entry['lvl']
            edtext = matcher.words[edtext_start:edtext_end + 1]
            words, _ = matcher._define_search_words(edtext)
            search_words.append(words)
        assert search_words == expect

    def test_nested_multiwords_with_lemma(self):
        """Simulate the annotation procedure by getting the search word
        results for each nested level """
        text = (r"\edtext{lvl1 \edtext{lvl2 \edtext{lvl3-1}{\lemma{"
                r"l3}\Bfootnote{n3}} inter \edtext{lvl3-2}{\lemma{"
                r"l4}\Bfootnote{n4}}}{\lemma{l2}\Bfootnote{n2}}}{\lemma{"
                r"l1}\Bfootnote{n1}}")
        expect = [['l1'], ['l2'], ['l3'], ['l4']]
        tokenization = Tokenizer(text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        search_words = []
        for entry in matcher.registry:
            edtext_start = entry['data'][0]
            edtext_end = entry['data'][1]
            edtext_lvl = entry['lvl']
            edtext = matcher.words[edtext_start:edtext_end + 1]
            words, _ = matcher._define_search_words(edtext)
            search_words.append(words)
        assert search_words == expect

    def test_custom_ellipses_with_space(self):
        old_exclude = settings['exclude_macros']
        settings['exclude_macros'] += [
            "\\.\\.\\.",
            "-+",
            "\\,-\\,",
            "\\\\,-+\\\\,"
        ]
        single_dash = r'\edtext{A B C D E}{\lemma{A - E}\Afootnote{}}'
        double_dash = r'\edtext{A B C D E}{\lemma{A -- E}\Afootnote{}}'
        triple_dash = r'\edtext{A B C D E}{\lemma{A --- E}\Afootnote{}}'
        endash = r'\edtext{A B C D E}{\lemma{A – E}\Afootnote{}}'
        emdash = r'\edtext{A B C D E}{\lemma{A — E}\Afootnote{}}'
        comma_string = r'\edtext{A B C D E}{\lemma{A ,-, E}\Afootnote{}}'
        thin_space = r'\edtext{A B C D E}{\lemma{A\,--\,E}\Afootnote{}}'
        dots = r'\edtext{A B C D E}{\lemma{A \dots E}\Afootnote{}}'
        dots_brackets = r'\edtext{A B C D E}{\lemma{A \dots{} E}\Afootnote{}}'
        ldots = r'\edtext{A B C D E}{\lemma{A \ldots E}\Afootnote{}}'
        ldots_brackets = r'\edtext{A B C D E}{\lemma{A \ldots{} E}\Afootnote{}}'
        expect = ['A', 'E']
        assert self.run_wordlist(single_dash) == expect
        assert self.run_wordlist(double_dash) == expect
        assert self.run_wordlist(triple_dash) == expect
        assert self.run_wordlist(endash) == expect
        assert self.run_wordlist(emdash) == expect
        assert self.run_wordlist(comma_string) == expect
        assert self.run_wordlist(thin_space) == expect
        assert self.run_wordlist(dots) == expect
        assert self.run_wordlist(dots_brackets) == expect
        assert self.run_wordlist(ldots) == expect
        assert self.run_wordlist(ldots_brackets) == expect
        settings['exclude_macros'] = old_exclude

    def test_custom_ellipses_without_space(self):
        old_exclude = settings['exclude_macros']
        settings['exclude_macros'] += [
            "\\.\\.\\.",
            "-+",
            "\\,-\\,",
            "\\\\,-+\\\\,"
        ]
        single_dash = r'\edtext{A B C D E}{\lemma{A-E}\Afootnote{}}'
        double_dash = r'\edtext{A B C D E}{\lemma{A--E}\Afootnote{}}'
        triple_dash = r'\edtext{A B C D E}{\lemma{A---E}\Afootnote{}}'
        endash = r'\edtext{A B C D E}{\lemma{A–E}\Afootnote{}}'
        emdash = r'\edtext{A B C D E}{\lemma{A—E}\Afootnote{}}'
        comma_string = r'\edtext{A B C D E}{\lemma{A,-,E}\Afootnote{}}'
        dots = r'\edtext{A B C D E}{\lemma{A\dots{}E}\Afootnote{}}'
        ldots_brackets = r'\edtext{A B C D E}{\lemma{A\ldots{}E}\Afootnote{}}'
        expect = ['A', 'E']

        assert self.run_wordlist(single_dash) == expect
        assert self.run_wordlist(double_dash) == expect
        assert self.run_wordlist(triple_dash) == expect
        assert self.run_wordlist(endash) == expect
        assert self.run_wordlist(emdash) == expect
        assert self.run_wordlist(comma_string) == expect
        assert self.run_wordlist(dots) == expect
        assert self.run_wordlist(ldots_brackets) == expect
        settings['exclude_macros'] = old_exclude
