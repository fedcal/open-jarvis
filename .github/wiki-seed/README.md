# Wiki seed

This directory contains the **initial pages** for the GitHub Wiki of `fedcal/open-jarvis`.

GitHub does not allow programmatic creation of the very first wiki page. Once you create it manually, the rest can be pushed via git.

## How to publish the wiki

1. Open <https://github.com/fedcal/open-jarvis/wiki> and click **"Create the first page"**.
2. Paste the content of [`Home.md`](./Home.md) and save.
3. From your terminal:

   ```bash
   cd /tmp
   git clone git@github.com:fedcal/open-jarvis.wiki.git
   cd open-jarvis.wiki
   cp /path/to/repo/.github/wiki-seed/Home.md ./Home.md
   cp /path/to/repo/.github/wiki-seed/Home-EN.md ./Home-EN.md
   git add -A
   git commit -m "docs(wiki): seed bilingual home"
   git push
   ```

## Files

| File | Purpose |
|---|---|
| [`Home.md`](./Home.md) | Italian wiki home (default) |
| [`Home-EN.md`](./Home-EN.md) | English wiki home |
