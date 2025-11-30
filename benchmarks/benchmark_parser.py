"""
Benchmark the Stage 1 parser.

Measures performance of content analysis and element detection.

Usage:
    python -m benchmarks.benchmark_parser
"""

from datetime import datetime

from markdown_chunker.parser import ParserInterface

from .utils import format_time, generate_markdown_document, measure_all


def benchmark_parser():
    """Benchmark Stage 1 parser performance."""
    sizes=[1, 10, 50, 100]
    parser=ParserInterface()

    print("\n" + "=" * 80)
    print("BENCHMARK: Stage 1 Parser")
    print("=" * 80)
    print(f"{'Size':<15} {'Time':<15} {'Elements':<15}")
    print("-" * 80)

    for size_kb in sizes:
        content=generate_markdown_document(size_kb, "mixed")

        metrics=measure_all(parser.process_document, content)
        result=metrics["result"]
        time_taken=metrics["time"]

        element_count=result.elements.get_element_count()

        print(
            f"{size_kb} KB{'':<10} "
            f"{format_time(time_taken):<15} "
            f"{element_count}"
        )

    print("=" * 80)


def main():
    """Run parser benchmarks."""
    print("\n" + "=" * 80)
    print("PARSER BENCHMARKS")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    benchmark_parser()

    print("\n" + "=" * 80)
    print("BENCHMARKS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
