"""Module where all interfaces, events and exceptions live."""
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IPlotlyLayer(IDefaultBrowserLayer):
    """ Marker interface that defines a browser layer. """


class IPlotlyVisualizationField(Interface):
    """ Marker interface for plotly visualization JSON field """


class IPlotlyFileField(Interface):
    """ Marker interface for plotly file field """


class IPlotlyVisualization(Interface):
    """ Marker interface for plotly visualization """
