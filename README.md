# Linux / 国产操作系统应用兼容性自动化测试工具

一个面向 Linux 及国产 Linux 操作系统的应用兼容性自动化测试工具。

项目通过自动采集运行环境、执行多维度兼容性测试、分析失败原因并生成测试报告，对目标应用在当前 Linux 环境中的运行兼容性进行综合评估。

## 项目特点

- Linux 操作系统与 CPU 架构兼容性检测
- 国产 Linux 操作系统兼容性规则
- Python / Java 运行时检测
- 系统命令可用性检测
- 文件系统兼容性检测
- 权限兼容性检测
- 进程兼容性检测
- 网络兼容性检测
- 应用启动与健康检查
- 应用依赖环境检测
- 内存与磁盘资源检查
- 自动化测试流程编排
- 测试失败原因诊断
- 兼容性综合评估
- JSON / Markdown / HTML 多格式报告
- SQLite 测试历史记录

## 支持的平台

当前兼容性规则覆盖：

- Ubuntu
- Debian
- Kylin Linux
- UnionTech UOS
- openEuler
- RHEL
- CentOS
- Rocky Linux
- AlmaLinux
- Fedora

支持的主要 CPU 架构：

- x86_64 / amd64
- ARM64 / aarch64
- ppc64le
- s390x

其中针对 Kylin、UOS 和 openEuler 提供了独立的平台兼容性规则。

## 项目架构

```text
linux-os-compatibility-test/
├── bin/                    # 启动脚本
├── configs/                # 测试用例与兼容性规则
├── data/                   # SQLite 运行历史数据
├── examples/               # 示例应用
├── offline/                # 离线安装相关脚本
├── reports/                # 测试生成的报告
├── src/
│   ├── analyzer/           # 日志分析
│   ├── collector/          # 环境信息采集
│   ├── compatibility/      # 兼容性评估
│   ├── dependency/         # 依赖检查
│   ├── diagnostics/        # 失败原因诊断
│   ├── executor/           # 测试执行
│   ├── history/            # 测试历史记录
│   ├── orchestrator/       # 测试流程编排
│   ├── report/             # 报告生成
│   └── testcase/           # 测试用例
└── README.md
