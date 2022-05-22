import os


IGNORED_TAGS = ('meta', 'link', '!DOCTYPE', 'br', 'hr')


class Readme:
    def __init__(self, repos):
        self.REPOS = repos
        self.CATEGORIES = sorted(self.REPOS.keys())

    def generate(self):
        print('\n[~] Generating README.md:')



        contents = []
        index_start, index_end = load_template('index')
        contents += index_start

        # Navigation bar
        navbar_start, navbar_end = load_template('navbar')
        contents += navbar_start
        for key in self.CATEGORIES:
            anchor = get_anchor(key) + '-category'
            contents.append(f'<li><a class="dropdown-item" href="#{anchor}">{key}</a></li>')
        contents += navbar_end

        # Title
        contents += load_template('title')[0]

        # Table of Contents
        toc_start, toc_end = load_template('toc')
        contents += toc_start
        for i, key in enumerate(self.CATEGORIES):
            classes = 'mb-1' + (' mt-4' if i != 0 else '')
            button_target = get_anchor(key) + '-button'
            group_start, group_end = fill_template(
                'toc_group',
                variables={
                    '__CLASSES__': classes,
                    '__TARGET__': button_target,
                    '__CATEGORY__': key
                }
            )
            contents += group_start
            for repo in self.REPOS[key]:
                owner = repo.get('owner', {}).get('login', '')
                name = repo.get('name', '')
                anchor = get_anchor(f'{owner} {name}')
                title = repo.get('header', {}).get('title', '')
                contents.append(
                    f'<li class="list-group-item mt-1 pe-2">'
                    f'<a class="link-dark rounded text-decoration-none" '
                    f'href="#{anchor}">{title}</a></li>'
                )
            contents += group_end
        contents += toc_end

        # Categories and repositories
        for key in self.CATEGORIES:
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
                default_branch = repo.get('defaultBranchRef', {}).get('name', '')
                repo_anchor = get_anchor(f'{owner} {name}')
                repo_start, repo_end = fill_template(
                    'repository',
                    variables={
                        '__TITLE__': repo.get('header', {}).get('title', ''),
                        '__REPO__': f'{owner}/{name}',
                        '__REPO_ANCHOR__': repo_anchor,
                        '__DESCRIPTION__': repo.get('description', '')
                    }
                )
                contents += repo_start

                # Display images
                images = repo.get('header', {}).get('images', [])
                carousel_id = repo_anchor + '-carousel'
                indicators = []
                slides = []
                carousel_start, carousel_middle, carousel_end = fill_template(
                    'carousel',
                    variables={
                        '__CAROUSEL_ID__': carousel_id
                    }
                )
                for i, path in enumerate(images):
                    current = 'aria-current="true" ' if i == 0 else ''
                    indicator = f'<button type="button" data-bs-target="#{carousel_id}" data-bs-slide-to="{i}" ' \
                                f'class="active" {current}aria-label="Slide {i + 1}"></button>'
                    indicators.append(indicator)

                    active = ' active' if i == 0 else ''
                    url = f'https://raw.githubusercontent.com/{owner}/{name}/{default_branch}/{path}'
                    slides += [
                        f'<div class="carousel-item{active}">',
                        f'<img src="{url}" style="margin: auto;" class="d-block" height="300px" />',
                        '</div>'
                    ]

                # Build carousel
                contents += carousel_start
                contents += indicators
                contents += carousel_middle
                contents += slides
                contents += carousel_end
                contents += repo_end
            contents += category_end

        contents += index_end       # Finish index
        indent(contents)            # Add indentation

        print(' -  Finished compiling contents')

        # Save to file
        contents.append('')
        with open('index.html', 'w') as file:
            file.write('\n'.join(contents))
        print(' -  Saved result to README.md')


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
