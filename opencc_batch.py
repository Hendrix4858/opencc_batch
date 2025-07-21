import os
import shutil
import mimetypes
import click
from opencc import OpenCC
import chardet

def is_text_file(path):
    mime, _ = mimetypes.guess_type(path)
    return mime and mime.startswith("text")

def detect_encoding(path):
    with open(path, 'rb') as f:
        raw = f.read(2048)
    return chardet.detect(raw)['encoding']

def ensure_utf8_encoding(path):
    encoding = detect_encoding(path)
    if encoding.lower() != 'utf-8':
        click.echo(f"文件 {path} 当前编码为 {encoding}，不是 UTF-8")
        choice = input("是否转换为 UTF-8 编码再处理？[y/N]: ").strip().lower()
        if choice == 'y':
            with open(path, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read()
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            click.echo(f"{path} 已转换为 UTF-8")
            return True
        else:
            click.echo(f"跳过文件: {path}")
            return False
    return True

def convert_file(file_path, converter, append):
    if not ensure_utf8_encoding(file_path):
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    converted = converter.convert(content)

    if append:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(converted)
    else:
        shutil.copyfile(file_path, file_path + ".bak")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(converted)

    click.echo(f"已处理: {file_path}")

@click.command()
@click.argument('input')
@click.option('-p','--path', is_flag=True, help='将 text 作为路径，处理目录下所有文本文件')
@click.option(
    '-m',
    '--mode',
    default='t2s',
    show_default=True,
    type=click.Choice([
        'tw2t', 'hk2s', 'hk2t', 'jp2t',
        's2hk', 's2t', 's2tw', 's2twp',
        't2hk', 't2jp', 't2s', 't2tw',
        'tw2s', 'tw2sp'
    ], case_sensitive=False),
    help='''\b
    指定转换模式：
      t2s    繁体 -> 简体
      s2t    简体 -> 繁体
      tw2t   台湾正体 -> 通用繁体
      hk2s   香港繁体 -> 简体
      hk2t   香港繁体 -> 通用繁体
      jp2t   日本汉字 -> 繁体
      s2hk   简体 -> 香港繁体
      s2tw   简体 -> 台湾正体
      s2twp  简体 -> 台湾正体（含词汇转换）
      t2hk   繁体 -> 香港繁体
      t2jp   繁体 -> 日本汉字
      t2tw   繁体 -> 台湾正体
      tw2s   台湾正体 -> 简体
      tw2sp  台湾正体 -> 简体（含词汇转换）
'''
)
@click.option('-a', '--append', is_flag=True, help='直接覆盖原文件(不备份)')
@click.version_option("0.1.1", '-v', '--version', help='打印版本信息', message="opencc_batch %(version)s")
def main(text, path, mode, append):
    converter = OpenCC(mode)

    # 中文路径兼容：确保解码正常
    text = os.path.normpath(text)

    if path:
        if os.path.isdir(text):
            for root, _, files in os.walk(text):
                for name in files:
                    file_path = os.path.join(root, name)
                    if is_text_file(file_path):
                        convert_file(file_path, converter, append)
        elif os.path.isfile(text) and is_text_file(text):
            convert_file(text, converter, append)
        else:
            click.echo("提供的路径不是有效的文本文件或文件夹")
    else:
        result = converter.convert(text)
        click.echo(result)

if __name__ == "__main__":
    main()
