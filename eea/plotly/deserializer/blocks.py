""" block-related utils """

from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from plone.restapi.deserializer.utils import path2uid
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
from eea.plotly.utils import getLink, delProperty, sanitizeBlockData


@implementer(IBlockFieldDeserializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class EmbedVisualizationDeserializationTransformer:
    """Embed visualization deserialization"""

    order = 9999
    block_type = "embed_visualization"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        value = sanitizeBlockData(value)
        delProperty(value, 'visualization')
        delProperty(value, 'properties')
        delProperty(value, 'image_scales')
        if 'viz_url' in value:
            value['viz_url'] = path2uid(
                context=self.context, link=getLink(value['viz_url'])
            )
        return value
