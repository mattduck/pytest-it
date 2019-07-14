# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import defaultdict

import pytest
from _pytest.terminal import TerminalReporter

REGISTERED = False


def pytest_addoption(parser):
    group = parser.getgroup("terminal reporting", "reporting", after="general")
    group.addoption(
        "--it",
        action="store_true",
        dest="it",
        default=False,
        help="Display test reports as a plaintext spec, inspired by RSpec",
    )
    group.addoption(
        "--it-no-color",
        action="store_false",
        dest="it_color",
        default=None,
        help="Disable coloured output when using --it",
    )


@pytest.mark.trylast
def pytest_configure(config):
    global REGISTERED
    if (config.option.it or (config.option.it_color is False)) and not REGISTERED:
        default = config.pluginmanager.getplugin("terminalreporter")
        config.pluginmanager.unregister(default)
        config.pluginmanager.register(
            ItTerminalReporter(default.config), "terminalreporter"
        )

    config.addinivalue_line(
        "markers",
        "describe(arg): pytest-it marker to apply a 'Describe: ' block to the report.",
    )
    config.addinivalue_line(
        "markers",
        "context(arg): pytest-it marker to apply a 'Context: ' block to the report.",
    )
    config.addinivalue_line(
        "markers",
        """it(arg): pytest-it marker to specify the 'It: ' output for the report. If not provided, pytest-it will automatically add an 'It :' marker to any test function starting with `test_it_`.""",  # noqa
    )


class ItItem(object):

    INDENT = "  "
    COLORS = {
        "reset": "\033[0m",
        "passed": "\033[92m",
        "failed": "\033[91m",
        "skipped": "\033[93m",
    }

    def __init__(self, item):
        assert item
        self._item = item

    @property
    def path(self):
        """ Path to the test """

        # TODO: docstrings show up in the path. This is used for verbose mode. Should only show
        # the actual path without docstrings.
        return "::".join(self._item.nodeid.split("::")[:-1])

    def formatted_result(self, outcome):
        icons = {"passed": "- ✓", "failed": "- F", "skipped": "- s"}
        title = ""
        for mark in self._item.iter_markers(name="it"):
            try:
                title = mark.args[0]
                break
            except IndexError:
                pass
        if title:
            prefix = "It:"
        else:
            prefix = ""
            title = self._item.name
        try:
            if "[doctest]" in self._item.location[-1]:
                title = self._item.name + " - [doctest]"
        except IndexError:
            pass
        if self._item.config.option.verbose > 0:
            title = self.path + "::{} - {}".format(self._item.name, title)
        if "[" in self._item.name:  # Parametrised test
            title = title + " - [{}".format(self._item.name.split("[")[1])
        return "{color}{icon}{prefix}{reset} {title}".format(
            color=self.color(outcome),
            reset=self.color("reset"),
            icon=icons.get(outcome, "-"),
            prefix=" " + prefix if prefix else "",
            title=title,
        )

    @property
    def parent_marks(self):
        markers = []
        for m in self._item.iter_markers():
            if m.name in ("describe", "context"):
                try:
                    markers.append((m.name, m.args[0]))
                except IndexError:
                    pass
        return list(reversed(markers))

    def color(self, s):
        if self._item.config.option.it_color in (True, None):
            return self.COLORS.get(s, self.COLORS["skipped"])
        return ""

    def _print_marker(self, value, value_type, value_depth, type_depth, tw):
        if value_type == "describe":
            value = "- Describe: {}...".format(value.capitalize())
        elif value_type == "context":
            if type_depth > 1:
                value = "- ...{}...".format(self._uncapitalize(value))
            else:
                value = "- Context: {}...".format(value.capitalize())

        if value_depth <= 3:
            tw.sep(" ")
        if value_depth <= 1:
            tw.line(value)
        else:
            tw.line((self.INDENT * (value_depth - 1)) + value)

    @property
    def module(self):
        try:
            return self._item.module
        except AttributeError:
            # a DocTestItem doesn't have a module attribute, but the parent
            # does
            return self._item.parent.module

    def reconcile_and_print(self, prev, tw, outcome, is_first_test=False):
        if prev:
            prev_marks = prev.parent_marks
            is_first_module_test = self.module != prev.module
        else:
            prev_marks, is_first_module_test = [], True
        depth = defaultdict(int)
        diff_broken = False
        self_depth = 0
        for self_depth, self_marker_info in enumerate(self.parent_marks, 1):
            self_type, self_value = self_marker_info
            depth[self_type] += 1

            prev_marker_info = None
            try:
                prev_marker_info = prev_marks[self_depth - 1]
            except IndexError:
                diff_broken = True
            if prev_marker_info != self_marker_info:
                diff_broken = True

            if not diff_broken:
                continue

            # Start printing Describe/Context markers at the point where the
            # marker hierarchy differs from the previous test.
            self._print_marker(
                value=self_value,
                value_type=self_type,
                value_depth=self_depth,
                type_depth=depth[self_type],
                tw=tw,
            )

        # Print a separator before the test if this test is displayed after a deeper block.
        prev_depth = max(0, (len(prev_marks)))
        if self_depth < prev_depth and not diff_broken:
            tw.sep(" ")
        # If this is a new module, add a separate to avoid printing "* my_module.py... It: does something"
        # on a single line.
        elif self_depth == 0 and is_first_module_test:
            tw.sep(" ")

        # Print the test with appropriate indent
        if self_depth:
            tw.line((self.INDENT * self_depth) + self.formatted_result(outcome))
        else:
            tw.line(self.formatted_result(outcome))

    def _uncapitalize(self, s):
        return s[0].lower() + s[1:]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    result = yield
    report = result.get_result()
    report._item = item


@pytest.hookimpl(hookwrapper=True)
def pytest_collection_modifyitems(items):
    """
    Allow a test to use the naming convention `test_it_does_something`. Interpret this
    the same as if @pytest.mark.it was used.
    """
    for item in items:
        if item.name.startswith("test_it_"):
            if len(list(item.iter_markers(name="it"))) == 0:
                name = item.name.split("test_it_")[1].replace("_", " ").capitalize()
                item.add_marker(pytest.mark.it(name))
    yield items


class ItTerminalReporter(TerminalReporter):

    _current_pytest_it_fspath = None

    def __init__(self, config, file=None):
        TerminalReporter.__init__(self, config, file)
        self._prev_item = None
        self._showfs_path = False

    def _register_stats(self, report):
        res = self.config.hook.pytest_report_teststatus(
            report=report, config=self.config
        )
        self.stats.setdefault(res[0], []).append(report)
        self._tests_ran = True

    def pytest_runtest_logreport(self, report):
        self._register_stats(report)
        if report.when != "call" and not report.skipped:
            return
        item = ItItem(report._item)
        item.reconcile_and_print(self._prev_item, self._tw, report.outcome)
        self._prev_item = item

    # This is probably the best function to override. _print_collecteditems() is also a candidate, but
    # I think it's more liable to change because it's a private method.
    def pytest_collection_finish(self, session):
        if self.config.getoption("collectonly"):
            prev_it_item = None
            for item in session.items:
                it_item = ItItem(item)
                it_item.reconcile_and_print(prev_it_item, self._tw, outcome=None)
                prev_it_item = it_item

        # NOTE: this logic is copied from TerminalReporter.pytest_collection_finish
        lines = self.config.hook.pytest_report_collectionfinish(
            config=self.config, startdir=self.startdir, items=session.items
        )
        self._write_report_lines_from_hooks(lines)
        if self.config.getoption("collectonly"):
            if self.stats.get("failed"):
                self._tw.sep("!", "collection failures")
                for rep in self.stats.get("failed"):
                    rep.toterminal(self._tw)

    def pytest_runtest_logstart(self, nodeid, location):
        """
        Disable the normal running test output
        """
        if self.showfspath:
            fsid = nodeid.split("::")[0]
            # below logic is very similar to self.write_fspath_result(). Ideally we would
            # call it directly, but there's no way to inject the "*" character before the
            # path.
            fspath = self.config.rootdir.join(fsid)
            if fspath != self.currentfspath:
                if self.currentfspath is not None and self._show_progress_info:
                    self._write_progress_information_filling_space()
                self.currentfspath = fspath
                fspath = self.startdir.bestrelpath(fspath)
                self._tw.line()
                self._tw.line()
                self._tw.write("* " + fspath + "... ")
