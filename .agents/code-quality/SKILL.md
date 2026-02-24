---
name: Code Quality & Testing
description: Use these tools to ensure all code meets the project's architectural and quality standards before considering a task complete.
---

**Allowed Commands:**
- `npm run lint:fix`: Automatically resolve styling and standard linting errors.
- `npm run test:unit`: Execute the core logic test suite.
- `npm run test:e2e`: Run the end-to-end browser tests for UI validation.
**Guardrails:** If test coverage drops below 85% after modifying a module, you must automatically write the missing tests before marking the task as done.
