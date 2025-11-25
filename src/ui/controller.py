import os
from typing import List
import asyncio

from src.core.task_manager import async_basic_analysis, async_get_github_links

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

async def scan_paper_for_github_links(source: str) -> List[str]:
    results = await async_get_github_links(source)
    
    return results


async def analyze_github(url: str, mode: str) -> dict:
    md = await async_basic_analysis(url)
    return {
        "markdown": md,
    }