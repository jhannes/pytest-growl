import time
import pkg_resources
from growl import growl

icon_success = pkg_resources.resource_stream(__name__, "icon_success.png").read()
icon_failed = pkg_resources.resource_stream(__name__, "icon_failed.png").read()
icon_error = pkg_resources.resource_stream(__name__, "icon_error.png").read()

QUIET_MODE_INI='quiet_growl'

def pytest_addoption(parser):
    """Adds options to control growl notifications."""
    group = parser.getgroup('terminal reporting')
    group.addoption('--growl',
                    dest='growl',
                    default=True,
                    help='Enable Growl notifications.')
    parser.addini(QUIET_MODE_INI,
                  default=True,
                  help='Minimize notifications (only results).')


def pytest_sessionstart(session):
    if (session.config.option.growl
        and not session.config.getini(QUIET_MODE_INI)):
        send_growl(title="Session Begins At", message="%s" % time.strftime("%I:%M:%S %p"))


def pytest_terminal_summary(terminalreporter):
    if terminalreporter.config.option.growl:
        tr = terminalreporter
        quiet_mode = tr.config.getini(QUIET_MODE_INI)
 
        passes = len(tr.stats.get("passed", []) )
        fails = len(tr.stats.get("failed", []) )
        errors = len(tr.stats.get("error", []) )
        skips = len(tr.stats.get("deselected", []) )

        if errors == 1:
            test_name = tr.stats["error"][0].nodeid
            send_growl(
                title = "Error in %s" % test_name,
                message = "Error %s\n(Tests: %d failed, %d ok)" % (test_name, fails, passes),
                icon = icon_error)
        elif errors > 1:
            send_growl(
                title = "Error in %d files" % errors,
                message = "Errors: %d\n(Tests: %d failed, %d ok)" % (errors, fails, passes),
                icon = icon_error)
        elif fails == 1:
            test_name = tr.stats["failed"][0].nodeid
            send_growl(
                title = tr.stats["failed"][0].location[0],
                message = "%s failed\n%d tests ok" % (test_name, passes),
                icon = icon_failed)
        elif fails > 1:
            send_growl(
                title = "%d tests failed" % fails,
                message = "%d failed, %d ok" % (fails, passes),
                icon = icon_failed)
        elif skips > 1:
            send_growl(title="Tests Complete",
                message = "%s Passed %s Failed %s Skipped" % (passes, fails, skips),
                icon = icon_success)
        else:
            send_growl(title="Tests Complete",
                message="%s Passed %s Failed" % (passes, fails),
                icon = icon_success)
        if not quiet_mode:
            send_growl(title="Session Ended At", message="%s" % time.strftime("%I:%M:%S %p"))



def send_growl(message='', title='Blarg', icon = None):
    growl(message=message, title=title, icon = icon)
