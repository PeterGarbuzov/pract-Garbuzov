import getpass
import os
import re
import socket
import sys


def replace_variable(match):
    name = match.group(1) or match.group(2)
    return os.environ.get(name, "")


def execute_command(line):
    line = re.sub(
        r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)",
        replace_variable,
        line
    )
    parts = line.split()

    if not parts:
        return True

    command = parts[0]
    args = parts[1:]

    if command == "ls":
        print("Команда: ls")
        print("Аргументы:", " ".join(args) if args else "нет")
    elif command == "cd":
        if len(args) > 1:
            print("Ошибка: cd принимает не более одного аргумента")
        else:
            print("Команда: cd")
            print("Аргументы:", " ".join(args) if args else "нет")
    elif command == "exit":
        if args:
            print("Ошибка: exit не принимает аргументы")
        else:
            print("Выход")
            return False
    else:
        print("Ошибка: неизвестная команда", command)

    return True


def main():
    vfs_path = None
    script_path = None

    index = 1
    while index < len(sys.argv):
        option = sys.argv[index]
        if option not in ("--vfs", "--script"):
            print("Ошибка: неизвестный параметр", option)
            return
        if (
                index + 1 >= len(sys.argv)
                or sys.argv[index + 1].startswith("--")
        ):
            print("Ошибка: не указано значение для", option)
            return
        if option == "--vfs":
            vfs_path = sys.argv[index + 1]
        else:
            script_path = sys.argv[index + 1]
        index += 2

    print("[config] VFS:", vfs_path if vfs_path else "не задан")
    print(
        "[config] Стартовый скрипт:",
        script_path if script_path else "не задан"
    )

    username = getpass.getuser()
    hostname = socket.gethostname()
    prompt = username + "@" + hostname + ":~$ "

    if script_path:
        try:
            with open(script_path, "r", encoding="utf-8-sig") as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    print(prompt + line)
                    if not execute_command(line):
                        return
        except OSError as error:
            print("Ошибка выполнения стартового скрипта:", error)
            return

    while True:
        try:
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\nВыход")
            break
        if not execute_command(line):
            break


if __name__ == "__main__":
    main()
