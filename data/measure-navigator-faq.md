# Measure Navigator FAQ - SYN-CBP MY2026

## Can an inpatient or emergency department BP reading count for CBP?
A reading taken during an acute inpatient stay or emergency department visit is excluded from numerator evidence in this synthetic prototype. Verify the place of service with CHK-READING-SETTING.
Sources: ["CHK-READING-SETTING","SYN.CBP.VS.015"]

## Why might a CBP result be numerator non-compliant?
Check the representative reading date, care setting, CPT II modifier, and both BP values. The decision tree evaluates each fact and carries unknown conditions forward.
Sources: ["CHK-READING-DATE-VALID","CHK-READING-SETTING","CHK-READING-MODIFIER","CHK-BP-CONTROLLED"]

## Why might a member be excluded from CBP?
The prototype evaluates ESRD diagnosis or procedures, pregnancy, hospice, non-acute inpatient care, and the combined frailty plus advanced illness path.
Sources: ["route_exclusions"]

## What happens when a fact is unknown?
The engine records an OPEN_CONDITION, states both possible outcomes, and continues through other relevant checks. The BP threshold requires both numeric values.
Sources: ["OPEN_CONDITION","CHK-BP-CONTROLLED"]
