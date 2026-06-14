# Social Media Mental Health Risk Analyzer - Input Validation Audit Report

This report outlines all input validation rules, combined metrics constraints, journal text safety checks, and soft warning limits implemented across both the backend and frontend of the system.

## 1. Numeric Validation Limits

| Metric | Valid Range | Backend Validation | Frontend Validation | Action on Failure |
| :--- | :--- | :--- | :--- | :--- |
| **Age** | 15 – 60 | `15 <= age <= 60` | `min="15" max="60"` | Block submission, show toast error |
| **Sleep Hours** | 0 – 24 | `0.0 <= sleep <= 24.0` | Range Slider / input boundary check | Block submission, show toast error |
| **Study Hours** | 0 – 24 | `0.0 <= study <= 24.0` | Range Slider / input boundary check | Block submission, show toast error |
| **Work Hours** | 0 – 24 | `0.0 <= work <= 24.0` | Range Slider / input boundary check | Block submission, show toast error |
| **Screen Time** | 0 – 24 | `0.0 <= screen <= 24.0` | Range Slider / input boundary check | Block submission, show toast error |

## 2. Combined Workload Validation

* **Constraint**: `Study Hours + Work Hours <= 24`
* **Purpose**: Restrict the sum of active study and work hours to a realistic 24-hour day limit.
* **Failure Handling**:
  - Frontend: Validated on form submission. Shows toast: `"Combined study hours and work hours cannot exceed 24 hours."` and blocks API call.
  - Backend: Validated in JSON validation middleware layer with `400 Bad Request`.

## 3. Lexical Journal Validation Constraints

To prevent model dilution and ensure meaningful Text Analysis Model inference, the journal text is passed through the following safety filters:

1. **Length Constraints**:
   - Minimum character length: **30 characters**.
   - Minimum word count: **5 words** (whitespace split).
2. **Numeric-Only Block**:
   - Rejects text consisting of digits only (e.g., `"12345 67890 12345"`).
   - Regex check: strips non-alphanumeric chars; blocks if digits are present but no letters.
3. **Symbols-Only Block**:
   - Rejects text consisting of symbols or punctuation only (e.g., `"!@# $%^ &*() _+"`).
   - Blocks if stripped alphanumeric characters length is 0.
4. **Keyboard Spam Filter**:
   - Rejects long consecutive character repetitions (e.g., `"aaaa"`, `"xxxx"`, `"!!!!"`).
   - Regex check: matches any character repeated 4 or more times consecutively: `/(.)\1{3,}/`.
5. **Repeated Nonsense Token Block**:
   - Rejects consecutive word repetitions of 3 or more times (e.g., `"blah blah blah"`).
   - Regex check: `/\b(\w+)\b\s+\1\s+\1/i`.
   - Rejects repeated word patterns: blocks if overall unique words ratio in journal text is `< 35%` (for texts $\ge 5$ words).
6. **Gibberish Detection**:
   - Rejects nonsense inputs using consonant cluster analysis, vowel density checks, and English stopwords dictionary filters.

## 4. Soft Warnings (Alert Only)

To guide the student while preserving realistic outliers, the following values trigger a non-blocking toast alert warning without preventing API submission:

* **Sleep Hours > 16**: Warning toast: `"Notice: Sleep duration is unusually high (over 16 hours)."`
* **Study Hours > 16**: Warning toast: `"Notice: Study duration is unusually high (over 16 hours)."`
* **Work Hours > 16**: Warning toast: `"Notice: Work duration is unusually high (over 16 hours)."`
* **Screen Time > 18**: Warning toast: `"Notice: Screen time is unusually high (over 18 hours)."`
