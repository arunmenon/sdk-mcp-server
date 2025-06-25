"""
SDK Providers - Download SDKs from various sources
"""
import os
import shutil
import asyncio
import zipfile
import tarfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import aiohttp
import subprocess


class SDKProvider(ABC):
    """Base class for SDK providers"""
    
    @abstractmethod
    async def download(self, config: Dict[str, Any], cache_dir: Path) -> Path:
        """Download SDK source code"""
        pass
    
    @abstractmethod
    def get_cache_key(self, config: Dict[str, Any]) -> str:
        """Generate unique cache key for this SDK source"""
        pass


class GitHubProvider(SDKProvider):
    """Download SDKs from GitHub repositories"""
    
    async def download(self, config: Dict[str, Any], cache_dir: Path) -> Path:
        """Download from GitHub repository"""
        repo = config["repo"]
        branch = config.get("branch", "main")
        path = config.get("path", "")
        
        # Create cache directory structure
        repo_name = repo.replace("/", "_")
        sdk_dir = cache_dir / repo_name / branch
        
        # Check if already downloaded
        if sdk_dir.exists() and self._is_recent_cache(sdk_dir):
            print(f"Using cached version of {repo}")
            return sdk_dir / path
        
        # Create directory
        sdk_dir.parent.mkdir(parents=True, exist_ok=True)
        
        # Clone or update repository
        if sdk_dir.exists():
            # Update existing clone
            await self._update_repo(sdk_dir, branch)
        else:
            # Clone fresh
            await self._clone_repo(repo, sdk_dir, branch)
        
        final_path = sdk_dir / path
        if not final_path.exists():
            raise FileNotFoundError(f"Path {path} not found in repository {repo}")
        
        return final_path
    
    async def _clone_repo(self, repo: str, target_dir: Path, branch: str) -> None:
        """Clone a GitHub repository"""
        url = f"https://github.com/{repo}.git"
        
        # Use sparse checkout for efficiency
        cmd = [
            "git", "clone", 
            "--depth", "1",
            "--branch", branch,
            "--single-branch",
            url,
            str(target_dir)
        ]
        
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            raise RuntimeError(f"Failed to clone {repo}: {stderr.decode()}")
    
    async def _update_repo(self, repo_dir: Path, branch: str) -> None:
        """Update existing repository"""
        # Git pull in the directory
        cmd = ["git", "-C", str(repo_dir), "pull", "origin", branch]
        
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        await proc.communicate()
    
    def _is_recent_cache(self, cache_dir: Path, max_age_hours: int = 24) -> bool:
        """Check if cache is recent enough"""
        import time
        
        if not cache_dir.exists():
            return False
        
        # Check modification time
        mtime = cache_dir.stat().st_mtime
        age_hours = (time.time() - mtime) / 3600
        
        return age_hours < max_age_hours
    
    def get_cache_key(self, config: Dict[str, Any]) -> str:
        """Generate cache key for GitHub source"""
        repo = config["repo"]
        branch = config.get("branch", "main")
        return f"github_{repo.replace('/', '_')}_{branch}"


class URLProvider(SDKProvider):
    """Download SDKs from direct URLs (ZIP, TAR files)"""
    
    async def download(self, config: Dict[str, Any], cache_dir: Path) -> Path:
        """Download from URL"""
        url = config["url"]
        extract_path = config.get("path", "")
        
        # Generate cache directory name from URL
        parsed = urlparse(url)
        filename = Path(parsed.path).name
        sdk_name = filename.split('.')[0]
        
        sdk_dir = cache_dir / "url_downloads" / sdk_name
        
        # Check cache
        if sdk_dir.exists() and self._is_recent_cache(sdk_dir):
            print(f"Using cached version of {url}")
            return sdk_dir / extract_path
        
        # Download file
        sdk_dir.mkdir(parents=True, exist_ok=True)
        archive_path = sdk_dir / filename
        
        await self._download_file(url, archive_path)
        
        # Extract archive
        extract_dir = sdk_dir / "extracted"
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        
        self._extract_archive(archive_path, extract_dir)
        
        final_path = extract_dir / extract_path
        if not final_path.exists():
            # Try to find the path in subdirectories
            for item in extract_dir.iterdir():
                if item.is_dir():
                    candidate = item / extract_path
                    if candidate.exists():
                        final_path = candidate
                        break
        
        if not final_path.exists():
            raise FileNotFoundError(f"Path {extract_path} not found in archive {url}")
        
        return final_path
    
    async def _download_file(self, url: str, target_path: Path) -> None:
        """Download file from URL"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                
                with open(target_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
    
    def _extract_archive(self, archive_path: Path, extract_dir: Path) -> None:
        """Extract ZIP or TAR archive"""
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        if archive_path.suffix == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zf:
                zf.extractall(extract_dir)
        elif archive_path.suffix in ['.tar', '.gz', '.tgz']:
            with tarfile.open(archive_path, 'r:*') as tf:
                tf.extractall(extract_dir)
        else:
            raise ValueError(f"Unsupported archive format: {archive_path.suffix}")
    
    def _is_recent_cache(self, cache_dir: Path, max_age_hours: int = 24) -> bool:
        """Check if cache is recent enough"""
        import time
        
        if not cache_dir.exists():
            return False
        
        mtime = cache_dir.stat().st_mtime
        age_hours = (time.time() - mtime) / 3600
        
        return age_hours < max_age_hours
    
    def get_cache_key(self, config: Dict[str, Any]) -> str:
        """Generate cache key for URL source"""
        url = config["url"]
        parsed = urlparse(url)
        filename = Path(parsed.path).name
        return f"url_{filename}"


class ProviderFactory:
    """Factory for creating SDK providers"""
    
    @staticmethod
    def create_provider(source_type: str) -> SDKProvider:
        """Create appropriate provider based on source type"""
        providers = {
            "github": GitHubProvider(),
            "url": URLProvider(),
        }
        
        provider = providers.get(source_type)
        if not provider:
            raise ValueError(f"Unknown source type: {source_type}")
        
        return provider