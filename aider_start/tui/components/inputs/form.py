
from prompt_toolkit.layout import HSplit
from ..base import Component

class Form(Component):
    """Form container component"""

    def __init__(self, fields=None, style="class:form"):
        super().__init__()
        self.fields = fields or []
        self.style = style

    def add_field(self, field):
        self.fields.append(field)

    def get_values(self):
        values = {}
        for field in self.fields:
            values[field.name] = field.value
        return values

    def set_values(self, values):
        for field in self.fields:
            if field.name in values:
                field.set_value(values[field.name])

    def validate(self):
        valid = True
        for field in self.fields:
            if hasattr(field, "validate") and callable(field.validate):
                field_valid = field.validate()
                valid = valid and field_valid
        return valid

    def __pt_container__(self):
        return HSplit(self.fields)
