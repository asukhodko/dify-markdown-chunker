"""
Results manager for benchmark data collection and reporting.

Collects, stores, and exports benchmark results in multiple formats.
"""

import json
import os
import platform
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class ResultsManager:
    """Manage benchmark results collection, storage, and reporting."""

    def __init__(self, results_dir: Path):
        """
        Initialize results manager.

        Args:
            results_dir: Directory to store results
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.results = {
            "metadata": self._collect_environment_metadata(),
            "benchmarks": {},
        }

    def _collect_environment_metadata(self) -> Dict[str, str]:
        """
        Collect environment information for reproducibility.

        Returns:
            Dictionary with environment metadata
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "platform": platform.platform(),
            "processor": platform.processor(),
            "machine": platform.machine(),
        }

    def add_benchmark_result(
        self,
        category: str,
        name: str,
        result: Dict[str, Any]
    ):
        """
        Add a benchmark result.

        Args:
            category: Benchmark category (e.g., "size", "content_type")
            name: Benchmark name or identifier
            result: Benchmark result dictionary
        """
        if category not in self.results["benchmarks"]:
            self.results["benchmarks"][category] = {}

        self.results["benchmarks"][category][name] = result

    def save_baseline(self):
        """Save results as baseline for regression detection."""
        baseline_path = self.results_dir / "baseline.json"
        with open(baseline_path, "w") as f:
            json.dump(self.results, f, indent=2)

    def save_latest_run(self):
        """Save results from latest run."""
        latest_path = self.results_dir / "latest_run.json"
        with open(latest_path, "w") as f:
            json.dump(self.results, f, indent=2)

    def load_baseline(self) -> Dict:
        """
        Load baseline results if they exist.

        Returns:
            Baseline results dictionary or empty dict
        """
        baseline_path = self.results_dir / "baseline.json"
        if baseline_path.exists():
            with open(baseline_path, "r") as f:
                return json.load(f)
        return {}

    def generate_markdown_report(self) -> str:
        """
        Generate a markdown report from benchmark results.

        Returns:
            Markdown-formatted report string
        """
        lines = []
        lines.append("# Performance Benchmark Report")
        lines.append("")
        lines.append(f"**Generated**: {self.results['metadata']['timestamp']}")
        lines.append("")

        # Environment information
        lines.append("## Test Environment")
        lines.append("")
        lines.append(f"- **Platform**: {self.results['metadata']['platform']}")
        lines.append(f"- **Python**: {self.results['metadata']['python_version'].split()[0]}")
        lines.append(f"- **Machine**: {self.results['metadata']['machine']}")
        lines.append("")

        # Benchmark results by category
        for category, benchmarks in self.results["benchmarks"].items():
            lines.append(f"## {category.replace('_', ' ').title()} Benchmarks")
            lines.append("")

            if category == "size":
                lines.extend(self._format_size_benchmarks(benchmarks))
            elif category == "content_type":
                lines.extend(self._format_content_type_benchmarks(benchmarks))
            elif category == "strategy":
                lines.extend(self._format_strategy_benchmarks(benchmarks))
            elif category == "config":
                lines.extend(self._format_config_benchmarks(benchmarks))
            elif category == "scalability":
                lines.extend(self._format_scalability_benchmarks(benchmarks))
            else:
                lines.extend(self._format_generic_benchmarks(benchmarks))

            lines.append("")

        return "\n".join(lines)

    def _format_size_benchmarks(self, benchmarks: Dict) -> List[str]:
        """Format size-based benchmark results."""
        lines = []
        lines.append("| Size Category | Avg Time (ms) | Min (ms) | Max (ms) | Throughput (KB/s) | Peak Memory (MB) |")
        lines.append("|---------------|---------------|----------|----------|-------------------|------------------|")

        for size_cat, data in sorted(benchmarks.items()):
            avg_time_ms = data["time"]["mean"] * 1000
            min_time_ms = data["time"]["min"] * 1000
            max_time_ms = data["time"]["max"] * 1000
            throughput = data.get("throughput", {}).get("kb_per_sec", 0)
            memory = data["memory"]["mean"]

            lines.append(
                f"| {size_cat.title()} | {avg_time_ms:.2f} | {min_time_ms:.2f} | "
                f"{max_time_ms:.2f} | {throughput:.1f} | {memory:.2f} |"
            )

        return lines

    def _format_content_type_benchmarks(self, benchmarks: Dict) -> List[str]:
        """Format content type benchmark results."""
        lines = []
        lines.append("| Content Type | Avg Time (ms) | Strategy | Chunks | Avg Chunk Size |")
        lines.append("|--------------|---------------|----------|--------|----------------|")

        for content_type, data in sorted(benchmarks.items()):
            avg_time_ms = data["time"]["mean"] * 1000
            strategy = data.get("strategy", "N/A")
            chunks = data.get("output", {}).get("chunk_count", 0)
            avg_chunk = data.get("output", {}).get("avg_chunk_size", 0)

            lines.append(
                f"| {content_type.replace('_', ' ').title()} | {avg_time_ms:.2f} | "
                f"{strategy} | {chunks} | {avg_chunk:.0f} |"
            )

        return lines

    def _format_strategy_benchmarks(self, benchmarks: Dict) -> List[str]:
        """Format strategy performance results."""
        lines = []
        lines.append("| Strategy | Avg Time (ms) | Documents Tested | Avg Chunks |")
        lines.append("|----------|---------------|------------------|------------|")

        for strategy, data in sorted(benchmarks.items()):
            avg_time_ms = data["time"]["mean"] * 1000
            doc_count = data.get("document_count", 0)
            avg_chunks = data.get("output", {}).get("avg_chunk_count", 0)

            lines.append(
                f"| {strategy} | {avg_time_ms:.2f} | {doc_count} | {avg_chunks:.1f} |"
            )

        return lines

    def _format_config_benchmarks(self, benchmarks: Dict) -> List[str]:
        """Format configuration impact results."""
        lines = []
        lines.append("| Configuration | Avg Time (ms) | Memory (MB) | Relative Performance |")
        lines.append("|---------------|---------------|-------------|----------------------|")

        # Get baseline (default config) for comparison
        baseline_time = benchmarks.get("default", {}).get("time", {}).get("mean", 1.0)

        for config, data in sorted(benchmarks.items()):
            avg_time_ms = data["time"]["mean"] * 1000
            memory = data["memory"]["mean"]
            relative = data["time"]["mean"] / baseline_time if baseline_time > 0 else 1.0

            lines.append(
                f"| {config} | {avg_time_ms:.2f} | {memory:.2f} | {relative:.2f}x |"
            )

        return lines

    def _format_scalability_benchmarks(self, benchmarks: Dict) -> List[str]:
        """Format scalability analysis results."""
        lines = []

        if "regression" in benchmarks:
            reg = benchmarks["regression"]
            lines.append("### Linear Regression Analysis")
            lines.append("")
            lines.append(f"**Processing Time Model**: Time(ms) = {reg.get('coefficient', 0):.4f} × Size(KB) + {reg.get('intercept', 0):.2f}")
            lines.append(f"**R-squared**: {reg.get('r_squared', 0):.4f}")
            lines.append("")

        if "projections" in benchmarks:
            lines.append("### Performance Projections")
            lines.append("")
            lines.append("| Document Size | Projected Time | Projected Memory |")
            lines.append("|---------------|----------------|------------------|")

            for proj in benchmarks["projections"]:
                size = proj["size_mb"]
                time_s = proj["time_seconds"]
                memory_mb = proj["memory_mb"]
                lines.append(f"| {size} MB | {time_s:.2f}s | {memory_mb:.1f} MB |")

        return lines

    def _format_generic_benchmarks(self, benchmarks: Dict) -> List[str]:
        """Format generic benchmark results."""
        lines = []
        lines.append("| Benchmark | Avg Time (ms) | Memory (MB) |")
        lines.append("|-----------|---------------|-------------|")

        for name, data in sorted(benchmarks.items()):
            avg_time_ms = data.get("time", {}).get("mean", 0) * 1000
            memory = data.get("memory", {}).get("mean", 0)
            lines.append(f"| {name} | {avg_time_ms:.2f} | {memory:.2f} |")

        return lines

    def save_report(self):
        """Save markdown report to file."""
        report = self.generate_markdown_report()
        report_path = self.results_dir / "performance_report.md"
        with open(report_path, "w") as f:
            f.write(report)

    def export_csv(self, category: str = None):
        """
        Export results to CSV format.

        Args:
            category: Specific category to export, or None for all
        """
        import csv

        csv_path = self.results_dir / f"results_{category or 'all'}.csv"

        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow([
                "Category", "Name", "Avg Time (s)", "Min Time (s)",
                "Max Time (s)", "Stddev Time", "Avg Memory (MB)",
                "Peak Memory (MB)"
            ])

            # Write data
            benchmarks = self.results["benchmarks"]
            if category:
                benchmarks = {category: benchmarks.get(category, {})}

            for cat, results in benchmarks.items():
                for name, data in results.items():
                    writer.writerow([
                        cat,
                        name,
                        data.get("time", {}).get("mean", 0),
                        data.get("time", {}).get("min", 0),
                        data.get("time", {}).get("max", 0),
                        data.get("time", {}).get("stddev", 0),
                        data.get("memory", {}).get("mean", 0),
                        data.get("memory", {}).get("max", 0),
                    ])

    def print_summary(self):
        """Print a console summary of results."""
        print("\n" + "=" * 70)
        print("PERFORMANCE BENCHMARK SUMMARY")
        print("=" * 70)

        for category, benchmarks in self.results["benchmarks"].items():
            print(f"\n{category.upper()}:")
            for name, data in list(benchmarks.items())[:5]:  # First 5 per category
                avg_time_ms = data.get("time", {}).get("mean", 0) * 1000
                print(f"  {name}: {avg_time_ms:.2f}ms")

        print("\n" + "=" * 70)
