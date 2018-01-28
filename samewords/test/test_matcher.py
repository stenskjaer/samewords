from samewords.matcher import Matcher
from samewords.tokenize import Tokenizer
from samewords import settings


class TestMatcher:

    def run_annotation(self, input_text):
        tokenization = Tokenizer(input_text)
        matcher = Matcher(tokenization.wordlist, tokenization.registry)
        words = matcher.annotate()
        return words.write()

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

    def test_match_single_level_multiple_context_matches(self):
        text = (r'emphasis a emphasis \edtext{emphasis}{\Bfootnote{fnote}} '
                r'and emphasis')
        expect = (r'\sameword{emphasis} a \sameword{emphasis} \edtext{'
                  r'\sameword[1]{emphasis}}{\Bfootnote{fnote}} and \sameword{'
                  r'emphasis}')
        assert self.run_annotation(text) == expect

    def test_match_single_level_multiword(self):
        text = (r'\sameword{a b} and a b \edtext{a b}{\Bfootnote{fnote}} a b '
                r'and a b')
        expect = (r'\sameword{a b} and \sameword{a b} \edtext{\sameword[1]{a '
                  r'b}}{\Bfootnote{fnote}} \sameword{a b} and \sameword{a b}')
        assert self.run_annotation(text) == expect

    def test_match_single_level_multiword_lemma(self):
        text = (r'\sameword{a b} and a b \edtext{a b}{\lemma{a b}\Bfootnote{'
                r'fnote}} a b and a b')
        expect = (r'\sameword{a b} and \sameword{a b} \edtext{\sameword[1]{a '
                  r'b}}{\lemma{a b}\Bfootnote{fnote}} \sameword{a b} and '
                  r'\sameword{a b}')
        assert self.run_annotation(text) == expect

    def test_match_single_level_multiword_lemma_ellipsis(self):
        text = (r'\sameword{a} b and c \edtext{a and c}{\lemma{a \dots{} '
                r'c}\Bfootnote{fnote}} and c and c')
        expect = (r'\sameword{a} b and \sameword{c} \edtext{\sameword[1]{a} '
                  r'and \sameword[1]{c}}{\lemma{a \dots{} c}\Bfootnote{'
                  r'fnote}} and \sameword{c} and \sameword{c}')
        assert self.run_annotation(text) == expect

    def test_three_close_nested_levels(self):
        text = (r"so \edtext{\edtext{\edtext{so}{\lemma{so}\Bfootnote{lev "
                r"3}}}{\lemma{so}\Bfootnote{lev 2}}}{\lemma{so}\Bfootnote{lev"
                r" 1}}")
        expect = (r"\sameword{so} \edtext{\edtext{\edtext{\sameword[1,2,"
                  r"3]{so}}{\lemma{so}\Bfootnote{lev 3}}}{\lemma{"
                  r"so}\Bfootnote{lev 2}}}{\lemma{so}\Bfootnote{lev "
                  r"1}}")
        assert self.run_annotation(text) == expect

    def test_flat_proximity_match(self):
        text = (r"so sw \edtext{so}{\lemma{so}\Bfootnote{foot content}}  and "
                r"again sw it is all and something after.")
        expect = (r"\sameword{so} sw \edtext{\sameword[1]{so}}{\lemma{"
                  r"so}\Bfootnote{foot content}}  and again sw it is all and "
                  r"something after.")
        assert self.run_annotation(text) == expect

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
                  "\lemma{and}\Afootnote{lvl 3}} that's it}{\lemma{and \dots{"
                  "} it}\Afootnote{lvl 2}}}{\lemma{first \dots{} "
                  "it}\Afootnote{note lvl 1}} after")
        assert self.run_annotation(text) == expect

    def test_nested_ldots_lemma(self):
        text = (r"sw and \edtext{sw so \edtext{\edtext{sw}{\lemma{"
                "sw}\Bfootnote{lvl 3 note}} another thing \edtext{and more}{"
                "\lemma{and more}\Bfootnote{lvl 3 note}}}{\lemma{sw another "
                "thing and more}\Bfootnote{lvl 2 note}}}{\lemma{sw \ldots "
                "more}\Afootnote{lvl 1 note}} and a sw after and one more "
                "\edtext{flat}{\lemma{flat}\Bfootnote{note here}} entry.")
        expect = (r"\sameword{sw} and \edtext{\sameword[1]{sw} so \edtext{"
                  r"\edtext{\sameword[3]{sw}}{\lemma{"
                  r"sw}\Bfootnote{lvl 3 note}} another thing \edtext{and "
                  r"\sameword[1]{more}}{\lemma{and more}\Bfootnote{lvl 3 "
                  r"note}}}{\lemma{sw another thing and more}\Bfootnote{lvl 2 "
                  r"note}}}{\lemma{sw \ldots more}\Afootnote{lvl 1 note}} and "
                  r"a \sameword{sw} after and one \sameword{more} \edtext{"
                  r"flat}{\lemma{flat}\Bfootnote{note here}} entry.")
        assert self.run_annotation(text) == expect

    def test_multiword_lemma(self):
        text = (r"per multa per causam tamen scire \edtext{causam}{\lemma{"
                r"causam}\Bfootnote{fnote}} est \edtext{per causam}{\lemma{"
                r"per causam}\Bfootnote{causam rei B}} cognoscere \edtext{"
                r"causam}{\lemma{causam}\Bfootnote{fnote}}.")
        expect = (r"per multa \sameword{per \sameword{causam}} tamen scire "
                  r"\edtext{\sameword[1]{causam}}{\lemma{causam}\Bfootnote{"
                  r"fnote}} est \edtext{\sameword[1]{per \sameword{causam}}}{"
                  r"\lemma{per causam}\Bfootnote{causam rei B}} cognoscere "
                  r"\edtext{\sameword[1]{causam}}{\lemma{causam}\Bfootnote{"
                  r"fnote}}.")
        assert self.run_annotation(text) == expect

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
        expect = (r"List comprehensions provide a concise a way \sameword{to} "
                  r"create lists. Common applications are \sameword{to} make "
                  r"new lists where each element is the result of some "
                  r"operations applied \sameword{to} each member of another "
                  r"sequence or iterable, or \edtext{\sameword[1]{to}}{"
                  r"\lemma{to}\Bfootnote{note}} create a "
                  r"subsequence of those elements that satisfy a certain "
                  r"condition. List comprehensions provide a concise way "
                  r"\sameword{to} create lists. \edtext{Common}{\lemma{"
                  r"Common}\Bfootnote{note}} applications are \sameword{to} "
                  r"make new lists where each element is the result of some "
                  r"operations applied to each member of another sequence or "
                  r"iterable, or to create \sameword{a} subsequence of those "
                  r"elements that satisfy \sameword{a} certain condition. Start"
                  r" \edtext{\sameword[1]{a}}{\lemma{a}\Bfootnote{"
                  r"lvl 1}} and another \sameword{a} List comprehensions "
                  r"provide \sameword{a} concise way to create lists. Common "
                  r"applications are to make new lists where each element is "
                  r"the result \sameword{of} some operations applied to each "
                  r"member \sameword{of} another sequence or iterable, "
                  r"or to create a subsequence \edtext{\sameword[1]{of}}{"
                  r"\lemma{of}\Bfootnote{note}} those elements that satisfy a "
                  r"certain condition.")
        assert self.run_annotation(text) == expect

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
                  r'\enquote{fides \edtext{\sameword[2]{est}}{\lemma{'
                  r'est}\Bfootnote{\emph{om.} R}} substantia rerum '
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

    def test_custom_macros(self):
        """Macro `\exclude` is explicitly excluded, so what is compared is
        'Sortes' and 'Sortes' which is then matched and annotated. """
        old_exclude = settings.exclude_macros
        settings.exclude_macros += [r'\exclude']
        text = (r'Han var sonr \edtext{Hákon\emph{ar}\exclude{Håkon II}}{'
                r'\Afootnote{k\emph{on}gſ hakon\emph{ar} Sk}}, '
                r'sons Hákonar\exclude{Håkon I}')
        expect = (r'Han var sonr \edtext{\sameword[1]{Hákon\emph{'
                  r'ar}}\exclude{Håkon II}}{\Afootnote{k\emph{on}gſ '
                  r'hakon\emph{ar} Sk}}, sons \sameword{Hákonar}\exclude{'
                  r'Håkon I}')
        assert self.run_annotation(text) == expect
        settings.exclude_macros = old_exclude

    def test_custom_multiword(self):
        """Macro `\exclude` is explicitly excluded, so what is compared is
        'Hákonar' and 'Hákonar' which is then matched and annotated. """
        old_exclude = settings.exclude_macros
        settings.exclude_macros += [r'\exclude']
        text = (r'Han var sonr \edtext{Hákon\emph{ar}\exclude{Håkon II} '
                r'konungs}{\Afootnote{k\emph{on}gſ hakon\emph{ar} Sk}}, '
                r'sons Hákonar\exclude{Håkon I} konungs')
        expect = (r'Han var sonr \edtext{\sameword[1]{Hákon\emph{'
                  r'ar}\exclude{Håkon II} konungs}}{\Afootnote{k\emph{on}gſ '
                  r'hakon\emph{ar} Sk}}, sons \sameword{Hákonar\exclude{'
                  r'Håkon I} konungs}')
        assert self.run_annotation(text) == expect
        settings.exclude_macros = old_exclude

    def test_custom_not_excluded_macro_with_match(self):
        """Macro is not explicitly excluded, which means that the
        search-words are 'Sortes1' and 'Sortes1', which matche"""
        text = (r'\edtext{Sortes\test{1}}{\Afootnote{Socrates B}} dicit: '
                r'Sortes\test{1} probus')
        expect = (r'\edtext{\sameword[1]{Sortes\test{1}}}{\Afootnote{Socrates '
                  r'B}} dicit: \sameword{Sortes\test{1}} probus')
        assert self.run_annotation(text) == expect

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
                  r'\sameword[1]{per causam}}{\lemma{per causam}\Bfootnote{'
                  r'causam rei B}} cognoscere')
        assert self.run_annotation(text) == expect

    def test_two_multi_words(self):
        text = (r"\edtext{nobis apparentes}{\lemma{nobis "
                r"apparentes}\Bfootnote{\emph{om.} B}} \edtext{nobis "
                r"apparentes}{\lemma{nobis apparentes}\Bfootnote{\emph{om.} "
                r"B}}")
        expect = (r"\edtext{\sameword[1]{nobis apparentes}}{\lemma{nobis "
                  r"apparentes}\Bfootnote{\emph{om.} B}} \edtext{\sameword["
                  r"1]{nobis apparentes}}{\lemma{nobis apparentes}\Bfootnote{"
                  r"\emph{om.} B}}")
        assert self.run_annotation(text) == expect

    def test_neutrality_on_already_wrapped(self):
        text = (r"Praeterea intellectus intelligit se: \edtext{\sameword[1]{"
                r"aut}}{\lemma{aut}\Bfootnote{aliter Aguin.}} ergo per suam "
                r"essentiam, \edtext{\sameword[1]{aut}}{\lemma{"
                r"aut}\Bfootnote{aliter Aguin.}} per speciem, \edtext{"
                r"\sameword[1]{aut}}{\lemma{aut}}\Bfootnote{aliter Aguin.}} "
                r"per suum actum; sed \edtext{\sameword[1]{nec}}{\lemma{"
                r"nec}}\Bfootnote{non Aguin.}} per speciem |\ledsidenote{B "
                r"174vb} \sameword{nec} per suum actum;")
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
                  r"\sameword{est} scientia \sameword{est} intelligibile, "
                  r"quia cum scientia sit habitus intellectus, de quo "
                  r"\sameword{est} scientia oportet esse intelligibile; sed "
                  r"anima non \sameword{est} intelligibile, quia omnis nostra "
                  r"cognitio ortum habet a sensu, \edtext{unde ipsum "
                  r"intelligere non \sameword[1]{est}}{\lemma{unde \dots{} "
                  r"est}\Bfootnote{quia nihil intelligimus B}} sine "
                  r"phantasmate, sed anima sub sensu non cadit, nec phantasma "
                  r"facit; ergo et cetera.\edlabelE{da-49-l1q1-ysmgk1}")
        assert self.run_annotation(text) == expect

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
        text = (r"test twenty-ninth twenty-eighth twenty-seventh "
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
        expect = (r"\sameword{test} twenty-ninth twenty-eighth twenty-seventh "
                  r"twenty-sixth twenty-fifth twenty-fourth twenty-third "
                  r"twenty-second twenty-first twentieth nineteenth "
                  r"eighteenth seventeenth sixteenth fifteenth fourteenth "
                  r"thirteenth twelfth eleventh tenth ninth eighth seventh "
                  r"sixth fifth fourth third second first \edtext{\sameword["
                  r"1]{test}}{\Afootnote{check}} first second third fourth "
                  r"fifth sixth seventh eighth ninth tenth eleventh twelfth "
                  r"thirteenth fourteenth fifteenth sixteenth seventeenth "
                  r"eighteenth nineteenth twentieth twenty-first "
                  r"twenty-second twenty-third twenty-fourth twenty-fifth "
                  r"twenty-sixth twenty-seventh twenty-eighth twenty-ninth "
                  r"thirtieth test")
        assert self.run_annotation(text) == expect

    def test_match_word_boundary_match_inside_at_end(self):
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
                r"twenty-ninth test")
        expect = (r"test thirtieth twenty-ninth twenty-eighth twenty-seventh "
                  r"twenty-sixth twenty-fifth twenty-fourth twenty-third "
                  r"twenty-second twenty-first twentieth nineteenth "
                  r"eighteenth seventeenth sixteenth fifteenth fourteenth "
                  r"thirteenth twelfth eleventh tenth ninth eighth seventh "
                  r"sixth fifth fourth third second first \edtext{\sameword["
                  r"1]{test}}{\Afootnote{check}} first second third fourth "
                  r"fifth sixth seventh eighth ninth tenth eleventh twelfth "
                  r"thirteenth fourteenth fifteenth sixteenth seventeenth "
                  r"eighteenth nineteenth twentieth twenty-first "
                  r"twenty-second twenty-third twenty-fourth twenty-fifth "
                  r"twenty-sixth twenty-seventh twenty-eighth twenty-ninth "
                  r"\sameword{test}")
        assert self.run_annotation(text) == expect

    def test_match_word_boundary_match_both_ends(self):
        text = (r"test twenty-ninth twenty-eighth twenty-seventh "
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
                r"twenty-ninth test")
        expect = (r"\sameword{test} twenty-ninth twenty-eighth twenty-seventh "
                  r"twenty-sixth twenty-fifth twenty-fourth twenty-third "
                  r"twenty-second twenty-first twentieth nineteenth "
                  r"eighteenth seventeenth sixteenth fifteenth fourteenth "
                  r"thirteenth twelfth eleventh tenth ninth eighth seventh "
                  r"sixth fifth fourth third second first \edtext{\sameword["
                  r"1]{test}}{\Afootnote{check}} first second third fourth "
                  r"fifth sixth seventh eighth ninth tenth eleventh twelfth "
                  r"thirteenth fourteenth fifteenth sixteenth seventeenth "
                  r"eighteenth nineteenth twentieth twenty-first "
                  r"twenty-second twenty-third twenty-fourth twenty-fifth "
                  r"twenty-sixth twenty-seventh twenty-eighth twenty-ninth "
                  r"\sameword{test}")
        assert self.run_annotation(text) == expect

    def test_spaced_index_command(self):
        text = r'\edtext{A}{\Afootnote{a}}\index{A, A}'
        assert self.run_annotation(text) == text

    def test_on_comments(self):
        text = r'\edtext{A}{\Afootnote{a}}     %A'
        assert self.run_annotation(text) == text

    def test_case_insensitive_context_no_match_lemma(self):
        settings.sensitive_context_match = False
        text = r'\edtext{A}{\lemma{A}\Afootnote{x}} a'
        expect = r'\edtext{\sameword[1]{A}}{\lemma{A}\Afootnote{x}} \sameword{a}'
        assert self.run_annotation(text) == expect
        settings.sensitive_context_match = True

    def test_case_insensitive_context_no_match_edtext(self):
        settings.sensitive_context_match = False
        text = r'\edtext{A}{\Afootnote{x}} a'
        expect = r'\edtext{\sameword[1]{A}}{\Afootnote{x}} \sameword{a}'
        assert self.run_annotation(text) == expect
        settings.sensitive_context_match = True

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
                  'member', 'of', 'another', 'sequence', 'or', 'iterable',
                  'or', 'to', 'create', 'a', 'subsequence']
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
        expect = ['Common', '', 'applications', '', '', 'are', 'to', 'make',
                  'new', 'element', 'is', 'the', 'result', 'of', 'some',
                  'operations', 'applied', 'to', 'each', 'member', 'of',
                  'another', 'sequence', 'or', 'iterable', 'or', 'to', '',
                  '', '', 'a', 'subsequence', 'of', 'those', 'element', 's']
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
        expect = ['new', 'lists', 'where', 'each', 'element', 'is', 'the',
                  'result', 'of', 'some', 'operations', 'applied', 'to',
                  'each', 'member', 'of', 'another', 'sequence', 'or',
                  'iterable', 'or', 'to', 'create', 'a', 'subsequence', 'of',
                  'those', 'elements', 'that', 'satisfy']
        assert self.run_get_context_before(text, 45) == expect

    def test_get_from_long_context_before_with_empty(self):
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
        expect = ['lists', 'Common', '', 'applications', '', '', 'are', 'to',
                  'make', 'new', 'element', 'is', 'the', 'result', 'of',
                  'some', 'operations', 'applied', 'to', 'each', 'member',
                  'of', 'another', 'sequence', 'or', 'iterable', 'or', 'to',
                  '', '', '', 'a', 'subsequence', 'of', 'those', 'element']
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
        expect = ['another', 'sequence', 'or', 'iterable', 'or', 'to',
                  'create', 'a', 'subsequence', 'of']
        assert self.run_get_context_after(text, 18) == []

    def test_et_backward_from_start(self):
        text = (r"another sequence or iterable, or to create a subsequence of "
                r"those elements that satisfy a certain condition. Start ")
        expect = ['another', 'sequence', 'or', 'iterable', 'or', 'to',
                  'create', 'a', 'subsequence', 'of']
        assert self.run_get_context_before(text, 0) == []


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
        old_exclude = settings.exclude_macros
        settings.exclude_macros += [
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
        settings.exclude_macros = old_exclude

    def test_custom_ellipses_without_space(self):
        old_exclude = settings.exclude_macros
        settings.exclude_macros += [
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
        settings.exclude_macros = old_exclude
