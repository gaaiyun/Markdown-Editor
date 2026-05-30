"""导出功能完整测试"""
import unittest
import os
import tempfile
from exporter import MarkdownExporter


class TestExporter(unittest.TestCase):
    """测试导出器"""

    def setUp(self):
        self.test_markdown = "# Test\n\nContent"
        self.exporter = MarkdownExporter(self.test_markdown)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        # 清理临时文件
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_export_html(self):
        """测试 HTML 导出"""
        output_path = os.path.join(self.temp_dir, "test.html")
        result = self.exporter.export_html(output_path)

        self.assertTrue(os.path.exists(result))
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("<!DOCTYPE html>", content)
            self.assertIn("<h1>Test</h1>", content)
            self.assertIn("Content", content)

    def test_export_pdf(self):
        """测试 PDF 导出"""
        output_path = os.path.join(self.temp_dir, "test.pdf")
        result = self.exporter.export_pdf(output_path)

        self.assertTrue(os.path.exists(result))
        self.assertTrue(os.path.getsize(result) > 0)

    def test_export_word(self):
        """测试 Word 导出"""
        output_path = os.path.join(self.temp_dir, "test.docx")
        result = self.exporter.export_word(output_path)

        self.assertTrue(os.path.exists(result))
        self.assertTrue(os.path.getsize(result) > 0)

    def test_export_html_with_complex_content(self):
        """测试 HTML 导出复杂内容"""
        complex_markdown = """# Title

## Subtitle

Paragraph with **bold** and *italic*

- Item 1
- Item 2
"""
        exporter = MarkdownExporter(complex_markdown)
        output_path = os.path.join(self.temp_dir, "complex.html")
        result = exporter.export_html(output_path)

        self.assertTrue(os.path.exists(result))
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Title", content)
            self.assertIn("Subtitle", content)
            self.assertIn("bold", content)

    def test_export_pdf_with_headings(self):
        """测试 PDF 导出带标题"""
        heading_markdown = "# Main Title\n\n## Section\n\nContent here"
        exporter = MarkdownExporter(heading_markdown)
        output_path = os.path.join(self.temp_dir, "headings.pdf")
        result = exporter.export_pdf(output_path)

        self.assertTrue(os.path.exists(result))
        self.assertTrue(os.path.getsize(result) > 0)

    def test_export_word_with_multiple_elements(self):
        """测试 Word 导出多元素"""
        multi_markdown = """# Heading 1

## Heading 2

### Heading 3

Paragraph 1

Paragraph 2
"""
        exporter = MarkdownExporter(multi_markdown)
        output_path = os.path.join(self.temp_dir, "multi.docx")
        result = exporter.export_word(output_path)

        self.assertTrue(os.path.exists(result))
        self.assertTrue(os.path.getsize(result) > 0)

    def test_export_empty_content(self):
        """测试导出空内容"""
        exporter = MarkdownExporter("")
        output_path = os.path.join(self.temp_dir, "empty.html")
        result = exporter.export_html(output_path)

        self.assertTrue(os.path.exists(result))


if __name__ == '__main__':
    unittest.main()
