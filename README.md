# Markdown 编辑器 📝

一个功能齐全的实时预览 Markdown 编辑器，基于 Streamlit 构建。

## ✨ 功能特性

- **实时预览**：编辑 Markdown 时立即看到渲染效果
- **语法高亮**：支持代码块的语法高亮显示
- **目录生成**：自动从标题生成文章目录
- **导出功能**：支持导出为 HTML、PDF、Word 格式
- **图床支持**：可配置图床，上传图片自动生成 Markdown 链接
- **主题切换**：提供多种编辑主题（default、dark、github、paper）
- **文件操作**：新建、打开、保存 Markdown 文件
- **统计分析**：实时显示字符数、行数、字数统计

## 🚀 快速开始

### 安装依赖

```bash
cd markdown-editor
pip install -r requirements.txt
```

### 运行应用

```bash
streamlit run dashboard.py
```

浏览器会自动打开 http://localhost:8501

## 📁 项目结构

```
markdown-editor/
├── dashboard.py          # 主界面
├── markdown_editor.py    # 编辑器模块
├── exporter.py           # 导出模块
├── requirements.txt      # 依赖列表
├── README.md            # 本文档
└── tests/
    └── test_editor.py   # 单元测试
```

## 🎯 使用说明

### 编辑 Markdown

1. 在左侧编辑区输入 Markdown 内容
2. 右侧实时预览渲染效果
3. 使用侧边栏切换主题

### 文件操作

- **新建**：创建空白文档
- **打开**：上传本地 Markdown 文件
- **保存**：保存当前内容到文件

### 导出文档

1. 在侧边栏选择导出格式（HTML/PDF/Word）
2. 点击"导出文件"按钮
3. 文件将保存到当前目录

### 图片上传

1. 在侧边栏配置图床 API（可选）
2. 上传图片文件
3. 如果配置了图床，自动生成 Markdown 链接
4. 否则仅在本地预览

### 主题切换

在侧边栏选择主题：
- **default**：默认白色主题
- **dark**：深色主题
- **github**：GitHub 风格
- **paper**：纸张质感

## 🧪 运行测试

```bash
# 运行单元测试
pytest tests/test_editor.py -v

# 生成覆盖率报告
pytest tests/test_editor.py -v --cov=. --cov-report=html

# 查看覆盖率报告
# 打开 htmlcov/index.html
```

## 📦 依赖说明

- **streamlit**：Web 应用框架
- **markdown**：Markdown 解析
- **pygments**：语法高亮
- **reportlab**：PDF 生成
- **python-docx**：Word 文档处理
- **Pillow**：图片处理
- **requests**：HTTP 请求（图床上传）
- **pytest**：测试框架
- **pytest-cov**：测试覆盖率

## ⚙️ 图床配置

支持配置任意图床 API，常见选项：

### ImgBB
```
API URL: https://api.imgbb.com/1/upload
API Key: 你的 API Key
```

### SM.MS
```
API URL: https://api.sm.ms/v2/upload
API Key: 你的 API Token
```

### 自建图床
按照图床 API 文档配置 URL 和密钥

## 🎨 自定义

### 添加新主题

在 `dashboard.py` 的 `get_theme_css()` 函数中添加新主题：

```python
themes = {
    "custom": """
        body { background-color: #your-color; color: #your-text; }
        .preview-container { background-color: #your-bg; }
    """,
    # ... 其他主题
}
```

### 扩展导出格式

在 `exporter.py` 中添加新的导出方法：

```python
def export_custom(self, output_path: str) -> str:
    # 自定义导出逻辑
    pass
```

## 📝 Markdown 语法支持

支持标准 Markdown 语法及扩展：

- 标题（H1-H6）
- 粗体、斜体
- 列表（有序、无序）
- 链接、图片
- 代码块（带语法高亮）
- 表格
- 引用块
- 分隔线
- 任务列表

## 🐛 已知问题

- PDF 导出对复杂 Markdown 格式支持有限
- 图片上传需要配置图床 API

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请创建 Issue。

---

**Made with ❤️ using Streamlit**
