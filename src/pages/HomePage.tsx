import { useState } from 'react'
import { CloudSun, ChevronRight, Bookmark, Camera, Wand2, Palette } from 'lucide-react'
import OutfitCard from '@/components/OutfitCard'
import SceneSelector from '@/components/SceneSelector'

const MOCK_OUTFITS = [
  {
    id: 'o1',
    name: '温柔通勤',
    items: ['米色针织开衫', '白色直筒裤', '奶油色乐福鞋', '金色耳链'],
    matchScore: 92,
    reason: '针织质感搭配直筒线条，温润知性，适合今日22°C微凉天气',
    tags: ['通勤', '简约', '温柔'],
  },
  {
    id: 'o2',
    name: '干练职场',
    items: ['黑色西装外套', '白色衬衫', '灰色阔腿裤', '尖头高跟鞋'],
    matchScore: 88,
    reason: '经典黑白灰三色搭配，权威感十足，适合正式商务场景',
    tags: ['职场', '正式', '干练'],
  },
  {
    id: 'o3',
    name: '休闲周末',
    items: ['牛仔外套', '条纹T恤', '卡其短裤', '帆布鞋'],
    matchScore: 85,
    reason: '轻松舒适的牛仔+条纹组合，适合周末逛街出行',
    tags: ['休闲', '周末', '轻松'],
  },
]

export default function HomePage() {
  const [activeScene, setActiveScene] = useState<string | null>(null)
  const [showSceneSelector, setShowSceneSelector] = useState(false)

  return (
    <div className="max-w-lg mx-auto gradient-mesh">
      {/* Weather & Status Bar */}
      <header className="px-5 pt-8 pb-4 animate-fade-up">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CloudSun size={22} className="text-moss" />
            <div>
              <p className="text-sm font-semibold text-ink">北京 · 22°C 微凉</p>
              <p className="text-xs text-muted-foreground">适宜轻外套+长裤</p>
            </div>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-forest/8 rounded-full">
            <span className="font-handwritten text-sm text-forest font-semibold">今日为你准备了3套穿搭</span>
          </div>
        </div>
      </header>

      {/* Daily Outfit Recommendations */}
      <section className="px-5 pb-6">
        <div className="flex items-center justify-between mb-4 animate-fade-up delay-100">
          <h2 className="text-xl font-bold text-ink tracking-tight">
            每日穿搭推荐
          </h2>
          <button className="flex items-center gap-1 text-sm text-forest font-medium hover:text-forest-deep transition-colors">
            <Bookmark size={14} />
            收藏库
          </button>
        </div>

        <div className="space-y-4">
          {MOCK_OUTFITS.map((outfit, idx) => (
            <div key={outfit.id} className={`animate-fade-up delay-${(idx + 2) * 100}`}>
              <OutfitCard outfit={outfit} />
            </div>
          ))}
        </div>
      </section>

      {/* Core Feature Buttons */}
      <section className="px-5 pb-8">
        <h3 className="text-base font-semibold text-ink mb-4 animate-fade-up delay-400">
          更多搭配方式
        </h3>
        <div className="grid grid-cols-3 gap-3 animate-fade-up delay-500">
          <button
            onClick={() => setShowSceneSelector(true)}
            className="flex flex-col items-center gap-2 py-5 bg-white rounded-2xl shadow-sm ring-1 ring-sand/30 outfit-card-lift group"
          >
            <div className="p-2 bg-coral/10 rounded-xl group-hover:bg-coral/20 transition-colors">
              <Wand2 size={20} className="text-coral" />
            </div>
            <span className="text-sm font-medium text-ink">场景定制</span>
            <span className="text-xs text-muted-foreground">按场景搭配</span>
          </button>

          <button className="flex flex-col items-center gap-2 py-5 bg-white rounded-2xl shadow-sm ring-1 ring-sand/30 outfit-card-lift group">
            <div className="p-2 bg-forest/10 rounded-xl group-hover:bg-forest/20 transition-colors">
              <Palette size={20} className="text-forest" />
            </div>
            <span className="text-sm font-medium text-ink">智能避坑</span>
            <span className="text-xs text-muted-foreground">身材适配</span>
          </button>

          <button className="flex flex-col items-center gap-2 py-5 bg-white rounded-2xl shadow-sm ring-1 ring-sand/30 outfit-card-lift group">
            <div className="p-2 bg-lavender/20 rounded-xl group-hover:bg-lavender/30 transition-colors">
              <Camera size={20} className="text-lavender" />
            </div>
            <span className="text-sm font-medium text-ink">DIY创作</span>
            <span className="text-xs text-muted-foreground">自主搭配</span>
          </button>
        </div>
      </section>

      {/* Smart Avoid Tips */}
      <section className="px-5 pb-10">
        <div className="bg-white rounded-2xl p-5 ring-1 ring-sand/30 animate-fade-up delay-500">
          <div className="flex items-center gap-2 mb-3">
            <div className="p-1.5 bg-rose/10 rounded-lg">
              <Palette size={16} className="text-rose" />
            </div>
            <h3 className="text-sm font-semibold text-ink">智能避坑提示</h3>
          </div>
          <div className="space-y-2">
            <div className="flex items-start gap-2">
              <span className="text-xs text-coral font-bold mt-0.5">⚠</span>
              <p className="text-xs text-muted-foreground leading-relaxed">
                梨形身材应避免紧身下装——你衣橱中的<span className="text-ink font-medium">紧身牛仔裤</span>可搭配A字裙来平衡比例
              </p>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-xs text-moss font-bold mt-0.5">✓</span>
              <p className="text-xs text-muted-foreground leading-relaxed">
                暖皮肤色推荐暖色调单品——你的<span className="text-ink font-medium">奶油色针织衫</span>是今日最佳选择
              </p>
            </div>
          </div>
          <button className="mt-3 flex items-center gap-1 text-xs text-forest font-medium hover:text-forest-deep transition-colors">
            查看完整穿搭教程
            <ChevronRight size={12} />
          </button>
        </div>
      </section>

      {/* Scene Selector Modal */}
      {showSceneSelector && (
        <SceneSelector
          onClose={() => setShowSceneSelector(false)}
          onSelect={(scene) => {
            setActiveScene(scene)
            setShowSceneSelector(false)
          }}
        />
      )}
    </div>
  )
}