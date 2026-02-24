---
name: Database & Backend Management
description: Use these commands to manage local and remote database schemas, apply migrations, and generate types.
---

**Allowed Commands:**
- `supabase start`: Spin up the local development environment.
- `supabase db push`: Push local schema changes to the remote staging project.
- `supabase gen types typescript --local > types/supabase.ts`: Regenerate strictly typed database definitions after modifying the schema.
**Guardrails:** Never run `supabase db reset` on any environment other than local without explicit user approval.
