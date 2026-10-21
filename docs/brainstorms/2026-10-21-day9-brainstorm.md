# Day 9 brainstorm: rule-based baseline auditor

## Problem
Week 2 needs a real auditor so evals stop running on stubs. The baseline is the
honest floor: closed rules over the five provisional conditions, no NLP claims,
so the LLM auditor (item 10) has something concrete to beat. It must emit the
spec-007 shape and survive the runner's verbatim evidence check.

## Options considered

### What the baseline may know
1. The five provisional mappings (code, phrase, stem) plus the spec-003 closed
   sentences. Chosen: exactly what the data was built from, nothing more.
2. A general negation/keyword NLP pass. Rejected: out of scope, unverifiable on
   this vocabulary, and it would hide what the baseline cannot do.

### Support rule
Priority per condition: affirmed closed sentence > negated closed sentence >
uncertain closed sentence > plain mention (phrase or stem, case-insensitive) >
absent. SUPPORTED only for affirmed or plain mention; negated, uncertain and
absent all yield UNSUPPORTED. Day-1/2 prose notes have no closed sentences, so
plain mention is what scores them (open question resolved here).

### Unknown claimed codes
Any claimed code outside the five mappings gets UNSUPPORTED: the baseline has
no rule that could support it. Documented as a limit, not a judgment.

### Evidence quotes
Volunteer quotes where they exist: the affirmed sentence for closed SUPPORTED,
the verbatim matched substring for prose SUPPORTED, the absent sentence for
negated UNSUPPORTED. They are all verbatim by construction, so they pass the
day-8 check and exercise it. Uncertain/absent verdicts carry no quote.

### Missed codes
For each table condition affirmed or mentioned whose code is not claimed, list
the code (table order). The baseline can only miss what it can recognize.

### Where the table lives
Duplicate the five mappings in baseline.py, intentionally isolated like the
goldset's copy. Sharing a private table across modules couples them; the day-9
decision entry records the duplication.

## Risks
On the goldset's closed sentences the baseline will look perfect; that says
little, because the same templates built the data. The eval note must say so.
Prose scoring is lexical and will break on paraphrase. All counts stay
provisional until the milestone 6 review.
