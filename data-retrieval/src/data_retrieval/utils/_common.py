"""
@File: utils.py
@Date: 2024-09-13
@Author: Danny.gao
@Desc:
"""
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import asyncio


def _route_similarity(route1: list[dict], route2: list[dict]) -> float:
    route1 = [list(r.keys())[0] for r in route1]
    route2 = [list(r.keys())[0] for r in route2]
    # 使用最长公共子序列（LCS）计算路线相似度
    m, n = len(route1), len(route2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if route1[i - 1] == route2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    lcs_length = dp[m][n]
    similarity = 2 * lcs_length / (m + n)  # 归一化相似度
    return similarity


def format_table_datas(datas_json: dict) -> list[dict]:
    datas = datas_json.get('data', [])
    cols = [col['name'] for col in datas_json.get('columns', [])]
    new_datas = []
    for data in datas:
        new_data = {}
        for val, col in zip(data, cols):
            new_data[col] = val
        new_datas.append(new_data)
    return new_datas


def is_valid_url(url):
    """判断是否为有效的URL地址"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


_executor = ThreadPoolExecutor()


def run_blocking(coro):
    """
    Run an async coroutine from synchronous code.

    This function handles the case where:
    - No event loop is running: creates a new loop via asyncio.run()
    - Event loop is running: submits to thread pool to avoid nested loop issues

    WARNING: This should only be called from synchronous contexts.
    If you're in an async context, use `await` directly instead.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop, safe to use asyncio.run()
        return asyncio.run(coro)

    # There's a running loop, run in a separate thread to avoid conflicts
    return _executor.submit(lambda: asyncio.run(coro)).result()
