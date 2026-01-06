# 版本changelog说明

## 2.0.0
- [feat] agent配置
- [feat] agent发布
- [feat] agent模板
- [feat] agent自定义空间
- [feat] agent复制

## 2.0.1
- [dependency] Update agent-go-common-pkg to v1.0.4
对应pkg变更：更新于 context_organize_content.go，临时区变量增加['answer']

## 2.0.2
- [dependency] Update agent-go-common-pkg to v1.0.5
更新context_organize_content.go中的临时区相关内容: 增加临时区变量条件判断，仅在存在 answer 时将临时区信息添加到reference中


## 2.0.3
- [dependency] Update agent-go-common-pkg to v1.0.6
  - pkg的配置config结构体的数据源中增加“指标”、“知识条目”配置
- [feat] 添加智能体批量获取指定字段接口(目前模型工厂Benchmark使用)
- [feat] 日志logger的level改成使用chart中的配置项
- [feat] 新增智能问数内置产品类型；
- [feat] 新增策略分类列表接口 && 新增策略列表接口

## 2.0.4
- [feat] 增加http server优雅关闭
- [feat] 新增agent self_config字段结构查询接口
- [feat] 添加知识条目数量限制校验
- [feat] agent配置-“自然语言模式”支持开启和关闭”任务规划模式“
- [fix]  应用账号权限检查
- [fix] 修复历史版本排序问题
- [fix] 修复“自定义空间”列表接口重复问题


## 2.0.5
- [feat] 工具配置新增超时时间,修改agent-go-common-pkg版本
- [feat] AI生成接口使用默认大模型，去除configmap中的默认大模型配置
- [refact] 重构: 将 Model Factory 相关接口重命名为 Model API
- [chore] 删除部分无用的代码
- [feat] 增加x-account-id和x-account-type相关支持
- [feat] agent config.config_metadata中增加config_last_set_timestamp（配置最后设置时间）
- [feat] 添加业务域关联功能及HTTP请求日志
- [refact] 重构业务域服务、Agent导入及已发布代理列表相关代码
- [chore] 移除已发布智能体列表缓存及自定义空间相关代码
- [test] 添加MockGen生成的mock文件
- [chore] 删除spacesvc模块（自定义空间相关代码）
- [feat] 新增agent模板业务域关联修复功能及测试接口
- [fix] 适配mdl-go-lib VisitorType调整，支持User和RealName两种用户类型
- [fix] agent-permission/execute接口支持应用账号访问
- [refact] 权限服务移除自定义空间权限相关代码

## 2.0.6
- [fix] 去除部署工作台默认大模型配置
- [fix] 升级go依赖，解决高危漏洞
- [fix] agent更新时config比较忽略metadata字段，避免因metadata变化触发不必要的更新
- [chore] 代码格式化统一

## 2.0.7
- [feat] HTTP请求日志重构：区分客户端和服务端日志
- [feat] 支持 Agent 三态状态过滤及空列表时 IsLastPage 修复
- [feat] 添加MQ配置结构体及加载逻辑，初始化审计日志处理器
- [fix] 修复MQ配置加载时传递指针引用的问题
- [fix] 修复个人空间Agent列表查询的SQL构建问题
- [refact] 重构私有路由中间件注册方式
- [refact] 注释掉Agent资源类型更新逻辑
- [feat] 数据库SQL脚本下沉到微服务内部管理 && 数据库合并到ADP库
- [chore] 组件元数据配置新增redis和mq依赖

## 2.0.8
- [refact] 重构 Agent 最新版本号获取逻辑，提取 `getLatestVersion` 方法，修复未发布/取消发布场景的版本号问题
