import os

from kivy.utils import platform as PLATFORM


if PLATFORM == 'android':
    from android import mActivity
    from android.permissions import Permission
    from android.permissions import check_permission, request_permissions
    from android.storage import primary_external_storage_path
    from jnius import autoclass, cast


def ensure_storage_perms(fallback_func):
    """
    Decorator that ensures that the decorated function is only run if the user
    has granted the app permissions to write to the file system. Otherwise the
    fallback function is called instead.

    Because permissions on Android are requested asynchronously, the decorated
    function should not be expected to return a value.
    """
    def outer_wrapper(func):
        def inner_wrapper(*args, **kwargs):
            if PLATFORM == 'android':
                if check_permission(Permission.WRITE_EXTERNAL_STORAGE):
                    return func(*args, **kwargs)

                def callback(permissions, grant_results):
                    if grant_results[0]:
                        return func(*args, **kwargs)
                    else:
                        return fallback_func()

                request_permissions(
                    [Permission.WRITE_EXTERNAL_STORAGE], callback
                )
                return

            return func(*args, **kwargs)

        return inner_wrapper
    return outer_wrapper


def get_downloads_dir():
    """
    Return the path to the user's downloads dir.
    """
    if PLATFORM == 'android':
        Environment = autoclass('android.os.Environment')
        return os.path.join(
            primary_external_storage_path(),
            Environment.DIRECTORY_DOWNLOADS
        )
    else:
        return os.getcwd()


def open_dir(path):
    """
    Open the specified directory.
    """
    if PLATFORM == 'android':
        AndroidString = autoclass('java.lang.String')
        Document = autoclass('android.provider.DocumentsContract$Document')
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')

        intent = Intent()
        intent.setAction(Intent.ACTION_VIEW)
        intent.setDataAndType(Uri.parse(path), Document.MIME_TYPE_DIR)

        title = cast('java.lang.CharSequence', AndroidString('Open dir with'))
        mActivity.startActivity(Intent.createChooser(intent, title))
    else:
        pass
