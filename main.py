import os
import getpass
import socket
import re


def replace_variable(match):
    name = match.group(1) or match.group(2)
    return os.environ.get(name, "")


def main():
    username = getpass.getuser()
    hostname = socket.gethostname()

    while True:
        try:
            line = input(username + "@" + hostname + ":~$ ")
        except (EOFError, KeyboardInterrupt):
            print("\nВыход")
            break

        line = re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)", replace_variable, line)
        parts = line.split()

        if not parts:
            continue

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
                break
        else:
            print("Ошибка: неизвестная команда", command)


if __name__ == "__main__":
    main()
