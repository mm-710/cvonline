import { useState, useEffect, useRef } from 'react'
import {
  Mail, Phone, MapPin, ExternalLink,
  Briefcase, GraduationCap, Award, Code2, ChevronDown,
  Calendar, ArrowUpRight, Heart, Coffee, Globe, Link2, BarChart3, PenTool
} from 'lucide-react'

// ─── Data ────────────────────────────────────────────────
const resumeData = {
  name: '穆瑞琪',
  nameEn: 'Mu Ruiqi',
  title: '产品经理 / Product Manager',
  subtitle: '用数据驱动决策，用产品创造价值',
  avatar: 'https://i.pravatar.cc/200?img=32',
  contact: {
    email: '15206904458@163.com',
    phone: '15206904458',
    location: '北京 · Beijing',
    github: '',
    linkedin: '',
  },
  summary: '金融学硕士，具备数据分析与产品设计双重能力。从流量策略到 AI 产品，擅长用数据洞察问题、用方案验证假设、用迭代逼近目标。在快手、百度、360 等头部公司均有实战经验。',
  experience: [
    {
      period: '2026.01 – 至今',
      company: '快手 · 快手联盟',
      role: '流量策略产品经理',
      highlights: [
        '分行业分析素材消耗集中度/生命周期/稳定性，圈定 AI 素材 Top5 行业供给范围',
        '搭建多 agent 自动化协同、公域优质视频抽帧、背景叠加风格化 3 条 AIGC 生产链路，产能达 4000w/d',
        '探索 AIGC 素材冷启阶段专用检索池保送/素材优选干预/精排模型感知机制',
        '素材曝光 +0.28%，联盟整体预期消耗 +0.91%，主站总体消耗 +0.30%',
      ],
      accent: '从产能到效果，让 AI 素材真正跑通消耗闭环。',
    },
    {
      period: '2025.09 – 2026.01',
      company: '百度 · 移动生态事业群',
      role: 'AI 搜索产品经理',
      highlights: [
        '考研择校报告可视化：竞争力雷达图 + 择校策略思维链 + UGC 热议榜单，择校 pv +0.4%',
        '个人智能体对话策略优化：扩展技能卡片增强人设感知，用户对话轮次增加 2.1 轮',
        'AI 图搜链路：意图识别 + 置信度动态融合，拍搜零结果率下降 23%，主动 pv +1%',
        '搜索百看化：搭建 AI 动画讲解 / 热点拼接 / AIGC 知识点 3 条产线，搜题 pv +1%',
      ],
      accent: '做 AI 产品，关键不是模型能力，而是把能力嵌进用户真实场景。',
    },
    {
      period: '2024.09 – 2024.12',
      company: '快手 · 商业化',
      role: '平台产品经理',
      highlights: [
        '为渠道销售定制搭建 PRM 平台 1.0：日常数据看板、政策透传、审批入口汇总',
        'PRM 周使用率达 84%，上线后功能调研满意度 78%（较上季度翻一番）',
        'PRM 2.0 迭代：岗位定制看板 + 审批待办红点 + 公告栏更新机制，周使用率升至 88%',
        '审批入口使用率提升 1 倍，渠道销售审批效率提高 67%',
      ],
      accent: '好的平台产品，是让用户愿意每天都打开的东西。',
    },
    {
      period: '2024.04 – 2024.07',
      company: '三六零 · 商业产品事业部',
      role: '流量策略产品经理',
      highlights: [
        '搜索策略优化：query 处理层 + 文本语义多路召回 + 多目标精排，ctr +2%，cvr +1%',
        '导流位推荐策略：用户重定向 + 浏览器子主页/Cube 位精准推荐 + 猜你想搜联想',
        '新导流位推全当月，主站 pv +15%，ctr +4%，留资率 +2%',
      ],
      accent: '流量不是目的，转化才是。每一个百分点背后都是真实的用户行为。',
    },
  ],
  education: [
    {
      period: '2024.09 – 2026.06',
      school: '对外经济贸易大学',
      degree: '金融学 · 硕士 · 国际经济贸易学院',
      note: '',
    },
    {
      period: '2020.09 – 2024.06',
      school: '四川大学',
      degree: '金融学 · 本科 · 经济学院',
      note: '',
    },
  ],
  skills: [
    { category: '数据分析', items: ['SQL', 'Python', 'NumPy', 'Stata', 'SPSS', '可视化分析', '概率论'] },
    { category: '产品设计', items: ['Axure', 'Figma', '竞品分析', '用户研究', '需求文档'] },
    { category: 'AI 能力', items: ['AI 工作流设计', '对话设计', '提示词工程', 'RAG', 'Few-shot'] },
    { category: '产品策略', items: ['流量策略', '搜索策略', '推荐策略', 'AIGC 素材', '数据驱动迭代'] },
  ],
  projects: [],
}

// ─── Intersection Observer Hook ──────────────────────────
function useReveal() {
  const ref = useRef<HTMLDivElement>(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setVisible(true); observer.disconnect() } },
      { threshold: 0.15 }
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  return { ref, visible }
}

// ─── Components ──────────────────────────────────────────

function SectionDivider() {
  return (
    <div className="flex items-center justify-center py-4">
      <div className="w-2 h-2 rounded-full bg-[#FF5533]" />
      <div className="mx-3 h-px w-24 bg-[#E5E7EB]" />
      <div className="w-2 h-2 rounded-full bg-[#1A1A1A]" />
    </div>
  )
}

function SkillBadge({ text }: { text: string }) {
  return (
    <span className="inline-flex items-center rounded-full bg-white px-3 py-1.5 text-sm font-medium text-[#1A1A1A] shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md">
      {text}
    </span>
  )
}

function ExperienceCard({ exp, index }: { exp: typeof resumeData.experience[0]; index: number }) {
  const { ref, visible } = useReveal()
  return (
    <div
      ref={ref}
      className={`group relative rounded-2xl bg-white p-6 shadow-sm transition-all duration-500 hover:-translate-y-1 hover:shadow-md ${
        visible ? 'animate-fade-up' : 'opacity-0'
      }`}
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      <div className="absolute left-0 top-6 bottom-6 w-1 rounded-full bg-[#FF5533]" />
      <div className="pl-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="heading-serif text-xl font-bold text-[#1A1A1A]">{exp.company}</h3>
            <p className="mt-1 text-sm font-medium text-[#6B7280]">{exp.role}</p>
          </div>
          <span className="flex items-center gap-1.5 text-sm font-medium text-[#FF5533] whitespace-nowrap">
            <Calendar className="w-3.5 h-3.5" />
            {exp.period}
          </span>
        </div>
        <ul className="mt-4 space-y-2">
          {exp.highlights.map((h, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-[#374151]">
              <ArrowUpRight className="w-4 h-4 mt-0.5 text-[#FF5533] shrink-0" />
              <span>{h}</span>
            </li>
          ))}
        </ul>
        <p className="mt-4 accent-emphasis text-sm border-t border-[#F3F4F6] pt-3">
          {exp.accent}
        </p>
      </div>
    </div>
  )
}

function EducationCard({ edu, index }: { edu: typeof resumeData.education[0]; index: number }) {
  const { ref, visible } = useReveal()
  return (
    <div
      ref={ref}
      className={`rounded-2xl bg-white p-6 shadow-sm transition-all duration-500 hover:-translate-y-1 hover:shadow-md ${
        visible ? 'animate-fade-up' : 'opacity-0'
      }`}
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="heading-serif text-xl font-bold text-[#1A1A1A]">{edu.school}</h3>
          <p className="mt-1 text-sm font-medium text-[#6B7280]">{edu.degree}</p>
          {edu.note && <p className="mt-1 text-sm text-[#FF5533]">{edu.note}</p>}
        </div>
        <span className="flex items-center gap-1.5 text-sm font-medium text-[#FF5533] whitespace-nowrap">
          <Calendar className="w-3.5 h-3.5" />
          {edu.period}
        </span>
      </div>
    </div>
  )
}

// ─── Main Page ───────────────────────────────────────────
export default function ResumePage() {
  const [expanded, setExpanded] = useState(false)
  const data = resumeData

  return (
    <div className="min-h-screen bg-[#FFFBF7] font-sans antialiased">
      {/* ─── Hero ─── */}
      <header className="container mx-auto max-w-5xl px-4 pt-20 pb-12 text-center">
        <div className="animate-fade-up">
          <div className="mx-auto mb-6 h-28 w-28 rounded-full overflow-hidden ring-4 ring-[#FF5533]/20 shadow-lg">
            <img src={data.avatar} alt={data.name} className="h-full w-full object-cover" />
          </div>
        </div>

        <div className="animate-fade-up-delay-1">
          <h1 className="heading-serif text-5xl md:text-6xl font-black text-[#1A1A1A] tracking-tight">
            {data.name}
          </h1>
          <p className="mt-2 text-lg font-medium text-[#6B7280]">{data.nameEn}</p>
        </div>

        <div className="animate-fade-up-delay-2">
          <p className="mt-4 heading-serif text-2xl md:text-3xl font-bold text-[#1A1A1A]">{data.title}</p>
          <p className="mt-2 accent-emphasis text-xl">{data.subtitle}</p>
        </div>

        <div className="animate-fade-up-delay-3">
          <p className="mt-6 max-w-2xl mx-auto text-base text-[#374151] leading-relaxed">{data.summary}</p>
        </div>

        {/* Contact icons */}
        <div className="animate-fade-up-delay-4 mt-8 flex flex-wrap items-center justify-center gap-3">
          <a href={`mailto:${data.contact.email}`} className="flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-medium text-[#1A1A1A] shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md active:scale-95">
            <Mail className="w-4 h-4 text-[#FF5533]" />
            {data.contact.email}
          </a>
          <a href={`tel:${data.contact.phone}`} className="flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-medium text-[#1A1A1A] shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md active:scale-95">
            <Phone className="w-4 h-4 text-[#FF5533]" />
            {data.contact.phone}
          </a>
          <span className="flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-medium text-[#1A1A1A] shadow-sm">
            <MapPin className="w-4 h-4 text-[#FF5533]" />
            {data.contact.location}
          </span>
        </div>
      </header>

      <SectionDivider />

      {/* ─── Experience ─── */}
      <section className="container mx-auto max-w-5xl px-4 py-16">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 rounded-full bg-[#FFF0EC] px-3 py-1 text-sm font-medium text-[#FF5533]">
            <Briefcase className="w-4 h-4" />
            实习经历
          </div>
          <h2 className="mt-4 heading-serif text-4xl md:text-5xl font-black text-[#1A1A1A]">
            Where I've <span className="accent-emphasis">worked</span>
          </h2>
        </div>
        <div className="space-y-6">
          {data.experience.map((exp, i) => (
            <ExperienceCard key={i} exp={exp} index={i} />
          ))}
        </div>
      </section>

      <SectionDivider />

      {/* ─── Skills ─── */}
      <section className="container mx-auto max-w-5xl px-4 py-16">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 rounded-full bg-[#FFF0EC] px-3 py-1 text-sm font-medium text-[#FF5533]">
            <BarChart3 className="w-4 h-4" />
            个人优势
          </div>
          <h2 className="mt-4 heading-serif text-4xl md:text-5xl font-black text-[#1A1A1A]">
            What I'm <span className="accent-emphasis">good at</span>
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {data.skills.map((group, i) => (
            <div key={group.category} className="rounded-2xl bg-white p-6 shadow-sm transition-all duration-500 hover:-translate-y-1 hover:shadow-md animate-fade-up" style={{ animationDelay: `${i * 0.1}s` }}>
              <h3 className="heading-serif text-lg font-bold text-[#1A1A1A] mb-4">
                {group.category === '数据分析' && <BarChart3 className="inline w-4 h-4 mr-1 text-[#FF5533]" />}
                {group.category === '产品设计' && <PenTool className="inline w-4 h-4 mr-1 text-[#FF5533]" />}
                {group.category === 'AI 能力' && <Heart className="inline w-4 h-4 mr-1 text-[#FF5533]" />}
                {group.category === '产品策略' && <Award className="inline w-4 h-4 mr-1 text-[#FF5533]" />}
                {group.category}
              </h3>
              <div className="flex flex-wrap gap-2">
                {group.items.map(item => <SkillBadge key={item} text={item} />)}
              </div>
            </div>
          ))}
        </div>
      </section>

      <SectionDivider />

      {/* ─── Education ─── */}
      <section className="container mx-auto max-w-5xl px-4 py-16">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 rounded-full bg-[#FFF0EC] px-3 py-1 text-sm font-medium text-[#FF5533]">
            <GraduationCap className="w-4 h-4" />
            教育经历
          </div>
          <h2 className="mt-4 heading-serif text-4xl md:text-5xl font-black text-[#1A1A1A]">
            Where I <span className="accent-emphasis">learned</span>
          </h2>
        </div>
        <div className="space-y-4 max-w-lg mx-auto">
          {data.education.map((edu, i) => (
            <EducationCard key={i} edu={edu} index={i} />
          ))}
        </div>
      </section>

      {/* ─── More toggle ─── */}
      <div className="container mx-auto max-w-5xl px-4 py-8 text-center">
        <button onClick={() => setExpanded(!expanded)} className="inline-flex items-center gap-2 rounded-full bg-[#FF5533] px-6 py-3 text-sm font-semibold text-white shadow-sm transition-all hover:bg-[#E64D2A] hover:shadow-md active:scale-95">
          {expanded ? '收起' : '了解更多'}
          <ChevronDown className={`w-4 h-4 transition-transform ${expanded ? 'rotate-180' : ''}`} />
        </button>
      </div>

      {expanded && (
        <section className="container mx-auto max-w-5xl px-4 py-12 animate-fade-up">
          <div className="rounded-2xl bg-white p-8 shadow-sm">
            <h3 className="heading-serif text-2xl font-bold text-[#1A1A1A] mb-4">
              关于我 · <span className="accent-emphasis">A bit more</span>
            </h3>
            <div className="space-y-3 text-sm text-[#374151] leading-relaxed">
              <p>金融学背景让我习惯了用数据说话，产品经理的角色让我学会把洞察变成行动。两者结合，就是我能做的事——不是拍脑袋决策，而是用假设驱动、用验证迭代。</p>
              <p>在快手联盟做 AIGC 素材策略、在百度做 AI 搜索产品、在 360 做流量推荐——这些经历的核心逻辑是一样的：找到问题 → 设计方案 → 数据验证 → 持续迭代。</p>
              <p className="accent-emphasis">数据不是终点，决策才是。而好的决策，往往来自对数据的诚实解读。</p>
            </div>
          </div>
        </section>
      )}

      {/* ─── Footer CTA ─── */}
      <footer className="container mx-auto max-w-5xl px-4 py-20 text-center">
        <div className="animate-fade-up">
          <h2 className="heading-serif text-3xl md:text-4xl font-black text-[#1A1A1A]">
            Let's <span className="accent-emphasis">talk</span>
          </h2>
          <p className="mt-3 text-base text-[#6B7280]">如果你在找一个既懂数据、又懂产品的人</p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <a href={`mailto:${data.contact.email}`} className="inline-flex items-center gap-2 rounded-full bg-[#FF5533] px-8 py-3 text-base font-semibold text-white shadow-sm transition-all hover:bg-[#E64D2A] hover:shadow-md hover:-translate-y-0.5 active:scale-95">
              <Mail className="w-5 h-5" />
              发邮件联系我
            </a>
            <a href={`tel:${data.contact.phone}`} className="inline-flex items-center gap-2 rounded-full bg-[#1A1A1A] px-8 py-3 text-base font-semibold text-white shadow-sm transition-all hover:bg-[#333] hover:shadow-md hover:-translate-y-0.5 active:scale-95">
              <Phone className="w-5 h-5" />
              电话联系我
            </a>
          </div>
        </div>
        <div className="mt-16 text-xs text-[#9CA3AF]">© {new Date().getFullYear()} {data.name} · 用心构建</div>
      </footer>
    </div>
  )
}