""" behavior module """

import json

from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from plone.schema import JSONField
from plone.namedfile.field import NamedBlobFile
from zope.interface import directlyProvides, provider


from eea.plotly.interfaces import IPlotlyVisualizationField, IPlotlyFileField


VIZ_SCHEMA = json.dumps({"type": "object", "properties": {}})


@provider(IFormFieldProvider)
class IPlotlyVisualization(model.Schema):
    """ A plotly visualization behavior provider """

    visualization = JSONField(
        title="Visualization", required=False, default={}, schema=VIZ_SCHEMA
    )

    directlyProvides(visualization, IPlotlyVisualizationField)

    file = NamedBlobFile(
        title="File",
        required=False,
        description="Data sources file",
        accept=["text/csv", 'text/tsv', "application/json"],
    )

    directlyProvides(file, IPlotlyFileField)
