import os


IGNORED_TAGS = ('meta', 'link', '!DOCTYPE', 'br', 'hr')
DELIMITER = ','


def parse_header(contents, max_depth):
    # Filter out empty lines
    contents = [line for line in contents if line.strip() != '']

    i = 0
    while i < len(contents) and '<!--' not in contents[i]:
        i += 1
    start = i + 1
    while i < len(contents) and '-->' not in contents[i]:
        i += 1
    end = i

    # Parse header for repository information
    header = {
        'title': None,
        'category': None,
        'images': None
    }
    if start < len(contents):
        line = contents[start].split(DELIMITER)
        ids = {x.strip().lower() for x in line}
    else:
        ids = set()
    for line in contents[start+1:end]:
        args = line.split(':', 1)
        if len(args) == 2:
            key = args[0].strip().lower()
            value = args[1].strip()
            if key in {'title'}:
                header[key] = value
            elif key in {'images'}:
                items = []
                for x in value.split(DELIMITER):
                    cleaned = x.strip()
                    if cleaned:
                        items.append(cleaned)
                header[key] = items
            elif key == 'category':
                result = []
                for x in value.split('/'):
                    stripped = x.strip()
                    if stripped:
                        result.append(stripped.title())
                header[key] = result[:max_depth]
    if all(x is not None for x in header.values()):     # Require all attributes to be present
        return ids, header
    else:
        return ids, None


def indent(contents):
    """Mutatively indents each line in CONTENTS."""

    curr_indent = 0
    for i in range(len(contents)):
        line = contents[i]
        next_indent = curr_indent
        if not any(line.startswith(f'<{x}') for x in IGNORED_TAGS):
            first = True
            for j in range(len(line)):
                if line[j] == '<':
                    if j < len(line) - 1 and line[j + 1] == '/':
                        if first:
                            curr_indent -= 1  # If '</' comes first, decrease current indent
                        next_indent -= 1
                    else:
                        next_indent += 1
                    first = False
                elif line[j] == '/' and j < len(line) - 1 and line[j + 1] == '>':
                    next_indent -= 1
        contents[i] = ' ' * 4 * max(0, curr_indent) + line
        curr_indent = next_indent


def get_anchor(string):
    return string.strip().lower().replace(' ', '-')


def load_template(name):
    blocks = []
    lines = []
    with open(os.path.join('src', 'resources', 'templates', f'{name}.txt')) as file:
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


def flatten_dict(curr_dict):
    result = curr_dict['items']
    for _, value in sorted(curr_dict['nested'].items()):
        result += flatten_dict(value)
    return result
