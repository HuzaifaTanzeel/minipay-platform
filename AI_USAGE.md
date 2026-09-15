# AI usage

AI (Cursor) helped with wording and commands. I ran the commands, reviewed the files, and made every git commit and pull request myself.

## Tools

- Cursor

## What I used it for

- Drafting README-style docs (`README.md`, `SETUP.md`, `ARCHITECTURE.md`, `database/README.md`)
- Drafting commit messages and PR titles/bodies (I pasted and sent them)
- Asking which Docker / `psql` / git commands to run next

## How I checked the output

- Read the docs before committing
- Ran Compose, seed, and `psql` checks myself
- Did not commit `.env` or generated seed SQL

## Example of changing AI output

pgAdmin rejected `admin@minipay.local`. I switched `PGADMIN_EMAIL` to `admin@example.com` and recreated the container.

I will add more rows here if AI is used on the API, tests, or Kubernetes.
