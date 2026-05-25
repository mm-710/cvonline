import { useState } from 'react'
import { Camera, Plus, AlertTriangle, Clock, BarChart3, Search, Filter } from 'lucide-react'

const MOCK_CATEGORIES = [
  { id: 'top', name: '上衣', count: 23, color: 'bg-coral/15' },
  { id: 'bottom', name: '下装', count: 15, color: 'bg-forest/10' },
  { id: 'outer', name: '外套', count: 8, color: 'bg-sand/40' },
  { id: 'dress', name: '裙装', count: 6, color: 'bg-lavender/20' },
  { id: 'shoes', name: '鞋子', count: 12, color: 'bg-moss/10' },
  { id: 'acc', name: '配饰', count: 18, color: 'bg-peach' },
]

const MOCK_ITEMS = [
  { id: '1', name: '奶油色针织开衫', category: '上衣', status: '常穿', daysUnused: 0, color: '#F5E6D3' },
  { id: '2', name: '黑色西装外套', category: '外套', status: '常穿', daysUnused: 5, color: '#1A1A1A' },
  { id: '3', name: '紧身牛仔裤', category: '下装', status: '常穿', daysUnused: 2, color: '#4A6FA5' },
  { id: '4', name: '条纹T恤', category: '上衣', status: '闲置', daysUnused: 30, color: '#E8E8E8' },
  { id: '5', name: '白色直筒裤', category: '下装', status: '常穿', daysUnused: 3, color: '#FFFFFF' },
  { id: '6', name: '碎花连衣裙', category: '裙装', status: '闲置', daysUnused: 90, color: '#FFB7C5' },
]

export default function WardrobePage() {
  const [activeCategory, setActiveCategory] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [showDuplicateAlert, setShowDuplicateAlert] = useState(false)

  const filteredItems = activeCategory
    ? MOCK_ITEMS.filter(i => i.category === activeCategory)
    : MOCK_ITEMS

  return (
    <div className="max-w-lg mx-auto gradient-mesh">
      {/* Data Overview */}
      <header className="px-5 pt-8 pb-4 animate-fade-up">
        <h1 className="text-xl font-bold text-ink tracking-tight">我的衣橱</h1>
        <div className="mt-3 grid grid-cols-4 gap-2">
          {[
            { label: '总衣物', value: 82, icon: ShirtIcon },
            { label: '本月穿搭', value: 24, icon: BarChart3 },
            { label: '闲置', value: 11, icon: Clock },
            { label: '复用率', value: '68%', icon: BarChart3 },
          ].map(({ label, value, icon: Icon }, idx) => (
            <div key={label} className={`bg-white rounded-xl p-3 ring-1 ring-sand/30 text-center animate-fade-up delay-${idx * 100}`}>
              <Icon size={14} className="mx-auto mb-1 text-forest" />
              <p className="text-lg font-bold text-ink">{value}</p>
              <p className="text-xs text-muted-foreground">{label}</p>
            </div>
          ))}
        </div>
      </header>

      {/* Category Filter */}
      <section className="px-5 pb-4 animate-fade-up delay-200">
        <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-2">
          <button
            onClick={() => setActiveCategory(null)}
            className={`px-3.5 py-2 rounded-xl text-sm font-medium transition-all duration-300 ${
              activeCategory === null
                ? 'bg-forest text-white shadow-sm'
                : 'bg-white ring-1 ring-sand/30 text-ink hover:bg-forest/5'
            }`}
          >
            全部
          </button>
          {MOCK_CATEGORIES.map(({ id, name, count, color }) => (
            <button
              key={id}
              onClick={() => setActiveCategory(id)}
              className={`px-3.5 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-all duration-300 ${
                activeCategory === id
                  ? 'bg-forest text-white shadow-sm'
                  : `bg-white ring-1 ring-sand/30 text-ink hover:bg-forest/5`
              }`}
            >
              {name} · {count}
            </button>
          ))}
        </div>
      </section>

      {/* Search */}
      <section className="px-5 pb-4 animate-fade-up delay-300">
        <div className="flex items-center gap-2 bg-white rounded-xl ring-1 ring-sand/30 px-3 py-2.5">
          <Search size={16} className="text-muted-foreground" />
          <input
            type="text"
            placeholder="搜索衣物名称..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="text-sm text-ink placeholder-muted-foreground bg-transparent outline-none flex-1"
          />
          <button className="p-1 hover:bg-sand/20 rounded-lg transition-colors">
            <Filter size={14} className="text-muted-foreground" />
          </button>
        </div>
      </section>

      {/* Duplicate Alert Demo */}
      {showDuplicateAlert && (
        <div className="mx-5 mb-4 bg-coral/10 rounded-2xl p-4 ring-1 ring-coral/30 animate-fade-in">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle size={16} className="text-coral" />
            <span className="text-sm font-semibold text-ink">防重复提醒</span>
          </div>
          <p className="text-xs text-muted-foreground mb-3">
            你的衣橱中已有相似单品「条纹T恤」，是否确定保存这件新单品？
          </p>
          <div className="flex gap-2">
            <button onClick={() => setShowDuplicateAlert(false)} className="px-4 py-2 bg-forest text-white rounded-xl text-sm font-medium">
              保留单品
            </button>
            <button onClick={() => setShowDuplicateAlert(false)} className="px-4 py-2 bg-white ring-1 ring-sand/30 text-ink rounded-xl text-sm font-medium">
              放弃保存
            </button>
          </div>
        </div>
      )}

      {/* Item List */}
      <section className="px-5 pb-10 animate-fade-up delay-400">
        <div className="space-y-3">
          {filteredItems.map((item) => (
            <div key={item.id} className="bg-white rounded-2xl ring-1 ring-sand/30 p-4 outfit-card-lift">
              <div className="flex items-center gap-3">
                {/* Color swatch */}
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center ring-1 ring-sand/20"
                  style={{ backgroundColor: item.color }}
                >
                  <span className="font-handwritten text-sm text-ink/50">衣</span>
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-semibold text-ink truncate">{item.name}</p>
                    {item.daysUnused >= 30 && (
                      <span className="px-2 py-0.5 text-xs bg-coral/15 text-coral rounded-full font-medium">
                        {item.daysUnused >= 90 ? '90天未穿' : '30天未穿'}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-muted-foreground">{item.category}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      item.status === '常穿' ? 'bg-forest/10 text-forest' : 'bg-coral/10 text-coral'
                    }`}>
                      {item.status}
                    </span>
                  </div>
                </div>

                <button className="p-2 hover:bg-forest/5 rounded-xl transition-colors">
                  <span className="font-handwritten text-sm text-forest">搭配 →</span>
                </button>
              </div>

              {/* Idle item action */}
              {item.daysUnused >= 30 && (
                <div className="mt-3 pt-3 border-t border-sand/20">
                  <button className="flex items-center gap-1 text-xs text-forest font-medium">
                    <Sparkles size={12} />
                    为这件闲置单品生成新搭配
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Upload Button */}
      <div className="fixed bottom-[80px] right-4 max-w-lg z-40 animate-fade-up delay-500">
        <button
          onClick={() => setShowDuplicateAlert(true)}
          className="flex items-center gap-2 px-5 py-3 bg-forest text-white rounded-2xl shadow-lg shadow-forest/20 hover:bg-forest-deep transition-all duration-300"
        >
          <Plus size={18} />
          <span className="text-sm font-semibold">添加衣物</span>
        </button>
      </div>
    </div>
  )
}

function ShirtIcon({ size }: { size: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20.38 3.46L16 2a4 4 0 01-8 0L3.62 3.46a2 2 0 00-1.34 2.23l.58 3.47a1 1 0 00.99.84H6v10c0 1.1.9 2 2 2h8a2 2 0 002-2V10h2.15a1 1 0 00.99-.84l.58-3.47a2 2 0 00-1.34-2.23z"/>
    </svg>
  )
}

function Sparkles({ size }: { size: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3l1.912 5.813a2 2 0 001.275 1.275L21 12l-5.813 1.912a2 2 0 00-1.275 1.275L12 21l-1.912-5.813a2 2 0 00-1.275-1.275L3 12l5.813-1.912a2 2 0 001.275-1.275L12 3z"/>
    </svg>
  )
}