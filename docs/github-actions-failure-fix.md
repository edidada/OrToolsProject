# GitHub Actions 失败分析与修复

## 现象

工作流 `PuLP Optimization CI` 在 2026-10-02 的运行 `37006144349` 失败。失败矩阵中，macOS/Linux 的 pytest 步骤失败，Windows 还在运行示例时提前失败。

## 根因

1. `test_pulp.py` 的四个断言使用了高于实际理论最优值的阈值。给定资源约束，原始目标 `30*x1 + 20*x2` 的最优解是 `x1=36`、`x2=28`，目标值为 `1640`，而不是至少 `2000`。敏感性用例的实际最优值分别是 `1640`、`2000`、`1920`。
2. Windows GitHub-hosted runner 默认输出编码为 CP1252。`pulp_example.py` 输出中文标题时触发 `UnicodeEncodeError`，因此示例步骤退出为 1。
3. 工作流直接安装未限定版本的 PuLP 与 pytest，与 `pyproject.toml` 声明的兼容范围不一致，后续依赖发布可能导致不可重复的 CI 结果。

## 修改方案

- 将最优值测试改为精确的 `pytest.approx` 断言，并在敏感性测试中检查求解状态。
- 为 `test-pulp` job 设置 `PYTHONUTF8=1`，让三种 runner 均按 UTF-8 输出中文。
- 将 CI 安装范围固定为 `pulp>=2.8,<3.0` 和 `pytest>=7.4,<8`，与项目声明一致。
- 更正示例的资源展示：PuLP 的 `constraint.value()` 是残差，右侧上限为 `-constraint.constant`；现在展示真实的已使用资源和上限。

## 验证

本地执行：

```bash
python pulp_example.py
python -m pytest test_pulp.py -v
```

预期：示例正常结束并展示资源用量，13 个测试全部通过。推送后由 GitHub Actions 在 Ubuntu、Windows、macOS 与 Python 3.9–3.11 矩阵中再次验证。
