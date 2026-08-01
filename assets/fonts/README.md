# Web font provenance

The public site self-hosts Latin variable-font subsets so typography does not
depend on a third-party runtime CDN. Chinese text falls back to the operating
system's `PingFang SC` or `Microsoft YaHei`, avoiding a multi-megabyte CJK webfont.

All three files were obtained from Fontsource variable-font packages at version
`5.3.0` on 2026-08-02. Each package includes its own OFL-1.1 license text in this
directory.

| Local file | Upstream | SHA-256 |
|---|---|---|
| `public-sans-latin.woff2` | [Public Sans](https://github.com/uswds/public-sans) via `@fontsource-variable/public-sans@5.3.0` | `5ed4d31c988e73b258894244f209069ebe77dc7e564861954b21198b6de90d68` |
| `space-grotesk-latin.woff2` | [Space Grotesk](https://github.com/floriankarsten/space-grotesk) via `@fontsource-variable/space-grotesk@5.3.0` | `0640890476fc1198ab4de571fb658de443c4d85b66466ec09534a8737ab1ce9d` |
| `jetbrains-mono-latin.woff2` | [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono) via `@fontsource-variable/jetbrains-mono@5.3.0` | `18be452724bfdc236c074ca94a249a7f41a86752c7d04ab258ce9ed5651f6a7e` |

The site uses Public Sans for body and interface copy, Space Grotesk for display
headings at weights no higher than 700, and JetBrains Mono for labels, receipts,
commands, and metadata.
