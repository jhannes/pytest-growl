import time
try:
    import gntp.notifier
except ImportError:
    from growl_fallback import growl_fallback
    pass


QUIET_MODE_INI='quiet_growl'

def pytest_addoption(parser):
    """Adds options to control growl notifications."""
    group = parser.getgroup('terminal reporting')
    group.addoption('--growl',
                    dest='growl',
                    default=True,
                    help='Enable Growl notifications.')
    parser.addini(QUIET_MODE_INI,
                  default=False,
                  help='Minimize notifications (only results).')


def pytest_sessionstart(session):
    if (session.config.option.growl
        and not session.config.getini(QUIET_MODE_INI)):
        send_growl(title="Session Begins At", message="%s" % time.strftime("%I:%M:%S %p"))


def pytest_terminal_summary(terminalreporter):
    if terminalreporter.config.option.growl:
        tr = terminalreporter
        quiet_mode = tr.config.getini(QUIET_MODE_INI)
        try:
            passes = len(tr.stats['passed'])
        except KeyError:
            passes = 0
        try:
            fails = len(tr.stats['failed'])
        except KeyError:
            fails = 0
        try:
            skips = len(tr.stats['deselected'])
        except KeyError:
            skips = 0
        if (passes + fails + skips) == 0:
            send_growl(title="Alert", message="No Tests Ran")
            if not quiet_mode:
                send_growl(title="Session Ended At", message="%s" % time.strftime("%I:%M:%S %p"))
            return
        else:
            if not skips:
                message_to_send = "%s Passed %s Failed" % (passes, fails)
            else:
                message_to_send = "%s Passed %s Failed %s Skipped" % (passes, fails, skips)
        send_growl(title="Tests Complete", message=message_to_send)
        if not quiet_mode:
            send_growl(title="Session Ended At", message="%s" % time.strftime("%I:%M:%S %p"))


def send_growl(message='', title=''):
    if 'gntp' in globals():
        gntp.notifier.mini(message, title=title, applicationName='pytest', noteType='Notification')
    else:
        growl_fallback(message, title)
