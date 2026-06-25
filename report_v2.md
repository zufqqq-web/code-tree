# Project Structure and Codebase Analysis Report

## Project Structure Tree
```text
.
├── codetree/
│   ├── __init__.py                           # Короткий файл (4 строк): """
codetree package.
"""
__version__...
│   ├── __main__.py                           # Короткий файл (3 строк): from codetree.cli import main

if __n...
│   ├── cli.py                                # Файл `cli.py` содержит основную логику командной строки для пр...
│   ├── frameworks.py                         # Файл `frameworks.py` содержит набор функций для анализа различ...
│   ├── languages.py                          # Файл `languages.py` содержит функцию для анализа статистики ко...
│   ├── llm_client.py                         # Файл `llm_client.py` содержит класс `LLMClient`, который предн...
│   ├── prioritization.py                     # Файл `prioritization.py` содержит набор функций для автоматиза...
│   ├── reporter.py                           # Файл `reporter.py` отвечает за генерацию отчетов о проекте. Он...
│   ├── scanner.py                            # Файл `scanner.py` содержит классы и функции для анализа проект...
│   └── skeleton.py                           # Файл `skeleton.py` содержит набор функций для извлечения струк...
├── tests/
│   ├── test_codetree.py                      # Файл `test_codetree.py` содержит набор тестов для различных ас...
│   └── test_skeleton_js.py                   # Файл `test_skeleton_js.py` содержит набор юнит-тестов для пров...
├── firsttest.md                              # Файл firsttest.md (роль не определена однозначно).
├── pyproject.toml                            # Файл pyproject.toml (роль не определена однозначно).
└── README.md                                 # Файл README.md (роль не определена однозначно).
```

## Programming Language Distribution
  - **Python** : `██████████████████░░` **90.8%**
  - **MD    ** : `█░░░░░░░░░░░░░░░░░░░` **8.1%**
  - **TOML  ** : `░░░░░░░░░░░░░░░░░░░░` **1.1%**


## Detected Frameworks and Libraries
  - *No framework signatures detected.*


## Detailed Module Analysis
### `codetree/skeleton.py`
  - **File Size**: 346 code lines
  - **Declarations**: 7 classes/functions
  - **Role**: `General Module`
  - **Importance Score**: 137.8
  - **Purpose**:
    Файл `skeleton.py` содержит набор функций для извлечения структуры кода на JavaScript/TypeScript и Python. Ключевые функции позволяют токенизировать код, извлекать его основную структуру (функции, классы, интерфейсы) и использовать эти данные для анализа или генерации кода.

### `codetree/scanner.py`
  - **File Size**: 308 code lines
  - **Declarations**: 10 classes/functions
  - **Role**: `core_logic`
  - **Importance Score**: 122.4
  - **Purpose**:
    Файл `scanner.py` содержит классы и функции для анализа проекта, включая обработку файлов `.gitignore`, подсчет строк кода, функций и классов, а также рекурсивный сканирование директорий.
    
    Ключевые функции:
    - `GitignoreRules`: парсит и проверяет пути файлов на соответствие правилам `.gitignore`.
    - `GitignoreScanner`: собирает файлы `.gitignore`, проверяет игнорирование путей.
    - `count_lines`: считает количество непустых строк без пробелов.
    - `count_functions_and_classes`: подсчитывает функции и классы в файлах, используя разные методы для разных языков программирования.
    - `scan_project`: рекурсивно сканирует корневую директорию, собирает метаданные файлов.

### `codetree/prioritization.py`
  - **File Size**: 241 code lines
  - **Declarations**: 7 classes/functions
  - **Role**: `core_logic`
  - **Importance Score**: 101.3
  - **Purpose**:
    Файл `prioritization.py` содержит набор функций для автоматизации процесса классификации файлов по их важности и семантической роли. Ключевые функции включают проверку, вероятно ли что-то сгенерировано (`is_likely_generated`), разбиение имени файла на токены (`get_tokens`), определение роли файла (`get_file_role`), генерацию краткого описания для недорогих модулей (`get_cheap_description`), построение графа импортов между файлами (`build_import_graph`), вычисление важности файлов (`calculate_importance_scores`) и классификацию файлов в категории ('detailed', 'cheap', 'batch', 'ignored') на основе их оценок важности и роли (`prioritize_files`).

### `codetree/cli.py`
  - **File Size**: 180 code lines
  - **Declarations**: 1 classes/functions
  - **Role**: `entry_point`
  - **Importance Score**: 71.0
  - **Purpose**:
    Файл `cli.py` содержит основную логику командной строки для приложения. В нём определена функция `main()`, которая отвечает за запуск программы и обработку пользовательского ввода.

### `codetree/frameworks.py`
  - **File Size**: 143 code lines
  - **Declarations**: 5 classes/functions
  - **Role**: `core_logic`
  - **Importance Score**: 62.9
  - **Purpose**:
    Файл `frameworks.py` содержит набор функций для анализа различных файлов конфигурации проекта, таких как `package.json`, `requirements.txt`, `Cargo.toml` и `go.mod`. Ключевая функция `detect_frameworks` сканирует эти файлы и маркерные файлы, чтобы определить используемые в проекте фреймворки. Она возвращает словарь с названиями фреймворков и соответствующими файлами, от которых они были обнаружены.
    
    The `frameworks.py` file includes a set of functions for analyzing various configuration files in a project, such as `package.json`, `requirements.txt`, `Cargo.toml`, and `go.mod`. The key function, `detect_frameworks`, scans these files and marker files to identify the frameworks used in the project. It returns a dictionary with framework names and the corresponding files from which they were detected.

### `tests/test_codetree.py`
  - **File Size**: 131 code lines
  - **Declarations**: 11 classes/functions
  - **Role**: `test`
  - **Importance Score**: 61.3
  - **Purpose**:
    Файл `test_codetree.py` содержит набор тестов для различных аспектов сканера кода, который анализирует структуру и содержимое проектов. Ключевые функции включают подсчет строк кода, определение языков программирования и их статистики, обнаружение фреймворков и приоритизацию файлов в проекте.

### `codetree/llm_client.py`
  - **File Size**: 126 code lines
  - **Declarations**: 7 classes/functions
  - **Role**: `core_logic`
  - **Importance Score**: 56.8
  - **Purpose**:
    Файл `llm_client.py` содержит класс `LLMClient`, который предназначен для взаимодействия с языковым моделем через API. Ключевые функции включают отправку запросов на получение сводок по отдельным файлам и пакету файлов, а также парсинг ответов модели и соответствование результатов файлам.

### `codetree/reporter.py`
  - **File Size**: 124 code lines
  - **Declarations**: 5 classes/functions
  - **Role**: `General Module`
  - **Importance Score**: 52.2
  - **Purpose**:
    Файл `reporter.py` отвечает за генерацию отчетов о проекте. Он содержит три ключевых функции: `generate_tree_lines`, которая создает текстовое представление структуры проекта с встроенными краткими описаниями файлов; `generate_language_bar_chart`, которая формирует ASCII-диаграмму, показывающую распределение языков программирования в проекте; и `generate_report`, которая объединяет все эти элементы в окончательный отчет в формате Markdown.

### `codetree/languages.py`
  - **File Size**: 58 code lines
  - **Declarations**: 1 classes/functions
  - **Role**: `General Module`
  - **Importance Score**: 29.4
  - **Purpose**:
    Файл `languages.py` содержит функцию для анализа статистики кода по языкам программирования. Основная функция `calculate_language_stats` принимает метаданные файлов и опциональный параметр для исключения конфигурационных файлов, а возвращает отсортированный список кортежей с названиями языков и их процентом использования кода.

### `tests/test_skeleton_js.py`
  - **File Size**: 37 code lines
  - **Declarations**: 7 classes/functions
  - **Role**: `test`
  - **Importance Score**: 25.1
  - **Purpose**:
    Файл `test_skeleton_js.py` содержит набор юнит-тестов для проверки различных аспектов JavaScript кода, таких как обычные функции, стрелочные функции без блока, шаблонные строки с фигурными скобками, обобщенные типы в TypeScript, классы с методами и комментарии с фигурными скобками. Ключевые функции этого файла - это методы `test_case_1_normal_function`, `test_case_2_arrow_function_no_block`, `test_case_3_template_string_with_braces`, `test_case_4_generic_ts`, `test_case_5_class_with_methods` и `test_case_6_comment_with_brace`, каждый из которых выполняет конкретный тест для проверки различных сценариев JavaScript кода.
