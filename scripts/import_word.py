"""One-time import of the original Word lessons. Edit the resulting Markdown afterward."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import html
import re
import json

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
ROOT = Path(__file__).resolve().parents[1]
META = {
    'tell-time': ('Telling the time', 'Η ώρα', 'Everyday Greek', 1, 'Ask the time, understand the clock, and make plans with natural Greek expressions.'),
    'days-of-the-week': ('Days of the week', 'Οι μέρες της εβδομάδας', 'Everyday Greek', 2, 'Talk about your week, everyday routines, and plans for next Monday.'),
    'imperative': ('Giving commands: the imperative', 'Η προστακτική', 'Grammar', 3, 'Give instructions, make requests, and understand positive and negative commands.'),
}
ANSWERS = {
    'days-of-the-week': ['Σήμερα είναι Τετάρτη.', 'Αύριο είναι Πέμπτη.', 'Πηγαίνω στο σούπερ μάρκετ κάθε Σάββατο.', 'Πήγα στην Αθήνα την περασμένη Δευτέρα.', 'Θα δούμε τους φίλους μας την Κυριακή.', 'Δούλευα κάθε Παρασκευή.', 'Είσαι ελεύθερος / ελεύθερη την Τρίτη;', 'Έχω ραντεβού με τον γιατρό την επόμενη Τετάρτη.', 'Τι θα κάνεις το Σαββατοκύριακο;', 'Θα σε πάρω τηλέφωνο κάποια στιγμή την επόμενη εβδομάδα.'],
    'imperative': ['Άνοιξε το παράθυρο.', 'Πες μου την αλήθεια.', 'Μην ανησυχείς!', 'Δώσε μου το.', 'Περίμενέ με!', 'Μιλήστε πιο αργά.', 'Μην ανοίξεις την πόρτα.', 'Γράψε στο βιβλίο σου.', 'Ρώτα τη μητέρα σου.', 'Βοηθήστε με με τις τσάντες.'],
    'tell-time': ['Τέσσερις και τέταρτο.', 'Έξι και μισή.', 'Εννιά παρά τέταρτο.', 'Μία παρά δέκα.', 'Στη μία.', 'Κατά τις εφτά.'],
}

def text(node):
    return ''.join(x.text or '' for x in node.findall('.//w:t', NS)).strip()

def blocks(node):
    for child in node:
        tag = child.tag.split('}')[-1]
        if tag in ('p', 'tbl'):
            yield child
        elif tag != 'sectPr':
            yield from blocks(child)

def answer_block(items):
    return '\n<details data-pagefind-ignore>\n<summary>Show answers</summary>\n<p>Suggested answers; other natural translations may also be possible.</p>\n<ol>\n' + '\n'.join('<li>' + html.escape(x) + '</li>' for x in items) + '\n</ol>\n</details>\n'

def convert(slug, meta):
    with ZipFile(ROOT / 'lessons-word' / (slug + '.docx')) as doc:
        body = ET.fromstring(doc.read('word/document.xml')).find('w:body', NS)
    title, greek, topic, order, summary = meta
    out = ['---', 'layout: lesson.njk', 'tags: lesson', f'title: {json.dumps(title, ensure_ascii=False)}', f'greekTitle: {json.dumps(greek, ensure_ascii=False)}', f'topic: {topic}', f'order: {order}', f'summary: {json.dumps(summary)}', f'permalink: /lessons/{slug}/', '---', '']
    feedback = []
    skip_clock = False
    first = True
    practice = False
    translation = False
    question_number = 0
    count = 0
    for block in blocks(body):
        if block.tag.endswith('}tbl'):
            if skip_clock:
                continue
            rows = [[text(c) for c in r.findall('w:tc', NS)] for r in block.findall('w:tr', NS)]
            if not rows:
                continue
            out += ['<div class="table-scroll"><table>', '<thead><tr>' + ''.join('<th scope="col">' + html.escape(c) + '</th>' for c in rows[0]) + '</tr></thead>', '<tbody>']
            for row in rows[1:]:
                out.append('<tr>' + ''.join('<td' + (' lang="el"' if re.search('[\u0370-\u03ff]', c) else '') + '>' + html.escape(c) + '</td>' for c in row) + '</tr>')
            out += ['</tbody></table></div>', '']
            continue
        value = text(block)
        if not value:
            continue
        if first:
            first = False
            continue
        # Exercise questions also begin with numbers; only known document sections are headings.
        heading = bool(re.match(r'^\d+\.\s+', value)) and not (practice and re.match(r'^[1-6]\.\s+', value))
        if slug == 'tell-time' and value.startswith('17. Interactive clock'):
            skip_clock = True
            continue
        if skip_clock:
            if not value.startswith('18. Practice'):
                continue
            skip_clock = False
        if heading:
            if practice and slug == 'tell-time':
                out.append(answer_block(ANSWERS[slug]))
            practice = 'Practice' in value
            translation = False
            out += ['## ' + value, '']
            continue
        if value.startswith('Correct!'):
            feedback.append(value.removeprefix('Correct!').strip())
            continue
        if value.startswith('Exercise B:') and feedback:
            out.append(answer_block(feedback))
            feedback = []
        if value.startswith('Exercise B:') or (slug == 'days-of-the-week' and value.startswith('Exercise A:')):
            translation = True
            question_number = 0
        if value.startswith('Show suggested answers'):
            out.append(answer_block(ANSWERS[slug]))
            continue
        if value in ('Try again', '0 / 6 correct', '5 of 5 answered · 5 correct'):
            continue
        if value.startswith(('Exercise A:', 'Exercise B:')) or value in ('Final learning tip', 'A useful pattern', 'Useful sentences', 'Examples', 'Everyday examples', 'More examples', 'Positive imperatives', 'Negative commands', 'Negative continuous commands', 'At home', 'In conversation', 'Giving directions', 'Encouragement and advice') or value.startswith(('Pattern A:', 'Pattern B:', 'Mistake ')):
            out += ['### ' + value, '']
        else:
            if translation and value != 'Use the singular imperative unless otherwise indicated.':
                question_number += 1
                value = str(question_number) + '. ' + value
            escaped = html.escape(value)
            is_greek = re.match(r'^[\u0370-\u03ff]', value)
            out += [('<p class="greek-line" lang="el">' + escaped + '</p>') if is_greek else value, '']
        count += 1
    destination = ROOT / 'src' / 'lessons' / (slug + '.md')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text('\n'.join(out), encoding='utf-8')
    print(f'Imported {slug}: {count} paragraphs')

for key, value in META.items():
    convert(key, value)
