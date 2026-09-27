import importlib.util
from pathlib import Path
import unittest
P=Path(__file__).parents[1]/"app"/"utils"/"performance.py"; s=importlib.util.spec_from_file_location("performance",P); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
class C:
    class embeddings:
        calls=0
        @classmethod
        def create(cls, **k):
            cls.calls+=1
            return type("R",(),{"data":[type("D",(),{"embedding":[1]})()]})()
class T(unittest.TestCase):
    def test_embedding_cache_respects_model(self):
        p=m.RequestPerformance(); p.embedding(C," A\n B ","x"); p.embedding(C,"A B","x"); p.embedding(C,"A B","y")
        self.assertEqual(p.metrics["cache"]["hits"],1); self.assertEqual(C.embeddings.calls,2)
if __name__=="__main__": unittest.main()
