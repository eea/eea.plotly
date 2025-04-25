from urllib.parse import urlparse


def setProperty(obj, name, value):
    if value is not None:
        obj[name] = value


def delProperty(obj, name):
    if name in obj:
        del obj[name]


def sanitizeVisualization(v={}):
    """Sanitize Visualization"""

    # backward compatibility
    chartData = v.get("chartData", {})
    columns = v.get("columns", [])
    dataSources = v.get("data_source", {})
    dataSources.update(v.get("dataSources", {}))

    viz = {
        "data": v.get("data", chartData.get("data", [])),
        "layout": v.get("layout", chartData.get("layout", {})),
        # "frames": v.get("frames", chartData.get("frames", [])),
        "columns": columns,
        "dataSources": dataSources,
        # "dataSourcesOrder": v.get("dataSourcesOrder", []),
    }
    setProperty(viz, "provider_url", v.get("provider_url", None))
    setProperty(viz, "variation", v.get("variation", None))
    setProperty(viz, "filters", v.get("filters", None))
    setProperty(viz, "id", v.get("id", None))
    setProperty(viz, "type", v.get("type", None))
    setProperty(viz, "label", v.get("label", None))

    return viz


def getLink(path):
    """
      Get link
      """

    URL = urlparse(path)

    if URL.netloc.startswith('localhost') and URL.scheme:
        return path.replace(URL.scheme + "://" + URL.netloc, "")
    return path


def getLinkHTML(url, text=None):
    """
      Get link HTML
      """

    if not url:
        return url

    if not text:
        text = url

    return '<a href="' + url + '" target="_blank">' + text + '</a>'


def isExpanded(request, name):
    """ Check if a given field is expanded. """

    expands = request.form.get("expand", [])
    if isinstance(expands, str):
        if "," in expands:
            # use of expands (with commas) was deprecated in plone.restapi 8
            # undeprecated with plone.restapi 9
            expands = expands.split(",")
        else:
            # allow still the use of non marked :list parameters present
            expands = [expands]

    return name in expands
