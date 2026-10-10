"""Preprocess KEYSTONE_R1.tex into a Pandoc-friendly LaTeX file for DOCX output."""
import re, sys
src, out = sys.argv[1], sys.argv[2]
aux = open(src.replace('.tex', '.aux')).read()
labels = {m.group(1): m.group(2) for m in re.finditer(r'\\newlabel\{([^}]*)\}\{\{([^}]*)\}', aux)}
s = open(src).read()
s = re.sub(r'\\input\{(tables/[^}]*)\}', lambda m: open(m.group(1) if m.group(1).endswith('.tex') else m.group(1) + '.tex').read(), s)
s = re.sub(r'(\\includegraphics\[[^\]]*\]\{figures/[^}]*)\.pdf\}', r'\1.png}', s)
s = re.sub(r'\\eqref\{([^}]*)\}', lambda m: '(' + labels[m.group(1)] + ')', s)
s = re.sub(r'\\ref\{([^}]*)\}', lambda m: labels[m.group(1)], s)
s = s.replace(r'\mathsf{false\ accept}', r'\text{false accept}').replace(r'\mathsf{accept}', r'\text{accept}')
s = re.sub(r'\$(\\[A-Z]+)\\not\\Rightarrow(\\[A-Z]+)\$', r'$\1$ does not imply $\2$', s)
s = s.replace(r'$\AKR\not\Rightarrow$', r'$\AKR$ does not imply').replace(r'$\not\Rightarrow$', 'does not imply')
def number(env, word):
    global s
    out, pos = [], 0
    for m in re.finditer(r'\\begin\{' + env + r'\*?\}.*?\\end\{' + env + r'\*?\}', s, re.S):
        block = m.group(0)
        lab = re.search(r'\\label\{([^}]*)\}', block)
        if lab and lab.group(1) in labels:
            block = block.replace(r'\caption{', r'\caption{' + word + ' ' + labels[lab.group(1)] + '. ', 1)
        out += [s[pos:m.start()], block]
        pos = m.end()
    out.append(s[pos:])
    s = ''.join(out)
# Pandoc drops \multicolumn cells and prints \cmidrule specs as text in DOCX:
# expand each \multicolumn{k}{spec}{text} to its text plus k-1 empty cells, drop \cmidrule.
def _expand_multicolumn(src):
    out, i, key = [], 0, '\\multicolumn{'
    while True:
        j = src.find(key, i)
        if j < 0:
            out.append(src[i:]); return ''.join(out)
        out.append(src[i:j])
        k_end = src.index('}', j + len(key)); k = int(src[j + len(key):k_end])
        spec_start = k_end + 1; depth = 0; pos = spec_start
        for _ in range(2):  # skip {spec}, then capture {text}
            start = pos; depth = 0
            while True:
                ch = src[pos]
                if ch == '{': depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0: break
                pos += 1
            if _ == 1: text = src[start + 1:pos]
            pos += 1
        out.append(text + ' &' * (k - 1)); i = pos
s = _expand_multicolumn(s)
# Run-in \paragraph headings are unnumbered in the PDF; keep them that way in DOCX.
s = re.sub(r'\\paragraph\{([^}]*)\}', r'\\textbf{\1}', s)
s = re.sub(r'\\cmidrule(\([a-z]*\))?\{[0-9-]+\}', '', s)
number('table', 'Table')
number('figure', 'Figure')
open(out, 'w').write(s)
