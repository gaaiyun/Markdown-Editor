"""
Markdown 编辑器单元测试
测试覆盖率目标：> 70%
"""

import pytest
import os
import tempfile
from pathlib import Path

from markdown_editor import MarkdownEditor, ImageUploader, create_editor
from exporter import MarkdownExporter, export_markdown


class TestMarkdownEditor:
    """测试 MarkdownEditor 类"""
    
    def test_init_empty(self):
        """测试空内容初始化"""
        editor = MarkdownEditor()
        assert editor.get_content() == ""
        assert editor.get_line_count() == 1
        assert editor.get_character_count() == 0
    
    def test_init_with_content(self):
        """测试带内容初始化"""
        content = "# Hello\n\nWorld"
        editor = MarkdownEditor(content)
        assert editor.get_content() == content
        assert editor.get_line_count() == 3
        assert editor.get_word_count() > 0
    
    def test_set_content(self):
        """测试设置内容"""
        editor = MarkdownEditor()
        new_content = "## New Content"
        editor.set_content(new_content)
        assert editor.get_content() == new_content
    
    def test_get_content(self):
        """测试获取内容"""
        content = "Test content"
        editor = MarkdownEditor(content)
        assert editor.get_content() == content
    
    def test_parse_toc_simple(self):
        """测试简单目录解析"""
        content = """# Title 1
## Section 1.1
## Section 1.2
# Title 2
"""
        editor = MarkdownEditor(content)
        toc = editor.get_table_of_contents()
        
        assert len(toc) == 4
        assert toc[0].level == 1
        assert toc[0].title == "Title 1"
        assert toc[1].level == 2
        assert toc[1].title == "Section 1.1"
    
    def test_parse_toc_empty(self):
        """测试空内容目录"""
        editor = MarkdownEditor()
        toc = editor.get_table_of_contents()
        assert len(toc) == 0
    
    def test_generate_anchor(self):
        """测试锚点生成"""
        editor = MarkdownEditor()
        
        assert editor._generate_anchor("Hello World") == "hello-world"
        assert editor._generate_anchor("Test!@#") == "test"
        assert editor._generate_anchor("中文标题") == "中文标题"
    
    def test_get_toc_html(self):
        """测试获取 HTML 格式目录"""
        content = """# Title
## Section
"""
        editor = MarkdownEditor(content)
        html = editor.get_toc_html()
        
        assert "<div class='toc'>" in html
        assert "<a href='#title'>Title</a>" in html
        assert "<a href='#section'>Section</a>" in html
    
    def test_get_toc_html_empty(self):
        """测试空目录 HTML"""
        editor = MarkdownEditor()
        html = editor.get_toc_html()
        assert html == ""
    
    def test_render_markdown(self):
        """测试 Markdown 渲染"""
        content = "**bold** and *italic*"
        editor = MarkdownEditor(content)
        html = editor.render_markdown()
        
        assert "<strong>bold</strong>" in html
        assert "<em>italic</em>" in html
    
    def test_render_with_highlight(self):
        """测试带语法高亮渲染"""
        content = """```python
print("Hello")
```"""
        editor = MarkdownEditor(content)
        html = editor.render_with_highlight()
        
        assert "<code" in html or "<pre" in html
    
    def test_word_count(self):
        """测试字数统计"""
        content = "Hello World Test"
        editor = MarkdownEditor(content)
        assert editor.get_word_count() > 0
    
    def test_line_count(self):
        """测试行数统计"""
        content = "Line 1\nLine 2\nLine 3"
        editor = MarkdownEditor(content)
        assert editor.get_line_count() == 3
    
    def test_character_count(self):
        """测试字符数统计"""
        content = "ABC"
        editor = MarkdownEditor(content)
        assert editor.get_character_count() == 3
    
    def test_create_editor_function(self):
        """测试便捷函数"""
        editor = create_editor("Test")
        assert isinstance(editor, MarkdownEditor)
        assert editor.get_content() == "Test"


class TestMarkdownExporter:
    """测试 MarkdownExporter 类"""
    
    def test_init(self):
        """测试初始化"""
        content = "# Test"
        exporter = MarkdownExporter(content)
        assert exporter.markdown_content == content
        assert "<h1" in exporter.html_content
    
    def test_export_html(self):
        """测试导出 HTML"""
        content = "# Test Document"
        exporter = MarkdownExporter(content)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            output_path = f.name
        
        try:
            result_path = exporter.export_html(output_path, "Test")
            assert result_path == output_path
            assert os.path.exists(output_path)
            
            with open(output_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                assert "<!DOCTYPE html>" in html_content
                assert "Test Document" in html_content
                assert "<h1>Test Document</h1>" in html_content
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_export_pdf(self):
        """测试导出 PDF"""
        content = "# Test PDF"
        exporter = MarkdownExporter(content)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            output_path = f.name
        
        try:
            result_path = exporter.export_pdf(output_path, "Test")
            assert result_path == output_path
            assert os.path.exists(output_path)
            # PDF 文件应该大于 0 字节
            assert os.path.getsize(output_path) > 0
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_export_word(self):
        """测试导出 Word"""
        content = "# Test Word"
        exporter = MarkdownExporter(content)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.docx', delete=False) as f:
            output_path = f.name
        
        try:
            result_path = exporter.export_word(output_path, "Test")
            assert result_path == output_path
            assert os.path.exists(output_path)
            # Word 文件应该大于 0 字节
            assert os.path.getsize(output_path) > 0
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_html_to_text(self):
        """测试 HTML 转文本"""
        content = "<p>Hello <strong>World</strong></p>"
        exporter = MarkdownExporter("# Test")
        text = exporter._html_to_text(content)
        
        assert "Hello" in text
        assert "World" in text
        assert "<" not in text
    
    def test_export_markdown_function_html(self):
        """测试便捷导出函数 HTML"""
        content = "# Test"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            output_path = f.name
        
        try:
            result_path = export_markdown(content, output_path, 'html', "Test")
            assert result_path == output_path
            assert os.path.exists(output_path)
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_export_markdown_function_invalid_format(self):
        """测试便捷导出函数无效格式"""
        content = "# Test"
        
        with pytest.raises(ValueError):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.invalid', delete=False) as f:
                output_path = f.name
            
            try:
                export_markdown(content, output_path, 'invalid', "Test")
            finally:
                if os.path.exists(output_path):
                    os.remove(output_path)


class TestImageUploader:
    """测试 ImageUploader 类"""
    
    def test_init_empty(self):
        """测试空配置初始化"""
        uploader = ImageUploader()
        assert uploader.api_url == ""
        assert uploader.api_key == ""
    
    def test_init_with_config(self):
        """测试带配置初始化"""
        uploader = ImageUploader("https://api.example.com", "test-key")
        assert uploader.api_url == "https://api.example.com"
        assert uploader.api_key == "test-key"
    
    def test_upload_image_no_url(self):
        """测试无 URL 时上传"""
        uploader = ImageUploader()
        result = uploader.upload_image("test.jpg")
        assert result is None
    
    def test_insert_image_markdown(self):
        """测试插入图片 Markdown"""
        uploader = ImageUploader()
        md = uploader.insert_image_markdown("https://example.com/image.jpg", "test")
        assert md == "![test](https://example.com/image.jpg)"
    
    def test_insert_image_markdown_default_alt(self):
        """测试默认替代文本"""
        uploader = ImageUploader()
        md = uploader.insert_image_markdown("https://example.com/image.jpg")
        assert md == "![image](https://example.com/image.jpg)"


class TestIntegration:
    """集成测试"""
    
    def test_full_workflow(self):
        """测试完整工作流"""
        # 创建编辑器
        content = """# Test Document

This is a **test** document.

## Section 1

Some content here.

```python
print("Hello")
```

## Section 2

More content.
"""
        editor = MarkdownEditor(content)
        
        # 测试目录
        toc = editor.get_table_of_contents()
        assert len(toc) == 3
        
        # 测试渲染
        html = editor.render_with_highlight()
        assert html is not None
        assert len(html) > 0
        
        # 测试导出
        exporter = MarkdownExporter(content)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 导出 HTML
            html_path = os.path.join(tmpdir, "test.html")
            exporter.export_html(html_path)
            assert os.path.exists(html_path)
            
            # 导出 PDF
            pdf_path = os.path.join(tmpdir, "test.pdf")
            exporter.export_pdf(pdf_path)
            assert os.path.exists(pdf_path)
            
            # 导出 Word
            word_path = os.path.join(tmpdir, "test.docx")
            exporter.export_word(word_path)
            assert os.path.exists(word_path)
    
    def test_editor_statistics(self):
        """测试编辑器统计功能"""
        content = """# Title

Line 1
Line 2
Line 3

Characters test
"""
        editor = MarkdownEditor(content)
        
        assert editor.get_line_count() > 0
        assert editor.get_character_count() > 0
        assert editor.get_word_count() > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=.", "--cov-report=html"])
