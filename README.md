<p align="center">
  <img src="assets/wow-skills-icon.svg" alt="wow-skills icon" width="320">
</p>

# wow-skills

这是一个持续积累和验证 skill 的仓库，主要收纳软件开发、日常办公相关、可以重复使用的高质量技能包。

这个项目的目标不是堆叠提示词，而是沉淀边界清晰、来源可追踪、效果可验证的工作单元，方便后续不断扩展。

## 当前收录

- `reliable-code-systems`：面向可靠软件开发的架构、验证、CI 和可观测性规范。

## 目录约定

- `skills/<skill-name>/SKILL.md`：skill 主说明
- `skills/<skill-name>/agents/`：该 skill 相关的 agent 配置
- 可选的 `assets/`、`scripts/`、`examples/`：示例、素材或辅助验证文件

## 收录标准

- 场景明确，知道它解决什么问题
- 可以重复执行，不依赖偶然结果
- 有验证方式，能检查是否真的有效
- 不依赖黑盒猜测，行为尽量可解释
- 能说清适用范围和边界
- 尽量附带示例、检查清单或测试方法

## 新增 Skill 的方式

1. 在 `skills/` 下创建独立目录
2. 写清触发条件、适用范围、步骤和输出
3. 补充验证方法、样例或脚本
4. 如有必要，把 agent 配置和辅助文件一起放进目录
5. 更新本 README 的“当前收录”列表

## 维护原则

- 先验证，再收录
- 先明确边界，再扩展功能
- 先保留可追溯性，再追求便捷
- 软件开发类 skill 和办公类 skill 都要能真正落地
