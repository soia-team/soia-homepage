# SOIA Homepage

Public source repository for the SOIA project website at
[https://soia-team.github.io/](https://soia-team.github.io/).

The first release is a static project preview: it explains the open capability
stack, delivery boundaries, and product-validation roadmap. It does not process
payments or collect credentials. The commercial site can move to SOIA's own
domain and server after ICP filing is complete.

## Validate

```bash
python3 scripts/validate_site.py
```

Open `index.html` directly for a local preview. Pushing `main` publishes the
same static files through GitHub Pages.

## License

MIT. See [LICENSE](./LICENSE).

## Reference boundary

The product ladder and evidence-first information architecture were informed by
[Kanvis Homepage](https://github.com/Kanvis-chen/kanvis-homepage). Its repository
does not declare a license as of 2026-08-01, so this project does not copy its
HTML, CSS, JavaScript, wording, branding, or assets. See
[docs/kanvis-reference.md](./docs/kanvis-reference.md).
