# 简搭衣橱

AI驱动的私人电子衣橱管理 + 场景化穿搭解决方案

## 核心功能
- 每日AI穿搭推荐（天气联动、场景定制、智能避坑）
- 我的衣橱管理（建档、分类、闲置统计、防重复采购）
- 穿搭记录沉淀（时间线、月度复盘、私人相册）
- 发现精选（身材/场景/色彩/衣橱干货，零带货）

## 开发

```bash
npm run dev     # 本地开发服务器
npm run build   # 生产构建
npm run preview # 预览构建产物
```

## 技术栈
- React 18 + Vite 7 + TypeScript
- TailwindCSS 4 + shadcn/ui
- react-router v7 + zustand
- 设计风格：Modern Warm SaaS（暖米色+森林绿+珊瑚橙）

## 项目结构
```
src/
├── App.tsx                # 路由入口 + 布局
├── main.tsx               # React根挂载
├── index.css              # 全局样式 + 动画定义
├── pages/
│   ├── HomePage.tsx       # 首页 - AI穿搭核心页
│   ├── WardrobePage.tsx   # 我的衣橱 - 资产管理
│   ├── RecordPage.tsx     # 穿搭记录 - 用户沉淀
│   ├── DiscoverPage.tsx   # 发现精选 - 轻内容
│   ├── ProfilePage.tsx    # 个人中心
│   └── OnboardingPage.tsx # 新用户初始化问卷
├── components/
│   ├── BottomNav.tsx      # 底部导航栏
│   ├── OutfitCard.tsx     # 穿搭推荐卡片
│   ├── SceneSelector.tsx  # 场景选择弹窗
│   └── ui/card.tsx        # shadcn/ui卡片组件
├── lib/
│   └── utils.ts           # cn()工具函数
```