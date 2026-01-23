# Demo PRD Addendum — Hiring Vision Alignment

Extension to `demo-prd.txt` to frame Signal Capture as Stage 1 of AI Hiring Pipeline.

---

## Purpose

Transform the demo presentation from:
> "Can we capture signals?"

To:
> "This is the signal ingestion layer of an AI hiring system."

---

## New Demo Sections

### 1. Interview Context Panel (READ-ONLY)

**What it displays:**
```
Interview Type:    Technical Screening (Demo)
Role:              Backend Engineer
Interview Stage:   Initial Screening
Question:          1 of 3
Response Mode:     Video + Audio
```

**What it does NOT do:**
- No actual questions displayed
- No answer capture
- No timers
- No scoring

**Maps to long-term PRD:** Candidate Interview Engine

---

### 2. Session Integrity Signals (READ-ONLY)

**What it displays:**
```
Session Integrity Signals
─────────────────────────
Face continuously present:    Yes / No
Multiple faces detected:      Yes / No
Audio interruptions detected: Yes / No
```

**What it does NOT do:**
- No severity levels
- No explanations
- No proctoring actions

**Maps to long-term PRD:** Identity & Integrity, Anti-Cheating

---

### 3. Evaluation Pipeline Preview (DISABLED)

**What it displays:**
```
Evaluation Pipeline (Disabled in Demo)
──────────────────────────────────────
○ Speech-to-text         [Not active in demo]
○ Answer relevance       [Not active in demo]
○ Behavioral analysis    [Not active in demo]
○ Composite score        [Not active in demo]
```

**Purpose:** Vision anchor — prevents "where is the AI?" questions

---

### 4. Candidate Lifecycle Indicator

**What it displays:**
```
Candidate Lifecycle
[■ Capture] → [○ Analysis] → [○ Review] → [○ Shortlist]
```

**Purpose:** Shows demo as Stage 1 of pipeline

---

### 5. Terminology Updates

| Old Term | New Term |
|----------|----------|
| User ID | Candidate ID |
| Signal Capture Demo | AI Interview – Signal Capture Stage |
| Session | Interview Capture |
| Session Complete | Interview Capture Complete |

---

## Constraints Preserved

All original PRD constraints remain:
- ❌ No AI scoring
- ❌ No NLP / speech-to-text
- ❌ No emotion labels
- ❌ No cloud storage
- ❌ No authentication

---

## Success Criteria

A client viewing the demo should immediately understand:
1. This is a hiring interview system
2. Signal capture is Stage 1
3. Evaluation comes in future stages
4. Architecture supports the full vision
