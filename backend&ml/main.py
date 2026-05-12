"""
FastAPI: POST /match — принимает CSV поставщика, возвращает лоты.
ColBERT reranking вместо LLM.
"""

import io
import time

import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.search import SearchEngine

app = FastAPI(title="Procurement Matcher", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine: SearchEngine | None = None


@app.on_event("startup")
def startup():
    global engine
    print("[startup] initializing search engine...")
    engine = SearchEngine()
    print("[startup] ready")


@app.get("/health")
def health():
    return {"status": "ok", "index_size": engine.zak_emb_full.shape[0] if engine else 0}


@app.post("/match")
async def match(file: UploadFile = File(...)):
    if engine is None:
        raise HTTPException(503, "Search engine not initialized")

    stages = {}
    t_total = time.time()

    # ── 1. Parse CSV ──
    t0 = time.time()
    raw = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(raw), sep=';', encoding='utf-8-sig')
    except Exception as e:
        raise HTTPException(400, f"CSV parse error: {e}")

    df.columns = df.columns.str.strip()
    required = {'Категория', 'Характеристики'}
    name_col = next((c for c in df.columns if 'аименован' in c), None)
    if not required.issubset(set(df.columns)) or name_col is None:
        raise HTTPException(
            400,
            f"Missing columns. Need: Категория, Наименование, Характеристики. "
            f"Got: {list(df.columns)}"
        )
    stages['parse_sec'] = round(time.time() - t0, 2)
    print(f"[match] parsed CSV: {len(df)} items, {stages['parse_sec']}s")

    # ── 2. Search + ColBERT rerank ──
    t0 = time.time()
    lots = engine.find_lots(df)
    stages['search_sec'] = round(time.time() - t0, 2)
    print(f"[match] search+rerank: {len(lots)} lots, {stages['search_sec']}s")

    stages['total_sec'] = round(time.time() - t_total, 2)

    # ── Stats ──
    total_matched_items = set()
    for lot in lots:
        for item in lot.get("matching_items", []):
            total_matched_items.add(item.get("id", 0))

    return {
        "lots": lots,
        "stats": {
            "total_supplier_items": len(df),
            "supplier_items_with_matches": len(total_matched_items),
            "total_lots_found": len(lots),
            "timing": stages,
        },
    }
