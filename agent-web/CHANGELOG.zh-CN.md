# 更新日志

## [0.1.0] - 2026-01-13

### 优化

#### 依赖清理

移除了项目中未使用的冗余依赖，减小了包体积，提升了构建速度。

**移除的 dependencies（14个）：**

| 依赖包                    | 版本    | 移除原因                                |
| ------------------------- | ------- | --------------------------------------- |
| `array-move`              | 4.0.0   | 未使用                                  |
| `buffer`                  | ^6.0.3  | 使用 @rsbuild/plugin-node-polyfill 替代 |
| `codemirror`              | ^6.0.1  | 项目使用 Monaco Editor                  |
| `events`                  | 3.3.0   | 使用 @rsbuild/plugin-node-polyfill 替代 |
| `immer`                   | ^10.1.1 | 项目使用 mobx 进行状态管理              |
| `markdown-it`             | 14.0.0  | md-editor-rt 已内置                     |
| `numeral`                 | 2.0.6   | 未使用                                  |
| `prettier`                | 3.5.3   | 仅在 devDependencies 中保留             |
| `react-sortable-hoc`      | 2.0.0   | 项目使用 @dnd-kit 进行拖拽排序          |
| `react-use`               | 17.6.0  | 未使用                                  |
| `redoc`                   | 2.5.0   | 未使用                                  |
| `stream`                  | 0.0.2   | 使用 @rsbuild/plugin-node-polyfill 替代 |
| `use-deep-compare-effect` | 1.8.1   | 未使用                                  |
| `uuid`                    | 11.1.0  | 未使用                                  |
| `zustand`                 | 4.5.5   | 项目使用 mobx 进行状态管理              |

**移除的 devDependencies（4个）：**

| 依赖包               | 版本     | 移除原因           |
| -------------------- | -------- | ------------------ |
| `@types/codemirror`  | ^5.60.15 | codemirror 已移除  |
| `@types/events`      | ^3.0.3   | events 已移除      |
| `@types/markdown-it` | 14.1.1   | markdown-it 已移除 |

**新增的 devDependencies（1个）：**

| 依赖包                          | 版本   | 说明                                       |
| ------------------------------- | ------ | ------------------------------------------ |
| `@rsbuild/plugin-node-polyfill` | ^1.4.2 | 自动处理 Node.js 内置模块的浏览器 polyfill |

### 影响

- 减少了约 15+ 个未使用的依赖包
- 降低了 node_modules 体积
- 使用官方推荐的 polyfill 方案替代手动安装的 Node.js polyfill 包
