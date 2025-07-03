"""JSON encoder that handles Decimal values."""
import decimal
import json


class JSONEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal values."""

    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super().default(o)
