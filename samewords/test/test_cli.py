import os
import subprocess

from samewords.test import __testroot__
from samewords.settings import settings

unprocessed_file = os.path.join(__testroot__, "assets/da-49-l1q1.tex")
processed_file = os.path.join(__testroot__, "assets/da-49-l1q1-processed.tex")


class TestConfigFileContent:
    def test_config_file_parsing(self):
        fname = os.path.join(__testroot__, "assets/sample_config.json")
        old = {
            "ellipsis_patterns": settings["ellipsis_patterns"],
            "exclude_macros": settings["exclude_macros"],
            "sensitive_context_match": settings["sensitive_context_match"],
            "context_distance": settings["context_distance"],
        }
        cli.parse_config_file(fname)
        assert "\\.\\.\\." in settings["ellipsis_patterns"]
        assert "-+" in settings["ellipsis_patterns"]
        assert "\\anotherMacro" in settings["exclude_macros"]
        assert settings["sensitive_context_match"] is True
        assert settings["context_distance"] == 25
        settings.update(old)


class TestCLIArguments:
    def test_default_annotate_file(self):
        proc = subprocess.Popen(
            ["samewords", unprocessed_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = proc.communicate()
        with open(processed_file) as f:
            result = f.read()
        assert out.decode().strip() == result.strip()

    def test_clean_file(self):
        proc = subprocess.Popen(
            ["samewords", processed_file, "--clean"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = proc.communicate()
        with open(unprocessed_file) as f:
            result = f.read()
        assert out.decode().strip() == result.strip()

    def test_update_file(self):
        proc = subprocess.Popen(
            [
                "samewords",
                os.path.join(__testroot__, "assets/simple-unupdated.tex"),
                "--update",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = proc.communicate()
        with open(os.path.join(__testroot__, "assets/simple-updated.tex")) as f:
            result = f.read()
        assert out.decode().strip() == result.strip()
