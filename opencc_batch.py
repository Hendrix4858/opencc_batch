import os
import mimetypes
import click
from opencc import OpenCC

def is_text_file(path):
    mime, _ = mimetypes.guess_type(path)
    return mime is not None and mime.startswith("text")

def convert_string(text, to_traditional):
    converter = OpenCC("s2t" if to_traditional else "t2s")
    result = converter.convert(text)
    click.echo(result)

def convert_file(path, to_traditional):
    converter = OpenCC("s2t" if to_traditional else "t2s")
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

@click.command()
@click.option("--file", "is_file", is_flag=True, help="处理文件或文件夹")
@click.option("--path", type=click.Path(exists=True, readable=True), help="文件或目录路径，仅 --file 时使用")
@click.option("--t2s", is_flag=True, default=True, help="繁转简（默认）")
@click.argument("text", required=False)
def main(is_file, path, t2s, text):
    """繁简转换工具，默认处理字符串繁转简。"""
    if is_file:
        if not path:
            click.echo("错误：未提供文件路径", err=True)
            return
        convert_file(path, to_traditional=not t2s)
    else:
        if not text:
            click.echo("错误：未提供文本字符串", err=True)
            return
        convert_string(text, to_traditional=not t2s)

if __name__ == "__main__":
    main()
