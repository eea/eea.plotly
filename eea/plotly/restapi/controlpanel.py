"""Plotly Controlpanel API"""
from zope.interface import Interface
from zope.component import adapter
from plone.restapi.controlpanels import RegistryConfigletPanel
from eea.plotly.interfaces import (
    IPlotlySettings,
    IPlotlyLayer
)


@adapter(Interface, IPlotlyLayer)
class PlotlyControlpanel(RegistryConfigletPanel):
    """Plotly Control Panel"""
    schema = IPlotlySettings
    schema_prefix = None
    configlet_id = "plotly"
    configlet_category_id = "Products"
    title = "Plotly Settings"
    group = "Products"
