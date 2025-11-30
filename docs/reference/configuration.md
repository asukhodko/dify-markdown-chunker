# Configuration Guide

## 🎯 Overview

The `stage1.config` module provides a flexible configuration system for all Stage 1 components. It allows fine-tuning of parsing, extraction, detection, and analysis behaviors.

## 📋 Main Configuration Classes

### `Stage1Config`

The main configuration class that orchestrates all component configurations:

```python
from stage1.config import Stage1Config

# Default configuration
config = Stage1Config()

# Custom configuration
config = Stage1Config(
    parser=ParserConfig(preferred_parser="markdown-it-py"),
    extractor=ExtractorConfig(include_positions=True),
    detector=DetectorConfig(generate_anchors=True),
    analyzer=AnalyzerConfig(analyze_languages=True)
)

# Use with interface
from stage1.interface import Stage1Interface
interface = Stage1Interface(config)
```

### Configuration Structure

```python
from stage1.config import (
    Stage1Config, ParserConfig, ExtractorConfig, 
    DetectorConfig, AnalyzerConfig
)

# Complete configuration example
config = Stage1Config(
    # Parser configuration
    parser=ParserConfig(
        preferred_parser="markdown-it-py",
        fallback_parsers=["mistune", "commonmark"],
        enable_positions=True,
        strict_mode=False
    ),
    
    # Fenced block extractor configuration
    extractor=ExtractorConfig(
        include_positions=True,
        handle_nesting=True,
        strict_mode=False,
        max_nesting_depth=10
    ),
    
    # Element detector configuration
    detector=DetectorConfig(
        detect_headers=True,
        detect_lists=True,
        detect_tables=True,
        generate_anchors=True,
        build_hierarchy=True
    ),
    
    # Content analyzer configuration
    analyzer=AnalyzerConfig(
        analyze_languages=True,
        detect_patterns=True,
        calculate_complexity=True,
        include_readability=True
    )
)
```

## 🔧 Component Configurations

### ParserConfig

Configuration for Markdown parsing:

```python
from stage1.config import ParserConfig

config = ParserConfig(
    # Parser selection
    preferred_parser="markdown-it-py",      # Primary parser choice
    fallback_parsers=["mistune", "commonmark"],  # Fallback order
    auto_fallback=True,                     # Auto-fallback on errors
    
    # Parser features
    enable_positions=True,                  # Include position information
    enable_extensions=True,                 # Enable parser extensions
    strict_mode=False,                      # Strict CommonMark compliance
    
    # Performance settings
    max_parse_time=10.0,                   # Maximum parse time (seconds)
    enable_caching=True,                   # Cache parsed results
    
    # Parser-specific options
    parser_options={
        "markdown-it-py": {
            "html": True,                   # Allow HTML
            "linkify": True,               # Auto-link URLs
            "typographer": True            # Enable typographic replacements
        },
        "mistune": {
            "escape": False,               # Don't escape HTML
            "hard_wrap": False             # Don't convert \n to <br>
        }
    }
)
```

### ExtractorConfig

Configuration for fenced block extraction:

```python
from stage1.config import ExtractorConfig

config = ExtractorConfig(
    # Position tracking
    include_positions=True,                 # Include line/column positions
    include_offsets=True,                  # Include character offsets
    
    # Nesting support
    handle_nesting=True,                   # Process nested blocks
    max_nesting_depth=10,                  # Maximum nesting level
    strict_nesting=False,                  # Strict nesting validation
    
    # Block validation
    strict_mode=False,                     # Allow malformed blocks
    require_language=False,                # Require language specification
    validate_syntax=False,                 # Validate code syntax
    
    # Language support
    supported_languages=None,              # None = all languages
    language_aliases={                     # Language name aliases
        "js": "javascript",
        "py": "python",
        "sh": "bash"
    },
    
    # Content processing
    preserve_indentation=True,             # Keep original indentation
    normalize_newlines=True,               # Normalize line endings
    trim_content=False,                    # Trim whitespace from content
    
    # Performance
    max_block_size=100000,                 # Maximum block size (chars)
    enable_caching=True                    # Cache extraction results
)
```

### DetectorConfig

Configuration for element detection:

```python
from stage1.config import DetectorConfig

config = DetectorConfig(
    # Element types to detect
    detect_headers=True,                   # Detect headers (h1-h6)
    detect_lists=True,                     # Detect lists
    detect_tables=True,                    # Detect tables
    detect_blockquotes=True,               # Detect blockquotes
    detect_horizontal_rules=True,          # Detect horizontal rules
    
    # Header processing
    generate_anchors=True,                 # Generate anchor IDs
    build_hierarchy=True,                  # Build header hierarchy
    normalize_anchors=True,                # Normalize anchor format
    anchor_prefix="",                      # Prefix for anchors
    
    # List processing
    detect_task_lists=True,                # Detect task lists (checkboxes)
    normalize_list_markers=True,           # Normalize list markers
    calculate_nesting=True,                # Calculate nesting levels
    
    # Table processing
    detect_alignment=True,                 # Detect column alignment
    normalize_tables=True,                 # Normalize table format
    require_headers=False,                 # Require table headers
    
    # Performance
    max_elements=10000,                    # Maximum elements to detect
    enable_caching=True                    # Cache detection results
)
```

### AnalyzerConfig

Configuration for content analysis:

```python
from stage1.config import AnalyzerConfig

config = AnalyzerConfig(
    # Analysis features
    analyze_languages=True,                # Detect programming languages
    detect_patterns=True,                  # Identify document patterns
    calculate_complexity=True,             # Compute complexity metrics
    include_readability=True,              # Calculate readability scores
    analyze_structure=True,                # Analyze document structure
    
    # Language detection
    min_code_block_size=10,               # Minimum size for detection
    language_confidence_threshold=0.7,     # Confidence threshold
    detect_inline_code=True,              # Analyze inline code
    
    # Complexity calculation
    complexity_weights={                   # Weights for complexity factors
        'nesting': 0.3,                   # Nesting depth weight
        'code_ratio': 0.2,                # Code content weight
        'structure': 0.3,                 # Structure complexity weight
        'length': 0.2                     # Document length weight
    },
    
    # Pattern detection
    pattern_confidence_threshold=0.6,      # Pattern detection threshold
    detect_api_docs=True,                 # Detect API documentation
    detect_tutorials=True,                # Detect tutorial format
    detect_references=True,               # Detect reference manuals
    
    # Performance settings
    max_analysis_time=5.0,                # Maximum analysis time
    enable_caching=True,                  # Cache analysis results
    sample_size=None                      # Sample size for large docs (None = all)
)
```

## 🎯 Configuration Patterns

### Environment-Based Configuration

```python
import os
from stage1.config import Stage1Config, ParserConfig

def create_config_from_env() -> Stage1Config:
    """Create configuration from environment variables."""
    return Stage1Config(
        parser=ParserConfig(
            preferred_parser=os.getenv("STAGE1_PARSER", "markdown-it-py"),
            enable_positions=os.getenv("STAGE1_POSITIONS", "true").lower() == "true",
            strict_mode=os.getenv("STAGE1_STRICT", "false").lower() == "true"
        )
    )

config = create_config_from_env()
```

### Profile-Based Configuration

```python
from stage1.config import Stage1Config

class ConfigProfiles:
    """Predefined configuration profiles."""
    
    @staticmethod
    def fast_processing() -> Stage1Config:
        """Configuration optimized for speed."""
        return Stage1Config(
            parser=ParserConfig(
                preferred_parser="mistune",
                enable_positions=False,
                enable_caching=True
            ),
            analyzer=AnalyzerConfig(
                analyze_languages=False,
                calculate_complexity=False,
                include_readability=False
            )
        )
    
    @staticmethod
    def comprehensive_analysis() -> Stage1Config:
        """Configuration for detailed analysis."""
        return Stage1Config(
            parser=ParserConfig(
                preferred_parser="markdown-it-py",
                enable_positions=True,
                strict_mode=True
            ),
            analyzer=AnalyzerConfig(
                analyze_languages=True,
                detect_patterns=True,
                calculate_complexity=True,
                include_readability=True
            )
        )
    
    @staticmethod
    def code_focused() -> Stage1Config:
        """Configuration optimized for code-heavy documents."""
        return Stage1Config(
            extractor=ExtractorConfig(
                handle_nesting=True,
                validate_syntax=True,
                preserve_indentation=True
            ),
            analyzer=AnalyzerConfig(
                analyze_languages=True,
                detect_patterns=False
            )
        )

# Use profiles
config = ConfigProfiles.fast_processing()
```

### Dynamic Configuration

```python
from stage1.config import Stage1Config
from stage1.content_analyzer import analyze_content

def adaptive_config(md_text: str) -> Stage1Config:
    """Create configuration based on content analysis."""
    # Quick analysis with minimal config
    quick_analysis = analyze_content(md_text)
    
    if quick_analysis.code_ratio > 0.5:
        # Code-heavy document
        return Stage1Config(
            extractor=ExtractorConfig(
                handle_nesting=True,
                validate_syntax=True
            ),
            analyzer=AnalyzerConfig(
                analyze_languages=True
            )
        )
    elif quick_analysis.complexity_score > 0.7:
        # Complex document
        return Stage1Config(
            detector=DetectorConfig(
                build_hierarchy=True,
                generate_anchors=True
            ),
            analyzer=AnalyzerConfig(
                calculate_complexity=True,
                analyze_structure=True
            )
        )
    else:
        # Simple document
        return ConfigProfiles.fast_processing()

# Use adaptive configuration
config = adaptive_config(markdown_text)
```

## 📁 Configuration Files

### JSON Configuration

```python
import json
from stage1.config import Stage1Config

def load_config_from_json(file_path: str) -> Stage1Config:
    """Load configuration from JSON file."""
    with open(file_path, 'r') as f:
        config_data = json.load(f)
    
    return Stage1Config.from_dict(config_data)

def save_config_to_json(config: Stage1Config, file_path: str):
    """Save configuration to JSON file."""
    with open(file_path, 'w') as f:
        json.dump(config.to_dict(), f, indent=2)

# Example JSON structure
config_json = {
    "parser": {
        "preferred_parser": "markdown-it-py",
        "enable_positions": True,
        "strict_mode": False
    },
    "extractor": {
        "include_positions": True,
        "handle_nesting": True,
        "max_nesting_depth": 10
    },
    "detector": {
        "detect_headers": True,
        "generate_anchors": True,
        "build_hierarchy": True
    },
    "analyzer": {
        "analyze_languages": True,
        "calculate_complexity": True
    }
}
```

### YAML Configuration

```python
import yaml
from stage1.config import Stage1Config

def load_config_from_yaml(file_path: str) -> Stage1Config:
    """Load configuration from YAML file."""
    with open(file_path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    return Stage1Config.from_dict(config_data)

# Example YAML file (stage1_config.yaml)
"""
parser:
  preferred_parser: markdown-it-py
  enable_positions: true
  strict_mode: false
  fallback_parsers:
    - mistune
    - commonmark

extractor:
  include_positions: true
  handle_nesting: true
  max_nesting_depth: 10
  supported_languages:
    - python
    - javascript
    - bash

detector:
  detect_headers: true
  detect_lists: true
  detect_tables: true
  generate_anchors: true
  build_hierarchy: true

analyzer:
  analyze_languages: true
  detect_patterns: true
  calculate_complexity: true
  complexity_weights:
    nesting: 0.3
    code_ratio: 0.2
    structure: 0.3
    length: 0.2
"""
```

## 🔍 Configuration Validation

### Validation Methods

```python
from stage1.config import Stage1Config, ConfigValidationError

try:
    config = Stage1Config(
        parser=ParserConfig(preferred_parser="invalid-parser")
    )
    config.validate()  # Raises ConfigValidationError
except ConfigValidationError as e:
    print(f"Configuration error: {e}")

# Check configuration compatibility
compatibility = config.check_compatibility()
if not compatibility.is_valid:
    print(f"Compatibility issues: {compatibility.issues}")
```

### Configuration Merging

```python
# Merge configurations
base_config = ConfigProfiles.fast_processing()
custom_config = Stage1Config(
    analyzer=AnalyzerConfig(analyze_languages=True)
)

merged_config = base_config.merge(custom_config)
```

## 📊 Configuration Impact

### Performance Impact

```python
from stage1.benchmark import benchmark_config

# Benchmark different configurations
configs = [
    ConfigProfiles.fast_processing(),
    ConfigProfiles.comprehensive_analysis(),
    ConfigProfiles.code_focused()
]

results = benchmark_config(configs, test_documents)
for config_name, metrics in results.items():
    print(f"{config_name}:")
    print(f"  Processing time: {metrics.avg_time:.3f}s")
    print(f"  Memory usage: {metrics.memory_usage}MB")
    print(f"  Accuracy score: {metrics.accuracy:.2f}")
```

### Feature Matrix

```python
# Get feature matrix for configuration
features = config.get_feature_matrix()
print("Enabled features:")
for component, component_features in features.items():
    print(f"  {component}:")
    for feature, enabled in component_features.items():
        status = "✓" if enabled else "✗"
        print(f"    {status} {feature}")
```

## 🎯 Best Practices

### Configuration Guidelines

1. **Start with profiles**: Use predefined profiles as starting points
2. **Environment-specific**: Create different configs for dev/prod
3. **Performance vs Features**: Balance features with performance needs
4. **Validation**: Always validate configurations before use
5. **Documentation**: Document custom configuration choices

### Common Patterns

```python
# Development configuration
dev_config = Stage1Config(
    parser=ParserConfig(strict_mode=False),
    analyzer=AnalyzerConfig(
        analyze_languages=True,
        calculate_complexity=True
    )
)

# Production configuration
prod_config = Stage1Config(
    parser=ParserConfig(
        enable_caching=True,
        max_parse_time=5.0
    ),
    analyzer=AnalyzerConfig(
        max_analysis_time=3.0,
        enable_caching=True
    )
)

# Testing configuration
test_config = Stage1Config(
    parser=ParserConfig(strict_mode=True),
    extractor=ExtractorConfig(strict_mode=True),
    detector=DetectorConfig(require_headers=True)
)
```