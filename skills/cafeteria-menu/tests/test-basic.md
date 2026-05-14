# 基本测试场景

## 环境准备

确保已配置 Cookie（参考 [reference/auth-guide.md](../reference/auth-guide.md)）：

```bash
# 方式一：环境变量
export KUAISHOU_CANTEEN_COOKIE="your_cookie_here"

# 方式二：本地文件
echo "your_cookie_here" > ~/.config/kuaishou_cookie.txt
```

---

## 场景 1：查询今日午餐（基础功能）

```bash
uv run scripts/cafeteria-recommendation.py --garden_name "元中心"
```

**预期结果：**
- 返回当天当前餐次的菜单
- 按品类分组展示（如：中式快餐/正餐、健康轻食等）

---

## 场景 2：口味过滤

```bash
uv run scripts/cafeteria-recommendation.py --garden_name "元中心" --taste_preference "辣"
```

**预期结果：**
- 只返回含辣/麻辣/香辣等词的菜品
- 按区域 → 档口分组展示

---

## 场景 3：指定档口查询

```bash
uv run scripts/cafeteria-recommendation.py --garden_name "元中心" --taste_preference "西部马华"
```

**预期结果：**
- 只返回"西部马华"档口的所有菜品
- 菜品数量上限自动扩大到 200

---

## 场景 4：指定日期

```bash
uv run scripts/cafeteria-recommendation.py --garden_name "杭州" --custom_date "2025-07-10" --taste_preference "低热量"
```

**预期结果：**
- 查询 2025-07-10 的菜单
- 按低热量关键词过滤

---

## 场景 5：负向过滤

```bash
uv run scripts/cafeteria-recommendation.py --garden_name "元中心" --taste_preference "不要葱"
```

**预期结果：**
- 返回不含"葱"字的菜品
- 结果列表不包含"小葱/葱油/葱花"等相关菜名

---

## 场景 6：无 Cookie 时的错误处理

清空 Cookie 环境变量和文件后运行：

```bash
unset KUAISHOU_CANTEEN_COOKIE
rm -f ~/.config/kuaishou_cookie.txt
uv run scripts/cafeteria-recommendation.py --garden_name "元中心"
```

**预期结果：**
- 输出清晰的 SSO 登录引导说明
- 不抛出未捕获异常，退出码为 1
