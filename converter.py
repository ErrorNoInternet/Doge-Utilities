class Conversion:
    def __init__(self, input, output, action, amount=0, shortened=True):
        self.input = input
        self.output = output
        self.action = action
        self.amount = amount
        self.shortened = shortened

    def __repr__(self):
        return f"<Conversion input={self.input} output={self.output} action={self.action} amount={self.amount}>"


abbreviations = {
    "mm": "millimeter",
    "cm": "centimeter",
    "m": "meter",
    "km": "kilometer",
    "mi": "mile",
    "ms": "millisecond",
    "s": "second",
    "min": "minute",
    "hr": "hour",
    "d": "day",
    "w": "week",
    "mo": "month",
    "y": "year",
    "b": "byte",
    "kb": "kilobyte",
    "mb": "megabyte",
    "gb": "gigabyte",
    "tb": "terabyte",
    "pb": "petabyte",
    "g": "gram",
    "kg": "kilogram",
    "t": "ton",
    "ft": "foot",
    "in": "inch",
}

replacers = {
    "feet": "foot",
    "inches": "inch",
}

conversions = [
    Conversion("millimeter", "centimeter", "divide", 10),
    Conversion("millimeter", "meter", "divide", 1000),
    Conversion("millimeter", "kilometer", "divide", 1000000),
    Conversion("centimeter", "meter", "divide", 100),
    Conversion("centimeter", "kilometer", "divide", 100000),
    Conversion("meter", "kilometer", "divide", 1000),
    Conversion("mile", "kilometer", "divide", 0.621371),
    Conversion("meter", "foot", "multiply", 3.2808399),
    Conversion("inch", "meter", "multiply", 0.0254),
    Conversion("foot", "inch", "multiply", 12),
    Conversion("foot", "centimeter", "multiply", 30.48),
    Conversion("inch", "centimeter", "multiply", 2.54),
    Conversion("ton", "kilogram", "multiply", 907.18474),
    Conversion("kilogram", "gram", "multiply", 1000),
    Conversion("byte", "kilobyte", "divide", 1000),
    Conversion("byte", "megabyte", "divide", 1000000),
    Conversion("byte", "gigabyte", "divide", 1000000000),
    Conversion("byte", "terabyte", "divide", 1000000000000),
    Conversion("byte", "petabyte", "divide", 1000000000000000),
    Conversion("kilobyte", "megabyte", "divide", 1000),
    Conversion("kilobyte", "gigabyte", "divide", 1000000),
    Conversion("kilobyte", "terabyte", "divide", 1000000000),
    Conversion("kilobyte", "petabyte", "divide", 1000000000000),
    Conversion("megabyte", "gigabyte", "divide", 1000),
    Conversion("megabyte", "terabyte", "divide", 1000000),
    Conversion("megabyte", "petabyte", "divide", 1000000000),
    Conversion("gigabyte", "terabyte", "divide", 1000),
    Conversion("gigabyte", "petabyte", "divide", 1000000),
    Conversion("terabyte", "petabyte", "divide", 1000),
    Conversion("millisecond", "second", "divide", 1000),
    Conversion("millisecond", "minute", "divide", 60000),
    Conversion("millisecond", "hour", "divide", 3600000),
    Conversion("millisecond", "day", "divide", 86400000),
    Conversion("millisecond", "week", "divide", 604800000),
    Conversion("millisecond", "month", "divide", 2592000000),
    Conversion("millisecond", "year", "divide", 31556952000),
    Conversion("second", "minute", "divide", 60),
    Conversion("second", "hour", "divide", 3600),
    Conversion("second", "day", "divide", 86400),
    Conversion("second", "week", "divide", 604800),
    Conversion("second", "month", "divide", 2592000),
    Conversion("second", "year", "divide", 31556926),
    Conversion("minute", "hour", "divide", 60),
    Conversion("minute", "day", "divide", 1440),
    Conversion("minute", "week", "divide", 10080),
    Conversion("minute", "month", "divide", 43200),
    Conversion("minute", "year", "divide", 525948.766),
    Conversion("hour", "day", "divide", 24),
    Conversion("hour", "week", "divide", 168),
    Conversion("hour", "month", "divide", 720),
    Conversion("hour", "year", "divide", 8765.81277),
    Conversion("day", "week", "divide", 7),
    Conversion("day", "month", "divide", 30.4368499),
    Conversion("day", "year", "divide", 365),
    Conversion("week", "month", "divide", 4.2857),
    Conversion("week", "year", "divide", 52.177457),
    Conversion("month", "year", "divide", 12),
    Conversion("fahrenheit", "celcius", "custom:(x-32)*0.5556", shortened=False),
    Conversion("celcius", "fahrenheit", "custom:(x*1.8)+32", shortened=False),
]

reversed_conversions = []
for conversion in conversions:
    if conversion.action.startswith("custom:"):
        continue
    new_action = "divide"
    if conversion.action == "divide":
        new_action = "multiply"
    reversed_conversions.append(
        Conversion(conversion.output, conversion.input, new_action, conversion.amount)
    )
[conversions.append(conversion) for conversion in reversed_conversions]


def convert(amount, input, output):
    if input.lower() == output.lower():
        return {"error": 403}
    if input.lower() in replacers:
        input = replacers[input.lower()]
    else:
        if input.lower()[:-1] in replacers:
            input = replacers[input.lower()[:-1]]
    if output.lower() in replacers:
        output = replacers[output.lower()]
    else:
        if output.lower()[:-1] in replacers:
            output = replacers[output.lower()[:-1]]
    for conversion in conversions:
        input_unit = input.lower()
        output_unit = output.lower()
        if conversion.shortened:
            found = False
            for i in range(2):
                for abbreviation in abbreviations:
                    if abbreviation == input_unit:
                        input_unit = abbreviations[abbreviation]
                if not found:
                    if input_unit.endswith("s"):
                        input_unit = input_unit[:-1]
            found = False
            for i in range(2):
                for abbreviation in abbreviations:
                    if abbreviation == output_unit:
                        output_unit = abbreviations[abbreviation]
                        found = True
                if not found:
                    if output_unit.endswith("s"):
                        output_unit = output_unit[:-1]
        if conversion.input == input_unit and conversion.output == output_unit:
            result = 0
            if conversion.action == "multiply":
                result = amount * conversion.amount
            elif conversion.action == "divide":
                result = amount / conversion.amount
            elif conversion.action.startswith("custom:"):
                expression = conversion.action.split("custom:")[1]
                expression = expression.replace("x", str(amount))
                result = eval(expression)
            else:
                raise Exception("unsupported action: " + conversion.action)
            input_abbreviation = conversion.input
            for abbreviation in abbreviations:
                if abbreviations[abbreviation] == input_unit:
                    input_abbreviation = abbreviation
                    break
            output_abbreviation = conversion.output
            for abbreviation in abbreviations:
                if abbreviations[abbreviation] == output_unit:
                    output_abbreviation = abbreviation
                    break
            return {
                "result": result,
                "input_abbreviation": input_abbreviation,
                "output_abbreviation": output_abbreviation,
                "input_unit": input_unit,
                "output_unit": output_unit,
                "error": None,
            }
    return {"error": 404}
