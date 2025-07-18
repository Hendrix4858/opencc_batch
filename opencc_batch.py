import os
import mimetypes
import click
from opencc import OpenCC

def is_text_file(path):
    mime, _ = mimetypes.guess_type(path)
    return mime is not None and mime.startswith("text")

@click.command()
@click.argument("path", type=click.Path(exists=True,readable=True))
@click.option("--reverse", is_flag=True, help="繁化简")

def convert(path, reverse):
    "将繁体字转化为简体."
    converter = OpenCC("t2s" if reverse else "s2t")
    files = []
    if os.path.isfile(path) and is_text_file(path):
        files.append(path)
    elif os.path.isdir(path):
        for root, _, filenames in os.walk(path):
            for name in filenames:
                full = os.path.join(root, name)
                if is_text_file(full):
                    files.append(full)

    for file in files:
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        converted = converter.convert(content)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(converted)
        click.echo(f"已替换: {file}")


if __name__== "__main__":
    convert()