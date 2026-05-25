import { useState } from 'react'
import { Calendar, TrendingUp, BarChart3, ChevronRight, Filter, Lock } from 'lucide-react'

const MOCK_RECORDS = [
  {
    id: 'r1',
    date: '2026-05-24',
    scene: '通勤',
    style: '简约',
    items: ['奶油色针织开衫', '白色直筒裤', '奶油色乐福鞋'],
    rating: '舒适 · 显瘦',
    isPrivate: true,
    hasPhoto: false,
  },
  {
    id: 'r2',
    date: '2026-05-23',
    scene: '约会',
    style: '温柔',
    items: ['碎花连衣裙', '白色帆布鞋', '金色耳链'],
    rating: '显高 · 温柔',
    isPrivate: true,
    hasPhoto: true,
  },
  {
    id: 'r3',
    date: '2026-05-22',
    scene: '休闲',
    style: '轻松',
    items: ['牛仔外套', '条纹T恤', '卡其短裤', '帆布鞋'],
    rating: '舒适 · 休闲',
    isPrivate: false,
    hasPhoto: false,
  },
  {
    id: 'r4',
    date: '2026-05-20',
    scene: '职场',
    style: '干练',
    items: ['黑色西装外套', '白色衬衫', '灰色阔腿裤', '尖头高跟鞋'],
    rating: '权威感 · 显气场',
    isPrivate: true,
    hasPhoto: true,
  },
]

const MONTH_SUMMARY = {
  totalOutfits: 24,
  topStyle: '简约通勤',
  topItem: '奶油色针织开衫（穿了8次）',
  idleItems: 3,
  reuseRate: '68%',
}

export default function RecordPage() {
  const [filterScene, setFilterScene] = useState<string | null>(null)
  const [showReport, setShowReport] = useState(false)

  return (
    <div className="max-w-lg mx-auto gradient-mesh">
      {/* Header */}
      <header className="px-5 pt-8 pb-4 animate-fade-up">
        <h1 className="text-xl font-bold text-ink tracking-tight">穿搭记录</h1>
        <p className="text-sm text-muted-foreground mt-1">沉淀你的专属穿搭体系</p>
      </header>

      {/* Month Summary Card */}
      <section className="px-5 pb-5 animate-fade-up delay-100">
        <div className="bg-forest rounded-2xl p-5 text-white">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Calendar size={16} />
              <span className="text-sm font-semibold">5月穿搭概览</span>
            </div>
            <button
              onClick={() => setShowReport(true)}
              className="flex items-center gap-1 px-3 py-1.5 bg-white/15 rounded-xl text-sm font-medium hover:bg-white/25 transition-colors"
            >
              <BarChart3 size={14} />
              月度复盘
            </button>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <p className="text-2xl font-bold">{MONTH_SUMMARY.totalOutfits}</p>
              <p className="text-xs opacity-70">次穿搭</p>
            </div>
            <div>
              <p className="text-2xl font-bold">{MONTH_SUMMARY.reuseRate}</p>
              <p className="text-xs opacity-70">复用率</p>
            </div>
            <div>
              <p className="text-2xl font-bold">{MONTH_SUMMARY.idleItems}</p>
              <p className="text-xs opacity-70">闲置单品</p>
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-white/15">
            <div className="flex items-center gap-1.5">
              <TrendingUp size={14} />
              <span className="text-xs">最常风格：{MONTH_SUMMARY.topStyle}</span>
            </div>
            <div className="flex items-center gap-1.5 mt-1">
              <TrendingUp size={14} />
              <span className="text-xs">最常单品：{MONTH_SUMMARY.topItem}</span>
            </div>
          </div>
        </div>
      </section>

      {/* Scene Filter */}
      <section className="px-5 pb-4 animate-fade-up delay-200">
        <div className="flex items-center gap-2 overflow-x-auto scrollbar-hide pb-2">
          <button
            onClick={() => setFilterScene(null)}
            className={`px-3 py-1.5 rounded-xl text-sm font-medium transition-all duration-300 ${
              filterScene === null
                ? 'bg-forest text-white'
                : 'bg-white ring-1 ring-sand/30 text-ink'
            }`}
          >
            全部
          </button>
          {['通勤', '约会', '休闲', '职场', '运动'].map((scene) => (
            <button
              key={scene}
              onClick={() => setFilterScene(scene)}
              className={`px-3 py-1.5 rounded-xl text-sm font-medium whitespace-nowrap transition-all duration-300 ${
                filterScene === scene
                  ? 'bg-forest text-white'
                  : 'bg-white ring-1 ring-sand/30 text-ink'
              }`}
            >
              {scene}
            </button>
          ))}
        </div>
      </section>

      {/* Timeline */}
      <section className="px-5 pb-10 animate-fade-up delay-300">
        <div className="space-y-4">
          {MOCK_RECORDS.map((record) => (
            <div key={record.id} className="bg-white rounded-2xl ring-1 ring-sand/30 p-4 outfit-card-lift">
              {/* Date & Scene */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-1 bg-forest/10 rounded-full text-xs font-semibold text-forest">
                    {record.scene}
                  </span>
                  <span className="text-xs text-muted-foreground">{record.date}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  {record.isPrivate && (
                    <Lock size={12} className="text-muted-foreground" />
                  )}
                  {record.hasPhoto && (
                    <span className="px-2 py-0.5 bg-coral/10 text-xs text-coral rounded-full font-medium">
                      有实拍
                    </span>
                  )}
                </div>
              </div>

              {/* Items */}
              <div className="flex gap-2 mb-3">
                {record.items.map((item, idx) => (
                  <div key={idx} className="flex-1 bg-cream/80 rounded-xl p-2.5 text-center">
                    <div className="w-full aspect-square bg-sand/30 rounded-lg mb-1.5 flex items-center justify-center">
                      <span className="font-handwritten text-base text-forest/40">
                        {idx === 0 ? '衫' : idx === 1 ? '裤' : idx === 2 ? '鞋' : '饰'}
                      </span>
                    </div>
                    <p className="text-xs text-ink font-medium truncate">{item}</p>
                  </div>
                ))}
              </div>

              {/* Rating & Actions */}
              <div className="flex items-center justify-between pt-2 border-t border-sand/20">
                <div className="flex items-center gap-1">
                  <span className="text-xs text-forest font-medium">{record.rating}</span>
                  <span className="px-2 py-0.5 bg-sand/40 text-xs text-ink/70 rounded-full">{record.style}</span>
                </div>
                <button className="flex items-center gap-1 text-xs text-forest font-medium hover:text-forest-deep transition-colors">
                  详情
                  <ChevronRight size={12} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Report Modal */}
      {showReport && (
        <div className="fixed inset-0 z-50 flex items-center justify-center animate-fade-in">
          <div className="absolute inset-0 bg-ink/30 backdrop-blur-sm" onClick={() => setShowReport(false)} />
          <div className="relative bg-cream rounded-2xl shadow-2xl w-[90%] max-w-md p-6 animate-slide-in-right">
            <h2 className="text-lg font-bold text-ink mb-4">5月穿搭复盘报告</h2>

            <div className="space-y-4">
              <div className="bg-white rounded-xl p-4 ring-1 ring-sand/30">
                <h3 className="text-sm font-semibold text-ink mb-2">穿搭频率分布</h3>
                <div className="space-y-2">
                  {[
                    { style: '简约通勤', count: 12, pct: 50 },
                    { style: '温柔约会', count: 6, pct: 25 },
                    { style: '休闲日常', count: 4, pct: 17 },
                    { style: '正式职场', count: 2, pct: 8 },
                  ].map(({ style, count, pct }) => (
                    <div key={style} className="flex items-center gap-2">
                      <span className="text-xs text-ink w-24">{style}</span>
                      <div className="flex-1 h-2 bg-cream rounded-full overflow-hidden">
                        <div className="h-full bg-forest rounded-full" style={{ width: `${pct}%` }} />
                      </div>
                      <span className="text-xs text-muted-foreground">{count}次</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white rounded-xl p-4 ring-1 ring-sand/30">
                <h3 className="text-sm font-semibold text-ink mb-2">最常用单品 TOP 5</h3>
                <div className="space-y-1.5">
                  {[
                    { name: '奶油色针织开衫', times: 8 },
                    { name: '白色直筒裤', times: 6 },
                    { name: '黑色西装外套', times: 4 },
                    { name: '乐福鞋', times: 5 },
                    { name: '金色耳链', times: 3 },
                  ].map(({ name, times }, idx) => (
                    <div key={name} className="flex items-center justify-between text-xs">
                      <span className="text-ink font-medium">
                        <span className="text-forest mr-1">#{idx + 1}</span>
                        {name}
                      </span>
                      <span className="text-muted-foreground">{times}次穿搭</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <button
              onClick={() => setShowReport(false)}
              className="mt-5 w-full py-2.5 bg-forest text-white rounded-xl text-sm font-semibold hover:bg-forest-deep transition-colors"
            >
              关闭报告
            </button>

            <p className="mt-3 text-center text-xs text-muted-foreground">
              📊 季度/年度深度报告为会员专属权益
            </p>
          </div>
        </div>
      )}
    </div>
  )
}