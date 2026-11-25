# 纤笺 · 手稿纸张纤维谱来源鉴别

西廊纸样研究室有 3 位纸样员和 1 位库房管理员。显微照片、参考藏批和回库单原先分成三份台账，常发生同藏批泄漏验证、拿旧图写意见或纸样误回架。系统使用合成观察计数和藏批资料，输出纸样材料归档意见给库房。

## 一天的工作顺序

1. 08:40 从 D3-11 接收汊口航程簿 MS41 切片 MS41-a.tif。
2. 09:10 确认 Q-X 参考样隔离，拟合剩余九份。
3. 10:00 选择棉布、苇浆、韧皮三项计数；按藏批留组。
4. 10:25 对 MS41 核对最接近苇浆纸及其距离。
5. 11:00 对 MS46 比对，候选余量不足时回库签单拒绝。
6. 13:15 用错架 B5-03 测试保管链，改回 D3-11。
7. 14:05 库房审签 MS41 并写明材料意见限制。

## 算法口径

先按所选维度逐来源取参考质心，以余弦相似度排序。每次移除相同藏批重新拟合以做模型验证。胜出和次优余弦差小于 0.12，或保留藏批准确率小于 80% 时，不允许签材料归属意见。比对排队时冻结切片修订与纳入的参考藏批，旧任务照常算完留档供复核；参考库任何变更都会永久废止此前比对（改回原样也不恢复），取像修订使旧意见不得签核，旧任务晚到也不会顶掉更新的比对。签单时以当下仍有效、复核员刚核过的那份比对为准。

## 上手

```sh
cp .env.example .env
docker compose up -d --build --wait
docker compose exec -T backend python -m scripts.seed_demo
docker compose down --remove-orphans
```

前端走本机 **18460**，API 走 **19460**，PostgreSQL 走 **17960**。本地开发可在安装 Python 3.11、PostgreSQL 和 Redis 后配置与 Compose 相同的环境变量，在 backend 运行 `uvicorn app:app --reload`，前端以 Nginx 同源代理启动。

| 角色 | 邮箱 | 业务权限 |
|---|---|---|
| 录入员 | operator@demo.local | 登记切片、运行特征实验 |
| 复核员 | reviewer@demo.local | 管理参考批的纳入范围、审签回库 |
| 查阅员 | viewer@demo.local | 查托盘、参考、比对和回库联 |

三个演示账号默认密码均为 `Demo2026!`。使用本地合成样本，seed 只插入缺失的自然键。关闭 `SEED_DEMO` 可跳过自动 seed。使用自己的 `JWT_SECRET`、`POSTGRES_PASSWORD` 和 `DEMO_PASSWORD` 部署。

| 目录 | 技术与职责 |
|---|---|
| backend | Python 3.11 / FastAPI，使用 PostgreSQL 16；Worker 轮询持久化队列，Redis 为登录限流及健康检查提供支持 |
| frontend | Nginx、HTML、CSS、JavaScript ES modules，HTTP 同源代理 |
| docker-compose.yml | 5 服务及健康检查、独立卷；Redis 与 worker 无宿主端口 |

角色、作业状态在 `backend/core.py`、`frontend/base.js` 定义，在 `backend/core.py`（鉴权、队列）与 `backend/worker.py` 使用。领域阶段由数据库约束与业务服务维护，`frontend/view.js` 负责显示。接口输出为最新已提交状态。

演示使用计数而非实际显微图文件。相似度仅表示材料近似程度，材料意见交由库方复核。

MIT License
