"""RestAPI enpoint @plotly GET"""

import os.path
import json
from plone.restapi.services import Service
from plone.registry.interfaces import IRegistry
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import implementer, alsoProvides
from zope.component import getUtility
from zope.publisher.interfaces import IPublishTraverse

from eea.plotly.controlpanel import IPlotlySettings


@implementer(IPublishTraverse)
class PlotlySettingsReset(Service):
    """Plotly Settings Reset"""

    def reply(self):
        """Reply"""
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        registry = getUtility(IRegistry)
        cp = registry.forInterface(IPlotlySettings)
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        profile_path = os.path.join(
            package_dir, "..", "profiles", "default", "controlpanel.json"
        )

        if os.path.exists(profile_path):
            with open(profile_path, "r") as f:
                settings = json.load(f)
                # Reset control panel with default settings
                cp.themes = settings.get("themes", [])
                cp.templates = settings.get("templates", [])
        else:
            print(f"File not found: {profile_path}")

        return {"themes": cp.themes, "templates": cp.templates}
