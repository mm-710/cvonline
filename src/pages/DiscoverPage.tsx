import { useState } from 'react'
import { Palette, Ruler, BookOpen, Leaf, ChevronRight, Heart, Share2, Eye } from 'lucide-react'

const CATEGORIES = [
  { id: 'body', name: '身材穿搭', icon: Ruler, color: 'bg-forest/10' },
  { id: 'scene', name: '场景模板', icon: BookOpen, color: 'bg-coral/10' },
  { id: 'color', name: '色彩干货', icon: Palette, color: 'bg-lavender/15' },
  { id: 'minimal', name: '衣橱思维', icon: Leaf, color: 'bg-moss/10' },
]

const MOCK_CONTENT: Record<string, Array<{
  id: string
  title: string
  desc: string
  tags: string[]
  likes: number
  isUGC: boolean
}>> = {
  body: [
    { id: 'b1', title: '梨形身材穿搭避坑指南', desc: '避开紧身下装，用A字裙平衡比例。5个实穿公式，从通勤到约会全覆盖。', tags: ['梨形', '避坑', '显瘦'], likes: 238, isUGC: false },
    { id: 'b2', title: 'H型身材怎么穿出曲线感', desc: '收腰+层次叠穿，让直板身材也有曲线。3套穿搭模板直接复刻。', tags: ['H型', '曲线', '收腰'], likes: 156, isUGC: false },
    { id: 'b3', title: '小个子显高穿搭终极攻略', desc: '高腰线+同色系+尖头鞋，三个原则让你视觉增高5cm。', tags: ['小个子', '显高', '比例'], likes: 189, isUGC: true },
  ],
  scene: [
    { id: 's1', title: '职场通勤5分钟穿搭公式', desc: '西装+衬衫+阔腿裤，3套公式覆盖从周一到周五，不再纠结穿什么。', tags: ['通勤', '职场', '公式'], likes: 312, isUGC: false },
    { id: 's2', title: '约会穿搭：从咖啡馆到晚餐厅', desc: '温柔针织→精致连衣裙→优雅小礼服，三个场景无缝切换。', tags: ['约会', '温柔', '精致'], likes: 267, isUGC: false },
    { id: 's3', title: '校园穿搭：上课也能很时髦', desc: '舒适为主+个性表达，条纹+牛仔+帆布鞋的无限组合。', tags: ['校园', '舒适', '青春'], likes: 98, isUGC: true },
  ],
  color: [
    { id: 'c1', title: '暖皮肤色配色圣经', desc: '大地色系、奶油白、暖橘是你的安全牌。附24色适配对照表。', tags: ['暖皮', '配色', '大地色'], likes: 421, isUGC: false },
    { id: 'c2', title: '同色系穿搭：高级感的秘密', desc: '不是全穿一个颜色，而是用3个相邻色阶制造层次感。', tags: ['同色系', '高级感', '层次'], likes: 298, isUGC: false },
    { id: 'c3', title: '秋冬配色：从焦糖到墨绿', desc: '5组季节配色方案，让你的秋冬衣橱告别黑白灰。', tags: ['秋冬', '配色', '焦糖'], likes: 167, isUGC: true },
  ],
  minimal: [
    { id: 'm1', title: '胶囊衣橱：30件衣服穿一整年', desc: '按场景+季节精选30件核心单品，每件至少3种搭配方式。', tags: ['胶囊衣橱', '极简', '复用'], likes: 534, isUGC: false },
    { id: 'm2', title: '断舍离穿搭：少即是多', desc: '不是扔衣服，而是留下真正适合你的。用数据判断哪些该走。', tags: ['断舍离', '精简', '数据'], likes: 189, isUGC: false },
    { id: 'm3', title: '衣物复用率提升50%的3个方法', desc: '标签化管理+搭配模板+闲置盘活，让你的衣橱效率翻倍。', tags: ['复用率', '管理', '效率'], likes: 145, isUGC: false },
  ],
}

export default function DiscoverPage() {
  const [activeCategory, setActiveCategory] = useState('body')

  const content = MOCK_CONTENT[activeCategory] || []

  return (
    <div className="max-w-lg mx-auto gradient-mesh">
      {/* Header */}
      <header className="px-5 pt-8 pb-3 animate-fade-up">
        <h1 className="text-xl font-bold text-ink tracking-tight">发现精选</h1>
        <p className="text-sm text-muted-foreground mt-1">干货穿搭教程 · 无带货 · 无种草</p>
      </header>

      {/* Category Tabs */}
      <section className="px-5 pb-5 animate-fade-up delay-100">
        <div className="grid grid-cols-4 gap-2">
          {CATEGORIES.map(({ id, name, icon: Icon, color }) => (
            <button
              key={id}
              onClick={() => setActiveCategory(id)}
              className={`flex flex-col items-center gap-1.5 py-3 rounded-xl transition-all duration-300 ${
                activeCategory === id
                  ? 'bg-forest text-white shadow-sm scale-105'
                  : 'bg-white ring-1 ring-sand/30 text-ink'
              }`}
            >
              <Icon size={18} />
              <span className="text-xs font-medium">{name}</span>
            </button>
          ))}
        </div>
      </section>

      {/* Content List */}
      <section className="px-5 pb-10">
        <div className="space-y-4">
          {content.map((item, idx) => (
            <div key={item.id} className={`bg-white rounded-2xl ring-1 ring-sand/30 overflow-hidden outfit-card-lift animate-fade-up delay-${(idx + 1) * 100}`}>
              {/* Cover area */}
              <div className={`h-40 bg-gradient-to-br ${
                activeCategory === 'body' ? 'from-forest/8 to-moss/5' :
                activeCategory === 'scene' ? 'from-coral/8 to-peach' :
                activeCategory === 'color' ? 'from-lavender/10 to-lavender/5' :
                'from-moss/8 to-cream'
              } flex items-center justify-center`}>
                <span className="font-handwritten text-2xl text-ink/20">
                  {activeCategory === 'body' ? '身材' :
                   activeCategory === 'scene' ? '场景' :
                   activeCategory === 'color' ? '色彩' : '衣橱'}
                </span>
              </div>

              {/* Content */}
              <div className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  {item.isUGC && (
                    <span className="px-2 py-0.5 bg-coral/10 text-xs text-coral rounded-full font-medium">
                      用户分享
                    </span>
                  )}
                  <h3 className="text-base font-bold text-ink">{item.title}</h3>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed mb-3">{item.desc}</p>

                {/* Tags */}
                <div className="flex items-center justify-between">
                  <div className="flex gap-1.5">
                    {item.tags.map((tag) => (
                      <span key={tag} className="px-2 py-0.5 text-xs bg-sand/40 text-ink/70 rounded-full">
                        {tag}
                      </span>
                    ))}
                  </div>
                  <div className="flex items-center gap-3">
                    <button className="flex items-center gap-1 text-xs text-muted-foreground hover:text-coral transition-colors">
                      <Heart size={14} />
                      {item.likes}
                    </button>
                    <button className="p-1.5 hover:bg-forest/5 rounded-lg transition-colors">
                      <Share2 size={14} className="text-muted-foreground" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* No-shopping guarantee */}
      <section className="px-5 pb-8">
        <div className="bg-sand/20 rounded-2xl p-4 text-center animate-fade-up delay-500">
          <p className="text-xs text-muted-foreground">
            🛡️ 发现页内容100%无商品导购 · 无带货种草 · 纯干货穿搭知识
          </p>
        </div>
      </section>
    </div>
  )
}