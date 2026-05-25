import { useState } from 'react'
import { ChevronRight, ChevronLeft, SkipForward, X } from 'lucide-react'

const STEPS = [
  {
    id: 'body',
    title: '你的身材类型',
    subtitle: '帮助AI精准适配穿搭',
    options: [
      { id: 'h', name: 'H型', desc: '肩腰臀接近，直板身材', icon: '📏' },
      { id: 'o', name: 'O型', desc: '腰腹丰满，圆润身材', icon: '🍎' },
      { id: 'x', name: 'X型', desc: '肩臀宽、腰细，沙漏身材', icon: '⏳' },
      { id: 'a', name: 'A型', desc: '臀宽肩窄，梨形身材', icon: '🍐' },
      { id: 'v', name: 'V型', desc: '肩宽臀窄，倒三角身材', icon: '🔻' },
    ],
  },
  {
    id: 'skin',
    title: '你的肤色类型',
    subtitle: '帮助AI精准配色推荐',
    options: [
      { id: 'cool', name: '冷皮', desc: '偏粉白、血管偏蓝紫', icon: '🧊' },
      { id: 'warm', name: '暖皮', desc: '偏黄暖、血管偏绿', icon: '☀️' },
      { id: 'neutral', name: '中性皮', desc: '不偏冷也不偏暖', icon: '🌡️' },
    ],
  },
  {
    id: 'style',
    title: '你的穿搭偏好',
    subtitle: '帮助AI推荐符合你审美的搭配',
    options: [
      { id: 'minimal', name: '简约', desc: '少即是多，干净利落', icon: '✨' },
      { id: 'commute', name: '通勤', desc: '专业干练，职场必备', icon: '💼' },
      { id: 'sweet', name: '甜酷', desc: '甜美+个性混搭', icon: '🎀' },
      { id: 'casual', name: '休闲', desc: '舒适自在，无拘无束', icon: '☕' },
      { id: 'french', name: '法式', desc: '优雅浪漫，慵懒精致', icon: '🇫🇷' },
    ],
  },
  {
    id: 'scene',
    title: '高频穿搭场景',
    subtitle: '帮助AI优先推荐日常搭配',
    options: [
      { id: 'work', name: '职场', desc: '上班开会商务场合', icon: '🏢' },
      { id: 'school', name: '上学', desc: '校园课堂日常', icon: '📚' },
      { id: 'date', name: '约会', desc: '浪漫出游社交', icon: '💕' },
      { id: 'travel', name: '通勤', desc: '赶地铁赶公交', icon: '🚇' },
      { id: 'sport', name: '运动', desc: '健身跑步瑜伽', icon: '🏃' },
      { id: 'rest', name: '休闲', desc: '在家逛街逛公园', icon: '🌿' },
    ],
  },
]

export default function OnboardingPage() {
  const [currentStep, setCurrentStep] = useState(0)
  const [selections, setSelections] = useState<Record<string, string>>({})
  const [showSkipConfirm, setShowSkipConfirm] = useState(false)

  const step = STEPS[currentStep]
  const progress = ((currentStep + 1) / STEPS.length) * 100

  const handleSelect = (optionId: string) => {
    setSelections({ ...selections, [step.id]: optionId })
  }

  const handleNext = () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleFinish = () => {
    // In real app, save selections and redirect to home
    window.location.href = '/'
  }

  const handleSkip = () => {
    setShowSkipConfirm(true)
  }

  return (
    <div className="min-h-screen bg-cream max-w-lg mx-auto">
      {/* Progress */}
      <div className="px-5 pt-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <button onClick={handleSkip} className="flex items-center gap-1 text-sm text-muted-foreground hover:text-ink transition-colors">
              <SkipForward size={14} />
              跳过
            </button>
          </div>
          <span className="text-sm text-muted-foreground">{currentStep + 1} / {STEPS.length}</span>
        </div>
        <div className="h-1.5 bg-sand/30 rounded-full overflow-hidden">
          <div
            className="h-full bg-forest rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Step Content */}
      <div className="px-5 pt-6 pb-10 animate-fade-in" key={step.id}>
        <h2 className="text-2xl font-bold text-ink tracking-tight">{step.title}</h2>
        <p className="text-sm text-muted-foreground mt-1 mb-6">{step.subtitle}</p>

        <div className="space-y-3">
          {step.options.map((option) => (
            <button
              key={option.id}
              onClick={() => handleSelect(option.id)}
              className={`w-full flex items-center gap-4 p-4 rounded-2xl transition-all duration-300 ${
                selections[step.id] === option.id
                  ? 'bg-forest text-white ring-0 shadow-md scale-[1.02]'
                  : 'bg-white ring-1 ring-sand/30 text-ink hover:bg-forest/5'
              }`}
            >
              <span className="text-2xl">{option.icon}</span>
              <div className="flex-1">
                <p className="text-base font-semibold">{option.name}</p>
                <p className={`text-sm ${selections[step.id] === option.id ? 'opacity-70' : 'text-muted-foreground'}`}>
                  {option.desc}
                </p>
              </div>
              {selections[step.id] === option.id && (
                <div className="w-5 h-5 bg-coral rounded-full flex items-center justify-center">
                  <span className="text-white text-xs">✓</span>
                </div>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Navigation */}
      <div className="fixed bottom-[90px] left-0 right-0 px-5 max-w-lg mx-auto">
        <div className="flex items-center justify-between">
          {currentStep > 0 ? (
            <button
              onClick={handlePrev}
              className="flex items-center gap-1 px-4 py-2.5 bg-white ring-1 ring-sand/30 rounded-xl text-sm font-medium text-ink hover:bg-forest/5 transition-colors"
            >
              <ChevronLeft size={16} />
              上一步
            </button>
          ) : (
            <div />
          )}

          {currentStep < STEPS.length - 1 ? (
            <button
              onClick={handleNext}
              className="flex items-center gap-1 px-6 py-2.5 bg-forest text-white rounded-xl text-sm font-semibold hover:bg-forest-deep transition-colors"
            >
              下一步
              <ChevronRight size={16} />
            </button>
          ) : (
            <button
              onClick={handleFinish}
              className="flex items-center gap-1 px-6 py-2.5 bg-forest text-white rounded-xl text-sm font-semibold hover:bg-forest-deep transition-colors"
            >
              完成开启体验
              <ChevronRight size={16} />
            </button>
          )}
        </div>
      </div>

      {/* Skip Confirmation Modal */}
      {showSkipConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center animate-fade-in">
          <div className="absolute inset-0 bg-ink/30 backdrop-blur-sm" onClick={() => setShowSkipConfirm(false)} />
          <div className="relative bg-cream rounded-2xl shadow-2xl w-[85%] max-w-sm p-6 animate-slide-in-right">
            <h2 className="text-lg font-bold text-ink mb-2">确认跳过？</h2>
            <p className="text-sm text-muted-foreground mb-5">
              跳过个性化设置后，AI搭配推荐将使用通用方案。后续可在「我的」→「个人资料」随时修改。
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowSkipConfirm(false)}
                className="px-4 py-2.5 bg-white ring-1 ring-sand/30 text-ink rounded-xl text-sm font-medium"
              >
                继续填写
              </button>
              <button
                onClick={() => window.location.href = '/'}
                className="px-4 py-2.5 bg-forest text-white rounded-xl text-sm font-semibold"
              >
                确认跳过
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}