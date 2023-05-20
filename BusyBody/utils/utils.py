from json import dump, load


def dump_json(path: str, data: list) -> None:
    with open(path, 'w') as f_out:
        dump(data, f_out, indent=4)


def load_json(path: str) -> list:
    file = open(path)
    data = load(file)
    file.close()
    return data
