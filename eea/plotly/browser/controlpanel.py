"""Control panel module"""

from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm

from eea.plotly.controlpanel import IPlotlySettings


class PlotlyRegistryEditForm(RegistryEditForm):
    """Plotly Registry Edit Form"""

    schema = IPlotlySettings
    id = "plotly"
    label = "Plotly Settings"


class PlotlyControlPanelFormWrapper(ControlPanelFormWrapper):
    """Plotly Control Panel Form Wrapper"""

    form = PlotlyRegistryEditForm
