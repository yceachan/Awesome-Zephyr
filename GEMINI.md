# Awesome-Zephyr

## Resource Map

- `docs` :zephyr官方权威先验文档
  - `chunks` : 分章节chunk切分好的小量级文档，供Agent快速索引。
- `note`:Agent与开发者共同治理的笔记
- `prj`:工程base路径
- `sdk`:zerphy ROTS 开发环境

## Gemini CLI Project Conventions

- **Note yaml header**

  - md文件 必须以yaml header 为文件开头，而非一级标题
  - yaml元素，与`---`结尾空开一行
  - tags 和 update由Agent 智能维护

  ```
  ---   
  title:
  tags: [tag1 , ... ] 
  update: YYYY-MM-dd
  
  ---
  
  # Title 1   
  ```

- **Mermaid** 
  
  - **whenever** naming a node ,especially with chars like `/ \ () （）`,and chinese,using`""`to include the whole node name.
    - e.g. `GpioLib["GPIO库"] -- register --> Sysfs["/sys/class/gpio"]`

- 中文知识输出：
  - 最终结论和文档输出必须使用中文，同时保留专业英文术语
  - 高价值的知识输出始终应固化在文件系统而非上下文缓存，当开发者未明确指示路径，Agent应智能判断一个适合的路径，并提出写入建议。