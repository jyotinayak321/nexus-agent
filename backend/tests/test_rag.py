"""
Tests for RAG document text extraction, chunking, and unsupported file handling.
"""
import unittest
from rag_service import extract_text, chunk_text

class TestRAGService(unittest.TestCase):
    def test_extract_txt_valid(self):
        sample_bytes = b"This is a test document detailing LangGraph multi-agent architecture."
        text = extract_text(sample_bytes, "framework_docs.txt")
        self.assertIn("LangGraph", text)
        self.assertEqual(text, sample_bytes.decode("utf-8"))

    def test_extract_md_valid(self):
        sample_bytes = b"# LangChain vs LangGraph\n\n- Multi-agent coordination\n- pgvector similarity"
        text = extract_text(sample_bytes, "comparison.md")
        self.assertIn("pgvector", text)
        self.assertIn("# LangChain vs LangGraph", text)

    def test_extract_unsupported_extension(self):
        sample_bytes = b"binary data payload"
        with self.assertRaises(ValueError) as ctx:
            extract_text(sample_bytes, "malicious_or_unknown.exe")
        self.assertIn("Unsupported file type", str(ctx.exception))

    def test_extract_empty_document(self):
        with self.assertRaises(ValueError) as ctx:
            extract_text(b"   \n   \t  ", "empty.txt")
        self.assertIn("empty", str(ctx.exception).lower())

    def test_chunk_text_basic(self):
        text = "Paragraph 1 describing AI agents. " * 30
        chunks = chunk_text(text, chunk_size=200, overlap=30)
        self.assertGreater(len(chunks), 1)
        for c in chunks:
            self.assertTrue(len(c.strip()) > 0)

    def test_chunk_text_short(self):
        text = "Short text under 200 characters."
        chunks = chunk_text(text, chunk_size=500, overlap=50)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], text)

if __name__ == "__main__":
    unittest.main()
