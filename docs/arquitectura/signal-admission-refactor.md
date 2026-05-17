# Signal Admission Refactor

## REMOVE

```python
if not contains_financial_keywords(message):
    return NoSignal()
```

---

## REPLACE

```python
signals = extract_operational_signals(message)

if not signals:
    return AdmissionResult(
        status="UNKNOWN_SIGNAL",
        needs_evidence=True
    )

hypotheses = infer_candidate_domains(signals)

evidence_gaps = build_evidence_gaps(hypotheses)

return AdmissionResult(
    status="SIGNAL_DETECTED",
    signals=signals,
    hypotheses=hypotheses,
    evidence_gaps=evidence_gaps,
    needs_evidence=True
)
```

---

## SIGNAL EXTRACTION

```python
message = "bajó la producción y las ventas porque faltan operarios"

signals = [
    OperationalSignal("production_drop"),
    OperationalSignal("sales_drop"),
    OperationalSignal("staff_shortage")
]
```

---

## DOMAIN INFERENCE

```python
hypotheses = [
    "operational_bottleneck",
    "capacity_loss",
    "delivery_risk",
    "possible_margin_impact"
]
```

---

## INVALID EPISTEMOLOGY

```python
absence_of_financial_keyword == absence_of_signal
```

---

## VALID EPISTEMOLOGY

```python
signal_detected != diagnosis_confirmed
```
