""" dxfields serializers """

import copy
import csv
from io import StringIO
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from plone.restapi.serializer.utils import uid_to_url
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.interfaces import IFieldSerializer
from eea.plotly.interfaces import IPlotlyVisualizationField
from eea.plotly.io_csv import CsvReader
from eea.plotly.utils import sanitizeVisualization


@implementer(IFieldSerializer)
@adapter(IPlotlyVisualizationField, IDexterityContent, Interface)
class VisualizationFieldSerializer(DefaultFieldSerializer):
    """Visualization field serializer"""

    def fileToJson(self, file):
        """Convert binary file data to JSON"""
        if not file:
            return None
        data = file.data
        if not data:
            return None
        buff = StringIO(data.decode('utf-8-sig'))
        try:
            data = {}
            headers = []
            i = -1
            for row in CsvReader(buff):
                i += 1
                j = -1
                for cell in row:
                    if i == 0:
                        data[cell] = []
                        headers.append(cell)
                        continue
                    j += 1
                    data[headers[j]].append(cell)
            return data
        except csv.Error:
            return None

    def __call__(self):
        value = copy.deepcopy(self.get_value())

        dataSources = self.fileToJson(self.context.file)
        if dataSources:
            value["dataSources"] = dataSources

        value = sanitizeVisualization(value)

        if 'provider_url' in value:
            value["provider_url"] = uid_to_url(value["provider_url"])

        return json_compatible(value)
