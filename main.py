import base64
import binascii
import getpass
import json
import os
import re
import socket
import sys


VARIABLE_PATTERN = r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)"


def replace_variable(match):
    name = match.group(1) or match.group(2)
    return os.environ.get(name, "")


def check_node(node):
    if not isinstance(node, dict):
        raise ValueError("узел должен быть объектом JSON")
    node_type = node.get("type")
    if node_type == "directory":
        children = node.get("children")
        if not isinstance(children, dict):
            raise ValueError("у каталога должно быть поле children")
        for name, child in children.items():
            if not name or "/" in name or "\\" in name:
                raise ValueError("недопустимое имя файла или каталога")
            check_node(child)
    elif node_type == "file":
        content = node.get("content")
        encoding = node.get("encoding", "text")
        if not isinstance(content, str):
            raise ValueError("содержимое файла должно быть строкой")
        if encoding == "base64":
            try:
                base64.b64decode(content, validate=True)
            except (ValueError, binascii.Error) as error:
                raise ValueError("неверные данные base64") from error
        elif encoding != "text":
            raise ValueError("неизвестная кодировка файла")
    else:
        raise ValueError("неизвестный тип узла")


def load_vfs(path):
    try:
        with open(path, "r", encoding="utf-8-sig") as file:
            data = json.load(file)
        check_node(data)
        if data["type"] != "directory":
            raise ValueError("корень VFS должен быть каталогом")
        print("[vfs] Файловая система загружена в память")
        return data
    except (OSError, UnicodeError, ValueError) as error:
        print("Ошибка загрузки VFS:", error)
        return None


def normalize_path(current_path, path):
    if path.startswith("/"):
        parts = []
    else:
        parts = current_path.copy()
    for part in path.split("/"):
        if part == "..":
            if parts:
                parts.pop()
        elif part and part != ".":
            parts.append(part)
    return parts


def find_node(vfs, parts):
    node = vfs
    for part in parts:
        if node["type"] != "directory":
            return None
        node = node["children"].get(part)
        if node is None:
            return None
    return node


def show_path(parts):
    return "/" + "/".join(parts)


def file_text(node):
    if node.get("encoding", "text") == "base64":
        return None
    return node["content"]


def command_ls(vfs, current_path, args):
    long_format = False
    paths = []
    for arg in args:
        if arg == "-l":
            long_format = True
        elif arg.startswith("-"):
            print("Ошибка: ls: неизвестный ключ", arg)
            return
        else:
            paths.append(arg)
    if not paths:
        paths = ["."]
    for index, path in enumerate(paths):
        parts = normalize_path(current_path, path)
        node = find_node(vfs, parts)
        if node is None:
            print("Ошибка: ls: путь не найден:", path)
            continue
        if index > 0:
            print()
        if len(paths) > 1:
            print(path + ":")
        if node["type"] == "file":
            names = [(path.split("/")[-1], node)]
        else:
            names = sorted(node["children"].items())
        for name, child in names:
            if long_format:
                kind = "d" if child["type"] == "directory" else "-"
                print(kind + " " + name)
            else:
                print(name)


def command_cd(vfs, current_path, args):
    if len(args) > 1:
        print("Ошибка: cd принимает не более одного аргумента")
        return current_path
    path = args[0] if args else "/"
    parts = normalize_path(current_path, path)
    node = find_node(vfs, parts)
    if node is None:
        print("Ошибка: cd: путь не найден:", path)
    elif node["type"] != "directory":
        print("Ошибка: cd: это не каталог:", path)
    else:
        return parts
    return current_path


def command_cat(vfs, current_path, args):
    if not args:
        print("Ошибка: cat: укажите файл")
        return
    for path in args:
        node = find_node(vfs, normalize_path(current_path, path))
        if node is None:
            print("Ошибка: cat: файл не найден:", path)
        elif node["type"] != "file":
            print("Ошибка: cat: это каталог:", path)
        elif file_text(node) is None:
            print("Ошибка: cat: двоичный файл:", path)
        else:
            print(file_text(node), end="")
            if not file_text(node).endswith("\n"):
                print()


def command_head(vfs, current_path, args):
    count = 10
    paths = []
    index = 0
    while index < len(args):
        if args[index] == "-n":
            if index + 1 >= len(args):
                print("Ошибка: head: после -n нужно число")
                return
            try:
                count = int(args[index + 1])
            except ValueError:
                print("Ошибка: head: неверное число строк")
                return
            if count < 0:
                print("Ошибка: head: число строк не может быть отрицательным")
                return
            index += 2
        elif args[index].startswith("-"):
            print("Ошибка: head: неизвестный ключ", args[index])
            return
        else:
            paths.append(args[index])
            index += 1
    if not paths:
        print("Ошибка: head: укажите файл")
        return
    for path in paths:
        node = find_node(vfs, normalize_path(current_path, path))
        if node is None:
            print("Ошибка: head: файл не найден:", path)
        elif node["type"] != "file":
            print("Ошибка: head: это каталог:", path)
        elif file_text(node) is None:
            print("Ошибка: head: двоичный файл:", path)
        else:
            print("".join(file_text(node).splitlines(keepends=True)[:count]),
                  end="")
            if count and file_text(node).splitlines() and not (
                "".join(file_text(node).splitlines(keepends=True)[:count])
            ).endswith("\n"):
                print()


def execute_command(line, vfs, current_path):
    line = re.sub(VARIABLE_PATTERN, replace_variable, line)
    parts = line.split()
    if not parts:
        return True, current_path
    command = parts[0]
    args = parts[1:]
    if command == "exit":
        if args:
            print("Ошибка: exit не принимает аргументы")
        else:
            print("Выход")
            return False, current_path
    elif command in ("ls", "cd", "cat", "head"):
        if vfs is None:
            print("Ошибка: VFS не загружена. Укажите --vfs")
        elif command == "ls":
            command_ls(vfs, current_path, args)
        elif command == "cd":
            current_path = command_cd(vfs, current_path, args)
        elif command == "cat":
            command_cat(vfs, current_path, args)
        else:
            command_head(vfs, current_path, args)
    else:
        print("Ошибка: неизвестная команда", command)
    return True, current_path


def main():
    vfs_path = None
    script_path = None
    index = 1
    while index < len(sys.argv):
        option = sys.argv[index]
        if option not in ("--vfs", "--script"):
            print("Ошибка: неизвестный параметр", option)
            return
        if (index + 1 >= len(sys.argv)
                or sys.argv[index + 1].startswith("--")):
            print("Ошибка: не указано значение для", option)
            return
        if option == "--vfs":
            vfs_path = sys.argv[index + 1]
        else:
            script_path = sys.argv[index + 1]
        index += 2

    print("[config] VFS:", vfs_path if vfs_path else "не задан")
    print("[config] Стартовый скрипт:",
          script_path if script_path else "не задан")
    vfs = None
    if vfs_path:
        vfs = load_vfs(vfs_path)
        if vfs is None:
            return

    username = getpass.getuser()
    hostname = socket.gethostname()
    current_path = []
    prompt = username + "@" + hostname + ":~$ "

    if script_path:
        try:
            with open(script_path, "r", encoding="utf-8-sig") as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    print(prompt + line)
                    running, current_path = execute_command(
                        line, vfs, current_path
                    )
                    if not running:
                        return
        except (OSError, UnicodeError) as error:
            print("Ошибка выполнения стартового скрипта:", error)
            return

    while True:
        try:
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\nВыход")
            break
        running, current_path = execute_command(line, vfs, current_path)
        if not running:
            break


if __name__ == "__main__":
    main()
