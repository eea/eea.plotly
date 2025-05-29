""" SOER miniature theme for Plotly visualizations. """
import math


def nice_step(vmin, vmax, target_ticks=5):
    """ Calculate a 'nice' step size for the axis ticks. """
    span = abs(vmax - vmin)
    if span == 0:
        return 1  # arbitrary fallback

    # Initial guess for raw step size
    raw_step = span / target_ticks

    # Determine the power of 10
    magnitude = 10 ** math.floor(math.log10(raw_step))
    residual = raw_step / magnitude

    # Choose a nice multiplier
    if residual < 1.5:
        nice_multiplier = 1
    elif residual < 3:
        nice_multiplier = 2
    elif residual < 7:
        nice_multiplier = 5
    else:
        nice_multiplier = 10

    return nice_multiplier * magnitude


def getMin(arr):
    """ Get minimum value from array """
    return min(float(v) for v in arr if v is not None)


def getMax(arr):
    """ Get maximum value from array """
    return max(float(v) for v in arr if v is not None)


def serialize(context):
    """ Serialize the context for SOER miniature theme"""

    # Solve x axis range

    years = context.visualization["data"][0].get("x", [])
    tickvals = context.visualization["layout"]["xaxis"].get("tickvals", [])

    if tickvals and years:
        min_year = getMin(tickvals)
        max_year = getMax(years)

        context.visualization["layout"]["xaxis"]["range"] = [
            min_year - 1, max_year + 1]
        context.visualization["layout"]["xaxis"]["autorange"] = False

    # Solve y axis range

    y_values = context.visualization["data"][0].get(
        "y", []) + context.visualization["data"][1].get("y", [])

    if y_values:
        min_y = getMin(y_values)
        max_y = getMax(y_values)

        step = nice_step(min_y, max_y, 10)

        context.visualization["layout"]["yaxis"]["range"] = [
            min_y - step, max_y + step]
        context.visualization["layout"]["yaxis"]["autorange"] = False

    return True
