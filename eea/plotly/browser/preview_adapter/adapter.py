""" Preview adapter for Plotly browser. """

adapters = {
    "soer_miniature": (
        "eea.plotly.browser.preview_adapter.soer_miniature.serialize"
    ),
}


def get_preview_adapter(context, name):
    """ Get the preview adapter for a given name.

    Args:
        name (str): The name of the preview adapter.

    Returns:
        class: The preview adapter class if found, otherwise None.
    """
    if name in adapters:
        module_name, func = adapters[name].rsplit(".", 1)
        module = __import__(module_name, fromlist=[func])
        return getattr(module, func)(context)
    return None
