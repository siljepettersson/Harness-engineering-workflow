# Feedback Loop

Feedback is an engineering artifact.

The loop is:

```text
question
    ↓
system output
    ↓
harness evaluation or user feedback
    ↓
failure capture
    ↓
hard case added to eval set
    ↓
future regression run
```

The system should not be described as automatically learning unless online learning or automated parameter updates are implemented.

High-value feedback should become eval cases or hard cases.
