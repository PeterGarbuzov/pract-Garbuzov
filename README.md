# Вариант №6 — этап 2. Конфигурация

Проект продолжает этап 1. Команды `ls` и `cd` остаются заглушками. VFS на этом этапе **не загружается**: путь к ней только принимается и выводится для отладки.

## Запуск в Windows PowerShell

В папке проекта:

```powershell
py main.py
py main.py --vfs example.json
py main.py --script startup.txt
py main.py --vfs example.json --script startup.txt
```

При запуске программа выводит оба параметра, затем выполняет команды стартового скрипта (если он указан) и переходит в интерактивный режим. Неверные команды в скрипте выводят ошибку, но не останавливают его. Если скрипт не удаётся открыть, выводится сообщение об ошибке.

## Скрипты Windows для демонстрации

Запустить двойным щелчком или из PowerShell:

```powershell
.\test_no_args.bat
.\test_vfs.bat
.\test_script.bat
```

Скрипты проверяют запуск без параметров, только с путём VFS и с обоими параметрами. Также можно проверить `py main.py --script startup.txt` отдельно.

## Примеры ошибок

```powershell
py main.py --bad example
py main.py --script
py main.py --script missing.txt
```
