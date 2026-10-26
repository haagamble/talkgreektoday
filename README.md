# Talk Greek Today

A static Modern Greek learning website built with Eleventy, Markdown, and Pagefind.

## Work locally

Install Node.js 24 or later, then run:

```sh
npm ci
npm run build
npm run dev
```

Open the local URL printed by Eleventy (usually http://localhost:8080). The build command generates both the website and search index. After changing lessons, run the build again to refresh search. Output lives in `_site/` and should not be edited directly.

## Write a lesson

Edit `src/lessons/*.md`. Each file begins with a title, category, subject tags, summary, and permanent URL. Copy an existing file to start a new lesson and use a unique URL. The library and search index update on build.

```yaml
layout: lesson.njk
tags: lesson
title: Colours
greekTitle: Χρώματα
category: Topics
subjects: [Colours, Descriptions]
summary: Learn colours and use them in simple descriptions.
permalink: /lessons/colours/
```

## Organization and navigation

- `/beginner-course/` is the ordered learning path. Edit `src/_data/beginnerCourse.json` to add or reorder steps. A step automatically becomes clickable when a lesson with its URL exists. Missing steps display “Coming soon”; next/previous navigation does not skip them.
- `/lessons/` is a compact alphabetical library with category, subject, and text filters. The quick search covers titles, summaries, and subject tags. The separate Search page covers full lesson content, including all three categories.
- Categories are exactly **Grammar**, **Topics**, and **Reference**. Subject tags such as `Nouns`, `Time`, and `Tenses` describe content independently of category or course membership. A level field can be added independently later; standalone material is not automatically labeled intermediate.
- Beginner course pages have only previous/next course links and a return to the course list after their exercises. They do not show related recommendations.
- Standalone pages may have `relatedLessons: ["/lessons/tell-time/"]`. Choose these URLs deliberately; the template shows at most two. Add a new related lesson by editing this list, not the template.
- The homepage shows two learning routes and at most three featured lessons. Add `featured: 1`, `featured: 2`, or `featured: 3` to select and order them. New lessons do not automatically add homepage cards.
- General lesson numbers have been removed. Course numbers come only from the course plan, so adding a reference or topic does not renumber the course.

Run `node scripts/check-organization.mjs` after building to verify homepage limits, course navigation, planned steps, recommendations, and combined library filters. Pass a path prefix such as `/greek` when checking a prefixed build.

Use ordinary Markdown for headings, paragraphs, lists, and links. Current converted lessons also use HTML for tables and Greek-language examples. Answers use:

Practice should reuse taught vocabulary and grammar in new combinations, rather than repeat the lesson's example sentences. Change the person, noun, time, or sentence type without introducing unexplained material. The first lesson, Nouns and gender, is the exception: direct vocabulary recall is appropriate there. Keep ten translation questions with matching grouped answers unless a lesson needs a different format.

Introduce several new words or expressions in a short list (`**Greek** — English`) before the chart or examples where they appear. A single new word can use one short sentence. A vocabulary chart already introduces its entries, so do not duplicate it with a list. Put usage notes and exceptions after the relevant chart or examples when they benefit from that context. Keep grammar explanations where they are needed to understand the examples. Maintain `src/_data/beginnerVocabulary.json` when adding or changing beginner vocabulary; lesson IDs match the course URL slugs and numbering stays in `beginnerCourse.json`.

Pair translated examples in a shared block so the Greek and English stay visually connected:

```html
<div class="example">
<p class="greek-line" lang="el">Σήμερα είναι Τρίτη.</p>
<p class="translation-line" lang="en">Today is Tuesday.</p>
</div>
```

Use `<strong>` around the particular phrase being taught, rather than the entire example. Exercise answers use:

```html
<details data-pagefind-ignore>
<summary>Show answers</summary>
<ol>
<li>The first answer.</li>
<li>The second answer.</li>
</ol>
</details>
```

Answer text is excluded from search previews so search does not reveal solutions. Greek examples use `lang="el"` to help assistive technology pronounce them correctly. Search runs locally in visitors' browsers. Accent-insensitive Greek matching has not yet been verified in a browser.

You can still supply Word documents or plain text drafts for conversion. Markdown is the easiest long-term source because it can be updated directly without reimporting. The originals in `lessons-word/` remain untouched and are ignored by Git. `scripts/import_word.py` is a historical one-time importer. Do not rerun it: it overwrites the three edited lessons and uses the original metadata format.

## Verb overview series

The two `verb-tenses-with-*.md` lessons use a shared structure: aspect and principal forms, eight active tenses side by side, optional six-person conjugations, subjunctives, commands, other active forms, and ten translations with hidden answers. Each tense gets one contextual example instead of several repeated explanations. Mediopassive paradigms and the long idiom lists from the drafts are omitted from these active-verb overviews.

`scripts/create_verb_overviews.py` prepared these two pages from the Word drafts and editorial data. It is a historical one-time generator; do not rerun it, because it overwrites the revised pages and uses the original metadata format. Edit or copy the Markdown for subsequent revisions and new verbs. Word originals remain unchanged.

Core forms were checked against the Centre for the Greek Language entries for [ανοίγω](https://www.greek-language.gr/greekLang/modern_greek/tools/lexica/search.html?lq=ανοίγω) and [βλέπω](https://www.greek-language.gr/greekLang/modern_greek/tools/lexica/triantafyllides/search.html?lq=βλέπω). This is not a native-speaker review of every example.

## Initial content decisions

- Imported all three lessons and their tables in document order.
- Replaced copied quiz controls and visible feedback with grouped, collapsed answer sections.
- Added suggested translations where the Word drafts contained an answer button without answer text.
- Omitted the nonfunctional copied clock widget; retained the written time explanations and exercises.
- This was a content conversion, not a full independent Greek-language review. Review the lesson explanations and suggested answers before sharing widely.
- No videos have been supplied yet; the Videos page clearly describes the forthcoming collection.
- Fonts are loaded from Google Fonts, with local fallback fonts if unavailable.

## GitHub Pages

Create a public GitHub repository, add these source files, and push to `main`. In the repository's Settings → Pages, select **GitHub Actions** as the publishing source. The included workflow installs dependencies, builds the site and search, and publishes `_site/`.

The workflow obtains the base path from GitHub Pages, supporting both repository URLs and a later custom domain. To check a project path locally in PowerShell:

```powershell
$env:SITE_PATH_PREFIX = '/greek'
npm run build
Remove-Item Env:SITE_PATH_PREFIX
```

When you buy a domain, configure it in GitHub Pages and at your domain registrar; verify the domain and enable HTTPS. Rebuild after changing the domain configuration.

Nothing has been pushed or published automatically from this workspace.
