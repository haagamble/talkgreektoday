"""Initial conversion of the two Word verb drafts. Output is editable Markdown.

Rerunning overwrites those two Markdown lessons. This does not touch other lessons.
"""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from html import escape
import json

ROOT = Path(__file__).resolve().parents[1]
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

def table(headers, rows):
    def cell(value, heading=False):
        tag = 'th' if heading else 'td'
        language = ' lang="el"' if any('\u0370' <= ch <= '\u03ff' for ch in value) and not heading else ''
        return f'<{tag}' + (' scope="col"' if heading else language) + '>' + escape(value) + f'</{tag}>'
    return '\n'.join(['<div class="table-scroll"><table>', '<thead><tr>' + ''.join(cell(x, True) for x in headers) + '</tr></thead>', '<tbody>'] + ['<tr>' + ''.join(cell(x) for x in row) + '</tr>' for row in rows] + ['</tbody></table></div>'])

def example(greek, english):
    return f'<div class="example">\n<p class="greek-line" lang="el">{greek}</p>\n<p class="translation-line" lang="en">{escape(english)}</p>\n</div>'

DATA = {
    'open': {
        'verb': 'ανοίγω', 'meaning': 'to open', 'order': 4,
        'summary': 'Compare the active tenses of ανοίγω, then practise commands and subjunctive forms.',
        'intro': 'Ανοίγω means “to open.” The examples use opening a door to compare the main active tenses. Commands and subjunctives are shown separately: they are moods, not tenses.',
        'pattern': 'Learn these forms together: **ανοίγω → άνοιξα → θα ανοίξω**. Ongoing forms use ανοιγ-; completed-action forms use ανοιξ-. Notice the stress change in άνοιξα.',
        'tense_rows': [
            ('Present — Ενεστώτας', 'Ανοίγω την πόρτα.', 'I open / am opening the door.'),
            ('Imperfect — Παρατατικός', 'Άνοιγα την πόρτα κάθε πρωί.', 'I used to open the door every morning.'),
            ('Simple past — Αόριστος', 'Άνοιξα την πόρτα χθες.', 'I opened the door yesterday.'),
            ('Continuous future — Εξακολουθητικός μέλλοντας', 'Θα ανοίγω την πόρτα κάθε πρωί.', 'I will open the door every morning.'),
            ('Simple future — Συνοπτικός μέλλοντας', 'Θα ανοίξω την πόρτα αύριο.', 'I will open the door tomorrow.'),
            ('Present perfect — Παρακείμενος', 'Έχω ανοίξει την πόρτα.', 'I have opened the door.'),
            ('Past perfect — Υπερσυντέλικος', 'Είχα ανοίξει την πόρτα πριν έρθεις.', 'I had opened the door before you arrived.'),
            ('Future perfect — Συντελεσμένος μέλλοντας', 'Μέχρι τις οκτώ, θα έχω ανοίξει την πόρτα.', 'By eight, I will have opened the door.'),
        ],
        'perfect': 'ανοίξει',
        'subjunctive': [
            ('Simple: action as a whole', 'Θέλω να ανοίξω την πόρτα.', 'I want to open the door.'),
            ('Continuous: a habit', 'Θέλω να ανοίγω τα παράθυρα κάθε πρωί.', 'I want to open the windows every morning.'),
            ('Perfect: completed by a reference time', 'Θέλω να έχω ανοίξει το μαγαζί μέχρι τις οκτώ.', 'I want to have opened the shop by eight.'),
        ],
        'commands': [
            ('Simple imperative', 'άνοιξε', 'ανοίξτε'),
            ('Continuous imperative', 'άνοιγε', 'ανοίγετε'),
            ('Negative simple command', 'μην ανοίξεις', 'μην ανοίξετε'),
            ('Negative continuous command', 'μην ανοίγεις', 'μην ανοίγετε'),
        ],
        'command_examples': [('Άνοιξε την πόρτα!', 'Open the door!'), ('Άνοιγε τα παράθυρα κάθε πρωί.', 'Open the windows every morning.')],
        'other': [
            ('Hypothetical', 'Θα άνοιγα την πόρτα, αλλά δεν έχω το κλειδί.', 'I would open the door, but I don’t have the key.'),
            ('Hypothetical past', 'Θα είχα ανοίξει την πόρτα, αλλά δεν είχα το κλειδί.', 'I would have opened the door, but I didn’t have the key.'),
            ('Adverbial participle', 'Ανοίγοντας την πόρτα, είδα τη γάτα.', 'Opening the door, I saw the cat.'),
        ],
        'note': 'Ανοίγω can also describe something opening by itself: **Η πόρτα ανοίγει** — “The door opens.” For a state, use the adjective: **Η πόρτα είναι ανοιχτή** — “The door is open.”',
        'practice': [
            ('I open the door every morning.', 'Ανοίγω την πόρτα κάθε πρωί.'),
            ('I used to open the windows every morning.', 'Άνοιγα τα παράθυρα κάθε πρωί.'),
            ('I opened the door yesterday.', 'Άνοιξα την πόρτα χθες.'),
            ('I will open the door tomorrow.', 'Θα ανοίξω την πόρτα αύριο.'),
            ('I will open the windows every morning. (A future habit.)', 'Θα ανοίγω τα παράθυρα κάθε πρωί.'),
            ('I have opened the door.', 'Έχω ανοίξει την πόρτα.'),
            ('I had opened the door before you arrived.', 'Είχα ανοίξει την πόρτα πριν έρθεις.'),
            ('By eight, I will have opened the shop.', 'Μέχρι τις οκτώ, θα έχω ανοίξει το μαγαζί.'),
            ('Open the door! (To several people.)', 'Ανοίξτε την πόρτα!'),
            ('I want to open the window.', 'Θέλω να ανοίξω το παράθυρο.'),
        ],
    },
    'see': {
        'verb': 'βλέπω', 'meaning': 'to see / watch', 'order': 5,
        'summary': 'Compare βλέπω, είδα, and θα δω across the active tenses, commands, and subjunctive forms.',
        'intro': 'Βλέπω means “to see” or “to watch,” depending on context. This overview compares its main active tenses. Commands and subjunctives are shown separately: they are moods, not tenses.',
        'pattern': 'Learn these irregular forms together: **βλέπω → είδα → θα δω**. Ongoing forms use βλεπ-, the simple past uses ειδ-, and the simple future and subjunctive use forms such as δω, δεις, and δει.',
        'tense_rows': [
            ('Present — Ενεστώτας', 'Βλέπω μια ταινία.', 'I am watching a film.'),
            ('Imperfect — Παρατατικός', 'Έβλεπα μια ταινία όταν ήρθες.', 'I was watching a film when you arrived.'),
            ('Simple past — Αόριστος', 'Είδα μια ταινία χθες.', 'I watched a film yesterday.'),
            ('Continuous future — Εξακολουθητικός μέλλοντας', 'Θα βλέπω μια ταινία κάθε Παρασκευή.', 'I will watch a film every Friday.'),
            ('Simple future — Συνοπτικός μέλλοντας', 'Θα δω μια ταινία απόψε.', 'I will watch a film tonight.'),
            ('Present perfect — Παρακείμενος', 'Έχω δει αυτή την ταινία.', 'I have seen this film.'),
            ('Past perfect — Υπερσυντέλικος', 'Είχα δει την ταινία πριν έρθεις.', 'I had seen the film before you arrived.'),
            ('Future perfect — Συντελεσμένος μέλλοντας', 'Μέχρι αύριο, θα έχω δει την ταινία.', 'By tomorrow, I will have seen the film.'),
        ],
        'perfect': 'δει',
        'subjunctive': [
            ('Simple: action as a whole', 'Θέλω να δω τη Μαρία.', 'I want to see Maria.'),
            ('Continuous: a habit', 'Θέλω να βλέπω τη Μαρία πιο συχνά.', 'I want to see Maria more often.'),
            ('Perfect: completed by a reference time', 'Θέλω να έχω δει την ταινία μέχρι αύριο.', 'I want to have seen the film by tomorrow.'),
        ],
        'commands': [
            ('Simple imperative', 'δες', 'δείτε'),
            ('Continuous imperative', 'βλέπε', 'βλέπετε'),
            ('Negative simple command', 'μη δεις', 'μη δείτε'),
            ('Negative continuous command', 'μη βλέπεις', 'μη βλέπετε'),
        ],
        'command_examples': [('Δες αυτή τη φωτογραφία!', 'Look at this photograph!'), ('Μη βλέπεις τόση τηλεόραση!', 'Don’t watch so much television!')],
        'other': [
            ('Hypothetical', 'Θα έβλεπα αυτή την ταινία, αλλά δεν έχω χρόνο.', 'I would watch this film, but I don’t have time.'),
            ('Hypothetical past', 'Θα είχα δει την ταινία, αλλά ήμουν άρρωστη.', 'I would have watched the film, but I was ill. (Female speaker.)'),
            ('Adverbial participle', 'Έμαθα ελληνικές λέξεις βλέποντας ταινίες.', 'I learned Greek words by watching films.'),
        ],
        'note': 'The present form covers both a current activity and a habit: **Βλέπω τηλεόραση** — “I am watching television”; **Βλέπω τη Μαρία κάθε μέρα** — “I see Maria every day.” English “see” and “watch” are chosen according to context.',
        'practice': [
            ('I see Maria every day.', 'Βλέπω τη Μαρία κάθε μέρα.'),
            ('I was watching a film when you arrived.', 'Έβλεπα μια ταινία όταν ήρθες.'),
            ('I saw Maria yesterday.', 'Είδα τη Μαρία χθες.'),
            ('I will see Maria tomorrow.', 'Θα δω τη Μαρία αύριο.'),
            ('I will see Maria every Friday. (A future habit.)', 'Θα βλέπω τη Μαρία κάθε Παρασκευή.'),
            ('I have seen this film.', 'Έχω δει αυτή την ταινία.'),
            ('I had seen the film before you arrived.', 'Είχα δει την ταινία πριν έρθεις.'),
            ('By tomorrow, I will have seen the film.', 'Μέχρι αύριο, θα έχω δει την ταινία.'),
            ('Look at this photograph! (To one person informally.)', 'Δες αυτή τη φωτογραφία!'),
            ('I want to see Maria more often.', 'Θέλω να βλέπω τη Μαρία πιο συχνά.'),
        ],
    },
}

def conjugations(key):
    """Retain the complete active-tense paradigms from the user's Word draft."""
    with ZipFile(ROOT / 'lessons-word' / f'verb-tenses-with-{key}.docx') as doc:
        root = ET.fromstring(doc.read('word/document.xml'))
    tables = []
    for node in root.findall('.//w:tbl', NS):
        rows = [[''.join(x.text or '' for x in c.findall('.//w:t', NS)) for c in r.findall('w:tc', NS)] for r in node.findall('w:tr', NS)]
        if rows and rows[0] == ['Person', 'Greek', 'English'] and len(rows) == 7:
            tables.append(rows[1:])
    # The first eight such tables are present, aorist, imperfect, simple future,
    # continuous future, present perfect, past perfect, and future perfect.
    assert len(tables) >= 8
    return tables[:8]

for key, data in DATA.items():
    verb = data['verb']
    out = ['---', 'layout: lesson.njk', 'tags: lesson', 'title: ' + json.dumps(verb + ' — ' + data['meaning'], ensure_ascii=False), 'greekTitle: ' + verb, 'topic: Verb overviews', 'order: ' + str(data['order']), 'summary: ' + json.dumps(data['summary'], ensure_ascii=False), f'permalink: /lessons/verb-tenses-with-{key}/', '---', data['intro'], '## 1. The main patterns', data['pattern'], '**Simple** forms present an action as a whole. **Continuous** forms present it as ongoing or habitual. This is aspect: it does not simply mean “once” versus “many times.”', data['note'], '## 2. The tenses side by side', table(['Tense', 'Greek example', 'English'], data['tense_rows']), 'The present can describe either an action happening now or a habit. The imperfect describes a past activity or habit; the simple past views the event as a whole. Perfect tenses relate an earlier action to the present, a past point, or a future point.', f'In perfect forms, **{data["perfect"]}** stays unchanged; έχω changes for the person and time.', '<details class="conjugations">\n<summary>Show conjugations for all six persons</summary>']
    paradigms = conjugations(key)
    people = ['εγώ', 'εσύ', 'αυτός / αυτή / αυτό', 'εμείς', 'εσείς', 'αυτοί / αυτές / αυτά']
    for headers, indices in [(['Person', 'Present', 'Imperfect', 'Simple past'], [0, 2, 1]), (['Person', 'Continuous future', 'Simple future'], [4, 3]), (['Person', 'Present perfect', 'Past perfect', 'Future perfect'], [5, 6, 7])]:
        out.append(table(headers, [[people[i]] + [paradigms[j][i][1] for j in indices] for i in range(6)]))
    out += ['<p>Εσείς also addresses one person politely. Subject pronouns are usually omitted when the verb ending makes the person clear.</p>\n</details>', '## 3. With να: the subjunctive', 'After να, the simple, continuous, and perfect forms retain the same aspect distinctions. These are not additional tenses.', table(['Form and use', 'Greek example', 'English'], data['subjunctive']), 'For the simple and continuous conjugations, replace θα in the future tables with να. For the perfect, put να before the present-perfect form.', '## 4. Commands', 'Imperatives address one person informally or several people / one person politely. Negative commands use **μη(ν) + subjunctive**, not imperative forms.', table(['Form', 'Singular', 'Plural / polite'], data['commands'])]
    out += [example(g, e) for g, e in data['command_examples']]
    out += ['## 5. Other active forms', 'Hypothetical meanings use θα with past forms. The adverbial participle expresses an accompanying action and does not change for person or number.', table(['Construction', 'Greek example', 'English'], data['other']), '## 6. Practice exercises', f'Translate into Greek using **{verb}**.']
    out += [f'{i}. {prompt}' for i, (prompt, _) in enumerate(data['practice'], 1)]
    out += ['<details data-pagefind-ignore>\n<summary>Show answers</summary>\n<p>Suggested answers; other natural translations may also be possible.</p>\n<ol>', '\n'.join('<li lang="el">' + escape(answer) + '</li>' for _, answer in data['practice']), '</ol>\n</details>']
    destination = ROOT / 'src' / 'lessons' / f'verb-tenses-with-{key}.md'
    destination.write_text('\n\n'.join(out) + '\n', encoding='utf-8')
    print(f'Created {destination.name}')
