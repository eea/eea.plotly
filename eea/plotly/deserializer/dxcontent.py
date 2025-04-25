import json
import plotly.io as pio
from io import StringIO
from plone.namedfile.file import NamedBlobFile, NamedBlobImage
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.deserializer.dxcontent import DeserializeFromJson
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from eea.plotly.behaviors import IPlotlyVisualization
from eea.plotly.io_csv import CsvWriter


@implementer(IDeserializeFromJson)
@adapter(IPlotlyVisualization, Interface)
class DeserializeVisualizationFromJson(DeserializeFromJson):
    def jsonToBinary(self, data):
        """Convert JSON data to binary"""
        if not data:
            return None

        output = StringIO()

        # Extract columns
        columns = list(data.keys())

        # Extract rows per column
        rows = []

        for column in columns:
            values = [column] + data[column]
            for i, value in enumerate(values):
                if len(rows) < i + 1:
                    rows.append([value])
                else:
                    rows[i].append(value)

        CsvWriter(output).writerows(rows)

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

        # Handle preview image
        fig = pio.from_json(
            json.dumps({
                "data": self.context.visualization.get("data", []),
                "layout": self.context.visualization.get("layout", {}),
                "frames": self.context.visualization.get("frames", [])
            }),
            skip_invalid=True
        )

        image = fig.to_image(format="svg")
        self.context.preview_image = NamedBlobImage(
            data=image,
            filename="preview.svg",
            contentType="image/svg+xml"
        )

        data = self.jsonToBinary(self.context.visualization.get(
            "dataSources", {})
        )

        if data:
            self.context.file = NamedBlobFile(
                data=data,
                filename="data.csv",
                contentType="text/csv"
            )

        if "dataSources" in self.context.visualization:
            del self.context.visualization["dataSources"]

        return self.context
