# Целевая Архитектура: Стратегия Тестирования

## Обзор

Переход от 1853 тестов (~45K строк) к ~50 тестам (~2K строк).

**Принцип:** Тестировать ЧТО система делает (доменные свойства), а не КАК она это делает (реализацию).

## Целевые метрики

| Метрика | Текущее | Целевое | Изменение |
|---------|---------|---------|-----------|
| Тестовых файлов | 162 | ~10 | -94% |
| Тестов | 1853 | ~50 | -97% |
| Строк тестов | ~45,600 | ~2,000 | -96% |
| Соотношение тесты/код | 1.9x | 0.4x | -79% |

## Структура тестов

```
tests/
├── conftest.py              # Общие фикстуры
├── test_properties.py       # 10 property-based тестов (доменные свойства)
├── test_design_fixes.py     # 6 property-based тестов (исправления дизайна)
├── test_integration.py      # 1 интеграционный тест (full pipeline)
├── test_edge_cases.py       # ~10 тестов на граничные случаи
├── test_serialization.py    # Round-trip тесты
└── fixtures/
    └── corpus/              # Тестовый корпус реальных документов
        ├── code_heavy/      # Документы с преобладанием кода
        ├── structured/      # Структурированные документы
        ├── mixed/           # Смешанный контент
        ├── simple/          # Простые документы
        └── edge_cases/      # Граничные случаи
```

## Тестовый корпус

Для валидации редизайна создаётся корпус из 15+ реальных markdown документов:

| Категория | Документы | Назначение |
|-----------|-----------|------------|
| code_heavy | python_tutorial.md, api_reference.md, code_snippets.md | Тестирование CodeAwareStrategy |
| structured | user_guide.md, architecture_doc.md, faq.md | Тестирование StructuralStrategy |
| mixed | readme.md, changelog.md, contributing.md | Тестирование смешанного контента |
| simple | notes.md, todo.md, blog_post.md | Тестирование FallbackStrategy |
| edge_cases | nested_code_blocks.md, large_tables.md, mixed_line_endings.md, unicode_heavy.md | Граничные случаи |

## Baseline Comparison

Перед редизайном сохраняются baseline результаты для сравнения:

```python
# scripts/save_baseline.py
def save_baseline(corpus_dir: Path, output_file: Path):
    """Сохранить baseline результаты для всех документов корпуса."""
    chunker = MarkdownChunker()
    results = {}
    
    for doc_path in corpus_dir.rglob("*.md"):
        content = doc_path.read_text()
        result = chunker.chunk(content)
        results[str(doc_path.relative_to(corpus_dir))] = {
            'chunk_count': len(result.chunks),
            'strategy_used': result.strategy_used,
            'chunks': [c.to_dict() for c in result.chunks]
        }
    
    output_file.write_text(json.dumps(results, indent=2))
```

## Rollback Criteria

| Метрика | Порог | Действие |
|---------|-------|----------|
| Chunk count difference | >5% | Review required |
| Content loss | >1% | Rollback |
| Property test failures | Any | Rollback |
| Table integrity errors | Any | Rollback |
| Fence balance errors | >1% increase | Review required |

## Property-Based тесты (test_properties.py)

### Критические свойства (MUST HAVE)

```python
"""
Property-based тесты для критических доменных свойств.

Используем Hypothesis для генерации тестовых данных.
"""

from hypothesis import given, strategies as st, settings
from markdown_chunker import MarkdownChunker, ChunkConfig


# Генератор валидного markdown
markdown_text = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')),
    min_size=1,
    max_size=10000
).filter(lambda x: x.strip())


class TestCriticalProperties:
    """Критические свойства системы."""
    
    @given(md_text=markdown_text)
    @settings(max_examples=100)
    def test_prop1_no_content_loss(self, md_text: str):
        """
        PROP-1: No Content Loss
        
        ∀ doc ∈ ValidMarkdown:
          concat(chunks) - overlaps ≡ doc
        """
        chunker = MarkdownChunker()
        result = chunker.chunk(md_text, include_analysis=True)
        
        # Собрать контент из чанков (без overlap)
        reconstructed = ""
        for i, chunk in enumerate(result.chunks):
            if i == 0:
                reconstructed += chunk.content
            else:
                overlap_size = chunk.metadata.get("overlap_size", 0)
                reconstructed += chunk.content[overlap_size:]
        
        # Нормализовать whitespace для сравнения
        original_normalized = ' '.join(md_text.split())
        reconstructed_normalized = ' '.join(reconstructed.split())
        
        assert original_normalized == reconstructed_normalized
    
    @given(md_text=markdown_text)
    @settings(max_examples=100)
    def test_prop2_size_bounds(self, md_text: str):
        """
        PROP-2: Chunk Size Bounds
        
        ∀ chunk ∈ Chunks:
          len(chunk.content) ≤ max_chunk_size 
          ∨ chunk.metadata["allow_oversize"] = True
        """
        config = ChunkConfig(max_chunk_size=1000)
        chunker = MarkdownChunker(config)
        result = chunker.chunk(md_text, include_analysis=True)
        
        for chunk in result.chunks:
            assert (
                len(chunk.content) <= config.max_chunk_size or
                chunk.metadata.get("allow_oversize", False)
            )
    
    @given(md_text=markdown_text)
    @settings(max_examples=100)
    def test_prop3_monotonic_ordering(self, md_text: str):
        """
        PROP-3: Monotonic Ordering
        
        ∀ i < j: chunks[i].start_line ≤ chunks[j].start_line
        """
        chunker = MarkdownChunker()
        result = chunker.chunk(md_text, include_analysis=True)
        
        for i in range(len(result.chunks) - 1):
            assert result.chunks[i].start_line <= result.chunks[i + 1].start_line
    
    @given(md_text=markdown_text)
    @settings(max_examples=100)
    def test_prop4_no_empty_chunks(self, md_text: str):
        """
        PROP-4: No Empty Chunks
        
        ∀ chunk ∈ Chunks: chunk.content.strip() ≠ ""
        """
        chunker = MarkdownChunker()
        result = chunker.chunk(md_text, include_analysis=True)
        
        for chunk in result.chunks:
            assert chunk.content.strip() != ""
    
    @given(md_text=markdown_text)
    @settings(max_examples=100)
    def test_prop5_valid_line_numbers(self, md_text: str):
        """
        PROP-5: Valid Line Numbers
        
        ∀ chunk ∈ Chunks:
          chunk.start_line ≥ 1 ∧ chunk.end_line ≥ chunk.start_line
        """
        chunker = MarkdownChunker()
        result = chunker.chunk(md_text, include_analysis=True)
        
        for chunk in result.chunks:
            assert chunk.start_line >= 1
            assert chunk.end_line >= chunk.start_line
```

### Важные свойства (SHOULD HAVE)

```python
class TestImportantProperties:
    """Важные свойства системы."""
    
    @given(md_text=markdown_text)
    @settings(max_examples=100)
    def test_prop9_idempotence(self, md_text: str):
        """
        PROP-9: Idempotence
        
        ∀ doc ∈ ValidMarkdown:
          chunk(doc) ≡ chunk(doc)  (повторный вызов даёт идентичный результат)
        """
        chunker = MarkdownChunker()
        
        result1 = chunker.chunk(md_text)
        result2 = chunker.chunk(md_text)
        
        assert len(result1.chunks) == len(result2.chunks)
        for c1, c2 in zip(result1.chunks, result2.chunks):
            assert c1.content == c2.content
            assert c1.start_line == c2.start_line
            assert c1.end_line == c2.end_line


class TestImportantPropertiesOther:
    """Важные свойства системы."""
    
    @given(md_text=st.text(min_size=10).filter(lambda x: '```' in x))
    @settings(max_examples=50)
    def test_prop6_code_block_integrity(self, md_text: str):
        """
        PROP-6: Code Block Integrity
        
        ∀ code_block ∈ doc.code_blocks:
          ∃! chunk ∈ Chunks: code_block ⊆ chunk.content
        """
        # Добавить валидный code block
        md_with_code = f"Text before\n\n```python\nprint('hello')\n```\n\nText after"
        
        chunker = MarkdownChunker()
        result = chunker.chunk(md_with_code, include_analysis=True)
        
        # Проверить, что code block не разбит
        code_block = "```python\nprint('hello')\n```"
        found_in_chunks = sum(
            1 for chunk in result.chunks 
            if code_block in chunk.content
        )
        
        assert found_in_chunks == 1, "Code block должен быть в ровно одном чанке"
    
    @given(md_text=st.text(min_size=10))
    @settings(max_examples=50)
    def test_prop7_table_integrity(self, md_text: str):
        """
        PROP-7: Table Integrity
        
        ∀ table ∈ doc.tables:
          ∃! chunk ∈ Chunks: table ⊆ chunk.content
        """
        # Добавить валидную таблицу
        md_with_table = """Text before

| Col1 | Col2 |
|------|------|
| A    | B    |
| C    | D    |

Text after"""
        
        chunker = MarkdownChunker()
        result = chunker.chunk(md_with_table, include_analysis=True)
        
        # Проверить, что таблица не разбита
        table_header = "| Col1 | Col2 |"
        found_in_chunks = sum(
            1 for chunk in result.chunks 
            if table_header in chunk.content
        )
        
        assert found_in_chunks == 1, "Таблица должна быть в ровно одном чанке"
    
    def test_prop8_serialization_roundtrip(self):
        """
        PROP-8: Serialization Round-Trip
        
        ∀ result ∈ ChunkingResult:
          ChunkingResult.from_dict(result.to_dict()) ≡ result
        """
        from markdown_chunker import ChunkingResult
        
        chunker = MarkdownChunker()
        original = chunker.chunk("# Test\n\nContent", include_analysis=True)
        
        # Round-trip
        as_dict = original.to_dict()
        restored = ChunkingResult.from_dict(as_dict)
        
        assert len(restored.chunks) == len(original.chunks)
        assert restored.strategy_used == original.strategy_used
        for orig, rest in zip(original.chunks, restored.chunks):
            assert orig.content == rest.content
            assert orig.start_line == rest.start_line
            assert orig.end_line == rest.end_line
```

## Интеграционный тест (test_integration.py)

```python
"""
Интеграционный тест полного pipeline.
"""

import pytest
from pathlib import Path
from markdown_chunker import MarkdownChunker, ChunkConfig


class TestFullPipeline:
    """Тест полного pipeline на реальных документах."""
    
    @pytest.fixture
    def sample_docs(self):
        """Загрузить тестовые документы."""
        docs_dir = Path(__file__).parent / "fixtures" / "sample_docs"
        return {
            "code_heavy": (docs_dir / "code_heavy.md").read_text(),
            "structured": (docs_dir / "structured.md").read_text(),
            "mixed": (docs_dir / "mixed.md").read_text(),
            "simple": (docs_dir / "simple.md").read_text(),
        }
    
    def test_full_pipeline_all_docs(self, sample_docs):
        """Проверить pipeline на всех типах документов."""
        chunker = MarkdownChunker()
        
        for doc_type, content in sample_docs.items():
            result = chunker.chunk(content, include_analysis=True)
            
            # Базовые проверки
            assert result.success, f"Failed for {doc_type}"
            assert len(result.chunks) > 0, f"No chunks for {doc_type}"
            assert result.strategy_used in ["code_aware", "structural", "fallback"]
            
            # Проверить доменные свойства
            self._verify_properties(result, content)
    
    def _verify_properties(self, result, original_content):
        """Проверить все доменные свойства."""
        # PROP-1: No content loss (упрощённая проверка)
        total_content = sum(len(c.content) for c in result.chunks)
        assert total_content >= len(original_content) * 0.95
        
        # PROP-2: Size bounds
        for chunk in result.chunks:
            assert (
                chunk.size <= 4096 or 
                chunk.metadata.get("allow_oversize", False)
            )
        
        # PROP-3: Monotonic ordering
        for i in range(len(result.chunks) - 1):
            assert result.chunks[i].start_line <= result.chunks[i + 1].start_line
        
        # PROP-4: No empty chunks
        for chunk in result.chunks:
            assert chunk.content.strip()
        
        # PROP-5: Valid line numbers
        for chunk in result.chunks:
            assert chunk.start_line >= 1
            assert chunk.end_line >= chunk.start_line
```

## Тесты граничных случаев (test_edge_cases.py)

```python
"""
Тесты граничных случаев.

Минимальный набор — только критичные edge cases.
"""

import pytest
from markdown_chunker import MarkdownChunker, ChunkConfig


class TestEdgeCases:
    """Граничные случаи."""
    
    def test_empty_input(self):
        """Пустой вход."""
        chunker = MarkdownChunker()
        result = chunker.chunk("", include_analysis=True)
        assert len(result.chunks) == 0
    
    def test_whitespace_only(self):
        """Только пробелы."""
        chunker = MarkdownChunker()
        result = chunker.chunk("   \n\n   ", include_analysis=True)
        assert len(result.chunks) == 0
    
    def test_single_character(self):
        """Один символ."""
        chunker = MarkdownChunker()
        result = chunker.chunk("X", include_analysis=True)
        assert len(result.chunks) == 1
        assert result.chunks[0].content == "X"
    
    def test_very_long_line(self):
        """Очень длинная строка без переносов."""
        chunker = MarkdownChunker(ChunkConfig(max_chunk_size=100))
        long_line = "word " * 100  # 500 символов
        result = chunker.chunk(long_line, include_analysis=True)
        
        # Должен разбить на несколько чанков
        assert len(result.chunks) > 1
    
    def test_oversized_code_block(self):
        """Code block больше max_chunk_size."""
        chunker = MarkdownChunker(ChunkConfig(max_chunk_size=100))
        large_code = "```python\n" + "x = 1\n" * 50 + "```"
        result = chunker.chunk(large_code, include_analysis=True)
        
        # Code block не должен быть разбит
        assert any("```python" in c.content and "```" in c.content 
                   for c in result.chunks)
    
    def test_nested_code_blocks(self):
        """Вложенные code blocks (markdown в markdown)."""
        md = '''
````markdown
```python
print("hello")
```
````
'''
        chunker = MarkdownChunker()
        result = chunker.chunk(md, include_analysis=True)
        
        # Внешний блок не должен быть разбит
        assert len(result.chunks) >= 1
    
    def test_unicode_content(self):
        """Unicode контент."""
        md = "# Заголовок 🎉\n\nТекст с эмодзи 👍 и кириллицей"
        chunker = MarkdownChunker()
        result = chunker.chunk(md, include_analysis=True)
        
        assert len(result.chunks) >= 1
        assert "🎉" in result.chunks[0].content
    
    def test_mixed_line_endings(self):
        """Смешанные переносы строк."""
        md = "Line1\r\nLine2\nLine3\rLine4"
        chunker = MarkdownChunker()
        result = chunker.chunk(md, include_analysis=True)
        
        assert len(result.chunks) >= 1
    
    def test_deeply_nested_headers(self):
        """Глубоко вложенные заголовки."""
        md = "\n".join([f"{'#' * i} Header {i}" for i in range(1, 7)])
        chunker = MarkdownChunker()
        result = chunker.chunk(md, include_analysis=True)
        
        assert len(result.chunks) >= 1
    
    def test_table_at_document_end(self):
        """Таблица в конце документа."""
        md = """# Title

| A | B |
|---|---|
| 1 | 2 |"""
        chunker = MarkdownChunker()
        result = chunker.chunk(md, include_analysis=True)
        
        # Таблица должна быть целой
        assert any("| A | B |" in c.content for c in result.chunks)
```

## Удаляемые тесты

### Категории для удаления

1. **Тесты реализации** — тестируют КАК работает, а не ЧТО
   - `test_strategy_selector.py` — внутренняя логика выбора
   - `test_fallback_manager.py` — механизм fallback
   - `test_orchestrator.py` — оркестрация

2. **Дублирующие тесты** — одно и то же в разных местах
   - `test_overlap_properties.py` + `test_overlap_properties_redesign.py`
   - `test_full_pipeline.py` + `test_end_to_end.py` + `test_full_api_flow.py`

3. **Тесты для багфиксов** — фиксируют реализацию
   - `test_critical_fixes.py`
   - `test_phase2_properties.py`
   - `test_overlap_duplication.py`

4. **Тесты отдельных стратегий** — объединить в один параметризованный
   - `test_code_strategy_properties.py`
   - `test_list_strategy_properties.py`
   - `test_mixed_strategy_properties.py`
   - `test_structural_strategy_properties.py`
   - `test_table_strategy_properties.py`
   - `test_sentences_strategy_properties.py`

### Сохраняемые тесты

- Property-based тесты для доменных свойств (переписать)
- Один интеграционный тест
- Минимальный набор edge cases
- Round-trip тесты для сериализации

## Дополнительные property-based тесты (Design Fixes)

```python
# tests/test_design_fixes.py
"""
Property-based тесты для исправлений дизайна.
"""

class TestDesignFixesProperties:
    """Property-based тесты для исправлений дизайна."""
    
    @given(md_text=markdown_text)
    @settings(max_examples=100)
    def test_line_ending_normalization(self, md_text: str):
        """
        Property: Line Ending Normalization
        
        ∀ doc: после обработки нет \r в контенте чанков
        **Validates: Requirements 6.1, 6.2, 6.3**
        """
        md_with_crlf = md_text.replace('\n', '\r\n')
        
        chunker = MarkdownChunker()
        result = chunker.chunk(md_with_crlf)
        
        for chunk in result.chunks:
            assert '\r' not in chunk.content
    
    @given(md_text=markdown_text)
    @settings(max_examples=100)
    def test_oversize_metadata_correctness(self, md_text: str):
        """
        Property: Oversize Metadata Correctness
        
        ∀ chunk с size > max_chunk_size: 
          allow_oversize=True AND oversize_reason ∈ {valid_reasons}
        **Validates: Requirements 5.1, 5.3**
        """
        config = ChunkConfig(max_chunk_size=500)
        chunker = MarkdownChunker(config)
        result = chunker.chunk(md_text)
        
        VALID_REASONS = {'code_block_integrity', 'table_integrity', 'section_integrity'}
        
        for chunk in result.chunks:
            if chunk.size > config.max_chunk_size:
                assert chunk.metadata.get("allow_oversize") == True
                assert chunk.metadata.get("oversize_reason") in VALID_REASONS
    
    def test_code_fence_balance(self):
        """
        Property: Code Fence Balance
        
        ∀ chunk: fence_count % 2 == 0 OR fence_balance_error=True
        **Validates: Requirements 3.1, 3.2**
        """
        md_with_code = "```python\nprint('hello')\n```\n\nText\n\n```js\nconsole.log('hi')\n```"
        
        chunker = MarkdownChunker(ChunkConfig(max_chunk_size=50))
        result = chunker.chunk(md_with_code)
        
        for chunk in result.chunks:
            fence_count = chunk.content.count('```')
            assert fence_count % 2 == 0 or chunk.metadata.get("fence_balance_error")
    
    def test_table_integrity(self):
        """
        Property: Table Integrity
        
        ∀ table: table содержится в ровно одном чанке
        **Validates: Requirements 4.1, 4.2, 4.3**
        """
        md_with_table = """# Title

| Col1 | Col2 | Col3 |
|------|------|------|
| A    | B    | C    |
| D    | E    | F    |

Some text after table."""
        
        chunker = MarkdownChunker()
        result = chunker.chunk(md_with_table)
        
        table_header = "| Col1 | Col2 | Col3 |"
        containing_chunks = [c for c in result.chunks if table_header in c.content]
        
        assert len(containing_chunks) == 1
    
    def test_overlap_integrity(self):
        """
        Property: Overlap Integrity
        
        ∀ chunk с overlap: previous_content является суффиксом предыдущего чанка
        **Validates: Requirements 2.1, 2.2, 2.3**
        """
        md = "A" * 1000 + "\n\n" + "B" * 1000
        
        chunker = MarkdownChunker(ChunkConfig(max_chunk_size=500, overlap_size=100))
        result = chunker.chunk(md)
        
        for i in range(1, len(result.chunks)):
            chunk = result.chunks[i]
            prev_chunk = result.chunks[i - 1]
            
            previous_content = chunk.metadata.get("previous_content", "")
            if previous_content:
                assert prev_chunk.content.endswith(previous_content)
```

## Миграция тестов

### Фаза 1: Создание новых тестов

1. Написать 10 property-based тестов (PROP-1 через PROP-10)
2. Написать 6 property-based тестов для design fixes
3. Написать 1 интеграционный тест
4. Написать ~10 edge case тестов
5. Убедиться, что текущий код проходит новые тесты

### Фаза 2: Параллельный запуск

1. Запускать и старые, и новые тесты
2. Сравнивать результаты
3. Фиксировать расхождения

### Фаза 3: Удаление старых тестов

1. После успешного редизайна удалить старые тесты
2. Оставить только новые
3. Обновить CI/CD
