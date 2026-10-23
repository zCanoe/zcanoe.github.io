import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_site", ROOT / "scripts/build_site.py")
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


class PublishingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "source"
        self.root.mkdir()
        for name in (*site.PUBLIC_FILES, "index.html"):
            shutil.copy2(ROOT / name, self.root / name)
        (self.root / "posts").mkdir()
        self.out = Path(self.temp.name) / "public"

    def post(self, slug="hello", draft="false", day="2026-10-23", body="## Heading\n\nHello **world**."):
        path = self.root / "posts" / f"{slug}.md"
        path.write_text(f'---\ntitle: "Test {slug}"\ndate: {day}\nslug: {slug}\nsummary: "Summary {slug}"\ntags: [Java]\ndraft: {draft}\n---\n{body}\n', encoding="utf-8")
        return path

    def contents(self):
        return "\n".join(p.read_text(encoding="utf-8") for p in self.out.rglob("*") if p.is_file())

    def test_published_everywhere_and_draft_nowhere(self):
        self.post()
        self.post("secret-draft", draft="true")
        site.build(self.root, self.out)
        for name in ("index.html", "blog/index.html", "blog/hello/index.html", "feed.xml", "sitemap.xml"):
            self.assertIn("/blog/hello/", (self.out / name).read_text(encoding="utf-8"))
        self.assertNotIn("secret-draft", self.contents())
        self.assertFalse((self.out / "posts").exists())
        self.assertFalse((self.out / "scripts").exists())
        self.assertIn('<h2 id="section-1">Heading</h2>', (self.out / "blog/hello/index.html").read_text(encoding="utf-8"))
        ET.parse(self.out / "feed.xml")
        ET.parse(self.out / "sitemap.xml")

    def test_order_latest_three_and_removal(self):
        for i in range(1, 5):
            self.post(f"note-{i}", day=f"2026-10-0{i}")
        site.build(self.root, self.out)
        home = (self.out / "index.html").read_text(encoding="utf-8")
        self.assertLess(home.index("Test note-4"), home.index("Test note-3"))
        self.assertNotIn("Test note-1", home)
        (self.root / "posts/note-4.md").unlink()
        self.post("note-3", draft="true")
        site.build(self.root, self.out)
        self.assertFalse((self.out / "blog/note-4").exists())
        self.assertFalse((self.out / "blog/note-3").exists())

    def test_invalid_metadata_keeps_last_good_build(self):
        path = self.post()
        site.build(self.root, self.out)
        previous = (self.out / "index.html").read_bytes()
        valid = path.read_text(encoding="utf-8")
        for bad in (valid.replace("slug: hello", "slug: ../escape"), valid.replace("draft: false", 'draft: "false"'),
                    valid.replace("date: 2026-10-23", "date: yesterday"), valid.replace('title: "Test hello"', "title: []"),
                    valid.replace("tags: [Java]", "tags: Java"), "No frontmatter"):
            with self.subTest(bad=bad):
                path.write_text(bad, encoding="utf-8")
                with self.assertRaises(ValueError):
                    site.build(self.root, self.out)
                self.assertEqual(previous, (self.out / "index.html").read_bytes())

    def test_duplicate_slug_rejected(self):
        path = self.post()
        shutil.copy2(path, path.with_name("duplicate.md"))
        with self.assertRaises(ValueError):
            site.build(self.root, self.out)

    def test_escaping_and_markdown_safety(self):
        path = self.post(body='<script>alert(1)</script>\n\n[x](javascript:alert(1))\n\n## <img onerror=alert(1)>')
        raw = path.read_text(encoding="utf-8").replace('title: "Test hello"', "title: '<img src=x onerror=alert(1)>'")
        path.write_text(raw, encoding="utf-8")
        site.build(self.root, self.out)
        page = (self.out / "blog/hello/index.html").read_text(encoding="utf-8")
        self.assertNotIn("<script>alert", page)
        self.assertNotIn("<img src=x", page)
        self.assertNotIn('href="javascript:', page)
        self.assertIn("&lt;img", page)

    def test_empty_archive(self):
        site.build(self.root, self.out)
        self.assertIn("第一篇随笔", (self.out / "blog/index.html").read_text(encoding="utf-8"))
        self.assertEqual(len(ET.parse(self.out / "feed.xml").findall("channel/item")), 0)


if __name__ == "__main__":
    unittest.main()
