from enum import Enum
from pydantic import BaseModel, RootModel

class direction(str, Enum): # "Is the value below the min or above the max?"
    BELOW_MIN = "BELOW_MIN"
    ABOVE_MAX = "ABOVE_MAX"

class threshold_type(str, Enum): # Essentially if the threshold is a distinct number or calculated
    NUMERIC = "NUMERIC"
    FORMULA = "FORMULA"

class condition(BaseModel): # A single bound of the thing being monitored. Think of like "this is/isn't a violation of a bound"
    direction: direction
    threshold: str
    threshold_type: threshold_type
    units: str
    sub_variable: str | None  # null normally. Named only in conjunctive conditions (two different variables, one trip)

class setpoint_record(BaseModel): # Name of the thing being monitored. Think "RC High Pressure" or "Water Tank Low Level". In short, it's the main object.
    variable: str
    function_name: str
    source_text: str # The original rule
    conditions: list[condition]

class setpoint_list(RootModel): # List of setpoint records
    root: list[setpoint_record]