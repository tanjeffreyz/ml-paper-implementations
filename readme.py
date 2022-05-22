import os


class Readme:
    def __init__(self, repos):
        self.REPOS = repos

    def generate(self):
        CATEGORIES = sorted(self.REPOS.keys())

        contents = []

        index_start, index_end = load_template('index')
        contents += index_start

        contents += load_template('sidebar')[0]

        # Navigation bar
        navbar_start, navbar_end = load_template('navbar')
        contents += navbar_start
        for key in CATEGORIES:
            anchor = get_anchor(key) + '-category'
            contents.append(f'<li><a class="dropdown-item" href="#{anchor}">{key}</a></li>')
        contents += navbar_end

        # Title
        contents += load_template('title')[0]

        # Table of Contents
        toc_start, toc_end = load_template('toc')
        contents += toc_start
        for i, key in enumerate(CATEGORIES):
            classes = 'list-group' + (' mt-4' if i != 0 else '')
            contents += [
                f'<ul class="{classes}">',
                f'<li class="list-group-item list-group-item-primary">{key}</li>'
            ]
            for repo in self.REPOS[key]:
                owner = repo.get('owner', {}).get('login', '')
                name = repo.get('name', '')
                anchor = get_anchor(f'{owner} {name}')
                title = repo.get('header', {}).get('title', '')
                contents.append(f'<li class="list-group-item">'
                                f'<a class="text-decoration-none ms-4" href="#{anchor}">{title}</a></li>')
            contents.append('</ul>')
        contents += toc_end

        # Categories and repositories
        for key in CATEGORIES:
            category_start, category_end = fill_template(
                'category',
                variables={
                    '__CATEGORY_ANCHOR__': get_anchor(key) + '-category',
                    '__CATEGORY_NAME__': key
                }
            )
            contents += category_start
            for repo in self.REPOS[key]:
                owner = repo.get('owner', {}).get('login', '')
                name = repo.get('name', '')
                contents += fill_template(
                    'repository',
                    variables={
                        '__TITLE__': repo.get('header', {}).get('title', ''),
                        '__REPO__': f'{owner}/{name}',
                        '__REPO_ANCHOR__': get_anchor(f'{owner} {name}'),
                        '__DESCRIPTION__': repo.get('description', '')
                    }
                )[0]


            contents += category_end


        contents += index_end       # Finish index

        # Add indentation
        indent = 0
        ignored = ('meta', 'link', '!DOCTYPE')
        for i in range(len(contents)):
            line = contents[i]
            next_indent = indent
            if not any(line.startswith(f'<{x}') for x in ignored):
                first = True
                for j in range(len(line)):
                    if line[j] == '<':
                        if j < len(line) - 1 and line[j+1] == '/':
                            if first:
                                indent -= 1         # If '</' comes first, decrease current indent
                            next_indent -= 1
                        else:
                            next_indent += 1
                        first = False
                    elif line[j] == '/' and j < len(line) - 1 and line[j+1] == '>':
                        next_indent -= 1
            contents[i] = ' ' * 4 * max(0, indent) + line
            indent = next_indent

        # Save to file
        contents.append('')
        with open('index.html', 'w') as file:
            file.write('\n'.join(contents))


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
