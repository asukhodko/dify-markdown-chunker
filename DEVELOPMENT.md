# Development Guide

Руководство по разработке и сопровождению плагина Advanced Markdown Chunker для Dify.

---

## Требования

- Python 3.12+
- dify-plugin CLI (для упаковки)
- Git

---

## Установка для разработки

### 1. Клонирование репозитория

```bash
git clone <repository_url>
cd dify-markdown-chunker
```

### 2. Создание виртуального окружения

```bash
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Установка dify-plugin CLI

```bash
# Linux/Mac
curl -L https://github.com/langgenius/dify-plugin-daemon/releases/latest/download/dify-plugin-linux-amd64 -o /tmp/dify-plugin
chmod +x /tmp/dify-plugin
sudo mv /tmp/dify-plugin /usr/local/bin/dify-plugin

# Проверка
dify-plugin version
```

---

## Структура проекта

```
dify-markdown-chunker/
├── manifest.yaml              # Метаданные плагина
├── main.py                    # Точка входа
├── requirements.txt           # Зависимости
├── _assets/
│   └── icon.svg              # Иконка плагина
├── provider/
│   ├── markdown_chunker.yaml # Конфигурация провайдера
│   └── markdown_chunker.py   # Класс провайдера
├── tools/
│   ├── markdown_chunk_tool.yaml  # Конфигурация инструмента
│   └── markdown_chunk_tool.py    # Логика чанкования
├── markdown_chunker/         # Библиотека чанкования
│   ├── api/
│   ├── chunker/
│   └── parser/
└── tests/                    # Тесты
```

---

## Разработка

### Запуск тестов

```bash
# Все тесты
make test

# Быстрые тесты
make test-quick

# Конкретный тест
venv/bin/pytest tests/test_manifest.py -v
```

### Линтинг

```bash
make lint
```

### Валидация

```bash
# Валидация структуры, синтаксиса, YAML
make validate
```

---

## Упаковка

### Создание пакета

```bash
make package
```

Создаёт: `dify-markdown-chunker-official-YYYYMMDD_HHMMSS.difypkg`

### Валидация пакета

```bash
make validate-package
```

### Полный релиз

```bash
make release
```

Выполняет: validate → test → lint → package → validate-package

---

## Важные правила

### 1. Пути к иконкам

**В YAML файлах всегда указывать без пути:**
```yaml
icon: icon.svg  # ✅ Правильно
icon: _assets/icon.svg  # ❌ Неправильно
```

**Физический файл:**
```
_assets/icon.svg  # ✅ Здесь должен быть файл
```

### 2. Теги

**Использовать только стандартные теги:**
- `productivity`
- `business`
- `social`
- `search`
- `news`
- `weather`

**Кастомные теги не проходят валидацию CLI:**
```yaml
tags:
  - productivity  # ✅ Правильно
  - business      # ✅ Правильно
  - rag           # ❌ Не пройдёт валидацию
```

### 3. Исключение файлов

**CLI использует `.gitignore` для исключения файлов из пакета.**

Обязательно исключить:
- `venv/`
- `__pycache__/`
- `tests/`
- `*.md` (кроме README.md)
- `*.difypkg`

### 4. Размер пакета

Максимальный размер: **50 MB** (несжатый)

CLI автоматически проверяет при упаковке.

---

## Отладка

### Debug режим

1. Создайте `.env` из `.env.example`:
```bash
cp .env.example .env
```

2. Получите debug key из Dify UI:
```
Settings → Plugins → Debug Mode
```

3. Обновите `.env`:
```env
INSTALL_METHOD=remote
REMOTE_INSTALL_HOST=https://debug.dify.ai
REMOTE_INSTALL_PORT=5003
REMOTE_INSTALL_KEY=your_debug_key_here
```

4. Запустите плагин:
```bash
python main.py
```

**⚠️ Важно:** Удалите `.env` перед упаковкой!

---

## Тестирование в Dify

### 1. Импорт плагина

```
Dify UI → Settings → Plugins → Install Plugin
→ Загрузите .difypkg файл
```

### 2. Использование в Knowledge Base

```
Knowledge Base → Chunking Settings
→ Custom → Advanced Markdown Chunker
```

### 3. Использование в Workflow

```
Workflow → Add Tool Node
→ Advanced Markdown Chunker
```

---

## Обновление версии

### 1. Обновите версию в manifest.yaml

```yaml
version: 2.0.1  # Новая версия
meta:
  version: 2.0.1  # Тоже обновить
```

### 2. Обновите CHANGELOG.md

```markdown
## [2.0.1] - YYYY-MM-DD

### Fixed
- Описание исправления

### Added
- Описание нового функционала
```

### 3. Создайте пакет

```bash
make release
```

### 4. Протестируйте

```bash
# Импортируйте в Dify
# Проверьте функциональность
```

---

## Troubleshooting

### Ошибка: "tool icon not found"

**Причина:** Неправильный путь к иконке в YAML

**Решение:**
```bash
# Проверьте все YAML файлы
grep -r "icon:" *.yaml provider/*.yaml tools/*.yaml

# Должно быть везде: icon: icon.svg
```

### Ошибка: "Plugin package size is too large"

**Причина:** venv/ включён в пакет

**Решение:**
```bash
# Убедитесь, что venv/ в .gitignore
echo "venv/" >> .gitignore
```

### Ошибка: "failed to package plugin: ... tag"

**Причина:** Кастомные теги не проходят валидацию

**Решение:**
```yaml
# Используйте только стандартные теги
tags:
  - productivity
  - business
```

### Тесты не проходят

**Решение:**
```bash
# Проверьте, что venv активирован
source venv/bin/activate

# Переустановите зависимости
pip install -r requirements.txt

# Запустите тесты с подробным выводом
venv/bin/pytest tests/ -v
```

---

## CI/CD

### GitHub Actions (пример)

```yaml
name: Build and Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          python -m venv venv
          source venv/bin/activate
          pip install -r requirements.txt
      
      - name: Run tests
        run: make test
      
      - name: Run lint
        run: make lint
      
      - name: Validate
        run: make validate
```

---

## Полезные команды

```bash
# Показать все команды
make help

# Очистить временные файлы
make clean

# Установить зависимости
make install

# Валидация структуры
python validate_structure.py

# Валидация синтаксиса
python validate_syntax.py

# Валидация YAML
python validate_yaml.py

# Валидация пакета
python validate_package.py <package>.difypkg
```

---

## Ресурсы

- **Официальные плагины Dify:** `reference/dify-official-plugins/`
- **Документация Dify:** https://docs.dify.ai/plugins
- **CLI репозиторий:** https://github.com/langgenius/dify-plugin-daemon
- **Dify GitHub:** https://github.com/langgenius/dify

---

## Контакты

- **Issues:** [GitHub Issues]
- **Discord:** [Dify Community](https://discord.gg/FngNHpbcY7)
