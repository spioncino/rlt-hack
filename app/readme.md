CSV поставщика (1075 товаров)
  ↓ parse
DataFrame
  ↓ build_supplier_texts
1075 текстов ("Ноутбук. HP ProBook 450. ультрабук, для работы")
  ↓ encode_dense (BGE-M3, CLS token)
1075 × 1024 float32
  ↓ FAISS search ×2 (full + short), top-200 каждый
1075 × 200 индексов + scores
  ↓ RRF fusion → top-100 per item
  ↓ Pre-score (0.4*short + 0.35*full + kw - gap_penalty)
  ↓ Threshold ≥ 0.5
  ↓ ColBERT reranking top-50 (MaxSim token-level)
  ↓ Final score = 0.6*pre + 0.4*colbert_norm
  ↓ Group by pn_lot
  ↓ Sort by match_score
≤200 лотов с matching_items
  ↓ [app_fut only] LLM verify → filter rejected
JSON response → фронт