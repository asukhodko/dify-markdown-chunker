"""GitHub README collector."""

import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import requests

from .base import BaseCollector, CollectionResult, DocumentMetadata
from .config import (
    GITHUB_API_BASE,
    GITHUB_RAW_BASE,
    GITHUB_RATE_LIMIT_DELAY,
    GITHUB_REPOS,
)


class GitHubCollector(BaseCollector):
    """Collector for GitHub README files."""

    def __init__(self, output_dir: Path, language: str, github_token: Optional[str] = None):
        super().__init__(output_dir)
        self.language = language
        self.github_token = github_token
        self.session = requests.Session()
        
        if github_token:
            self.session.headers.update({"Authorization": f"token {github_token}"})
        
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "MarkdownChunker-CorpusBuilder/1.0",
        })

    def collect(self) -> List[CollectionResult]:
        """Collect README files from GitHub repositories."""
        results = []
        repos = GITHUB_REPOS.get(self.language, [])
        
        print(f"Collecting {len(repos)} READMEs for {self.language}...")
        
        for repo in repos:
            try:
                result = self._collect_readme(repo)
                if result.success:
                    results.append(result)
                    print(f"  ✓ {repo}")
                else:
                    print(f"  ✗ {repo}: {result.error}")
                
                # Rate limiting
                time.sleep(GITHUB_RATE_LIMIT_DELAY)
                
            except Exception as e:
                print(f"  ✗ {repo}: {str(e)}")
                results.append(
                    CollectionResult(success=False, error=str(e))
                )
        
        return results

    def _collect_readme(self, repo: str) -> CollectionResult:
        """Collect README from a single repository."""
        # Try to get README via API
        api_url = f"{GITHUB_API_BASE}/repos/{repo}/readme"
        
        try:
            response = self.session.get(api_url, timeout=30)
            
            if response.status_code == 404:
                return CollectionResult(
                    success=False, error="README not found"
                )
            
            response.raise_for_status()
            readme_data = response.json()
            
            # Get raw content
            download_url = readme_data.get("download_url")
            if not download_url:
                return CollectionResult(
                    success=False, error="No download URL"
                )
            
            content_response = self.session.get(download_url, timeout=30)
            content_response.raise_for_status()
            content = content_response.text
            
            # Check for duplicates
            if self._is_duplicate(content):
                return CollectionResult(
                    success=False, error="Duplicate content"
                )
            
            # Analyze content
            analysis = self._analyze_content(content)
            
            # Create metadata
            repo_name = repo.split("/")[1]
            filename = f"{repo_name}.md"
            
            metadata = DocumentMetadata(
                filename=filename,
                category="github_readmes",
                subcategory=self.language,
                size_bytes=len(content.encode("utf-8")),
                source="github",
                source_url=f"https://github.com/{repo}",
                collection_date=datetime.now().isoformat(),
                content_hash=self._compute_hash(content),
                **analysis,
            )
            
            metadata.expected_strategy = self._determine_expected_strategy(analysis)
            
            # Save
            if self.save_document(content, filename, metadata):
                return CollectionResult(
                    success=True, content=content, metadata=metadata
                )
            else:
                return CollectionResult(
                    success=False, error="Failed to save document"
                )
                
        except requests.RequestException as e:
            return CollectionResult(success=False, error=f"Request failed: {str(e)}")
        except Exception as e:
            return CollectionResult(success=False, error=f"Unexpected error: {str(e)}")
