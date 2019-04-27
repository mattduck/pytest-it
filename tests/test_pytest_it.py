# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from pytest import mark as m


pytestmark = [pytest.mark.describe("pytest-it")]


@m.describe("The plugin integration with pytest")
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
    @m.it("Makes a pytest-it test run without error")
    def test_with_flag(self, testdir):
        """
        Quick catch-all test for the main features
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


@m.describe("The @pytest.mark.describe marker")
class TestDescribe(object):
    @m.it("Displays a '- Describe: ' block matching the decorator")
    def test_one_describe(self, testdir):
        testdir.makepyfile(
            """
            import pytest

            @pytest.mark.describe("A foo")
            def test_something():
                assert True
        """
        )
        result = testdir.runpytest("--it-no-color")
        result.stdout.fnmatch_lines(["*- Describe: A foo*"])

    @m.it("Displays a nested, indented '- Describe: ' block")
    def test_nested_describe(self, testdir):
        testdir.makepyfile(
            """
            import pytest

            @pytest.mark.describe("A foo")
            @pytest.mark.describe("A nested foo")
            def test_something():
                assert True
        """
        )
        result = testdir.runpytest("--it-no-color")
        result.stdout.fnmatch_lines(
            ["*  - Describe: A foo*", "*    - Describe: A nested foo*"]
        )


@m.describe("The @pytest.mark.context marker")
class TestContext(object):
    @m.it("Displays a '- Context: ' block matching the decorator")
    def test_one_context(self, testdir):
        testdir.makepyfile(
            """
            import pytest

            @pytest.mark.context("When something")
            def test_something():
                assert True
        """
        )
        result = testdir.runpytest("--it-no-color")
        result.stdout.fnmatch_lines(["*- Context: When something...*"])

    @m.it("Displays a nested, indented '..$context..' block")
    def test_nested_context(self, testdir):
        testdir.makepyfile(
            """
            import pytest

            @pytest.mark.context("When something")
            @pytest.mark.context("And when another thing")
            def test_something():
                assert True
        """
        )
        result = testdir.runpytest("--it-no-color")
        result.stdout.fnmatch_lines(
            ["*  - Context: When something...*", "*    - ...and when another thing...*"]
        )

    @m.it("Ignores a @pytest.mark.context decorator that has no argument")
    def test_no_argument(self):
        pytest.skip("NotImplemented")


@m.it("Handles indentation for arbitrary Describe and Context nesting")
def test_deep_nesting_of_context_and_describe(testdir):
    testdir.makepyfile(
        """
        import pytest

        @pytest.mark.describe("A thing")
        @pytest.mark.context("When something")
        @pytest.mark.context("And when another thing")
        @pytest.mark.describe("A nested thing")
        def test_something():
            assert True
    """
    )
    result = testdir.runpytest("--it-no-color")
    result.stdout.fnmatch_lines(
        [
            "*  - Describe: A thing...*",
            "*    - Context: When something...*",
            "*      - ...and when another thing...*",
            "*        - Describe: A nested thing*",
        ]
    )


@m.describe("The test function report format")
class TestIt(object):
    @m.it("Displays a test pass using '- ✓ '")
    def test_pytest_pass(self, testdir):
        testdir.makepyfile(
            """
            import pytest

            def test_something():
                assert True
        """
        )
        result = testdir.runpytest("--it-no-color")
        result.stdout.fnmatch_lines(["*- ✓ *"])

    @m.it("Displays a test fail using '- F '")
    def test_fail(self, testdir):
        testdir.makepyfile(
            """
            import pytest

            def test_something():
                assert False
        """
        )
        result = testdir.runpytest("--it-no-color")
        result.stdout.fnmatch_lines(["*- F *"])

    # TODO: would be nice for this to show the skip message
    @m.it("Displays a test skip using '- s '")
    def test_skip(self, testdir):
        testdir.makepyfile(
            """
            import pytest

            def test_something():
                pytest.skip("Skip reason")
        """
        )
        result = testdir.runpytest("--it-no-color")
        result.stdout.fnmatch_lines(["*- s *"])

    @m.it("Displays the pytest ID for test parameters at the end of the test")
    def test_param(self):
        pytest.skip("NotImplemented")

    @m.context("When @pytest.mark.it is used")
    @m.it("Displays an '- It: ' block matching the decorator")
    def test_it_decorator(self, testdir):
        testdir.makepyfile(
            """
            import pytest

            @pytest.mark.it("Does something")
            def test_something():
                assert True
        """
        )
        result = testdir.runpytest("--it-no-color")
        result.stdout.fnmatch_lines(["*- ✓ It: Does something*"])

    @m.context("When @pytest.mark.it is used")
    @m.context("When -v is higher than 0")
    @m.parametrize("v", [(1, 2, 3)])
    @m.it("Displays the full module::class::function prefix to the test")
    def test_verbose(self, testdir, v):
        testdir.makepyfile(
            """
            import pytest

            @pytest.mark.it("Does something")
            def test_something():
                assert True
        """
        )
        result = testdir.runpytest("--it-no-color", "-" + ("v" * v))
        result.stdout.fnmatch_lines(["*- ✓ It: Does something*"])
        raise NotImplemented

    @m.context("When @pytest.mark.it is not used")
    @m.it("Displays the test function name")
    def test_no_argument(self):
        pytest.skip("NotImplemented")

    @m.context("When @pytest.mark.it is not used")
    @m.context("but the test name starts with 'test_it_'")
    @m.it("Prettifies the test name into the 'It: ' value")
    def test_populates_the_it_marker_using_function_name(self):
        pytest.skip("NotImplemented")

    @m.context("When multiple @pytest.mark.it markers are used")
    @m.it("Uses the lowest decorator for the 'It : ' value")
    def test_uses_the_closest_it_decorator_if_there_are_many(self):
        pytest.skip("NotImplemented")


@m.describe("Unmarked tests")
class TestUndecoratedTests(object):
    @m.it("Displays the pytest path for an unmarked test method")
    def test_undecorated_method(self):
        pytest.skip("NotImplemented")

    @m.it("Displays the pytest path for an unmarked test function")
    def test_undecorated_function(self):
        pytest.skip("NotImplemented")


@m.describe("The --collect-only behaviour")
class TestCollection(object):
    @m.it("Displays all tests without the result status")
    def test_no_result_status_is_used(self):
        pytest.skip("NotImplemented")
