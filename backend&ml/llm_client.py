"""
LLM: батчевая генерация описаний лотов через Evolution API.
20 лотов на 1 промпт → 200 лотов = 10 вызовов.
"""

import asyncio
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv

load_dotenv()

LOTS_PER_PROMPT = int(os.getenv("LLM_LOTS_PER_PROMPT", "20"))
MAX_CONCURRENT = int(os.getenv("LLM_MAX_CONCURRENT", "5"))
_executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT + 2)
_client = None


def _get_client():
    global _client
    if _client is None:
        from evolution_openai import EvolutionOpenAI
        _client = EvolutionOpenAI(
            key_id=os.getenv("EVOLUTION_KEY_ID"),
            secret=os.getenv("EVOLUTION_SECRET"),
            base_url=os.getenv("EVOLUTION_BASE_URL"),
        )
    return _client


def _build_batch_prompt(lots_batch: list[dict]) -> str:
    lot_blocks = []
    for i, lot in enumerate(lots_batch, 1):
        units = ", ".join(lot.get("lot_units", [])[:5])
        cats = ", ".join(lot.get("matching_categories", [])[:3])
        items = ", ".join(it["name"][:50] for it in lot.get("matching_items", [])[:3])
        lot_blocks.append(
            f"{i}. «{lot['lot_subject'][:120]}»\n"
            f"   Товары лота: {units[:150]}\n"
            f"   Совпало: {lot['matched_products']}/{lot['total_products']} | "
            f"Категории поставщика: {cats} | Примеры: {items[:100]}"
        )
    block = "\n".join(lot_blocks)

    return (
        f"Для каждого из {len(lots_batch)} лотов госзакупок напиши краткое описание "
        "(2-3 предложения): что закупается, какие товары поставщика подходят, "
        "на что обратить внимание.\n\n"
        f"ЛОТЫ:\n{block}\n\n"
        "Ответь JSON массивом БЕЗ markdown:\n"
        '[{"id": 1, "summary": "текст"}, ...]\n'
        "Включи ВСЕ лоты по порядку."
    )


def _parse_summaries(text: str, n: int) -> list[str]:
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)

    try:
        arr = json.loads(text)
        if isinstance(arr, list):
            result = {}
            for item in arr:
                if isinstance(item, dict) and 'id' in item and 'summary' in item:
                    result[int(item['id'])] = str(item['summary'])
            return [result.get(i + 1, "") for i in range(n)]
    except (json.JSONDecodeError, ValueError):
        pass

    # Fallback: extract summary strings
    summaries = re.findall(r'"summary"\s*:\s*"([^"]*)"', text)
    if summaries:
        return (summaries + [""] * n)[:n]

    return [""] * n


def _call_batch_sync(lots_batch: list[dict]) -> list[str]:
    prompt = _build_batch_prompt(lots_batch)
    client = _get_client()
    resp = client.chat.completions.create(
        model=os.getenv("EVOLUTION_MODEL_NAME", "qwen35-vlm"),
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        max_tokens=8000,
        temperature=0.3,
    )
    raw = resp.choices[0].message.content
    return _parse_summaries(raw, len(lots_batch))


async def generate_lot_summaries(
    lots: list[dict],
    lots_per_prompt: int = LOTS_PER_PROMPT,
    max_concurrent: int = MAX_CONCURRENT,
) -> list[dict]:
    """
    Generate LLM summaries for lots in batches.
    200 lots / 20 per prompt = 10 LLM calls.
    """
    # Split into batches
    batches = []
    for i in range(0, len(lots), lots_per_prompt):
        batches.append(lots[i:i + lots_per_prompt])

    sem = asyncio.Semaphore(max_concurrent)
    loop = asyncio.get_event_loop()

    async def process_batch(batch_idx: int, batch: list[dict]):
        async with sem:
            try:
                summaries = await loop.run_in_executor(
                    _executor, _call_batch_sync, batch
                )
                for lot, summary in zip(batch, summaries):
                    lot["summary"] = summary
            except Exception as e:
                print(f"[llm] error batch {batch_idx}: {e}")
                for lot in batch:
                    lot["summary"] = ""

    t0 = time.time()
    tasks = [process_batch(i, b) for i, b in enumerate(batches)]
    await asyncio.gather(*tasks)
    elapsed = time.time() - t0

    filled = sum(1 for lot in lots if lot.get("summary"))
    print(f"[llm] {len(lots)} lots in {len(batches)} batches, "
          f"{elapsed:.1f}s ({filled} summaries generated)")

    return lots
