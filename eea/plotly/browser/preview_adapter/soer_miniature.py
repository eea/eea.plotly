""" SOER miniature theme for Plotly visualizations. """
import math


def nice_step(vmin, vmax, target_ticks=5):
    """Calculate a 'nice' step size for axis ticks, similar to Plotly/D3."""
    span = abs(vmax - vmin)
    if span == 0:
        return 1  # fallback

    raw_step = span / max(target_ticks - 1, 1)
    magnitude = 10 ** math.floor(math.log10(raw_step))
    residual = raw_step / magnitude

    # D3/Plotly uses [1, 2, 2.5, 5, 10]
    if residual <= 1:
        nice_multiplier = 1
    elif residual <= 2:
        nice_multiplier = 2
    elif residual <= 2.5:
        nice_multiplier = 2.5
    elif residual <= 5:
        nice_multiplier = 5
    else:
        nice_multiplier = 10

    return nice_multiplier * magnitude


def exact_step(vmin, vmax, target_ticks=5):
    """Get the exact step size to have target_ticks between vmin and vmax."""
    if target_ticks < 2:
        raise ValueError("target_ticks must be at least 2 to define a range.")
    return abs(vmax - vmin) / (target_ticks - 1)


def getMin(arr):
    """ Get minimum value from array """
    return min(float(v) for v in arr if v is not None)


def getMax(arr):
    """ Get maximum value from array """
    return max(float(v) for v in arr if v is not None)


def serialize(context):
    """ Serialize the context for SOER miniature theme"""
    if context.visualization is None:
        return False

    data = context.visualization["data"]
    layout = context.visualization["layout"]
    min_year = float("inf")
    max_year = float("-inf")
    first_val = None
    new_x = []
    new_y = []

    if len(data) < 5:
        layout["xaxis"]["showticklabels"] = False
        return False

    if "y" in data[0] and "x" in data[0]:
        for index, val in enumerate(data[0]["y"]):
            if val and not first_val:
                first_val = val
            if not first_val:
                continue
            year = data[0]["x"][index]
            new_x.append(year)
            new_y.append(val)
            if val and year > max_year:
                max_year = year
            if val and year < min_year:
                min_year = year

        text_len = len(data[0]["text"])
        data[0]["x"] = new_x
        data[0]["y"] = new_y
        data[0]["text"] = data[0]["text"][text_len - len(new_y):text_len + 1]

        if data[4].get("x") and data[4].get("y"):
            y_len = len(data[0]["y"])
            y4_len = len(data[4]["y"])
            data[4]["x"] = new_x
            data[4]["y"] = data[4]["y"][y4_len - y_len:y4_len + 1]
        else:
            data[4] = {
                "type": "scatter",
                "x": new_x,
                "y": [None] * len(new_y),
                "visible": True,
                "marker": {
                    "color": "rgba(0, 0, 0, 0)",
                    "line": {
                        "color": "rgba(0, 0, 0, 0)"
                    }
                }
            }
            data[4]["y"][len(data[4]["y"]) - 1] = new_y[-1]

        layout["xaxis"]["tickmode"] = "array"
        layout["xaxis"]["tickvals"] = [min_year, max_year, 2030]
        layout["xaxis"]["range"] = [
            min_year - 1, 2032]
        layout["xaxis"]["autorange"] = True

    y_values = (
        (data[0].get("y") or []) +
        (data[1].get("y") or []) +
        (data[4].get("y") or [])
    )

    if y_values:
        top = layout["margin"]["t"] or layout["template"]["margin"]["t"]
        min_y = getMin(y_values)
        max_y = getMax(y_values)

        min_y = min_y if min_y < 0 else 0
        max_y = max_y if max_y > 0 else 0

        nticks = max(int((context.height - top) / 100), 2)

        step = exact_step(min_y, max_y, nticks)

        layout["yaxis"]["tickmode"] = "linear"
        layout["yaxis"]["nticks"] = nticks
        layout["yaxis"]["tick0"] = min_y - step
        layout["yaxis"]["dtick"] = step

        layout["yaxis"]["range"] = [
            min_y - step, max_y + 2 * step]
        layout["yaxis"]["autorange"] = False

    if "text" in data[0]:
        data[0]["text"] = [
            (t if t is None else " " + str(t))
            for t in data[0]["text"]]

    data[1]["x"] = None
    data[1]["y"] = None
    data[2]["x"] = None
    data[2]["y"] = None
    data[3]["x"] = None
    data[3]["y"] = None

    return True
