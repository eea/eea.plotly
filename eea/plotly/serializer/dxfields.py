""" dxfields serializers """

import copy
import csv
import json
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from plone.restapi.serializer.utils import uid_to_url
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.interfaces import IFieldSerializer
from eea.plotly.interfaces import IPlotlyVisualizationField
from eea.plotly.utils import sanitizeVisualization


@implementer(IFieldSerializer)
@adapter(IPlotlyVisualizationField, IDexterityContent, Interface)
class VisualizationFieldSerializer(DefaultFieldSerializer):
    """Visualization field serializer"""

    def fileToJson(self, file):
        """Convert binary file data to JSON"""
        if not file:
            return None
        try:
            _, subtype = file.contentType.split("/")
        except ValueError:
            # The accept type is invalid. Skip it.
            return None
        data = file.data
        if not data or subtype not in ["csv", 'tsv', "json"]:
            return None
        decoded = data.decode('utf-8')
        if subtype == "json":
            try:
                return json.loads(decoded)
            except json.JSONDecodeError:
                return None
        try:
            csv.Sniffer().sniff(decoded)
            delimiter = ',' if subtype == "csv" else '\t'
            csv_data = decoded.splitlines()
            reader = csv.DictReader(csv_data, delimiter=delimiter)
            data = {}
            for row in reader:
                for key, value in row.items():
                    if key not in data:
                        data[key] = []
                    data[key].append(value)
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
