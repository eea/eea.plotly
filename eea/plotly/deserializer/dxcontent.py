import csv
import json
from io import StringIO
from plone.namedfile.file import NamedBlobFile
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.deserializer.dxcontent import DeserializeFromJson
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from eea.plotly.behaviors import IPlotlyVisualization


mime_types = {
    "csv": "text/csv",
    "tsv": "text/tsv",
    "json": "application/json",
}


@implementer(IDeserializeFromJson)
@adapter(IPlotlyVisualization, Interface)
class DeserializeVisualizationFromJson(DeserializeFromJson):
    def jsonToBinary(self, data, subtype="json"):
        """Convert JSON data to binary"""
        if not data:
            return None
        if subtype == "json":
            return json.dumps(data).encode('utf-8')
        output = StringIO()
        csvData = []
        delimiter = ',' if subtype == "csv" else '\t'
        for key, values in data.items():
            for i, value in enumerate(values):
                if i >= len(csvData):
                    csvData.append({})
                csvData[i][key] = value
        writer = csv.DictWriter(
            output, fieldnames=csvData[0].keys(),
            delimiter=delimiter)
        writer.writeheader()
        writer.writerows(csvData)
        return output.getvalue().encode('utf-8')

    def __call__(
            self, validate_all=False, data=None, create=False,
            mask_validation_errors=True):

        super().__call__(
            validate_all, data, create, mask_validation_errors
        )

        ok = False
        for interface, names in self.modified.items():
            if (interface == IPlotlyVisualization and
                    "IPlotlyVisualization.visualization" in names):
                ok = True
                break

        if not ok:
            return self.context

        ctype = 'csv'
        if hasattr(
                self.context, 'file') and hasattr(
                self.context.file, 'contentType'):
            ctype = self.context.file.contentType.split("/")[1]

        data = self.jsonToBinary(self.context.visualization.get(
            "dataSources", {}), ctype)
        if data:
            self.context.file = NamedBlobFile(
                data=data,
                filename=f"data.{ctype}",
                contentType=mime_types[ctype]
            )

        if "dataSources" in self.context.visualization:
            del self.context.visualization["dataSources"]

        return self.context
