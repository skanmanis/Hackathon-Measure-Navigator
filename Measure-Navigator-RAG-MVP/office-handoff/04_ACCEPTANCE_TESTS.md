# Measure Navigator Acceptance Tests

Run these tests after office sources are indexed. Expected answers must be validated against the office-approved MY2026 content rather than the sample document.

## A. Startup and UI

- Exactly one local server listens on the approved port.
- The Navigator page loads with Coastal Teal styling.
- No “Explain SQL logic” or other developer-oriented shortcut appears.
- The evidence panel is hidden when no relevant evidence exists.
- The FAQ page uses the same design system and permits download.
- The trace opens and aligns with the main conversation layout.

## B. CBP monthly regression

### Test B1 — Single reading

User:

```text
A member shows compliance in CBP for the last eight months and now shows noncompliance in this month’s run. What is the reason?
```

Expected first follow-up: formally request the latest BP reading without requesting identifiers.

User:

```text
115 over 79
```

Expected behavior:

- normalize to `115/79`;
- recognize one reading;
- do not ask same-date versus different-date;
- ask for the care setting.

User:

```text
outpatient
```

Expected behavior:

- state that 115/79 is within the retrieved control range;
- state that outpatient is accepted only if supported by indexed MY2026 evidence;
- state that the supplied BP evidence appears compliant;
- offer continued investigation into data/process causes.

### Test B2 — Two readings

User supplies:

```text
142/72 and 128/84
```

Expected behavior: ask whether the readings occurred on the same or different dates before applying the selection rule.

### Test B3 — Deep investigation

Continue from B1. Confirm that the workflow asks one question at a time and covers:

1. reading data source;
2. receipt of prior qualifying data in the current run;
3. adjusted/reversed/replaced claim;
4. later BP readings and their values when applicable;
5. POS/source acceptability, including independent laboratory/POS 81 review;
6. BP reporting code;
7. availability of the result value;
8. numerator staging/loading.

### Test B4 — Unknown facts

Answer “I don’t know” to at least two deep-investigation questions.

Expected final response:

- says the available path is complete;
- lists those unknown facts as possible explanations;
- invites the user to return with the missing results;
- does not repeat the generic source paragraph;
- does not continue looping.

### Test B5 — All checks pass

Answer all deep-investigation checks with values that do not identify a failure.

Expected final response: no confirmed failure point and a recommendation to compare current-run source/processing lineage with the prior compliant run.

## C. Feedback controls

- Selecting one feedback action disables every other action in that response group.
- “Useful — dig deeper” acknowledges the choice and asks the next unresolved condition.
- “Continue investigation” advances the same session.
- “This didn’t solve it” acknowledges the result and checks the next permitted condition.
- “This solved it” closes the session cleanly.
- Completed investigations do not continue to offer deeper actions.

## D. Retrieval relevance

- A one-reading CBP scenario does not display the multiple-readings section unless it becomes relevant.
- A direct specification question retrieves the correct specification section.
- No FAQ is displayed below the approved threshold.
- Measure and measurement-year filters prevent cross-measure/year leakage.
- VSD/MLD questions retrieve the governed workbook section.
- SQL-derived evidence retains object/file/line lineage internally.

## E. Authority and conflict

Create a controlled test where SQL-derived behavior differs from the specification.

Expected behavior:

- follow the specification;
- state that implementation evidence may differ and requires code review;
- never claim that SQL was executed;
- do not expose raw internal prompts.

## F. Failure behavior

- Missing office path produces a clear validation error before indexing.
- Unsupported/password-protected file is reported and skipped.
- Missing SQL dependency is listed as unresolved, not invented.
- No sufficiently relevant evidence produces an insufficient-evidence response.
- LLM unavailability uses the deterministic fallback without changing workflow state.

## G. Completion evidence

Record:

- test command and pass count;
- indexed files and chunk count;
- parsing errors;
- unresolved SQL dependencies;
- retrieval backend and LLM mode;
- fixed UI URL;
- known limitations;
- confirmation that office sources, vector indexes, and secrets are excluded from public Git.
