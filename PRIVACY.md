# Privacy Policy for Advanced Markdown Chunker

**Last Updated:** December 2025  
**Version:** 1.0.0

## Overview

This Privacy Policy describes how the Advanced Markdown Chunker plugin ("the Plugin") handles data when installed and used within the Dify platform.

## Data Collection

### Personal Data
**The Plugin does not collect, store, or transmit any personal data.**

The Plugin operates entirely within your Dify instance and processes data locally. No user information, identifiers, or personal details are gathered at any point.

### Content Data
The Plugin receives Markdown text as input for processing. This content:
- Is processed **locally** within the Dify runtime environment
- Is **not stored** beyond the immediate processing session
- Is **not transmitted** to any external servers or third parties
- Is **not logged** or recorded by the Plugin

## Data Processing

### What the Plugin Does
- ✅ Parses Markdown text using local AST (Abstract Syntax Tree) analysis
- ✅ Analyzes document structure (headers, code blocks, lists, tables)
- ✅ Splits content into semantic chunks based on structure
- ✅ Generates metadata about chunk boundaries and content types
- ✅ Returns processed chunks to the Dify workflow

### What the Plugin Does NOT Do
- ❌ Send data to external APIs or services
- ❌ Store data outside of Dify's standard mechanisms
- ❌ Log, track, or monitor user content
- ❌ Collect analytics or telemetry
- ❌ Use cookies or persistent identifiers
- ❌ Share data with third parties

## Data Storage

The Plugin does not implement any independent data storage. All data handling follows Dify's standard data management practices:
- Input text exists only during processing
- Output chunks are returned to Dify for further workflow handling
- No temporary files or caches are created outside Dify's control

## Third-Party Services

**None.** The Plugin does not integrate with or transmit data to any external services, APIs, or platforms. All processing is performed locally using built-in Python libraries.

## Dependencies

The Plugin uses the following open-source libraries for local processing:
- `markdown-it-py` — Markdown parsing (local processing only)
- `pydantic` — Data validation (local processing only)

These libraries do not collect or transmit any data.

## Data Security

Since all processing occurs locally within the Dify environment:
- Data security is managed by the Dify platform
- No additional network exposure is introduced by the Plugin
- No credentials or API keys are required or stored

## Children's Privacy

The Plugin does not knowingly process any data related to children. As the Plugin does not collect any personal data, no special provisions for children's data are necessary.

## Changes to This Policy

Updates to this Privacy Policy will be:
- Published in the Plugin repository
- Reflected in the Plugin release notes
- Versioned with the Policy version number above

## Contact

For privacy-related questions or concerns about this Plugin:

- **Repository:** https://github.com/asukhodko/dify-markdown-chunker
- **Issues:** https://github.com/asukhodko/dify-markdown-chunker/issues

## Summary

| Category | Status |
|----------|--------|
| Personal data collection | ❌ None |
| Content transmission | ❌ None |
| External API calls | ❌ None |
| Data storage | ❌ None (beyond Dify's standard handling) |
| Third-party sharing | ❌ None |
| Analytics/Telemetry | ❌ None |
