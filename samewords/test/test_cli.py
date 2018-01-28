from samewords import cli


class TestConfigFileContent:
    def test_config_file_parsing(self):
        fname = './samewords/test/assets/sample_config.json'
        settings = cli.parse_config_file(fname)
        assert "\\.\\.\\." in settings.ellipsis_patterns
        assert "-+" in settings.ellipsis_patterns
        assert "\\anotherMacro" in settings.exclude_macros
        assert settings.sensitive_context_match == True


# class TestCustomIncludeExclude:
#
#     def test_custom_exclude_file(self):
#         proc = subprocess.Popen(
#             ['samewords', './samewords/test/assets/include-exclude.tex',
#              '--config-file=./samewords/test/assets/conf_exclude.json'],
#             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         out, err = proc.communicate()
#         with open('./samewords/test/assets/exclusion-result.tex') as f:
#             result = f.read()
#         assert out.decode() == result
#
#     def test_custom_include_file(self):
#         proc = subprocess.Popen(
#             ['samewords', './samewords/test/assets/include-exclude.tex',
#              '--config-file=./samewords/test/assets/conf_include.json'],
#             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         out, err = proc.communicate()
#         with open('./samewords/test/assets/inclusion-result.tex') as f:
#             result = f.read()
#         assert out.decode() == result
