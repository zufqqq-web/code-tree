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
│   ├── cli.py                                # Файл важен (score 71.0), но детальный анализ недоступен без LL...
│   ├── frameworks.py                         # Файл важен (score 62.9), но детальный анализ недоступен без LL...
│   ├── languages.py                          # Файл важен (score 29.4), но детальный анализ недоступен без LL...
│   ├── llm_client.py                         # Файл важен (score 56.8), но детальный анализ недоступен без LL...
│   ├── prioritization.py                     # Файл важен (score 101.3), но детальный анализ недоступен без L...
│   ├── reporter.py                           # Файл важен (score 52.2), но детальный анализ недоступен без LL...
│   ├── scanner.py                            # Файл важен (score 122.4), но детальный анализ недоступен без L...
│   └── skeleton.py                           # Файл важен (score 137.8), но детальный анализ недоступен без L...
├── codetree.egg-info/
│   ├── dependency_links.txt                  # Короткий файл (0 строк): (пустой файл)
│   ├── entry_points.txt                      # Короткий файл (2 строк): [console_scripts]
codetree = codetree...
│   ├── PKG-INFO                              # Файл важен (score 17.7), но детальный анализ недоступен без LL...
│   ├── SOURCES.txt                           # Файл SOURCES.txt (роль не определена однозначно).
│   └── top_level.txt                         # Короткий файл (1 строк): codetree
├── tests/
│   ├── test_codetree.py                      # Файл важен (score 61.3), но детальный анализ недоступен без LL...
│   └── test_skeleton_js.py                   # Файл важен (score 25.1), но детальный анализ недоступен без LL...
├── firsttest.md                              # Файл firsttest.md (роль не определена однозначно).
├── pyproject.toml                            # Файл pyproject.toml (роль не определена однозначно).
└── README.md                                 # Файл README.md (роль не определена однозначно).
```

## Programming Language Distribution
  - **Python** : `█████████████████░░░` **87.0%**
  - **MD    ** : `█░░░░░░░░░░░░░░░░░░░` **7.8%**
  - **Other ** : `░░░░░░░░░░░░░░░░░░░░` **3.0%**
  - **TOML  ** : `░░░░░░░░░░░░░░░░░░░░` **1.1%**
  - **TXT   ** : `░░░░░░░░░░░░░░░░░░░░` **1.1%**


## Detected Frameworks and Libraries
  - *No framework signatures detected.*


## Detailed Module Analysis
### `codetree/skeleton.py`
  - **File Size**: 346 code lines
  - **Declarations**: 7 classes/functions
  - **Role**: `General Module`
  - **Importance Score**: 137.8
  - **Purpose**:
    Файл важен (score 137.8), но детальный анализ недоступен без LLM (запустите без --no-llm)

### `codetree/scanner.py`
  - **File Size**: 308 code lines
  - **Declarations**: 10 classes/functions
  - **Role**: `core_logic`
  - **Importance Score**: 122.4
  - **Purpose**:
    Файл важен (score 122.4), но детальный анализ недоступен без LLM (запустите без --no-llm)

### `codetree/prioritization.py`
  - **File Size**: 241 code lines
  - **Declarations**: 7 classes/functions
  - **Role**: `core_logic`
  - **Importance Score**: 101.3
  - **Purpose**:
    Файл важен (score 101.3), но детальный анализ недоступен без LLM (запустите без --no-llm)

### `codetree/cli.py`
  - **File Size**: 180 code lines
  - **Declarations**: 1 classes/functions
  - **Role**: `entry_point`
  - **Importance Score**: 71.0
  - **Purpose**:
    Файл важен (score 71.0), но детальный анализ недоступен без LLM (запустите без --no-llm)

### `codetree/frameworks.py`
  - **File Size**: 143 code lines
  - **Declarations**: 5 classes/functions
  - **Role**: `core_logic`
  - **Importance Score**: 62.9
  - **Purpose**:
    Файл важен (score 62.9), но детальный анализ недоступен без LLM (запустите без --no-llm)

### `tests/test_codetree.py`
  - **File Size**: 131 code lines
  - **Declarations**: 11 classes/functions
  - **Role**: `test`
  - **Importance Score**: 61.3
  - **Purpose**:
    Файл важен (score 61.3), но детальный анализ недоступен без LLM (запустите без --no-llm)

### `codetree/llm_client.py`
  - **File Size**: 126 code lines
  - **Declarations**: 7 classes/functions
  - **Role**: `core_logic`
  - **Importance Score**: 56.8
  - **Purpose**:
    Файл важен (score 56.8), но детальный анализ недоступен без LLM (запустите без --no-llm)

### `codetree/reporter.py`
  - **File Size**: 124 code lines
  - **Declarations**: 5 classes/functions
  - **Role**: `General Module`
  - **Importance Score**: 52.2
  - **Purpose**:
    Файл важен (score 52.2), но детальный анализ недоступен без LLM (запустите без --no-llm)

### `codetree/languages.py`
  - **File Size**: 58 code lines
  - **Declarations**: 1 classes/functions
  - **Role**: `General Module`
  - **Importance Score**: 29.4
  - **Purpose**:
    Файл важен (score 29.4), но детальный анализ недоступен без LLM (запустите без --no-llm)

### `tests/test_skeleton_js.py`
  - **File Size**: 37 code lines
  - **Declarations**: 7 classes/functions
  - **Role**: `test`
  - **Importance Score**: 25.1
  - **Purpose**:
    Файл важен (score 25.1), но детальный анализ недоступен без LLM (запустите без --no-llm)

### `codetree.egg-info/PKG-INFO`
  - **File Size**: 59 code lines
  - **Declarations**: 0 classes/functions
  - **Role**: `General Module`
  - **Importance Score**: 17.7
  - **Purpose**:
    Файл важен (score 17.7), но детальный анализ недоступен без LLM (запустите без --no-llm)
