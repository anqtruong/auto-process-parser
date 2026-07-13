# Section B Rationale — why every decision in SECTION_B_SPEC.md is what it is

Companion to `SECTION_B_SPEC.md`. Same section numbering. The spec says *what*;
this says *why*, so a future reader (or a design review with Dr. Hawrylak) can
challenge any decision on its actual merits instead of guessing at intent.

---

## B.0 Contract

**Why accept both Pydantic models and plain dicts.**
`extract_rules()` returns Pydantic `setpoint_record` objects, but Gate A lets a
human *edit* records before translation — and edited JSON re-enters as plain
dicts. If the translator only accepted Pydantic objects, every Gate A edit
would need re-validation plumbing before translation could run. Accepting both
(and normalizing internally) keeps Gate A simple. The cost is that Pydantic's
enum guarantees vanish for edited records — which is exactly why B.4 refuses to
default on an unrecognized direction instead of trusting the type system.

**Why three artifacts from one pass.**
PDL text, queue, and report could each be computed by separate walks over the
records. Separate walks can *disagree* — a bug fixed in one walk but not
another produces a report that doesn't describe the PDL next to it. Deriving
all three from a single pass makes disagreement structurally impossible: the
report is the translation's own bookkeeping, not a reconstruction of it.

**Why the accounting invariant is a hard failure, not a warning.**
The translator's worst possible failure is a record that silently vanishes —
the output file is smaller but perfectly valid, and nothing downstream can
detect the absence of a setpoint that was never emitted. For a nuclear Tech
Spec, a missing trip bound is worse than a crashed run. Warnings get ignored;
a raised `AccountingError` stops the pipeline until someone looks. This is the
cheap insurance against every "forgot a code path" bug at once.

**Why byte-identical determinism.**
Three reasons. (1) *Gate B economics*: the human re-reviews generated PDL only
when it changes; if harmless nondeterminism (dict ordering, set iteration)
reshuffles the file, every run looks changed and Gate B drowns. (2) *Git*: the
approved JSON and generated PDL commit together; a meaningful diff requires
deterministic output. (3) *Debuggability*: "same input, same output" turns
every bug report into a reproducible case. Timestamps are banned from the PDL
body because they break all three for zero benefit — the report is the right
home for run metadata.

**Why only two sanctioned digit rewrites.**
The whole pipeline inherits the extraction prompt's rule: never change a
digit. But PDL's lexer physically cannot accept `4.7×10⁻³` or (under the
current grammar) a bare `1420`, so two rewrites are unavoidable. Naming them
exhaustively — sci-notation expansion, trailing-dot suffix — means anything
else that changes a digit is by definition a bug, and Gate B's raw/emitted
columns make both sanctioned rewrites visible to the reviewer anyway.

## B.1 File layout

**Why a single module.** The translator is a few hundred lines of pure
functions with one entry point. Splitting it into packages would spread a
single audit surface across files; one module means one place to read when
someone asks "what exactly does the translator do to my numbers?"

**Why `variable_map.json` lives in `important_files/`.** It sits next to
`json_schema.py` because the two are the same kind of thing: contracts that
humans maintain and the pipeline obeys. Config-like data shouldn't hide among
code.

**Why the generated ANTLR target gets its own `tests/parsing/` directory.**
Generated code mixed with handwritten code invites accidental edits (which the
next regeneration silently destroys). Quarantining it also makes the
`skipif`-when-absent fallback in B.9 a simple directory check.

## B.2 Variable map

**Why a map exists at all.**
Two naming worlds share zero syntax: the NRC document says
`"Feed/Steam Flow Mismatch"`; the PDL lexer's `PV` token accepts one uppercase
letter followed by only lowercase/digits/dots, and (empirically, from the
lexer's rule ordering) the name must contain a dot or it tokenizes as `ID` and
the parse fails. *Something* must own the conversion, and it must be
inspectable.

**Why a lookup file instead of pure auto-naming.**
The name suggester (suggest_pv_name) is deterministic but has no judgment: `"Steam Flow"` from two
different systems both reduce to `steamflow`, silently merging two different
setpoints onto one monitored variable — undetectable downstream, and the exact
kind of error a safety pipeline exists to prevent. The map makes every name
assignment an explicit human decision, and gives the loader something to
*check* (collisions, regex validity). The suggester survives only as a
suggestion generator for queue entries, where a human approves before anything
is emitted.

**Why exact-match lookup, never fuzzy.**
Asymmetric failure costs. A fuzzy match that lands *wrong* cross-wires two
setpoints silently — expensive and invisible. An exact-match *miss* lands in
the review queue — cheap and visible; the human adds an alias entry and
re-runs. When one failure mode is invisible-catastrophic and the other is
visible-trivial, the design must always choose the visible one.

**Why local names are lowercase and the process prefix supplies the capital.**
The PV token demands an initial capital and forbids capitals afterwards. By
convention the prefix (`P1`) carries the capital and everything after the dot
stays lowercase — so the *whole* PV is valid by construction, and the map
loader can validate each half with a simple regex instead of reasoning about
concatenation.

**Why load-time validation is fail-fast (abort, not queue).**
A broken map poisons every record, not one. Translating 40 records against a
map with a collision produces 40 outputs of unknown trustworthiness. Refusing
to start is the only honest behavior, and map errors are developer errors
(fix the file), not document errors (review the record) — different audiences,
different mechanisms.

## B.3 Record classification

**Why the checks run in this exact order.**
Two properties. (1) *Most-fundamental-first*: a `MISSING_*` sentinel means the
extractor itself declared the record incomplete — no interpretation of its
shape can be trusted, so that check precedes everything. Empty conditions
means there is nothing to classify; FORMULA means the threshold can't be
expressed regardless of shape; only then is shape worth examining.
(2) *Stable reason codes*: a record with two defects must queue with the same
reason every run (determinism extends to the queue), so the order is part of
the contract, not an implementation detail.

**Why atomic translate-or-queue, never partial.**
Consider a two-sided record where the lower bound translates and the upper
bound fails. Emitting the lower bound alone produces a PDL file that *looks*
like it covers the variable while silently missing half its protection — and
the queue entry ("upper bound failed") reads as if the record is being handled.
Partial emission converts a visible failure into an invisible coverage gap.
Whole-record atomicity keeps the mental model binary: a record is either fully
live or fully in human hands.

**Why rule 5 merges "simple" and "two-sided" into one path.**
The dissertation (Fig 3.4, §3.1.1.2) expresses a range violation as two
independent `value` statements — there is no "range" construct in PDL. So a
two-sided record isn't a special shape needing special code; it's just two
legs that each become a statement. One code path means the N-leg
generalization costs nothing and there's no two-sided-specific bug surface.

**Why mixed legs queue instead of best-effort splitting.**
A record with one null leg and one named leg matches no schema shape — the
extractor's own prompt forbids it, so its *meaning* is unknown. Maybe the LLM
half-formed a conjunctive; maybe two records got merged. Guessing either way
fabricates a monitoring rule. Unknown meaning → human decides; that's the
queue's entire purpose.

## B.4 Direction → operator

**Why strict `<` / `>` and not `<=` / `>=`.**
The JSON schema defines both directions as "a reading *equal to* the threshold
is acceptable" — violation begins strictly beyond the bound. A PDL `value`
statement expresses the *alert* condition (fire when this is true), so the
operator must be true only in violation: strictly less / strictly greater.
This also matches the dissertation's own example (Fig 3.4: acceptable range
10–100 becomes `>100` and `<10`). Using `>=` would alert on a reading that the
Tech Spec explicitly permits.

**Why an unrecognized direction queues rather than defaults.**
A defaulted comparison direction is a *flipped safety bound* waiting to
happen — the single most dangerous silent error available to this translator.
The case is reachable because Gate A hands back human-edited dicts that
bypass Pydantic's enum. Two valid values, everything else is a question for a
human.

## B.5 Threshold normalization

**Why two layers.**
`parse_threshold` answers a question of *fact*: what number does this string
denote? `format_number` answers a question of *policy*: how must that number
be spelled so today's grammar accepts it? Facts don't change when the grammar
does; policy does. Isolating the policy in a ~5-line function is what makes
the pending Diego decision a five-minute edit instead of a re-audit of the
translator — the seam is the spec's main insurance against schedule risk.

**Why `Decimal` and never `float`.**
Binary floats cannot represent most decimal fractions: `4.7e-3` as a float is
`0.004699999...`, and formatting it back can change digits — violating the
never-change-a-digit rule in a way no reviewer would spot. `Decimal` does
exact base-10 arithmetic, so sci-notation expansion is a pure exponent shift
with provably unchanged digits.

**Why the accepted-input grammar is a closed list (plain decimal,
sci-notation, comma-stripping) and everything else queues.**
Every format the parser accepts is a format the tests must prove it converts
digit-perfectly. An open-ended "try to make sense of it" parser has an
unbounded test surface and fails by guessing. Tolerances (`±`), time
qualifiers, and ranges are *not* single numbers — converting them would mean
choosing which number to keep, which is a human judgment (Gate A), not a
string operation.

**Why the trailing-dot rule.**
In the current `lexerRules.g4`, `INT : [0-9]+` is declared before `DOUBLE`,
and ANTLR resolves equal-length matches by declaration order — so bare `1420`
lexes as `INT`, and the `value` rule demands `DOUBLE`: parse failure. `1420.`
matches `DOUBLE` by the longest-match rule. It's a workaround for a grammar
quirk, which is precisely why it lives in the policy layer where the Diego
decision can delete it.

**Why negatives queue.**
No token in the grammar can carry a minus sign into the number position — a
leading `-` lexes as the `SUB` operator, which `value : PV OPERATOR DOUBLE ;`
has no slot for. The translator cannot emit what the grammar cannot parse;
until the grammar changes, honesty means queueing.

**Why digit-preservation (pass plain decimals through verbatim).**
Round-tripping every threshold through `Decimal` and back would be simpler
code, but reformatting can normalize away the document's own notation
(`38.0` → `38`), and precision notation is *information* in an engineering
document — `38.0` asserts tenths precision. Passing already-plain inputs
through untouched also makes Gate B's raw/emitted columns mostly identical,
so the reviewer's attention lands only on the rows where something actually
changed.

## B.6 Statement emission

**Why the output format is specified to the byte (single spaces, one
statement per line).**
Whitespace is semantically irrelevant to ANTLR but not to determinism: two
"equivalent" spellings are different bytes, different git diffs, and different
Gate B re-reviews. Fixing the format to the byte makes "did anything change?"
answerable by hash.

**Why values first, then multipleMatch.**
Not a style choice — `masterRule` in `MonitoringNeeds.g4` is an ordered
sequence (`status* value* multiple* ...`), so a `multipleMatch` before the
last `value` is a parse error. Within each group, input order is preserved
because any re-sorting would need a defined sort key (more spec surface) and
would scramble the record→statement correspondence Gate B relies on.

**Why provenance rides in comments.**
PDL has no metadata slot — no field for a trip name, units, or source row.
The grammar's `COMMENT : '/*' .*? '*/' -> skip ;` makes comments free: carried
in the file, invisible to the parser. Without them, Gate B's reviewer would be
matching anonymous `value` statements back to table rows by hand.

**Why comment sanitization is non-negotiable.**
`source_text` is verbatim OCR output — untrusted bytes. If it ever contains
`*/`, the comment terminates early and the remainder lands in the token
stream: a parse error at best, and in the worst case tokens that *parse as a
statement*. That is an injection vulnerability, mechanically identical to SQL
injection, sitting inside a safety file. Escaping `*/` → `* /` costs one line.

**Why the version header.**
Gate B re-reviews when "the translator changed" — but that's only decidable if
the output *says* which translator produced it. The header (version + document
ID + counts) makes every PDL file self-describing: given the file alone, you
can tell whether it's stale relative to the current translator and whether its
counts match its report.

**Why empty input still emits a header-only file.**
"Ran and found nothing" and "never ran" must be distinguishable artifacts. A
header-only file with `0 translated / 0 queued` is positive evidence the
document was processed; an absent file is silence. (It also gives the tests a
trivially checkable fixture for the pipeline's do-nothing path.)

## B.7 Queue and report

**Why a closed set of reason codes.**
The Gate A UI, tests, and metrics all need to `switch` on reasons. Free-text
reasons drift into unmatchable variants ("missing units", "units missing",
"no unit"). A closed enum keeps every consumer exhaustive — and adding a new
code is a deliberate, reviewable act rather than a typo.

**Why `suggested_pv` on unmapped-variable entries.**
The resolution workflow should be one human judgment ("yes, that name is
fine") plus one paste into `variable_map.json`. Without the suggestion, the
human must also *invent* a lexer-legal name — the mechanical part the suggester
already does better. The suggestion is machine-generated but human-ratified,
preserving the B.2 rule that the suggester never emits directly.

**Why the report covers every record, both outcomes.**
The report is the audit trail: for any record you can ask "what happened to
it?" and get an answer without diffing files. The raw/emitted threshold
pairs exist because normalization is the only place digits legitimately
change — so it's the place a reviewer must be able to watch.

**Why one unified row type with the queue as a view (revised 2026-07-13).**
The original design had two types — `QueueEntry` and `ReportRow` — and a
queued record appeared in both lists with four fields duplicated. An's review
caught the smell: duplicated truth can drift, the field split was arbitrary
(why did only queue entries carry `source_text`?), and `reason`/`detail`
didn't say what they held. Now every row carries the full context
(`variable`, `source_text`, `suggested_pv`) plus renamed `reason_code`
(machine-readable enum) and `explanation` (human-readable), and
`TranslationResult.queue` is a filtered view of the report rather than a
second list. Cost: bulkier report files (source text on every row). Gain: one
schema for both Section C gates, no cross-list consistency to maintain, and
the accounting invariant reads directly off one list.

**Why `translate_records()` is a pure function with no I/O.**
Testability (call it with literals, assert on strings — no tmp-dir fixtures),
reusability (Streamlit Gate B can call it live without touching disk), and
separation of concerns: *where* files go is a Section C pipeline decision that
shouldn't be baked into the translation logic.

## B.8 Test plan

**Why the golden tests are the extraction prompt's own eight examples.**
They're already input/output pairs, already human-reviewed, and already the
canonical definition of what the extractor produces — so using them keeps the
extractor's spec and the translator's spec pinned to the same examples. If
the prompt's schema ever changes, these tests break loudly, which is exactly
the alarm you want.

**Why each edge test exists.**
Every edge test is one failure mode identified during design review, pinned so
it can't regress: sci-notation (digit-exact expansion), `1,941` (comma
handling), `38.0` (precision preservation), `*/` in source text (comment
injection), duplicate map values (collision detection), mixed legs (shape
policy), 3-leg conjunctive (no hardcoded pair), interleaved shapes (ordering),
monkeypatched imbalance (the invariant actually raises). The determinism test
(translate twice, byte-equal) catches the whole class of dict/set-ordering
bugs with one assertion.

## B.9 Parse-check harness

**Why a Python ANTLR target instead of `grun`.**
`grun` is interactive (GUI trees, human eyeballs) and its exit status doesn't
reflect parse errors usefully — fine for exploration, useless for CI. A
generated Python parser makes "does this parse?" a function call inside
pytest, on every test, forever.

**Why the error listener must raise.**
ANTLR's *default* error strategy prints the error to stderr and then
*recovers and continues*, returning a tree as if things were fine. A test
that just calls the parser would pass on garbage. `BailErrorStrategy` (or a
raising listener) converts the first syntax error into an exception — turning
the parser into an oracle a test can trust.

**Why the `skipif` fallback exists but the harness stays in the exit
criterion.**
The harness is the one Section B step with environment risk (Java version
friction, per the ANTLR readme). `skipif` keeps that risk from blocking the
pure-Python 90% of the work — but if it were *optional*, "all tests pass"
could mean "nothing was ever parse-checked," which would gut the section's
guarantee. So: skippable day-to-day, required to call Section B done.

## B.10 Build order

**Why pure functions first.**
`parse_threshold`/`format_number` have zero dependencies, seconds-long test
loops, and sit exactly where unknown real-world input formats will surface —
the highest-information work per hour. Classification/emission (step 3) needs
one uninterrupted block because its pieces reference each other; the map
(step 2) and bookkeeping (step 4) are separable small sessions. The harness
is listed last as the dependency order, but doing its 30-minute feasibility
check *early* is smart schedule management — it's the only step that can
reveal a blocked environment.

**Why the exit criterion names `format_number`'s rewrite time.**
"The Diego decision changes one function in five minutes" is the measurable
form of the seam-isolation promise in B.5. If, at the end, the rewrite would
take longer than that, the seam leaked into other code — and the exit
criterion catches the leak before the meeting does.

## Watch-outs

**Why comment sanitization is singled out.** It's the only hazard that gets
*worse* with real data: the golden examples contain no `*/`, so nothing forces
the escape logic to exist until a real OCR'd document breaks the file — in
production, after the tests all passed.

**Why comments attach to statements, not records.** As specced, a record's
statements never split across the values/multipleMatch boundary, so
record-level comments work today. But that's an *invariant of the current
rules*, not of the design — if a future shape ever splits, record-attached
comments would drift away from their statements. Attaching to statements (and
duplicating when needed) is the version that stays correct under change.
