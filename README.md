# Talk Greek Today

A static website for learners of Modern Greek.

## Built with

- [Eleventy](https://www.11ty.dev/) for the site and lesson pages
- Markdown and Nunjucks for content and templates
- [Pagefind](https://pagefind.app/) for client-side search
- GitHub Actions and GitHub Pages for deployment

## Run locally

Requires Node.js 24 or later.

```sh
npm ci
npm run dev
```

Open the local address shown by Eleventy, usually `http://localhost:8080`.

To create a production build:

```sh
npm run build
```

The generated site is written to `_site/`.

## Project structure

- `src/` — pages, lessons, templates, styles, and scripts
- `src/lessons/` — lesson Markdown files
- `src/_includes/` — shared Nunjucks templates
- `src/_data/` — course and vocabulary data
- `.github/workflows/pages.yml` — GitHub Pages deployment workflow

## GitHub Pages

Push the repository to GitHub, then set **Settings → Pages → Source** to **GitHub Actions**. The included workflow installs dependencies, builds the site, and publishes `_site/` whenever changes are pushed to `main`.

The build supports both a repository URL and a later custom domain.
