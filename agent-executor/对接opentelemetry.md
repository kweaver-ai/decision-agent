请你对当前代码做一些改造，当前代码中使用的trace 和 log 是自研的sdk，o11y 。 我希望在后续替换成开源的 Opentelemetry sdk ，现在需要你帮我先改造一部分代码验证一下可行性和效果，你可以先改造run_agent.py，然后验证。
要求：
1. 使用支持python 3.10.12的最新版本的OpentelemetrySDK
2. 能够进行 log trace metric 的 埋点和上报，并且不使用collector 而是直接使用 http方式，同时要支持控制台打印方式（console）； 
3. 支持trace 和 log 的关联
4. log 也使用 Opentelemetry 规范的标准log SDK
5. 注释尽可能详尽
6. 埋点方式详细，包括路由请求的埋点，内部方法实现的埋点
7. 解释一下上报到哪里， 会如何调用上报方法
8. 服务的框架基于fastapi
9. 中要支持span 和 log 都 附加一些attributes
10. 支持配置项，比如是否启用trace 、log 、metric, 三种数据都可以选择是否启用，同时也能选择启用上报的方式是console 还是http 
11. 代码编写时注意结构简洁，不要在一个方法内包含所有代码
12. 给出的代码中应该包含所有trace/log/metric的使用示例，比如中间件的实现，handler中记录span，记录log，记录metric等