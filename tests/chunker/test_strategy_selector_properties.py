"""
Property-based tests for strategy selector.

Tests Property 5: Strategy Selection Consistency
Validates: Requirements 2.2, 3.2
"""

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.selector import StrategySelector
from markdown_chunker.chunker.strategies import (
    CodeStrategy,
    ListStrategy,
    MixedStrategy,
    SentencesStrategy,
    StructuralStrategy,
    TableStrategy,
)
from markdown_chunker.chunker.types import ChunkConfig


# Test configuration
@pytest.fixture
def config():
    """Create chunk config."""
    return ChunkConfig(max_chunk_size=2000)


@pytest.fixture
def chunker(config):
    """Create markdown chunker with config."""
    return MarkdownChunker(config=config)


@pytest.fixture
def parser():
    """Create parser for analysis."""
    from markdown_chunker.parser import ParserInterface

    return ParserInterface()


@pytest.fixture
def selector():
    """Create strategy selector with all strategies."""
    strategies = [
        CodeStrategy(),
        MixedStrategy(),
        ListStrategy(),
        TableStrategy(),
        StructuralStrategy(),
        SentencesStrategy(),
    ]
    return StrategySelector(strategies, mode="strict")


# Property 5a: Strategy selection is deterministic
@settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    text_lines=st.integers(min_value=5, max_value=20),
    code_blocks=st.integers(min_value=0, max_value=3),
)
def test_property_selection_is_deterministic(
    selector, parser, config, text_lines, code_blocks
):
    """
    Property 5a: Strategy selection is deterministic.

    For any document, selecting strategy twice should give same result.
    """
    # Generate markdown
    markdown_lines = []

    for i in range(text_lines):
        markdown_lines.append(f"Text line {i}")

    for i in range(code_blocks):
        markdown_lines.append("")
        markdown_lines.append("```python")
        markdown_lines.append(f"code_{i} = {i}")
        markdown_lines.append("```")

    markdown = "\n".join(markdown_lines)

    # Get analysis from parser
    stage1_results = parser.process_document(markdown)
    analysis = stage1_results.analysis

    # Select strategy twice
    selected1 = selector.select_strategy(analysis, config)
    selected2 = selector.select_strategy(analysis, config)

    # Verify same strategy selected
    assert selected1.name == selected2.name, (
        f"Strategy selection should be deterministic. "
        f"First: {selected1.name}, Second: {selected2.name}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
