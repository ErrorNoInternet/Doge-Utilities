class Conversion:
    def __init__(self, input, output, action, amount):
        self.input = input
        self.output = output
        self.action = action
        self.amount = amount

    def __repr__(self):
        return f"<Conversion input={self.input} output={self.output} action={self.action} amount={self.amount}>"

abbreviations = {
    "mm": "millimeter",
    "cm": "centimeter",
    "m": "meter",
    "km": "kilometer",
    "ms": "millisecond",
    "s": "second",
    "min": "minute",
    "hr": "hour",
    "d": "day",
    "w": "week",
    "mo": "month",
    "y": "year",
}

conversions = [
    Conversion("millimeter", "centimeter", "divide", 10),
    Conversion("millimeter", "meter", "divide", 1000),
    Conversion("millimeter", "kilometer", "divide", 1000000),
    Conversion("centimeter", "meter", "divide", 100),
    Conversion("centimeter", "kilometer", "divide", 100000),
    Conversion("meter", "kilometer", "divide", 1000),

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
]

reversed_conversions = []
for conversion in conversions:
    new_action = "divide"
    if conversion.action == "divide":
        new_action = "multiply"
    reversed_conversions.append(Conversion(conversion.output, conversion.input, new_action, conversion.amount))
[conversions.append(conversion) for conversion in reversed_conversions]

def convert(amount, input_unit, output_unit):
    input_unit = input_unit.lower()
    output_unit = output_unit.lower()
    for conversion in conversions:
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
            else:
                raise Exception("unsupported action: " + conversion.action)
            input_abbreviation = "unknown"
            for abbreviation in abbreviations:
                if abbreviations[abbreviation] == input_unit:
                    input_abbreviation = abbreviation
                    break
            output_abbreviation = "unknown"
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

