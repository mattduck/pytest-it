# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pytest import mark as m


@m.describe("pytest-it plugin configuration")
class TestSanity(object):

    BASIC_PYTEST_TEST_CODE = """
        import pytest

        @pytest.mark.describe("A basic foo")
        @pytest.mark.context("When called with no arguments")
        @pytest.mark.context("and also in another circumstance")
        @pytest.mark.it("Does something")
        def test_foo():
            assert True
    """

    @m.context("When pytest is called with the --it flag")
    @m.it("Makes a basic pytest-it test run without error")
    def test_with_flag(self, testdir):
        """
        Quick catch-all test for the supported markers
        """
        testdir.makepyfile(self.BASIC_PYTEST_TEST_CODE)
        result = testdir.runpytest("--it", "--it-no-color")
        result.stdout.fnmatch_lines(
            [
                "*- Describe: A basic foo*",
                "*- Context: When called with no arguments*",
                "*- ...and also in another circumstance...*",
                "*- ✓ It: Does something*",
            ]
        )
        assert result.ret == 0  # 0 exit code for the test suite

    @m.context("When pytest is called with the --it flag")
    @m.it("Does not error when processing a marker that has no arg value")
    def test_with_flag_but_no_args(self, testdir):
        testdir.makepyfile(
            """
            import pytest

            @pytest.mark.describe
            @pytest.mark.context
            @pytest.mark.context
            @pytest.mark.it
            def test_foo():
                assert True
        """
        )
        result = testdir.runpytest("--it", "--it-no-color")
        assert result.ret == 0  # 0 exit code for the test suite

    @m.context("When pytest is called without the --it flag")
    @m.it("Does not cause pytest to error")
    def test_without_flag(self, testdir):
        testdir.makepyfile(self.BASIC_PYTEST_TEST_CODE)
        result = testdir.runpytest()
        assert result.ret == 0
