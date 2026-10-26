import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const prefix = (process.argv[2] || '').replace(/\/$/, '');
const read = name => fs.readFileSync(`_site/${name}`, 'utf8');
const course = JSON.parse(fs.readFileSync('src/_data/beginnerCourse.json', 'utf8'));
const home = read('index.html');
const library = read('lessons/index.html');
const coursePage = read('beginner-course/index.html');
const expectedCategories = new Set(['Grammar', 'Topics', 'Reference']);
assert.equal((home.match(/class="card"/g) || []).length, 3, 'Homepage must show only three featured cards.');
assert(home.includes(`${prefix}/beginner-course/`));
assert(home.includes(`${prefix}/lessons/`));
const planned = course.filter(step => !fs.existsSync(`_site${step.url}index.html`));
assert.equal((coursePage.match(/class="status-label"/g) || []).length, planned.length, 'Unavailable course steps must be marked planned.');

const available = course.filter(step => fs.existsSync(`_site${step.url}index.html`));
for (const step of available) {
  const page = read(`${step.url.slice(1)}index.html`);
  const nav = page.match(/<nav class="course-navigation"[\s\S]*?<\/nav>/)?.[0];
  assert(nav, `${step.title}: course navigation is missing.`);
  assert(!page.includes('class="related"'), `${step.title}: beginner pages must not have related recommendations.`);
  const index = course.indexOf(step);
  const expected = [course[index-1], course[index+1]].filter(other => other && fs.existsSync(`_site${other.url}index.html`)).map(other => prefix + other.url);
  const links = [...nav.matchAll(/href="([^"]+)"/g)].map(match => match[1]);
  assert.deepEqual(links, [...expected, `${prefix}/beginner-course/`], step.title);
  assert(page.includes('data-pagefind-body'), `${step.title}: lesson must remain searchable.`);
}
for (const slug of ['tell-time', 'days-of-the-week', 'imperative', 'verb-tenses-with-open', 'verb-tenses-with-see']) {
  const page = read(`lessons/${slug}/index.html`);
  assert(!page.includes('class="course-navigation"'), slug);
  const related = page.match(/<nav class="related"[\s\S]*?<\/nav>/)?.[0];
  assert(related, `${slug}: curated recommendations missing.`);
  assert([...related.matchAll(/href=/g)].length <= 2, slug);
}
planned.forEach(step => assert(!coursePage.includes(`href="${prefix}${step.url}"`)));

// Exercise the actual browser filtering code with DOM elements from the generated library.
class Element {
  constructor(dataset = {}) { this.dataset = dataset; this.events = {}; this.value = ''; this.hidden = false; this.classList = { toggle() {} }; }
  addEventListener(event, callback) { this.events[event] = callback; }
  setAttribute(name, value) { this[name] = value; }
  append(child) { (this.children ||= []).push(child); }
  fire(event) { this.events[event]?.(); }
}
const decode = value => value.replace(/&quot;/g, '"').replace(/&#39;|&#x27;/g, "'").replace(/&amp;/g, '&');
const rows = [...library.matchAll(/<li class="lesson-row"[^>]*>/g)].map(([tag]) => {
  const value = name => decode(tag.match(new RegExp(`data-${name}="([^"]*)"`))?.[1] || '');
  return new Element({ category: value('category'), subjects: value('subjects'), search: value('search') });
});
const totalLessons = fs.readdirSync('src/lessons').filter(name => name.endsWith('.md')).length;
assert.equal(rows.length, totalLessons);
rows.forEach(row => assert(expectedCategories.has(row.dataset.category), row.dataset.category));
const controls = new Element(); controls.hidden = true;
const query = new Element();
const subject = new Element(); subject.value = 'all';
const count = new Element();
const empty = new Element();
const buttons = ['all', 'Grammar', 'Topics', 'Reference'].map(filter => new Element({ filter }));
const nodes = { '[data-library-controls]': controls, '#library-query': query, '#library-subject': subject, '#library-count': count, '#library-empty': empty };
const document = {
  querySelector: selector => nodes[selector] || null,
  querySelectorAll: selector => selector === '.lesson-row' ? rows : selector === '[data-filter]' ? buttons : [],
  createElement: () => new Element()
};
vm.runInNewContext(fs.readFileSync('src/assets/site.js', 'utf8'), { document });
const shown = () => rows.filter(row => !row.hidden);
assert.equal(shown().length, totalLessons);
assert.equal(controls.hidden, false);
buttons[3].fire('click'); assert.equal(shown().length, rows.filter(row => row.dataset.category === 'Reference').length);
query.value = '\u03b1\u03bd\u03bf\u03b9\u03b3\u03c9'; query.fire('input'); assert.equal(shown().length, 1, 'Unaccented Greek search');
query.value = '\u0392\u039b\u0388\u03a0\u03a9'; query.fire('input'); assert.equal(shown().length, 1, 'Uppercase Greek search');
query.value = ''; buttons[1].fire('click'); subject.value = 'Nouns'; subject.fire('change'); assert.equal(shown().length, rows.filter(row => row.dataset.category === 'Grammar' && row.dataset.subjects.split('|').includes('Nouns')).length, 'Category plus subject');
query.value = 'no-such-subject'; query.fire('input'); assert.equal(shown().length, 0); assert.equal(empty.hidden, false);
query.value = ''; subject.value = 'all'; buttons[0].fire('click'); assert.equal(shown().length, totalLessons); assert.equal(empty.hidden, true);
assert.equal(count.textContent, `${totalLessons} lessons`);
console.log(`Organization checks passed${prefix ? ` for ${prefix}` : ''}: homepage, course order/navigation, planned steps, curated links, and combined library filters.`);
