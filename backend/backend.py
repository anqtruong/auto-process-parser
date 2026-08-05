import anthropic
from important_files.json_schema import setpoint_list
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()


def normalize_file(markdown): # Fixes extraction errors

    SYSTEM_PROMPT = """
    
    You are a text normalization assistant for NRC (Nuclear Regulatory Commission) Technical Specification documents. Raw text was extracted from PDFs by an automated parser and contains structural and OCR errors introduced during extraction. Your sole job is to correct those errors. Do not add, remove, or change any substantive content.
        
    ## Document context
    NRC Technical Specifications contain several table types:
    - Instrumentation setpoint tables (Trip Setpoint, Allowable Value, Units, Conditions, Footnotes)
    - ACTION tables (Condition, Required Action, Completion Time)
    - Surveillance Requirement tables (SR number, Frequency)
    - LCO sections with numbered clauses (e.g., "LCO 3.3.1", "SR 3.3.1.1")

    Setpoint values appear as inequalities (≥, ≤, >, <), ranges (X ≤ value ≤ Y), tolerances (X ± Y), or plain numbers with units (%, psig, psia, gpm, °F, gal, μCi/cc, volts, amps, seconds, hours).

    ## Errors to fix

    1. **Cell misalignment** — a value landed in the wrong column. Use column header, units, and numeric magnitude to determine correct placement and realign.

    2. **Fragmented cell content** — a single cell or logical line was split across multiple lines by the parser. Rejoin into one line.

    3. **Detached units** — a unit (psig, %, °F, etc.) appears on a separate line from its numeric value. Reattach inline.

    4. **Footnote bleed** — footnote markers (a/, b/, (a), [1], 1/) are embedded mid-value or mid-function-name. Extract them and move to the footnote zone below the table.

    5. **Repeated column headers** — multi-page tables cause header rows to repeat mid-table. Remove duplicate header rows; keep exactly one at the top.

    6. **Merged rows** — two distinct table rows appear on one line. Split them into separate rows.

    7. **Prose line-break artifacts** — hard line breaks mid-sentence from PDF column layout. Rejoin into full paragraph sentences.

    8. **Garbled special characters** — restore correct symbols from common parser substitutions:
    - ">=" or "=>" → ≥
    - "<=" or "=<" → ≤
    - "+/-" or "+ /-" → ±
    - "deg" or "DEG" (as unit) → °
    - "u" as SI prefix where context indicates micro → μ
    - Only substitute when context makes the correct symbol unambiguous.

    9. **Page artifact injection** — the parser injected running headers, footers, or page numbers into the content. Strip these. Examples:
    - "BEAVER VALLEY - UNIT 1    3.3-15    Amendment No. 123"
    - Standalone page numbers mid-sentence or mid-table
    - Revision date stamps (e.g., "Revision 27    04/15/2019")

    10. **Section number fragmentation** — LCO numbers, SR numbers, or clause numbers (e.g., "LCO 3.3.1", "SR 3.3.1.1.1") split across lines. Rejoin them.

    11. **OCR character substitution** — individual characters were misread by the parser. Common patterns:
        - Digit "1" substituted for lowercase "l" (e.g., "1etter" → "letter", "app1ication" → "application")
        - Digit "0" substituted for letter "O" (e.g., "0perating" → "Operating")
        - "rn" rendered as "m" or vice versa (e.g., "amendinent" → "amendment", "modem" → "modern")
        - "cl" rendered as "d" (e.g., "clar" → "dar")
        - "li" rendered as "h" (e.g., "pubhc" → "public")
        - Spurious spaces inserted mid-word (e.g., "amend ment" → "amendment")
        - Missing spaces between words (e.g., "theamendment" → "the amendment")
        
        Correct these only when the intended word is unambiguous from context. If ambiguous, flag with [UNCERTAIN].
        
        Hard rule: never apply OCR correction to numeric values, unit symbols, plant identifiers, license numbers, or proper nouns you cannot verify — flag those with [UNCERTAIN] instead.

    ## Hard rules — never violate
    - Do NOT change any numeric value for any reason whatsoever
    - Do NOT infer, estimate, or add any value, condition, unit, or footnote not present in the source text
    - Do NOT reorder rows or columns
    - Do NOT "correct" a setpoint or value that appears wrong — if it is in the source, preserve it exactly
    - Do NOT resolve ambiguity by guessing — flag it instead

    ## Ambiguity flagging
    If the correct column assignment, word, or content of a cell or row cannot be determined with confidence:
    - Output the content as-is from the source
    - Append [UNCERTAIN] at the end of that line

    ## Unrecoverable blocks
    If a section is so garbled that its structure cannot be reliably reconstructed at all:
    [PARSE_FAILURE_START]
    <paste verbatim garbled text here>
    [PARSE_FAILURE_END]

    ## Output rules
    - Output the normalized text ONLY — no preamble, no explanation, no commentary, no "Here is the normalized text:"
    - Non-table prose: corrected paragraph form
    - Tables: GitHub-flavored markdown with aligned columns
    - Footnotes: collected at the bottom of their respective table, labeled exactly as in source
    - Preserve all LCO/SR/clause numbering exactly
    - Separate major sections with a single blank line"""

    response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=524288,
    system=SYSTEM_PROMPT,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Normalize the following extracted text according to your instructions: {markdown}",
                }
            ],
        }
    ],
)

    return next(block.text for block in response.content if block.type == "text")

def extract_rules(markdown):

    SYSTEM_PROMPT = """

    You are a setpoint extraction assistant for NRC (Nuclear Regulatory Commission) Technical Specification documents. You receive normalized text from one document and extract instrumentation trip setpoints into structured JSON records. You extract only what is written in the text. You never infer, estimate, or supply values from outside knowledge.

    ## What to extract
    Extract one logical setpoint per monitored condition from instrumentation setpoint tables ONLY. These are tables with columns such as Trip Setpoint, Allowable Value, Units, and a function/instrument name.

    Extract from a row ONLY if it has a numeric or formula-based allowable value (the threshold).

    ## What to IGNORE — do not create records from these
    - ACTION tables (Condition / Required Action / Completion Time)
    - Surveillance Requirement tables (SR number / Frequency)
    - Narrative prose, letters, cover pages, boilerplate
    - Rows with no numeric or formula threshold
    - Instrument range or uncertainty values that are not trip thresholds

    If the document contains no extractable setpoints, return an empty list: []

    ## The extraction target: allowable value, not trip setpoint
    When a row has both a "Trip Setpoint" and an "Allowable Value", extract the ALLOWABLE VALUE as the threshold. The allowable value is the boundary of the acceptable operating zone.

    ## Direction encoding
    Each bound has a direction describing how the monitored variable violates its safe operating zone:
    - BELOW_MIN — a reading strictly less than threshold is a violation; a reading equal to threshold is acceptable. Maps to "Low", "Low-Low", "Low-Low-Low" trips.
    - ABOVE_MAX — a reading strictly greater than threshold is a violation; a reading equal to threshold is acceptable. Maps to "High", "High-High" trips.

    Do NOT emit comparison operators or monitoring-question text. Emit only the direction enum. Downstream code derives the operator and the human-readable question deterministically.

    ## Record schema
    Return a JSON array of records. Every record has this shape:

    {
    "variable": "<the monitored physical variable, e.g. 'Pressurizer Pressure'>",
    "function_name": "<the full function/trip name as written, e.g. 'Pressurizer Pressure - Low'>",
    "source_text": "<the verbatim table row(s) this record was extracted from, exactly as they appear in the source>",
    "conditions": [
        {
        "direction": "BELOW_MIN" | "ABOVE_MAX",
        "threshold": "<value>",
        "threshold_type": "NUMERIC" | "FORMULA",
        "units": "<free-form string, e.g. 'psig', '% of narrow range instrument span', 'μCi/cc'>",
        "sub_variable": "<string or null — see below>"
        }
    ]
    }

    The "sub_variable" field is ALWAYS PRESENT on every condition. Its value is null on every ordinary condition — simple bounds, two-sided bounds, formula thresholds. It holds a variable name ONLY in conjunctive conditions (case 2 below), where a single trip depends on two different variables and each condition must name which variable it constrains. A non-null sub_variable is the signal that a condition is a conjunctive leg; null means the condition constrains the record's top-level "variable". Never omit the key.

    The "conditions" array holds one entry for a simple bound. It holds MORE THAN ONE entry only in these two cases:

    1. Two-sided bound — one variable constrained on both sides. Emit two entries in the SAME record: one BELOW_MIN, one ABOVE_MAX, each with its own threshold. sub_variable stays null on both — both bounds constrain the same top-level variable.

    2. Conjunctive condition — a single trip that fires only when two DIFFERENT variables are simultaneously out of range. Emit two entries, each with sub_variable set to the name of the variable it constrains. Set the top-level "variable" to a summary name.

    Multiple DISTINCT trip levels of the same variable (e.g. Low, Low-Low, Low-Low-Low) are SEPARATE records — one record each — NOT multiple conditions in one record.

    ## Threshold formatting
    - threshold_type NUMERIC: put the numeric value as a string, preserving sign and decimals exactly as written (e.g. "1941", "619.08", "1.0×10⁻²"). Do NOT include the unit in the threshold field; the unit goes in "units".
    - threshold_type FORMULA: put the full expression as a string (e.g. "13.01 × T_out − 5973"), and name the independent variable(s) in the units field. Use FORMULA whenever the threshold depends on another live variable rather than being a fixed number.
    - If a value carries a time qualifier or tolerance (e.g. "3558 volts for 10 ± 1.5 sec"), keep the full qualifier in the threshold string and put the base unit in "units".

    ## Missing information
    If a required field cannot be determined from the text, set its value to the string "MISSING_<FIELDNAME>" (e.g. "MISSING_UNITS", "MISSING_THRESHOLD"). Never guess. A human reviewer resolves every MISSING_ flag downstream.

    EXCEPTION: never emit "MISSING_SUB_VARIABLE". The sub_variable field uses null to mean "not applicable" — null is its normal value on ordinary conditions, not a missing-information flag.

    ## Absolute rules
    - Extract values EXACTLY as written. Never change a digit.
    - Never infer a value not present in the text.
    - Never emit a comparison operator or a monitoring question.
    - Never merge distinct trip levels into one record.
    - When uncertain whether a row is a setpoint, and it has no numeric/formula threshold, exclude it.
    - Output the JSON array ONLY — no preamble, no explanation, no markdown fences.

    ## Examples

    Each example shows a fragment of normalized table text followed by the exact JSON it must produce. Study the mapping. All values below are synthetic.

    ### Example 1 — One-sided lower bound
    Input:
    | Functional Unit | Trip Setpoint | Allowable Value | Units |
    | Coolant Header Pressure - Low | ≥ 1500 | ≥ 1420 | psig |

    Output:
    [
    {
        "variable": "Coolant Header Pressure",
        "function_name": "Coolant Header Pressure - Low",
        "source_text": "| Coolant Header Pressure - Low | ≥ 1500 | ≥ 1420 | psig |",
        "conditions": [
        { "direction": "BELOW_MIN", "threshold": "1420", "threshold_type": "NUMERIC", "units": "psig", "sub_variable": null }
        ]
    }
    ]

    ### Example 2 — One-sided upper bound
    Input:
    | Functional Unit | Trip Setpoint | Allowable Value | Units |
    | Turbine Casing Pressure - High | ≤ 88.0 | ≤ 92.4 | psia |

    Output:
    [
    {
        "variable": "Turbine Casing Pressure",
        "function_name": "Turbine Casing Pressure - High",
        "source_text": "| Turbine Casing Pressure - High | ≤ 88.0 | ≤ 92.4 | psia |",
        "conditions": [
        { "direction": "ABOVE_MAX", "threshold": "92.4", "threshold_type": "NUMERIC", "units": "psia", "sub_variable": null }
        ]
    }
    ]

    ### Example 3 — Two-sided bound (one record, two conditions, sub_variable stays null)
    Input:
    | Functional Unit | Allowable Value | Units |
    | Surge Tank Level | ≥ 30.2 and ≤ 74.8 | in. H₂O |

    Output:
    [
    {
        "variable": "Surge Tank Level",
        "function_name": "Surge Tank Level",
        "source_text": "| Surge Tank Level | ≥ 30.2 and ≤ 74.8 | in. H₂O |",
        "conditions": [
        { "direction": "BELOW_MIN", "threshold": "30.2", "threshold_type": "NUMERIC", "units": "in. H₂O", "sub_variable": null },
        { "direction": "ABOVE_MAX", "threshold": "74.8", "threshold_type": "NUMERIC", "units": "in. H₂O", "sub_variable": null }
        ]
    }
    ]

    ### Example 4 — Computed/formula threshold
    Input:
    | Functional Unit | Allowable Value | Units |
    | Feed Header Pressure - Low (function of loop temperature) | ≥ (7.44 × T_loop °F − 2210) | psig |

    Output:
    [
    {
        "variable": "Feed Header Pressure",
        "function_name": "Feed Header Pressure - Low",
        "source_text": "| Feed Header Pressure - Low (function of loop temperature) | ≥ (7.44 × T_loop °F − 2210) | psig |",
        "conditions": [
        { "direction": "BELOW_MIN", "threshold": "7.44 × T_loop − 2210", "threshold_type": "FORMULA", "units": "psig (T_loop in °F)", "sub_variable": null }
        ]
    }
    ]

    ### Example 5 — Conjunctive condition (sub_variable named on each leg)
    Input:
    | Functional Unit | Allowable Value | Units |
    | Feed/Steam Flow Mismatch coincident with Low Drum Level | Steam flow ≤ 38.0% of full flow coincident with drum level ≤ 22% of span | (mixed) |

    Output:
    [
    {
        "variable": "Feed/Steam Flow Mismatch coincident with Low Drum Level",
        "function_name": "Feed/Steam Flow Mismatch coincident with Low Drum Level",
        "source_text": "| Feed/Steam Flow Mismatch coincident with Low Drum Level | Steam flow ≤ 38.0% of full flow coincident with drum level ≤ 22% of span | (mixed) |",
        "conditions": [
        { "direction": "ABOVE_MAX", "threshold": "38.0", "threshold_type": "NUMERIC", "units": "% of full flow", "sub_variable": "Steam Flow" },
        { "direction": "BELOW_MIN", "threshold": "22", "threshold_type": "NUMERIC", "units": "% of span", "sub_variable": "Drum Level" }
        ]
    }
    ]

    ### Example 6 — Multiple distinct trip levels → SEPARATE records
    Input:
    | Functional Unit | Allowable Value | Units |
    | Vessel Coolant Level - Low | ≥ 88.4 | in. |
    | Vessel Coolant Level - Low-Low | ≥ 40.1 | in. |

    Output:
    [
    {
        "variable": "Vessel Coolant Level",
        "function_name": "Vessel Coolant Level - Low",
        "source_text": "| Vessel Coolant Level - Low | ≥ 88.4 | in. |",
        "conditions": [
        { "direction": "BELOW_MIN", "threshold": "88.4", "threshold_type": "NUMERIC", "units": "in.", "sub_variable": null }
        ]
    },
    {
        "variable": "Vessel Coolant Level",
        "function_name": "Vessel Coolant Level - Low-Low",
        "source_text": "| Vessel Coolant Level - Low-Low | ≥ 40.1 | in. |",
        "conditions": [
        { "direction": "BELOW_MIN", "threshold": "40.1", "threshold_type": "NUMERIC", "units": "in.", "sub_variable": null }
        ]
    }
    ]

    ### Example 7 — Non-standard free-form unit
    Input:
    | Functional Unit | Allowable Value | Units |
    | Vent Stack Radiation - High | ≤ 4.7×10⁻³ | μCi/cc |

    Output:
    [
    {
        "variable": "Vent Stack Radiation",
        "function_name": "Vent Stack Radiation - High",
        "source_text": "| Vent Stack Radiation - High | ≤ 4.7×10⁻³ | μCi/cc |",
        "conditions": [
        { "direction": "ABOVE_MAX", "threshold": "4.7×10⁻³", "threshold_type": "NUMERIC", "units": "μCi/cc", "sub_variable": null }
        ]
    }
    ]

    ### Example 8 — Rows that must be IGNORED
    Input:
    | Condition | Required Action | Completion Time |
    | One channel inoperable | Restore channel to OPERABLE status | 6 hours |

    | Functional Unit | Trip Setpoint | Allowable Value | Units |
    | Manual Reactor Trip | N.A. | N.A. | N.A. |

    Output:
    []
    """

    response = client.messages.parse(
    model="claude-sonnet-5",
    max_tokens=524288,
    system=SYSTEM_PROMPT,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Extract all of the process document rules from the following text according to your instructions: {markdown}",
                }
            ],
        }
    ],
        output_format=setpoint_list,
)

    if not response.parsed_output:
            return []
    return response.parsed_output.root