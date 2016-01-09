try:
    import gntp.notifier
    notifier = gntp.notifier.GrowlNotifier(
            applicationName = "pytest",
            notifications = ["Notification"],
            defaultNotifications = ["Notification"],
            # hostname = "computer.example.com", # Defaults to localhost
            # password = "abc123" # Defaults to a blank password
    )
    notifier.register()
except ImportError:
    from growl_fallback import growl_fallback
    pass


def growl(message='', title='', icon = None, callback = None):
    if 'gntp' in globals():
        notifier.notify(noteType = "Notification", title = title, description = message, icon = icon, callback = callback)
    else:
        growl_fallback(message, title)
