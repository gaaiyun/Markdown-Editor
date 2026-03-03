"""
Markdown 编辑器模块
提供 Markdown 解析、预览、目录生成等功能
"""

import re
import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TableOfContentsItem:
    """目录项"""
    level: int
    title: str
    anchor: str
    line_number: int


class MarkdownEditor:
    """Markdown 编辑器"""
    
    def __init__(self, content: str = ""):
        """
        初始化编辑器
        
        Args:
            content: 初始 Markdown 内容
        """
        self.content = content
        self.toc: List[TableOfContentsItem] = []
    
    def set_content(self, content: str) -> None:
        """
        设置编辑器内容
        
        Args:
            content: Markdown 内容
        """
        self.content = content
        self._parse_toc()
    
    def get_content(self) -> str:
        """
        获取编辑器内容
        
        Returns:
            Markdown 内容
        """
        return self.content
    
    def _parse_toc(self) -> None:
        """解析目录"""
        self.toc = []
        lines = self.content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # 匹配标题 # H1, ## H2, ### H3 等
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                anchor = self._generate_anchor(title)
                self.toc.append(TableOfContentsItem(
                    level=level,
                    title=title,
                    anchor=anchor,
                    line_number=line_num
                ))
    
    def _generate_anchor(self, title: str) -> str:
        """
        生成标题锚点
        
        Args:
            title: 标题文本
            
        Returns:
            锚点字符串
        """
        # 转换为小写，替换空格为连字符，移除特殊字符
        anchor = title.lower()
        anchor = re.sub(r'[^\w\s-]', '', anchor)
        anchor = re.sub(r'\s+', '-', anchor)
        return anchor
    
    def get_table_of_contents(self) -> List[TableOfContentsItem]:
        """
        获取目录
        
        Returns:
            目录项列表
        """
        if not self.toc:
            self._parse_toc()
        return self.toc
    
    def get_toc_html(self) -> str:
        """
        获取 HTML 格式的目录
        
        Returns:
            HTML 格式的目录
        """
        if not self.toc:
            self._parse_toc()
        
        if not self.toc:
            return ""
        
        html = "<div class='toc'>\n<h3>目录</h3>\n<ul>\n"
        
        for item in self.toc:
            indent = "  " * (item.level - 1)
            html += f"{indent}<li><a href='#{item.anchor}'>{item.title}</a></li>\n"
        
        html += "</ul>\n</div>"
        return html
    
    def render_markdown(self, extensions: List[str] = None) -> str:
        """
        渲染 Markdown 为 HTML
        
        Args:
            extensions: Markdown 扩展列表
            
        Returns:
            HTML 内容
        """
        if extensions is None:
            extensions = ['extra', 'codehilite', 'toc']
        
        md = markdown.Markdown(extensions=extensions)
        html = md.convert(self.content)
        return html
    
    def render_with_highlight(self) -> str:
        """
        渲染带语法高亮的 Markdown
        
        Returns:
            带语法高亮的 HTML 内容
        """
        # 使用 codehilite 扩展进行代码高亮
        md = markdown.Markdown(
            extensions=['extra', 'codehilite'],
            extension_configs={
                'codehilite': {
                    'linenums': True,
                    'guess_lang': False
                }
            }
        )
        return md.convert(self.content)
    
    def get_word_count(self) -> int:
        """
        获取字数统计
        
        Returns:
            字数
        """
        # 移除 Markdown 标记
        text = re.sub(r'[#*`_\[\]()<>]', '', self.content)
        text = re.sub(r'\s+', ' ', text)
        return len(text.strip())
    
    def get_line_count(self) -> int:
        """
        获取行数统计
        
        Returns:
            行数
        """
        return len(self.content.split('\n'))
    
    def get_character_count(self) -> int:
        """
        获取字符数统计
        
        Returns:
            字符数
        """
        return len(self.content)


class ImageUploader:
    """图片上传器（图床支持）"""
    
    def __init__(self, api_url: str = "", api_key: str = ""):
        """
        初始化图片上传器
        
        Args:
            api_url: 图床 API URL
            api_key: API 密钥
        """
        self.api_url = api_url
        self.api_key = api_key
    
    def upload_image(self, image_path: str) -> Optional[str]:
        """
        上传图片到图床
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            图片 URL，如果上传失败则返回 None
        """
        if not self.api_url:
            return None
        
        try:
            import requests
            
            with open(image_path, 'rb') as f:
                files = {'file': f}
                headers = {}
                
                if self.api_key:
                    headers['Authorization'] = f'Bearer {self.api_key}'
                
                response = requests.post(self.api_url, files=files, headers=headers)
                response.raise_for_status()
                
                # 假设返回 JSON 格式：{"url": "https://..."}
                data = response.json()
                return data.get('url')
                
        except Exception as e:
            print(f"图片上传失败：{e}")
            return None
    
    def insert_image_markdown(self, image_url: str, alt_text: str = "image") -> str:
        """
        生成图片的 Markdown 语法
        
        Args:
            image_url: 图片 URL
            alt_text: 替代文本
            
        Returns:
            Markdown 格式的图片语法
        """
        return f"![{alt_text}]({image_url})"


def create_editor(content: str = "") -> MarkdownEditor:
    """
    创建 Markdown 编辑器的便捷函数
    
    Args:
        content: 初始内容
        
    Returns:
        MarkdownEditor 实例
    """
    return MarkdownEditor(content)
