# SOIA Homepage

Canonical public source for the
[SOIA website](https://soia-team.github.io/).

The repository name describes the product. The organization-root GitHub Pages
repository, `soia-team/soia-team.github.io`, is kept as the deployment mirror so
the public URL remains `https://soia-team.github.io/`.

SOIA turns repeatable work into open Skills, multi-Skill workflows, installable
plugins, and role-based experts for Codex, Claude Code, and WorkBuddy.

## Routes

- `/` — brand and product overview
- `/open/` — eight public capability domains
- `/products/` — Skills, workflows, plugins, and experts
- `/course/` — SOIA Agent workflow course
- `/services/` — workflow and private expert delivery
- `/about/` — principles, boundaries, and public evidence

## Validate

```bash
python3 scripts/validate_site.py
```

The site is dependency-free and uses shared HTML, CSS, and JavaScript. It does
not process payments or collect credentials.

## Repository roles

- `soia-team/soia-homepage` — canonical website source and review history.
- `soia-team/soia-team.github.io` — root-domain GitHub Pages deployment mirror.

## License

MIT. See [LICENSE](./LICENSE).

## Reference boundary

The conversion path was informed by
[Kanvis Homepage](https://github.com/Kanvis-chen/kanvis-homepage), but the SOIA
site has original information architecture, copy, design, and code. Kanvis does
not declare a repository license as of 2026-08-01; see
[docs/kanvis-reference.md](./docs/kanvis-reference.md).
