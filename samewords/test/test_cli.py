import subprocess

class TestCustomIncludeExclude:

    def test_custom_exclude_file(self):
        proc = subprocess.Popen(['samewords', './samewords/test/assets/include-exclude.tex',
                              '--exclude-macros=./samewords/test/assets/include-exclude.txt'],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        with open('./samewords/test/assets/exclusion-result.tex') as f:
            result = f.read()
        assert out.decode() == result

    def test_custom_include_file(self):
        proc = subprocess.Popen(['samewords', './samewords/test/assets/include-exclude.tex',
                              '--include-macros=./samewords/test/assets/include-exclude.txt'],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        with open('./samewords/test/assets/inclusion-result.tex') as f:
            result = f.read()
        assert out.decode() == result


