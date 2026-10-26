const libraryControls = document.querySelector('[data-library-controls]');
if (libraryControls) {
  const rows = [...document.querySelectorAll('.lesson-row')];
  const query = document.querySelector('#library-query');
  const subjectSelect = document.querySelector('#library-subject');
  const count = document.querySelector('#library-count');
  const empty = document.querySelector('#library-empty');
  const buttons = [...document.querySelectorAll('[data-filter]')];
  const normalise = value => value.normalize('NFD').replace(/\p{M}/gu, '').toLocaleLowerCase().replace(/ς/g, 'σ');
  let category = 'all';
  const subjects = [...new Set(rows.flatMap(row => row.dataset.subjects.split('|').filter(Boolean)))].sort((a,b) => a.localeCompare(b));
  subjects.forEach(subject => {
    const option = document.createElement('option'); option.value = subject; option.textContent = subject; subjectSelect.append(option);
  });
  function filterLessons() {
    const words = normalise(query.value.trim()).split(/\s+/).filter(Boolean);
    let visible = 0;
    rows.forEach(row => {
      const match = (category === 'all' || row.dataset.category === category)
        && (subjectSelect.value === 'all' || row.dataset.subjects.split('|').includes(subjectSelect.value))
        && words.every(word => normalise(row.dataset.search).includes(word));
      row.hidden = !match;
      if (match) visible++;
    });
    count.textContent = `${visible} ${visible === 1 ? 'lesson' : 'lessons'}`;
    empty.hidden = visible > 0;
  }
  buttons.forEach(button => button.addEventListener('click', () => {
    category = button.dataset.filter;
    buttons.forEach(b => { b.classList.toggle('active', b === button); b.setAttribute('aria-pressed', String(b === button)); });
    filterLessons();
  }));
  query.addEventListener('input', filterLessons);
  subjectSelect.addEventListener('change', filterLessons);
  libraryControls.hidden = false;
  filterLessons();
}
const toc = document.querySelector('#lesson-toc');
if(toc) document.querySelectorAll('.lesson-body h2').forEach((heading, i) => {
  heading.id ||= `section-${i+1}`;
  const link = document.createElement('a'); link.href = `#${heading.id}`; link.textContent = heading.textContent.replace(/^\d+\.\s*/, ''); toc.append(link);
});

const greekSpeechSupported = typeof window !== 'undefined' && 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window;
if (greekSpeechSupported) {
  document.querySelectorAll('.lesson-body [lang="el"], .phrase-card [lang="el"]').forEach(element => {
    const text = element.textContent.trim();
    if (!text || element.querySelector('.speak-button')) return;
    if (/^-[\p{Script=Greek}]+$/u.test(text)) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'speak-button';
    button.setAttribute('aria-label', `Play Greek audio: ${text}`);
    button.title = 'Play Greek audio';
    button.textContent = '🔊';
    button.addEventListener('click', () => {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'el-GR';
      utterance.rate = 0.88;
      window.speechSynthesis.speak(utterance);
    });
    element.append(' ', button);
  });
}
