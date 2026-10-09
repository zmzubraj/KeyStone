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
number('table', 'Table')
number('figure', 'Figure')
open(out, 'w').write(s)
