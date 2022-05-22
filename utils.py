import os


IGNORED_TAGS = ('meta', 'link', '!DOCTYPE', 'br', 'hr')


def parse_header(contents):
    i = 0
    while i < len(contents) and '<!--' not in contents[i]:
        i += 1
    start = i + 1
    while i < len(contents) and '-->' not in contents[i]:
        i += 1
    end = i

    # Parse header for repository information
    header = {
        'tags': None,
        'title': None,
        'images': None,
        'category': None
    }
    for line in contents[start:end]:
        args = line.split(':')
        if len(args) == 2:
            key = args[0].strip().lower()
            value = args[1].strip()
            if key in {'tags'}:
                header[key] = {x.strip().lower() for x in value.split(',')}
            elif key in {'category', 'title'}:
                header[key] = value
            elif key in {'images'}:
                header[key] = [x.strip() for x in value.split(',')]
    if all(x is not None for x in header.values()):
        return header


def indent(contents):
    """Mutatively indents each line in CONTENTS."""

    indent = 0
    for i in range(len(contents)):
        line = contents[i]
        next_indent = indent
        if not any(line.startswith(f'<{x}') for x in IGNORED_TAGS):
            first = True
            for j in range(len(line)):
                if line[j] == '<':
                    if j < len(line) - 1 and line[j + 1] == '/':
                        if first:
                            indent -= 1  # If '</' comes first, decrease current indent
                        next_indent -= 1
                    else:
                        next_indent += 1
                    first = False
                elif line[j] == '/' and j < len(line) - 1 and line[j + 1] == '>':
                    next_indent -= 1
        contents[i] = ' ' * 4 * max(0, indent) + line
        indent = next_indent


def get_anchor(string):
    return string.lower().replace(' ', '-')


def load_template(name):
    blocks = []
    lines = []
    with open(os.path.join('resources', 'templates', f'{name}.txt')) as file:
        for line in file.readlines():
            line = line.strip()
            if line != '__DIVIDER__':
                if line:
                    lines.append(line)
            else:
                blocks.append(lines)
                lines = []
    if len(lines) > 0:
        blocks.append(lines)
    return blocks


def fill_template(name, variables=dict()):
    blocks = load_template(name)
    for block in blocks:
        for i in range(len(block)):
            for var in variables:
                block[i] = block[i].replace(var, variables[var])
    return blocks