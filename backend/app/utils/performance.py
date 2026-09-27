"""Métricas cuantitativas y caché efímero para una ejecución jurídica."""
import hashlib, re, time, unicodedata

def normalize_text(text):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", str(text))).strip()

class RequestPerformance:
    def __init__(self):
        self.cache = {}; self.started = time.perf_counter()
        self.metrics = {"openai_calls":0,"embedding_calls":0,"supabase_queries":0,"zep_calls":0,"tokens":{"input":0,"output":0,"cached":0},"cache":{"hits":0,"misses":0},"latency_ms":{}}
    def key(self, text, model):
        return hashlib.sha256(f"{model}:{normalize_text(text)}".encode()).hexdigest()
    def embedding(self, client, text, model):
        key = self.key(text, model)
        if key in self.cache:
            self.metrics["cache"]["hits"] += 1; return self.cache[key]
        self.metrics["cache"]["misses"] += 1; self.metrics["openai_calls"] += 1; self.metrics["embedding_calls"] += 1
        value = client.embeddings.create(input=text, model=model).data[0].embedding
        self.cache[key] = value; return value
    def public_summary(self):
        return {**self.metrics, "latency_ms": {"total": round((time.perf_counter()-self.started)*1000)}}
