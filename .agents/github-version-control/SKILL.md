---
name: GitHub & Version Control
description: Use these commands to manage feature branches and prepare code for architectural review.
---

**Allowed Commands:**
- `git checkout -b feature/[ISSUE_ID]-[SHORT_DESC]`: Create a standardized feature branch.
- `git commit -m "[TYPE]: [DESCRIPTION]"`: Commit using conventional commit standards (e.g., feat, fix, chore).
- `gh pr create --title "[Title]" --body "[Description of architectural changes]"`: Open a pull request for the Tech Lead to review.
**Guardrails:** Never push directly to the `main` or `production` branches. All work must be submitted via a Pull Request.
