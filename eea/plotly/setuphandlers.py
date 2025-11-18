"""Custom setup"""

import os.path
import json
from Products.CMFPlone.interfaces import INonInstallable
from plone.registry.interfaces import IRegistry
from zope.interface import implementer
from zope.component import getUtility
from eea.plotly.controlpanel import IPlotlySettings


@implementer(INonInstallable)
class HiddenProfiles:
    """Hidden profiles"""

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "eea.plotly:uninstall",
        ]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.
    package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    profile_path = os.path.join(
        package_dir, "plotly", "profiles", "default", "controlpanel.json"
    )

    if os.path.exists(profile_path):
        with open(profile_path, "r") as f:
            settings = json.load(f)
            # Initialize control panel with default settings
            registry = getUtility(IRegistry)
            cp = registry.forInterface(IPlotlySettings)
            cp.themes = settings.get("themes", [])
            cp.templates = settings.get("templates", [])
    else:
        print(f"File not found: {profile_path}")


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
