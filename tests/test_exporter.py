"""导出功能完整测试"""
import unittest
import os
import tempfile
from exporter import Exporter


class TestExporter(unittest.TestCase):
    """测试导出器"""
    
    def setUp(self):
        self.exporter = Exporter()
        self.test_html = "<h1>Test</h1><p>Content</p>"
        self.test_css = "body { margin: 0; }"
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        # 清理临时文件
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def test_export_html(self):
        """测试 HTML 导出"""
        output_path = os.path.join(self.temp_dir, "test.html")
        result = self.exporter.export_html(self.test_html, self.test_css, output_path)
        
        self.assertTrue(os.path.exists(result))
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("<!DOCTYPE html>", content)
            self.assertIn("<h1>Test</h1>", content)
            self.assertIn(self.test_css, content)
    
    def test_export_pdf(self):
        """测试 PDF 导出"""
        output_path = os.path.join(self.temp_dir, "test.pdf")
        result = self.exporter.export_pdf(self.test_html, output_path)
        
        self.assertTrue(os.path.exists(result))
        self.assertTrue(os.path.getsize(result) > 0)
    
    def test_export_docx(self):
        """测试 Word 导出"""
        output_path = os.path.join(self.temp_dir, "test.docx")
        result = self.exporter.export_docx(self.test_html, output_path)
        
        self.assertTrue(os.path.exists(result))
        self.assertTrue(os.path.getsize(result) > 0)
    
    def test_export_html_with_complex_content(self):
        """测试 HTML 导出复杂内容"""
        complex_html = """
        <h1>Title</h1>
        <h2>Subtitle</h2>
        <p>Paragraph with <strong>bold</strong> and <em>italic</em></p>
        <ul><li>Item 1</li><li>Item 2</li></ul>
        """
        output_path = os.path.join(self.temp_dir, "complex.html")
        result = self.exporter.export_html(complex_html, self.test_css, output_path)
        
        self.assertTrue(os.path.exists(result))
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Title", content)
            self.assertIn("Subtitle", content)
            self.assertIn("bold", content)
    
    def test_export_pdf_with_headings(self):
        """测试 PDF 导出带标题"""
        heading_html = "<h1>Main Title</h1><h2>Section</h2><p>Content here</p>"
        output_path = os.path.join(self.temp_dir, "headings.pdf")
        result = self.exporter.export_pdf(heading_html, output_path)
        
        self.assertTrue(os.path.exists(result))
        self.assertTrue(os.path.getsize(result) > 0)
    
    def test_export_docx_with_multiple_elements(self):
        """测试 Word 导出多元素"""
        multi_html = """
        <h1>Heading 1</h1>
        <h2>Heading 2</h2>
        <h3>Heading 3</h3>
        <p>Paragraph 1</p>
        <p>Paragraph 2</p>
        """
        output_path = os.path.join(self.temp_dir, "multi.docx")
        result = self.exporter.export_docx(multi_html, output_path)
        
        self.assertTrue(os.path.exists(result))
        self.assertTrue(os.path.getsize(result) > 0)
    
    def test_export_empty_content(self):
        """测试导出空内容"""
        empty_html = ""
        output_path = os.path.join(self.temp_dir, "empty.html")
        result = self.exporter.export_html(empty_html, self.test_css, output_path)
        
        self.assertTrue(os.path.exists(result))


if __name__ == '__main__':
    unittest.main()
