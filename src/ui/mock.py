import os
from typing import List
import asyncio

from src.core.task_manager import get_github_links, basic_analysis

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

async def mock_scan_paper_for_github_links(source: str) -> List[dict]:
    await asyncio.sleep(3.0)
    results = [{
        "url":         "https://github.com/example/research-code",
        "recommended": True,
        "reason":      "Contains experiments and notebook demos",
    },
    {
        "url":    "https://github.com/example/auxiliary-scripts",
        "recommended": False,
        "reason": "Related utility code",
    },
    {
        "url": "https://github.com/another/repo",
        "recommended": False,
        "reason": "Related utility code",
    }
    
    ]
    return results


async def mock_analyze_github(url: str, mode: str) -> dict:
    # await asyncio.sleep(1.5 if mode == "basic" else 3.0)
    md = basic_analysis(url)
    return {
        "markdown": md,
    }