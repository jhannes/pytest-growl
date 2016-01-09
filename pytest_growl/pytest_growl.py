import time
import pkg_resources
import os
from growl import growl

icon_success = pkg_resources.resource_stream(__name__, "icon_success.png").read()
icon_failed = pkg_resources.resource_stream(__name__, "icon_failed.png").read()
icon_error = pkg_resources.resource_stream(__name__, "icon_error.png").read()

QUIET_MODE_INI='quiet_growl'
GROWL_CALLBACK_URL='growl_callback_url'

def pytest_addoption(parser):
    """Adds options to control growl notifications."""
    group = parser.getgroup('terminal reporting')
    group.addoption('--growl',
                    dest='growl',
                    default=True,
                    help='Enable Growl notifications.')
    parser.addini(GROWL_CALLBACK_URL,
                    default = "subl://{path}:{lineno}",
                    help = "URL to open when notification is clicked")
    parser.addini(QUIET_MODE_INI,
                  default=True,
                  help='Minimize notifications (only results).')


def pytest_sessionstart(session):
    if (session.config.option.growl
        and not session.config.getini(QUIET_MODE_INI)):
        growl(title="Session Begins At", message="%s" % time.strftime("%I:%M:%S %p"))


def pytest_terminal_summary(terminalreporter):
    if terminalreporter.config.option.growl:
        tr = terminalreporter
        quiet_mode = tr.config.getini(QUIET_MODE_INI)
        callback_url = tr.config.getini(GROWL_CALLBACK_URL)

        passes = len(tr.stats.get("passed", []) )
        fails = len(tr.stats.get("failed", []) )
        errors = len(tr.stats.get("error", []) )
        skips = len(tr.stats.get("deselected", []) )

        if errors == 1:
            error_test = tr.stats["error"][0]
            try:
                path = error_test.longrepr.reprcrash.path
                filename = os.path.basename(path)
                lineno = error_test.longrepr.reprcrash.lineno
                message = error_test.longrepr.reprcrash.message
                growl(
                    title = "1 error %s:%d" % (filename, lineno),
                    message = "%s\n\n(Tests: %d failed, %d ok)" % (message, fails, passes),
                    icon = icon_error,
                    callback = callback_url.format(path=path, lineno=lineno))
            except AttributeError:
                print error_test.longrepr.__dict__
                growl(
                    title = "1 error %s" % (error_test.nodeid),
                    message = "%s\n\n%d tests ok" % (error_test.nodeid, passes),
                    icon = icon_failed)
        elif errors > 1:
            growl(
                title = "Error in %d files" % errors,
                message = "Errors: %d\n(Tests: %d failed, %d ok)" % (errors, fails, passes),
                icon = icon_error)
        elif fails == 1:
            failed_test = tr.stats["failed"][0]
            try:
                path = failed_test.longrepr.reprcrash.path
                filename = os.path.basename(path)
                lineno = failed_test.longrepr.reprcrash.lineno
                message = failed_test.longrepr.reprcrash.message
                growl(
                    title = "1 failed %s:%d" % (filename, lineno),
                    message = "%s\n\n%d tests ok" % (message, passes),
                    icon = icon_failed,
                    callback = callback_url.format(path=path, lineno=lineno))
            except AttributeError:
                growl(
                    title = "1 failed %s" % (failed_test.nodeid),
                    message = "%s\n\n%d tests ok" % (failed_test.nodeid, passes),
                    icon = icon_failed)                
        elif fails > 1:
            growl(
                title = "%d tests failed" % fails,
                message = "%d failed, %d ok" % (fails, passes),
                icon = icon_failed)
        elif passes == 0:
            growl(
                title = "No tests",
                message = "No tests (%d skipped)" % (skips) ,
                icon = icon_failed)
        elif skips > 1:
            growl(title="Tests Complete",
                message = "%s Passed %s Failed %s Skipped" % (passes, fails, skips),
                icon = icon_success)
        else:
            growl(title="Tests Complete",
                message="%s Passed %s Failed" % (passes, fails),
                icon = icon_success)
        if not quiet_mode:
            growl(title="Session Ended At", message="%s" % time.strftime("%I:%M:%S %p"))


