"""dxfields deserializers"""

from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from plone.restapi.deserializer.utils import path2uid
from eea.plotly.utils import getLink, sanitizeVisualization
from eea.plotly.interfaces import IPlotlyVisualizationField


@implementer(IFieldDeserializer)
@adapter(IPlotlyVisualizationField, IDexterityContent, IBrowserRequest)
class VisualizationFieldDeserializer(DefaultFieldDeserializer):
    """Visualization field deserializer"""

    def __call__(self, value):
        value = sanitizeVisualization(value)

        if "provider_url" in value:
            url = value["provider_url"]
            value["provider_url"] = path2uid(context=self.context, link=getLink(url))

        return value
