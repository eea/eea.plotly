"""Pydantic models for structured LLM output of chart operations."""

from pydantic import BaseModel, Field


class VisualizationData(BaseModel):
    """The Plotly chart configuration stored in the visualization field."""

    data: list[dict] = Field(
        description=(
            "Ordered list of Plotly trace objects. Each trace must have a "
            "'type' field, '*src' references to dataSources columns, "
            "dereferenced inline data arrays, and 'meta.columnNames' mapping."
        ),
    )

    layout: dict = Field(
        description=(
            "Plotly layout object with title, axis definitions, and "
            "layout.template set to the active site theme."
        ),
        default_factory=dict,
    )

    dataSources: dict = Field(
        description=(
            "Dict of column_name -> array of values. Contains all data "
            "columns referenced by traces via *src fields."
        ),
        default_factory=dict,
    )

    columns: list[dict] = Field(
        description=(
            "List of column metadata objects, each with a 'key' field "
            "matching a dataSources column name. "
            'Example: [{"key": "Country"}, {"key": "Value"}]'
        ),
        default_factory=list,
    )


class ChartGenerationResult(BaseModel):
    """Result of LLM visualization content generation.

    Represents a full visualization content type with metadata and chart data.
    """

    title: str = Field(
        description="Content title for the visualization page.",
    )

    description: str = Field(
        description=(
            "Short summary describing the visualization (1-3 sentences). "
            "Used as the page description / Dublin Core description."
        ),
        default="",
    )

    visualization: VisualizationData = Field(
        description=(
            "The complete Plotly visualization with traces (data), layout, "
            "dataSources (raw dataset columns), and columns metadata."
        ),
    )

    topics: list[str] = Field(
        description=(
            "List of EEA topic tags relevant to this visualization "
            "(e.g. 'Climate change mitigation', 'Air pollution')."
        ),
        default_factory=list,
    )

    temporal_coverage: list[int] = Field(
        description=(
            "List of years covered by the data "
            "(e.g. [2018, 2019, 2020, 2021, 2022])."
        ),
        default_factory=list,
    )

    geo_coverage: list[str] = Field(
        description=(
            "List of geographic areas covered by the data "
            "(e.g. ['Europe', 'EU-27', 'Germany'])."
        ),
        default_factory=list,
    )
