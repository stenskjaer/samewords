import subprocess

from pytest import mark

from samewords import cli
from samewords.settings import settings


class TestConfigFileContent:

    def test_config_file_parsing(self):
        fname = './samewords/test/assets/sample_config.json'
        old = {
            'ellipsis_patterns': settings['ellipsis_patterns'],
            'exclude_macros': settings['exclude_macros'],
            'sensitive_context_match': settings['sensitive_context_match'],
            'context_distance': settings['context_distance']
        }
        cli.parse_config_file(fname)
        assert "\\.\\.\\." in settings['ellipsis_patterns']
        assert "-+" in settings['ellipsis_patterns']
        assert "\\anotherMacro" in settings['exclude_macros']
        assert settings['sensitive_context_match'] == True
        assert settings['context_distance'] == 25
        settings.update(old)


class TestCLIArguments:

    @mark.slow
    def test_default_annotate_file(self):
        proc = subprocess.Popen(
            ['samewords', './samewords/test/assets/da-49-l1q1.tex'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        with open('./samewords/test/assets/da-49-l1q1-processed.tex') as f:
            result = f.read()
        assert out.decode().strip() == result.strip()

    @mark.slow
    def test_clean_file(self):
        proc = subprocess.Popen(
            ['samewords', './samewords/test/assets/da-49-l1q1-processed.tex',
             '--clean'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        with open('./samewords/test/assets/da-49-l1q1.tex') as f:
            result = f.read()
        assert out.decode().strip() == result.strip()

    @mark.slow
    def test_update_file(self):
        proc = subprocess.Popen(
            ['samewords', './samewords/test/assets/simple-unupdated.tex',
             '--update'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        with open('./samewords/test/assets/simple-updated.tex') as f:
            result = f.read()
        assert out.decode().strip() == result.strip()
