# Triage pseudocode

```text
FUNCTION triage(new_complaint):
    preserve original text
    validate required fields
    normalised_text = normalise(new_complaint.text)

    duplicate_candidates = compare_with_existing_records(normalised_text)
    route_suggestion = suggest_department(normalised_text)
    safety_flag = check_configured_safety_phrases(normalised_text)

    IF required information is missing OR confidence is below threshold:
        mark for manual review
        do not apply any suggestion

    RETURN candidates, route_suggestion, safety_flag, reasons

FUNCTION staff_review(complaint_id, action, reason, staff_id):
    verify complaint exists
    require explicit staff action
    IF action changes department:
        require selected department
    record action, reason, staff_id and timestamp in audit log
    update only the fields approved by staff
    RETURN updated record and audit event
```
