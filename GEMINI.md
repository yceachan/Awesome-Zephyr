# Awesome-Zephyr

## Resource Map
- `sdk`:zerphy ROTS 开发环境
  - `$ZEPHYR_BASE=/home/pi/Zephyr-Suite/sdk/source/zephyr`
  - `$ZEPHYR_BASE/doc/**.rts` : 与官方wiki结构对齐的本地rst文档，优先参阅.
  - `wiki url`:[Developing with Zephyr — Zephyr Project Documentation]
- `docs` :soft link to`$ZEPHYR_BASE/doc`
  - [tree -f -d 索引](DocIndex.md)
- `note`:Agent与开发者共同治理的笔记
- `prj`:工程base路径
(https://docs.zephyrproject.org/latest/develop/index.html)

## Gemini CLI Project Conventions

- **Note yaml header**

  ```yaml
  #always begin markdown with yaml ,but not H1 title.
  ---   
  #Maintenanced by Agent.
  title:
  tags: [tag1 , ... ] 
  desc: one sentence description
  update: YYYY-MM-dd
  #leave a new line between yaml end with`---`
  ---
  
  # H1 Title 
  ```
  
- **Mermaid** 
  
  - **whenever** naming a node ,especially with chars like `/ \ () （）`,and chinese,using`""`to include the whole node name.
    - e.g. `GpioLib["GPIO库"] -- register --> Sysfs["/sys/class/gpio"]`

- 中文知识输出：
  - 最终结论和文档输出必须使用中文，同时保留专业英文术语
  - 高价值的知识输出始终应固化在文件系统而非上下文缓存，当开发者未明确指示路径，Agent应智能判断一个适合的路径，并提出写入建议。
  
- Reference:

  - respective all authority source,if Agent refer then ,mark it  below the 1st H1 Title :

    - ```md
      # H1 Title
      
      > [!note]
      > **Ref:** [wiki](url)
      
      text...
      ```

