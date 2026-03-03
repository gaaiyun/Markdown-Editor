"""
Markdown 编辑器 - 主界面
使用 Streamlit 构建的实时预览 Markdown 编辑器
"""

import streamlit as st
import os
import base64
from datetime import datetime
from pathlib import Path

from markdown_editor import MarkdownEditor, ImageUploader
from exporter import MarkdownExporter


# 页面配置
st.set_page_config(
    page_title="Markdown 编辑器",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS 样式
def load_css():
    """加载自定义 CSS"""
    st.markdown("""
    <style>
    .stTextArea label {
        font-weight: bold;
    }
    .editor-container {
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 10px;
    }
    .preview-container {
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 20px;
        background-color: #fafafa;
    }
    .toc-container {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .stat-box {
        display: inline-block;
        padding: 10px 20px;
        margin: 5px;
        background-color: #e3f2fd;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)


def get_theme_css(theme: str) -> str:
    """
    获取主题 CSS
    
    Args:
        theme: 主题名称
        
    Returns:
        CSS 样式字符串
    """
    themes = {
        "default": """
            body { background-color: #ffffff; color: #333333; }
            .preview-container { background-color: #fafafa; }
        """,
        "dark": """
            body { background-color: #1e1e1e; color: #d4d4d4; }
            .preview-container { background-color: #2d2d2d; color: #d4d4d4; }
            .toc-container { background-color: #3c3c3c; color: #d4d4d4; }
        """,
        "github": """
            body { background-color: #f6f8fa; color: #24292e; }
            .preview-container { background-color: #ffffff; border: 1px solid #e1e4e8; }
        """,
        "paper": """
            body { background-color: #f5f5dc; color: #333333; }
            .preview-container { background-color: #fffef0; }
        """
    }
    return themes.get(theme, themes["default"])


def init_session_state():
    """初始化会话状态"""
    if 'content' not in st.session_state:
        st.session_state.content = """# 欢迎使用 Markdown 编辑器

这是一个功能齐全的 **Markdown 编辑器**，支持：

## 功能特性

- ✅ **实时预览**：编辑时立即看到效果
- ✅ **语法高亮**：代码块自动高亮
- ✅ **目录生成**：自动生成文章目录
- ✅ **导出功能**：支持 HTML、PDF、Word
- ✅ **图床支持**：图片上传到图床
- ✅ **主题切换**：多种编辑主题

## 代码示例

```python
def hello_world():
    print("Hello, Markdown!")
```

## 表格示例

| 功能 | 状态 |
|------|------|
| 实时预览 | ✅ |
| 语法高亮 | ✅ |
| 导出功能 | ✅ |

开始编辑吧！✏️
"""
    if 'theme' not in st.session_state:
        st.session_state.theme = "default"
    if 'image_host_url' not in st.session_state:
        st.session_state.image_host_url = ""
    if 'image_host_key' not in st.session_state:
        st.session_state.image_host_key = ""


def main():
    """主函数"""
    load_css()
    init_session_state()
    
    # 侧边栏
    with st.sidebar:
        st.title("🛠️ 工具栏")
        
        # 主题选择
        theme = st.selectbox(
            "🎨 选择主题",
            ["default", "dark", "github", "paper"],
            index=["default", "dark", "github", "paper"].index(st.session_state.theme)
        )
        st.session_state.theme = theme
        
        # 应用主题
        st.markdown(f"<style>{get_theme_css(theme)}</style>", unsafe_allow_html=True)
        
        st.divider()
        
        # 文件操作
        st.subheader("📁 文件操作")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 新建", use_container_width=True):
                st.session_state.content = "# 新文档\n\n开始写作..."
                st.rerun()
        
        with col2:
            # 文件上传
            uploaded_file = st.file_uploader("打开", type=['md', 'txt'], label_visibility="collapsed")
            if uploaded_file:
                content = uploaded_file.read().decode('utf-8')
                st.session_state.content = content
                st.rerun()
        
        # 保存文件
        if st.button("💾 保存", use_container_width=True):
            file_name = st.text_input("文件名", value=f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
            if file_name:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(st.session_state.content)
                st.success(f"已保存到 {file_name}")
        
        st.divider()
        
        # 导出功能
        st.subheader("📤 导出")
        
        export_format = st.selectbox("导出格式", ["HTML", "PDF", "Word"])
        
        if st.button("导出文件", use_container_width=True):
            editor = MarkdownEditor(st.session_state.content)
            exporter = MarkdownExporter(st.session_state.content)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if export_format == "HTML":
                output_path = f"export_{timestamp}.html"
                exporter.export_html(output_path)
                st.success(f"已导出为 HTML: {output_path}")
            elif export_format == "PDF":
                output_path = f"export_{timestamp}.pdf"
                exporter.export_pdf(output_path)
                st.success(f"已导出为 PDF: {output_path}")
            elif export_format == "Word":
                output_path = f"export_{timestamp}.docx"
                exporter.export_word(output_path)
                st.success(f"已导出为 Word: {output_path}")
        
        st.divider()
        
        # 图床设置
        st.subheader("🖼️ 图床设置")
        
        with st.expander("配置图床"):
            api_url = st.text_input("API URL", value=st.session_state.image_host_url)
            api_key = st.text_input("API Key", value=st.session_state.image_host_key, type="password")
            
            if st.button("保存配置"):
                st.session_state.image_host_url = api_url
                st.session_state.image_host_key = api_key
                st.success("图床配置已保存")
        
        # 图片上传
        uploaded_image = st.file_uploader("上传图片", type=['png', 'jpg', 'jpeg', 'gif', 'webp'])
        if uploaded_image:
            # 保存临时文件
            temp_path = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_image.name}"
            with open(temp_path, 'wb') as f:
                f.write(uploaded_image.getvalue())
            
            # 上传到图床
            if st.session_state.image_host_url:
                uploader = ImageUploader(st.session_state.image_host_url, st.session_state.image_host_key)
                image_url = uploader.upload_image(temp_path)
                if image_url:
                    image_md = uploader.insert_image_markdown(image_url, uploaded_image.name)
                    st.code(image_md, language="markdown")
                    st.session_state.content += "\n" + image_md + "\n"
                    st.rerun()
                else:
                    st.error("上传失败")
            else:
                # 本地显示
                st.image(uploaded_image, caption=uploaded_image.name)
                st.info("配置图床后可上传到图床")
            
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    # 主界面
    st.title("📝 Markdown 编辑器")
    
    # 统计信息
    editor = MarkdownEditor(st.session_state.content)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("字符数", editor.get_character_count())
    with col2:
        st.metric("行数", editor.get_line_count())
    with col3:
        st.metric("字数", editor.get_word_count())
    
    # 目录
    toc = editor.get_table_of_contents()
    if toc:
        with st.expander("📑 目录", expanded=False):
            toc_html = editor.get_toc_html()
            st.markdown(toc_html, unsafe_allow_html=True)
    
    # 编辑区域
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✏️ 编辑")
        content = st.text_area(
            "Markdown 内容",
            value=st.session_state.content,
            height=600,
            label_visibility="collapsed",
            key="editor"
        )
        st.session_state.content = content
    
    with col2:
        st.subheader("👁️ 预览")
        
        # 渲染 Markdown
        html_content = editor.render_with_highlight()
        
        # 添加自定义样式
        styled_html = f"""
        <style>
        .preview-container {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            background-color: #fafafa;
            overflow-y: auto;
            max-height: 600px;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', Courier, monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        pre code {{
            padding: 0;
            background: none;
        }}
        blockquote {{
            border-left: 4px solid #ddd;
            padding-left: 15px;
            color: #666;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f4f4f4;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
        </style>
        <div class="preview-container">
        {html_content}
        </div>
        """
        
        st.markdown(styled_html, unsafe_allow_html=True)
    
    # 底部信息
    st.divider()
    st.caption("Markdown 编辑器 v1.0 | 基于 Streamlit 构建")


if __name__ == "__main__":
    main()
