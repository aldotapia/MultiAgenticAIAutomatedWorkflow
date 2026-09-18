# Cross-agent issues (append; mark [RESOLVED] when fixed)

## ISSUE-001 — evaluation row indices vs dates [OPEN] (owner: user; audit: a02)
User-specified eval rows 265:1360. File has 14,610 rows = WY1949–WY1988 if start 1948-10-01; PET climatology peaks at
cycle row ~266 and is minimal at ~102, consistent with an Oct-1 start. Then rows 265:1360 = 1949-06-23..1952-06-21,
not Oct 1948–Sep 1951 (which would be rows 0:1095). Active config follows the user's index. To switch:
`periods.definition: dates` in config/project.yaml.
