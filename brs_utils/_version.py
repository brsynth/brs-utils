def get_version(filename: str = None) -> str:
    if filename is None:
        filename = 'CHANGELOG.md'
    with open(filename, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith('##'):
            from re import search
            m = search("\[(.+)\]", line)
            if m:
                return m.group(1)
