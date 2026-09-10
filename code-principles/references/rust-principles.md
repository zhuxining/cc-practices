---
paths:
- "**/*.rs"
---

# Rust 代码规范

编写**安全、惯用、可维护**的 Rust 代码。优先使用类型系统和所有权表达约束，避免不必要的分配、复制和抽象。

## 项目约束

- 修改前检查 `Cargo.toml`、`rust-toolchain.toml`、edition、`rust-version`、feature 和 CI 配置
- 遵循项目已有的错误类型、异步运行时、日志、测试和依赖约定
- 使用新语法、标准库 API 或依赖版本前，确认不会无意提高 MSRV
- 注意 `no_std`、目标平台和 workspace resolver，不假设所有 feature 可以同时启用

## 类型设计

- 使用 enum 表达互斥状态，避免用多个布尔值组合出非法状态
- 使用 newtype 区分容易混淆的值，或封装表示和不变量；不要机械包装每个基础类型
- 仅在 API 使用顺序属于重要且稳定的不变量时使用 typestate
- 静态分发使用泛型或 `impl Trait`；需要运行时多态或异构集合时使用 `dyn Trait`
- 为公开类型实现语义成立且调用者需要的常用 trait，不要盲目派生 `Clone`、`PartialEq`、`Hash` 或 `Default`
- 优先使用标准转换 trait，如 `From`、`TryFrom`、`AsRef` 和 `AsMut`
- API 应使非法状态难以表达，但类型复杂度应与误用风险相称

## 所有权与借用

- 只读访问通常使用借用；需要存储、转移、跨线程发送或消费值时按值接收
- 小型 `Copy` 类型通常按值传递
- 借用 owned 容器时使用底层视图：`&str`、`&[T]`、`&Path`，除非接口确实需要具体容器能力
- 避免不必要的 `.clone()`，但不要仅为消除 clone 引入复杂生命周期
- 显式生命周期只用于消除歧义或表达输入输出关系，不为标注而标注
- 仅在多数路径可借用、少数路径需要拥有且确有收益时使用 `Cow`
- 使用 RAII 管理资源，确保提前返回、错误和 panic 路径也能释放资源

## 惯用写法

- 使用模式匹配表达结构和分支；单一模式使用 `if let`，提前退出可使用 `let-else`
- 使用 `?` 传播错误，避免只为拆包编写重复的 `match`
- 循环和迭代器都属于惯用写法，选择更清晰且不产生无意义中间集合的实现
- 使用迭代器适配器表达转换流程，复杂控制流使用普通循环
- 使用 `format!` 构造新字符串，向已有缓冲区写入时使用 `write!`
- 使用解构减少重复字段访问，但不要牺牲可读性
- 使用 `Default` 表达有明确语义的默认值，不为所有类型强行实现默认状态

## 错误处理

- 使用 `Option` 表达值可能不存在，使用 `Result` 表达操作可能失败
- 使用 `?` 保留错误传播路径，并在跨越有意义的系统边界时补充上下文
- 库的公开错误应便于调用者检查和处理；应用边界可在无需按变体恢复时使用类型擦除错误
- `thiserror` 和 `anyhow` 是常见选择，不是强制依赖
- 保留底层错误 source，不要仅用字符串丢失错误链和可检查的类别
- `unwrap` 和 `expect` 仅用于已证明不可能失败、测试代码或 panic 明确属于程序契约的场景
- `expect` 信息应说明该状态为何不可能发生，而不是重复底层错误
- 不要静默忽略错误；有意忽略时必须让原因在代码或注释中清晰可见

## 公开 API

- 公开 API 使用 rustdoc 说明用途和契约
- 按适用情况记录 `# Errors`、`# Panics` 和 `# Safety`
- 文档示例适合编译运行时优先使用 doctest
- 谨慎暴露依赖 crate 的具体类型，避免将内部依赖变成公共 API
- 评估 SemVer：公开 enum 增加 variant、公开 struct 增加字段和改变 trait 实现都可能影响下游代码
- 需要保留扩展空间时使用私有字段、构造器、sealed trait 或 `#[non_exhaustive]`

## 并发

- 根据所有权、吞吐、背压和一致性要求选择消息传递或共享状态
- 缩小锁保护的数据和持锁范围
- 不要在持锁时执行 I/O、长计算、回调或获取顺序不明确的其他锁
- 共享所有权使用 `Arc`；内部同步原语根据读写模式和运行时选择，不默认使用 `RwLock`
- 仅在竞争分析或基准表明确有需要时使用分片容器或原子类型
- 原子代码必须说明内存序和依赖的不变量；`DashMap` 是分片锁容器，不是无锁容器
- 不要手动实现 `Send` 或 `Sync`，除非能完整证明线程安全契约

## 异步代码

- 不要在 executor 工作线程中执行阻塞 I/O 或长时间 CPU 计算
- 优先使用异步 API；必须卸载阻塞工作时使用运行时提供的 blocking 机制，并限制并发和关闭行为
- 不要跨 `.await` 持有同步锁 guard；异步锁也不要覆盖无关 I/O 或长计算
- 使用 `select!`、timeout 或取消时，确认 future 的 cancellation safety
- 后台任务必须有明确所有者负责取消、等待、处理错误和关闭
- 原生 trait `async fn` 适合静态分发；需要 `dyn Trait` 时显式返回 boxed Future，或在接受其成本时使用 `async-trait`
- 仅当 Future 被要求为 `Send` 时，跨 `.await` 持有 `!Send` 值才会报错；local task 可以使用 `!Send` 值

## Unsafe 与 FFI

- 优先使用安全 Rust；无需 unsafe 的 crate 可使用 `#![forbid(unsafe_code)]`
- 每个 `unsafe` 块必须写 `// SAFETY:`，说明调用前置条件以及当前代码如何满足条件
- `unsafe fn` 和 `unsafe trait` 必须在 `# Safety` 中记录调用者或实现者的责任
- 将 unsafe 封装在尽可能小的私有模块中，通过安全 API 保护不变量
- 检查有效性、对齐、别名、生命周期、初始化状态以及 panic/unwind 路径
- 除非能完整证明布局和有效值等不变量，否则不要使用 `transmute`；优先使用标准转换 API
- FFI 边界必须验证指针、长度、所有权、ABI 和外部数据有效性，不允许 panic 穿越不支持 unwind 的边界

## 性能与安全

- 先使用 profile、benchmark 或内存数据定位瓶颈，再优化
- 已知最终大小时使用 `with_capacity` 等方式预分配集合
- 避免无意义的中间集合和热路径分配，但以代码清晰为前提
- 仅因结构体较大不要使用 `Box`；装箱用于间接寻址、稳定地址、递归类型、trait object 或控制外层类型大小
- 外部输入必须验证，并限制大小、深度、数量、时间和并发
- 避免敏感值进入 `Debug`、错误和日志；根据威胁模型决定是否使用 `secrecy` 或 `zeroize`
- 使用项目约定的工具检查依赖漏洞和供应链风险；`cargo audit` 不能替代依赖审查

## 测试

- 单元测试放在被测模块内；较大测试集可以拆为子模块
- 跨 crate 的公共行为放在 `tests/`，公开文档示例优先使用 doctest
- 测试围绕一个可描述的场景组织，可以验证该场景下多个相关结果
- 覆盖成功路径、失败路径和关键边界；修复 bug 时添加回归测试
- 对返回 `Result` 的 API 优先断言错误值；仅当 panic 属于契约时使用 `#[should_panic]`
- 存在可表达不变量和较大输入空间时使用属性测试或 fuzz
- unsafe 或并发代码按风险使用 Miri、sanitizer 或 `loom`
- `#[ignore]` 必须注明原因和运行方式，不得长期掩盖关键回归失败

## 提交前检查

优先运行项目已有验证命令。没有项目约定时，按实际 workspace、target 和 feature 调整后运行：

```bash
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --workspace --all-features
```

`cargo clippy --fix` 会修改源码并隐含 `--all-targets`，仅在明确需要应用并审查自动修复时运行。互斥 feature 的项目不要使用 `--all-features`。

## 权威来源（不确定时参考）

| 主题 | 官方参考 |
|------|---------|
| 语言、标准库与 Unsafe | [Rust Documentation](https://doc.rust-lang.org/) |
| 语言规则与 dyn compatibility | [The Rust Reference](https://doc.rust-lang.org/reference/) |
| Cargo、MSRV、feature 与 SemVer | [The Cargo Book](https://doc.rust-lang.org/cargo/) |
| 公开 API 设计 | [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/) |
| Edition 迁移 | [Edition Guide](https://doc.rust-lang.org/edition-guide/) |
| 版本变更 | [Rust Release Notes](https://doc.rust-lang.org/releases.html) |
| Tokio 行为 | [Tokio Documentation](https://docs.rs/tokio/latest/tokio/) |
