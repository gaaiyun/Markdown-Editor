"""Markdown 编辑器完整测试"""
import unittest
from markdown_editor import MarkdownEditor


class TestMarkdownEditor(unittest.TestCase):
    """测试 Markdown 编辑器"""
    
    def setUp(self):
        self.editor = MarkdownEditor()
    
    def test_basic_conversion(self):
        """测试基本转换"""
        md_text = "# Hello\n\nThis is a test."
        html, toc = self.editor.convert_to_html(md_text)
        self.assertIn("<h1", html)
        self.assertIn("Hello", html)
        self.assertIn("<p>", html)
    
    def test_code_block(self):
        """测试代码块"""
        md_text = "```python\nprint('hello')\n```"
        html, toc = self.editor.convert_to_html(md_text)
        self.assertIn("highlight", html)
        self.assertIn("print", html)
    
    def test_table(self):
        """测试表格"""
        md_text = "| A | B |\n|---|---|\n| 1 | 2 |"
        html, toc = self.editor.convert_to_html(md_text)
        self.assertIn("<table>", html)
        self.assertIn("<th>", html)
        self.assertIn("<td>", html)
    
    def test_toc_generation(self):
        """测试目录生成"""
        md_text = "# Title 1\n## Title 2\n### Title 3"
        html, toc = self.editor.convert_to_html(md_text)
        self.assertIsNotNone(toc)
        self.assertIn("Title", toc)
    
    def test_css_generation(self):
        """测试 CSS 生成"""
        css = self.editor.get_css('default')
        self.assertIn("body", css)
        self.assertIn("highlight", css)
        
        css_monokai = self.editor.get_css('monokai')
        self.assertIn("highlight", css_monokai)
    
    def test_empty_input(self):
        """测试空输入"""
        html, toc = self.editor.convert_to_html("")
        self.assertIsNotNone(html)
    
    def test_bold_italic(self):
        """测试粗体和斜体"""
        md_text = "**bold** and *italic*"
        html, toc = self.editor.convert_to_html(md_text)
        self.assertIn("<strong>", html)
        self.assertIn("<em>", html)
    
    def test_link(self):
        """测试链接"""
        md_text = "[link](https://example.com)"
        html, toc = self.editor.convert_to_html(md_text)
        self.assertIn("<a", html)
        self.assertIn("href", html)
    
    def test_blockquote(self):
        """测试引用"""
        md_text = "> This is a quote"
        html, toc = self.editor.convert_to_html(md_text)
        self.assertIn("<blockquote", html)
    
    def test_list(self):
        """测试列表"""
        md_text = "- Item 1\n- Item 2\n- Item 3"
        html, toc = self.editor.convert_to_html(md_text)
        self.assertIn("<ul>", html)
        self.assertIn("<li>", html)
    
    def test_multiple_themes(self):
        """测试多种主题"""
        themes = ['default', 'monokai', 'github-dark', 'vim', 'colorful']
        for theme in themes:
            css = self.editor.get_css(theme)
            self.assertIn("highlight", css)


if __name__ == '__main__':
    unittest.main()
