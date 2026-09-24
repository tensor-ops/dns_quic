# Dataset Validation Report

**Generated**: 2026-09-10
**Specification**: `dataset/README.md` (Section 19 & 23)

## Summary

All **13 automated validation checks passed successfully**.

| Check | Status | Description |
|---|:---:|---|
| No missing flow IDs in packets | ✅ Passed | Section 19 rule compliance |
| No duplicate flow IDs in flows table | ✅ Passed | Section 19 rule compliance |
| Every flow has exactly one label | ✅ Passed | Section 19 rule compliance |
| Every packet belongs to a known flow | ✅ Passed | Section 19 rule compliance |
| Packet indices are sequential (0-based) per flow | ✅ Passed | Section 19 rule compliance |
| Timestamps are non-negative | ✅ Passed | Section 19 rule compliance |
| Packet sizes ≥ 40 bytes | ✅ Passed | Section 19 rule compliance |
| Packet sizes ≤ 1460 bytes | ✅ Passed | Section 19 rule compliance |
| No NaN values in ML features | ✅ Passed | Section 19 rule compliance |
| No Inf values in ML features | ✅ Passed | Section 19 rule compliance |
| All 5 traffic classes are present | ✅ Passed | Section 19 rule compliance |
| Train and test captures are disjoint | ✅ Passed | Section 19 rule compliance |
| All generated data can be traced back to PCAPs | ✅ Passed | Section 19 rule compliance |

## Traffic Class Summary

| Class ID | Class Label | Protocol | Packet Count | Total Bytes | Split |
|:---:|---|:---:|:---:|:---:|:---:|
| 0 | `HTTPS_WEB` | TCP | 120 | 109,032 B | `train` |
| 1 | `HTTP3_WEB` | QUIC | 110 | 94,891 B | `train` |
| 2 | `DOH` | TCP | 8 | 1,672 B | `train` |
| 3 | `DOH3` | QUIC | 7 | 1,351 B | `validation` |
| 4 | `DOQ` | QUIC | 6 | 1,131 B | `test` |
