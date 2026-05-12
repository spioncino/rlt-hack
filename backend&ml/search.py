"""
Lot-centric search: BGE-M3 + FAISS → RRF → ColBERT rerank → group by lot.
No LLM dependency. ColBERT uses the same BGE-M3 model already loaded.
"""

import numpy as np
import pandas as pd
import pickle
import faiss
import torch
import re
import time
from collections import defaultdict
from transformers import AutoTokenizer, AutoModel


class SearchEngine:
    def __init__(self,
                 embeddings_dir: str = "embeddings_output",
                 model_dir: str = "local_user_bge_m3"):
        t_total = time.time()

        # ── Device ──
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")
        print(f"[search] device: {self.device}")

        # ── BGE-M3 model ──
        t0 = time.time()
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModel.from_pretrained(model_dir).to(self.device).eval()
        if self.device.type == "cuda":
            self.model = self.model.half()
        print(f"[search] model loaded: {time.time()-t0:.1f}s")

        # ── Pre-computed embeddings ──
        t0 = time.time()
        self.zak_emb_full = np.load(f"{embeddings_dir}/zak_emb_full.npy")
        self.zak_emb_short = np.load(f"{embeddings_dir}/zak_emb_short.npy")
        print(f"[search] embeddings: {self.zak_emb_full.shape[0]:,} rows, {time.time()-t0:.1f}s")

        # ── Texts & metadata ──
        with open(f"{embeddings_dir}/zak_texts_short.pkl", "rb") as f:
            self.zak_texts_short = pickle.load(f)
        with open(f"{embeddings_dir}/zak_texts_full.pkl", "rb") as f:
            self.zak_texts_full = pickle.load(f)
        self.metadata = pd.read_pickle(f"{embeddings_dir}/metadata.pkl")

        # ── FAISS indexes ──
        t0 = time.time()
        dim = self.zak_emb_full.shape[1]
        n = self.zak_emb_full.shape[0]
        nlist = min(int(np.sqrt(n)), 512)

        quantizer_f = faiss.IndexFlatIP(dim)
        self.faiss_full = faiss.IndexIVFFlat(quantizer_f, dim, nlist, faiss.METRIC_INNER_PRODUCT)
        self.faiss_full.train(self.zak_emb_full)
        self.faiss_full.add(self.zak_emb_full)
        self.faiss_full.nprobe = 50

        quantizer_s = faiss.IndexFlatIP(dim)
        self.faiss_short = faiss.IndexIVFFlat(quantizer_s, dim, nlist, faiss.METRIC_INNER_PRODUCT)
        self.faiss_short.train(self.zak_emb_short)
        self.faiss_short.add(self.zak_emb_short)
        self.faiss_short.nprobe = 50
        print(f"[search] FAISS indexes: {time.time()-t0:.1f}s")

        # ── Lookup tables ──
        t0 = time.time()
        self.pn_lot_arr = self.metadata['pn_lot'].values
        self.unit_name_arr = self.metadata['unit_name'].values

        self.pn_lot_first_row = {}
        self.lot_unit_counts = defaultdict(int)
        self.lot_units = defaultdict(list)

        for idx in range(len(self.pn_lot_arr)):
            pl = str(self.pn_lot_arr[idx])
            if pl not in self.pn_lot_first_row:
                self.pn_lot_first_row[pl] = idx
            self.lot_unit_counts[pl] += 1
            name = str(self.unit_name_arr[idx]) if pd.notna(self.unit_name_arr[idx]) else ''
            if name and len(self.lot_units[pl]) < 20 and name not in self.lot_units[pl]:
                self.lot_units[pl].append(name)

        print(f"[search] lookups: {len(self.pn_lot_first_row):,} lots, {time.time()-t0:.1f}s")
        print(f"[search] ready in {time.time()-t_total:.1f}s")

    # ──────────────────────────────────────────────
    # Dense encoding (CLS token)
    # ──────────────────────────────────────────────
    def encode_dense(self, texts: list[str], batch_size: int = 128,
                     max_length: int = 512) -> np.ndarray:
        all_embs = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            inputs = self.tokenizer(batch, padding=True, truncation=True,
                                    max_length=max_length, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = self.model(**inputs)
            embs = outputs.last_hidden_state[:, 0]
            embs = torch.nn.functional.normalize(embs.float(), p=2, dim=1)
            all_embs.append(embs.cpu().numpy())
        return np.concatenate(all_embs, axis=0).astype(np.float32)

    # ──────────────────────────────────────────────
    # ColBERT encoding (all token embeddings)
    # ──────────────────────────────────────────────
    def encode_colbert(self, texts: list[str], batch_size: int = 32,
                       max_length: int = 256) -> list[np.ndarray]:
        """Returns list of (num_tokens, dim) arrays, one per text."""
        all_token_embs = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            inputs = self.tokenizer(batch, padding=True, truncation=True,
                                    max_length=max_length, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = self.model(**inputs)
            hidden = outputs.last_hidden_state
            mask = inputs['attention_mask']
            for j in range(hidden.size(0)):
                seq_len = mask[j].sum().item()
                token_embs = hidden[j, 1:int(seq_len)]
                token_embs = torch.nn.functional.normalize(token_embs.float(), p=2, dim=1)
                all_token_embs.append(token_embs.cpu().numpy())
        return all_token_embs

    @staticmethod
    def colbert_score(query_tokens: np.ndarray, doc_tokens: np.ndarray) -> float:
        """MaxSim: for each query token, max similarity with any doc token."""
        if len(query_tokens) == 0 or len(doc_tokens) == 0:
            return 0.0
        sim = query_tokens @ doc_tokens.T
        return float(sim.max(axis=1).sum())

    def rerank_colbert(self, query_text: str, candidate_doc_indices: list[int],
                       top_k: int = 50) -> list[tuple[int, float]]:
        """ColBERT rerank: encode query + candidate docs, compute MaxSim."""
        query_tokens = self.encode_colbert([query_text])[0]
        doc_texts = [self.zak_texts_full[idx] for idx in candidate_doc_indices]
        doc_token_embs = self.encode_colbert(doc_texts)
        scored = []
        for i, idx in enumerate(candidate_doc_indices):
            score = self.colbert_score(query_tokens, doc_token_embs[i])
            scored.append((idx, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    # ──────────────────────────────────────────────
    # Build supplier search texts from CSV
    # ──────────────────────────────────────────────
    @staticmethod
    def _find_name_col(df: pd.DataFrame) -> str:
        for c in df.columns:
            if 'аименован' in c:
                return c
        return df.columns[2]

    @staticmethod
    def build_supplier_texts(df: pd.DataFrame) -> list[str]:
        texts = []
        name_col = SearchEngine._find_name_col(df)
        for _, row in df.iterrows():
            parts = [str(row['Категория']).strip(), str(row[name_col]).strip()]
            chars = str(row.get('Характеристики', '')).strip().strip('"')
            text_chars = []
            for pair in chars.split(';'):
                if ':' in pair:
                    _, val = pair.split(':', 1)
                    val = val.strip()
                    if (val and not re.match(r'^[\d.,\s]+$', val)
                            and val.lower() not in ('0', '1', 'да', 'нет', 'true', 'false')):
                        text_chars.append(val)
            if text_chars:
                parts.append(', '.join(text_chars[:10]))
            texts.append('. '.join(parts))
        return texts

    # ──────────────────────────────────────────────
    # Keyword overlap
    # ──────────────────────────────────────────────
    @staticmethod
    def _tokenize(text: str) -> set[str]:
        return set(re.findall(r'[а-яёa-z0-9]{3,}', text.lower()))

    def _keyword_score(self, q_words: set[str], doc_idx: int) -> float:
        d_words = self._tokenize(self.zak_texts_short[doc_idx])
        if not q_words or not d_words:
            return 0.0
        return len(q_words & d_words) / max(len(q_words), 1)

    # ──────────────────────────────────────────────
    # Main pipeline: lot-centric search + ColBERT rerank
    # ──────────────────────────────────────────────
    def find_lots(self, df: pd.DataFrame,
                  top_k_faiss: int = 200,
                  row_score_threshold: float = 0.5,
                  colbert_top_k: int = 50,
                  max_lots: int = 200) -> list[dict]:
        timings = {}

        # 1. Encode supplier items
        t0 = time.time()
        sup_texts = self.build_supplier_texts(df)
        sup_emb = self.encode_dense(sup_texts)
        timings['encode'] = time.time() - t0

        # 2. FAISS batch search
        t0 = time.time()
        full_scores, full_indices = self.faiss_full.search(sup_emb, top_k_faiss)
        short_scores, short_indices = self.faiss_short.search(sup_emb, top_k_faiss)
        timings['faiss'] = time.time() - t0

        # 3. Supplier info
        name_col = self._find_name_col(df)
        sup_info = []
        for _, row in df.iterrows():
            sup_info.append({
                "id": int(row['id']) if 'id' in df.columns else 0,
                "category": str(row['Категория']),
                "name": str(row[name_col])[:100],
            })
        sup_token_sets = [self._tokenize(t) for t in sup_texts]

        # 4. RRF + scoring → collect candidates per supplier item
        t0 = time.time()
        lot_data = defaultdict(lambda: {
            "matched_units": {},
            "supplier_matches": {},
        })

        # Also collect top candidates per supplier item for ColBERT reranking
        colbert_candidates = {}  # sup_idx → list of (doc_idx, pre_score)

        for i in range(len(sup_texts)):
            rrf = defaultdict(float)
            full_map, short_map = {}, {}

            for rank in range(top_k_faiss):
                idx_f = int(full_indices[i][rank])
                idx_s = int(short_indices[i][rank])
                if idx_f >= 0:
                    rrf[idx_f] += 1.0 / (60 + rank + 1)
                    full_map[idx_f] = float(full_scores[i][rank])
                if idx_s >= 0:
                    rrf[idx_s] += 1.0 / (60 + rank + 1)
                    short_map[idx_s] = float(short_scores[i][rank])

            top_rrf = sorted(rrf.items(), key=lambda x: x[1], reverse=True)[:100]

            item_candidates = []
            for doc_idx, _ in top_rrf:
                fs = full_map.get(doc_idx, 0.0)
                ss = short_map.get(doc_idx, 0.0)
                kw = self._keyword_score(sup_token_sets[i], doc_idx)
                score = 0.4 * ss + 0.35 * fs + min(kw * 0.15, 0.1)
                gap = fs - ss
                score -= max(0, (gap - 0.1)) ** 2 * 0.8
                if score >= row_score_threshold:
                    item_candidates.append((doc_idx, score))

            colbert_candidates[i] = item_candidates

        timings['scoring'] = time.time() - t0

        # 5. ColBERT reranking — top candidates per supplier item
        t0 = time.time()
        colbert_reranked = 0

        for i, candidates in colbert_candidates.items():
            if not candidates:
                continue

            # Take top-N by pre-score for ColBERT reranking
            candidates.sort(key=lambda x: x[1], reverse=True)
            top_cands = candidates[:colbert_top_k]
            doc_indices = [idx for idx, _ in top_cands]

            # ColBERT rerank
            reranked = self.rerank_colbert(sup_texts[i], doc_indices, top_k=colbert_top_k)
            colbert_reranked += len(reranked)

            # Normalize ColBERT scores to 0-1 range
            if reranked:
                max_col = max(s for _, s in reranked)
                min_col = min(s for _, s in reranked)
                rng = max_col - min_col if max_col > min_col else 1.0

            # Build pre_score lookup
            pre_scores = dict(candidates)

            for doc_idx, col_score in reranked:
                col_norm = (col_score - min_col) / rng if rng > 0 else 0.5
                pre = pre_scores.get(doc_idx, 0.0)
                # Combined: 60% pre-score + 40% ColBERT
                final_score = 0.6 * pre + 0.4 * col_norm

                pn_lot = str(self.pn_lot_arr[doc_idx])
                lot = lot_data[pn_lot]
                prev = lot["matched_units"].get(doc_idx, 0)
                if final_score > prev:
                    lot["matched_units"][doc_idx] = final_score
                prev_s = lot["supplier_matches"].get(i, 0)
                if final_score > prev_s:
                    lot["supplier_matches"][i] = final_score

        timings['colbert'] = time.time() - t0
        print(f"[search] colbert reranked {colbert_reranked} pairs in {timings['colbert']:.1f}s")

        # 6. Build lot results
        t0 = time.time()
        results = []
        for pn_lot, data in lot_data.items():
            matched_count = len(data["matched_units"])
            total_units = self.lot_unit_counts.get(pn_lot, 1)
            unit_scores = list(data["matched_units"].values())
            avg_quality = sum(unit_scores) / len(unit_scores) if unit_scores else 0

            first = self.pn_lot_first_row.get(pn_lot)
            if first is None:
                continue
            m = self.metadata.iloc[first]
            procedure = str(m['procedure_name']) if pd.notna(m['procedure_name']) else ''
            lot_subject = str(m['lot_subject']) if pd.notna(m['lot_subject']) else ''
            tags = str(m['tags']) if pd.notna(m['tags']) else ''
            publish_date = str(m['publish_date']) if pd.notna(m['publish_date']) else ''
            platform_number = str(m['platform_number']) if pd.notna(m['platform_number']) else ''
            lot_number = str(m['lot_number']) if pd.notna(m['lot_number']) else ''

            matching_items = sorted(
                [{**sup_info[idx], "score": round(sc, 3)}
                 for idx, sc in data["supplier_matches"].items()],
                key=lambda x: x["score"], reverse=True,
            )[:20]

            categories = list(dict.fromkeys(
                item["category"] for item in matching_items
            ))

            # Match type based on score
            top_score = matching_items[0]["score"] if matching_items else 0
            if top_score > 0.7:
                match_type = "exact"
            elif top_score > 0.5:
                match_type = "strong"
            elif top_score > 0.4:
                match_type = "partial"
            else:
                match_type = "weak"

            results.append({
                "pn_lot": pn_lot,
                "platform_number": platform_number,
                "lot_number": lot_number,
                "procedure_name": procedure[:300],
                "lot_subject": lot_subject[:300],
                "tags": tags[:500],
                "publish_date": publish_date,
                "match_score": round(avg_quality * 100, 1),
                "match_type": match_type,
                "matched_products": matched_count,
                "total_products": total_units,
                "matching_categories": categories[:10],
                "matching_items": matching_items,
                "lot_units": self.lot_units.get(pn_lot, []),
            })

        results.sort(key=lambda x: x["match_score"], reverse=True)
        results = results[:max_lots]
        timings['build'] = time.time() - t0

        print(f"[search] encode={timings['encode']:.1f}s "
              f"faiss={timings['faiss']:.1f}s "
              f"scoring={timings['scoring']:.1f}s "
              f"colbert={timings['colbert']:.1f}s "
              f"build={timings['build']:.1f}s | "
              f"{len(results)} lots found")

        return results
