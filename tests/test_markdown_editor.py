"""Markdown 编辑器完整测试"""
import unittest
from markdown_editor import MarkdownEditor


class TestMarkdownEditor(unittest.TestCase):
    """测试 Markdown 编辑器"""

    def _render(self, md_text):
        """用指定 Markdown 文本构造编辑器并渲染为 HTML"""
        editor = MarkdownEditor(md_text)
        return editor.render_markdown()

    def test_basic_conversion(self):
        """测试基本转换"""
        html = self._render("# Hello\n\nThis is a test.")
        self.assertIn("<h1", html)
        self.assertIn("Hello", html)
        self.assertIn("<p>", html)

    def test_code_block(self):
        """测试代码块"""
        editor = MarkdownEditor("```python\nprint('hello')\n```")
        html = editor.render_with_highlight()
        self.assertIn("codehilite", html)
        self.assertIn("print", html)

    def test_table(self):
        """测试表格"""
        html = self._render("| A | B |\n|---|---|\n| 1 | 2 |")
        self.assertIn("<table>", html)
        self.assertIn("<th>", html)
        self.assertIn("<td>", html)

    def test_toc_generation(self):
        """测试目录生成"""
        editor = MarkdownEditor("# Title 1\n## Title 2\n### Title 3")
        toc_html = editor.get_toc_html()
        self.assertIsNotNone(toc_html)
        self.assertIn("Title", toc_html)

    def test_empty_input(self):
        """测试空输入"""
        html = self._render("")
        self.assertIsNotNone(html)

    def test_bold_italic(self):
        """测试粗体和斜体"""
        html = self._render("**bold** and *italic*")
        self.assertIn("<strong>", html)
        self.assertIn("<em>", html)

    def test_link(self):
        """测试链接"""
        html = self._render("[link](https://example.com)")
        self.assertIn("<a", html)
        self.assertIn("href", html)

    def test_blockquote(self):
        """测试引用"""
        html = self._render("> This is a quote")
        self.assertIn("<blockquote", html)

    def test_list(self):
        """测试列表"""
        html = self._render("- Item 1\n- Item 2\n- Item 3")
        self.assertIn("<ul>", html)
        self.assertIn("<li>", html)

    def test_statistics(self):
        """测试字数、行数、字符数统计"""
        editor = MarkdownEditor("Line 1\nLine 2\nLine 3")
        self.assertEqual(editor.get_line_count(), 3)
        self.assertGreater(editor.get_word_count(), 0)
        self.assertGreater(editor.get_character_count(), 0)


if __name__ == '__main__':
    unittest.main()
