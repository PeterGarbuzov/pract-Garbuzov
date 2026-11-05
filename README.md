# Вариант №6 — этап 3. VFS

Проект продолжает этапы 1 и 2. В этом этапе добавлена загрузка виртуальной
файловой системы из JSON **в оперативную память**. JSON-файл не изменяется.
Команды `ls` и `cd` пока остаются заглушками: настоящая работа с каталогами
относится к этапу 4.

## Запуск

Откройте PowerShell в папке проекта:

```powershell
py main.py --vfs vfs_minimal.json --script startup.txt
py main.py --vfs vfs_files.json --script startup.txt
py main.py --vfs vfs_deep.json --script startup.txt
```

После выполнения скрипта можно вводить команды вручную, например `ls`,
`cd folder`, `exit`. Ошибочные команды в скрипте не прерывают его.

## Проверка ошибок VFS

```powershell
py main.py --vfs vfs_invalid.json
py main.py --vfs missing.json
```

Первый запуск показывает ошибку формата, второй — ошибку отсутствия файла.

## Проверочные скрипты Windows

Запускайте двойным щелчком или из PowerShell:

```powershell
.\test_minimal.bat
.\test_files.bat
.\test_deep.bat
.\test_errors.bat
```

Первые три проверяют минимальную VFS, несколько файлов (включая двоичный
файл с данными base64) и вложенные каталоги глубиной больше трёх уровней.
Четвёртый проверяет сообщения об ошибках.

## Формат JSON

Каталог задаётся объектом с `"type": "directory"` и словарём `children`.
Файл задаётся объектом с `"type": "file"` и строкой `content`.
Для двоичного файла укажите `"encoding": "base64"`, тогда `content`
должен содержать корректную строку base64.

## GitHub

Замените `main.py` и `README.md` в существующем репозитории, добавьте
остальные файлы и создайте новый коммит:

`feat: implement stage 3 JSON VFS loading`
