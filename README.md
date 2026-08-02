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
- `/open/<domain>/` — level-3 capability-domain page
- `/open/<domain>/<skill>/` — level-4 Skill detail page
- `/products/` — three clear entry points: open ecosystem, course, and private services
- `/course/` — SOIA Agent workflow course
- `/services/` — workflow and private expert delivery
- `/about/` — principles, boundaries, and public evidence
- `/en/...` — complete English route family with reciprocal language links

The level-3 and level-4 catalog is generated from the public
`soia-open-skills/docs/skills/README.md` source, rather than being maintained by
hand in multiple pages. Top-level Chinese and English pages remain curated so a
catalog refresh cannot erase their editorial narrative.

## Run locally

```bash
pnpm dev
```

Then open `http://127.0.0.1:4173/`.

The latest shareable design and information-architecture receipt is in
[`docs/open-design-review-2026-08-02.md`](docs/open-design-review-2026-08-02.md).

## Validate

```bash
pnpm test
```

To refresh the bilingual capability catalog from a local checkout of the public
source repository:

```bash
python3 scripts/generate_capability_pages.py --source-root <path-to-soia-open-skills>
```

The site has no runtime package dependency and uses shared HTML, CSS, and
JavaScript. It does not process payments or collect credentials. Latin webfonts
are self-hosted with OFL-1.1 license and provenance files under `assets/fonts/`.

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
