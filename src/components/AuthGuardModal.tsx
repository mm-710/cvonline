import { useAuthStore } from '@/store/authStore'
import { X, Lock, Shirt, BookOpen, Crown } from 'lucide-react'

interface AuthGuardModalProps {
  feature: string
  onClose: () => void
}

export default function AuthGuardModal({ feature, onClose }: AuthGuardModalProps) {
  const { logout } = useAuthStore()

  const handleLogin = () => {
    logout() // clear guest state
    onClose()
    // Router will redirect to login page since isLoggedIn=false and isGuest=false
  }

  const featureIcons: Record<string, { icon: typeof Shirt; color: string }> = {
    wardrobe: { icon: Shirt, color: 'text-forest' },
    record: { icon: BookOpen, color: 'text-coral' },
    vip: { icon: Crown, color: 'text-lavender' },
  }

  const { icon: Icon, color } = featureIcons[feature] || { icon: Lock, color: 'text-ink' }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center animate-fade-in">
      <div className="absolute inset-0 bg-ink/30 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-cream rounded-2xl shadow-2xl w-[85%] max-w-sm p-6 animate-slide-in-right">
        <button onClick={onClose} className="absolute top-4 right-4 p-2 hover:bg-sand/20 rounded-xl transition-colors">
          <X size={18} className="text-muted-foreground" />
        </button>

        <div className="flex flex-col items-center text-center">
          {/* Icon */}
          <div className="w-16 h-16 bg-white rounded-2xl ring-1 ring-sand/30 flex items-center justify-center mb-4">
            <Icon size={28} className={color} />
          </div>

          <h2 className="text-lg font-bold text-ink mb-2">登录解锁全部工具权益</h2>
          <p className="text-sm text-muted-foreground mb-6">
            游客模式仅可浏览首页搭配Demo和发现页内容。<br />
            登录后即可使用衣橱存档、穿搭记录、数据统计等核心功能。
          </p>

          {/* Preview cards */}
          <div className="grid grid-cols-3 gap-2 mb-6">
            {[
              { label: '衣橱存档', emoji: '🧥' },
              { label: '穿搭记录', emoji: '📸' },
              { label: '数据统计', emoji: '📊' },
            ].map(({ label, emoji }) => (
              <div className="bg-white rounded-xl p-3 ring-1 ring-sand/30 text-center">
                <span className="text-lg mb-1 block">{emoji}</span>
                <span className="text-xs text-ink font-medium">{label}</span>
              </div>
            ))}
          </div>

          <button
            onClick={handleLogin}
            className="w-full py-3 bg-forest text-white rounded-xl text-sm font-semibold hover:bg-forest-deep transition-colors shadow-md shadow-forest/20"
          >
            一键登录
          </button>

          <p className="mt-3 text-xs text-muted-foreground">
            支持手机号 · 微信 · 邮箱三种方式
          </p>
        </div>
      </div>
    </div>
  )
}