import { useState } from 'react'
import { useNavigate } from 'react-router'
import { useAuthStore } from '@/store/authStore'
import { Phone, MessageSquare, Mail, Eye, EyeOff, X, Shield } from 'lucide-react'

type LoginMethod = 'phone' | 'wechat' | 'email'

export default function LoginPage() {
  const navigate = useNavigate()
  const { login, loginAsGuest } = useAuthStore()
  const [activeMethod, setActiveMethod] = useState<LoginMethod>('phone')
  const [phone, setPhone] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [verifyCode, setVerifyCode] = useState('')
  const [codeSent, setCodeSent] = useState(false)
  const [codeCountdown, setCodeCountdown] = useState(0)
  const [agreed, setAgreed] = useState(false)

  const sendCode = () => {
    if (!phone || phone.length < 11) return
    setCodeSent(true)
    setCodeCountdown(60)
    const timer = setInterval(() => {
      setCodeCountdown((c) => {
        if (c <= 1) {
          clearInterval(timer)
          return 0
        }
        return c - 1
      })
    }, 1000)
  }

  const handleLogin = () => {
    if (!agreed) return
    if (activeMethod === 'phone' && phone.length >= 11) {
      login('phone', phone)
      navigate('/onboarding')
    } else if (activeMethod === 'email' && email && password) {
      login('email', email)
      navigate('/onboarding')
    }
  }

  const handleWechatLogin = () => {
    if (!agreed) return
    login('wechat', '微信用户')
    navigate('/onboarding')
  }

  const handleGuest = () => {
    loginAsGuest()
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-cream max-w-lg mx-auto flex flex-col">
      {/* Header illustration area */}
      <div className="relative h-[280px] gradient-mesh flex items-center justify-center overflow-hidden">
        {/* Decorative blobs */}
        <div className="absolute w-32 h-32 bg-forest/8 blob-1 top-8 -left-8 animate-float" />
        <div className="absolute w-24 h-24 bg-coral/10 blob-2 top-16 right-8 animate-float delay-200" />
        <div className="absolute w-16 h-16 bg-sand/30 blob-1 bottom-12 left-16 animate-float delay-300" />

        <div className="text-center z-10 animate-fade-up">
          <div className="w-16 h-16 bg-forest rounded-2xl mx-auto mb-4 flex items-center justify-center shadow-lg shadow-forest/20">
            <span className="font-handwritten text-3xl text-white">简搭</span>
          </div>
          <h1 className="text-2xl font-bold text-ink tracking-tight">简搭衣橱</h1>
          <p className="text-sm text-muted-foreground mt-2">盘活你的每一件衣服，每天轻松穿出彩</p>
        </div>
      </div>

      {/* Login form */}
      <div className="flex-1 px-5 pt-8 pb-6">
        {/* Method tabs */}
        <div className="flex gap-2 mb-6 animate-fade-up delay-100">
          {([
            { method: 'phone' as LoginMethod, label: '手机号', icon: Phone },
            { method: 'wechat' as LoginMethod, label: '微信', icon: MessageSquare },
            { method: 'email' as LoginMethod, label: '邮箱', icon: Mail },
          ]).map(({ method, label, icon: Icon }) => (
            <button
              key={method}
              onClick={() => setActiveMethod(method)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-300 ${
                activeMethod === method
                  ? 'bg-forest text-white shadow-sm'
                  : 'bg-white ring-1 ring-sand/30 text-ink hover:bg-forest/5'
              }`}
            >
              <Icon size={16} />
              {label}
            </button>
          ))}
        </div>

        {/* Phone login form */}
        {activeMethod === 'phone' && (
          <div className="space-y-4 animate-fade-in">
            <div className="bg-white rounded-xl ring-1 ring-sand/30 px-4 py-3 flex items-center gap-2">
              <Phone size={16} className="text-muted-foreground" />
              <input
                type="tel"
                placeholder="请输入手机号"
                value={phone}
                onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 11))}
                className="text-sm text-ink placeholder-muted-foreground bg-transparent outline-none flex-1"
                maxLength={11}
              />
            </div>

            <div className="bg-white rounded-xl ring-1 ring-sand/30 px-4 py-3 flex items-center gap-2">
              <Shield size={16} className="text-muted-foreground" />
              <input
                type="text"
                placeholder="验证码"
                value={verifyCode}
                onChange={(e) => setVerifyCode(e.target.value.slice(0, 6))}
                className="text-sm text-ink placeholder-muted-foreground bg-transparent outline-none flex-1"
                maxLength={6}
              />
              <button
                onClick={sendCode}
                disabled={codeCountdown > 0 || phone.length < 11}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  codeCountdown > 0 || phone.length < 11
                    ? 'bg-sand/30 text-muted-foreground'
                    : 'bg-forest text-white hover:bg-forest-deep'
                }`}
              >
                {codeCountdown > 0 ? `${codeCountdown}s` : '获取验证码'}
              </button>
            </div>

            <button
              onClick={handleLogin}
              disabled={!agreed || phone.length < 11}
              className={`w-full py-3 rounded-xl text-sm font-semibold transition-all duration-300 ${
                agreed && phone.length >= 11
                  ? 'bg-forest text-white hover:bg-forest-deep'
                  : 'bg-sand/30 text-muted-foreground'
              }`}
            >
              登录
            </button>
          </div>
        )}

        {/* Wechat login */}
        {activeMethod === 'wechat' && (
          <div className="animate-fade-in flex flex-col items-center gap-5 py-8">
            <div className="w-56 h-56 bg-white rounded-2xl ring-1 ring-sand/30 flex flex-col items-center justify-center gap-3">
              <MessageSquare size={48} className="text-[#07C160]" />
              <p className="text-sm text-ink font-medium">微信快捷登录</p>
              <p className="text-xs text-muted-foreground">一键授权，无需输入密码</p>
            </div>

            <button
              onClick={handleWechatLogin}
              disabled={!agreed}
              className={`w-full py-3 rounded-xl text-sm font-semibold transition-all duration-300 ${
                agreed
                  ? 'bg-[#07C160] text-white hover:bg-[#06AD56]'
                  : 'bg-sand/30 text-muted-foreground'
              }`}
            >
              微信一键登录
            </button>
          </div>
        )}

        {/* Email login */}
        {activeMethod === 'email' && (
          <div className="space-y-4 animate-fade-in">
            <div className="bg-white rounded-xl ring-1 ring-sand/30 px-4 py-3 flex items-center gap-2">
              <Mail size={16} className="text-muted-foreground" />
              <input
                type="email"
                placeholder="请输入邮箱地址"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="text-sm text-ink placeholder-muted-foreground bg-transparent outline-none flex-1"
              />
            </div>

            <div className="bg-white rounded-xl ring-1 ring-sand/30 px-4 py-3 flex items-center gap-2">
              {showPassword ? <Eye size={16} className="text-muted-foreground" /> : <EyeOff size={16} className="text-muted-foreground" />}
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="请输入密码"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="text-sm text-ink placeholder-muted-foreground bg-transparent outline-none flex-1"
              />
              <button onClick={() => setShowPassword(!showPassword)} className="p-1 hover:bg-sand/20 rounded-lg transition-colors">
                {showPassword ? <EyeOff size={14} className="text-muted-foreground" /> : <Eye size={14} className="text-muted-foreground" />}
              </button>
            </div>

            <button
              onClick={handleLogin}
              disabled={!agreed || !email || !password}
              className={`w-full py-3 rounded-xl text-sm font-semibold transition-all duration-300 ${
                agreed && email && password
                  ? 'bg-forest text-white hover:bg-forest-deep'
                  : 'bg-sand/30 text-muted-foreground'
              }`}
            >
              登录
            </button>
          </div>
        )}

        {/* Agreement */}
        <div className="mt-5 flex items-center gap-2 animate-fade-up delay-200">
          <button
            onClick={() => setAgreed(!agreed)}
            className={`w-4 h-4 rounded border-2 flex items-center justify-center transition-all duration-300 ${
              agreed
                ? 'bg-forest border-forest text-white'
                : 'border-sand/50 bg-white'
            }`}
          >
            {agreed && <span className="text-xs">✓</span>}
          </button>
          <p className="text-xs text-muted-foreground">
            我已阅读并同意
            <span className="text-forest font-medium">《用户协议》</span>
            和
            <span className="text-forest font-medium">《隐私政策》</span>
          </p>
        </div>

        {/* Guest entry */}
        <div className="mt-6 text-center animate-fade-up delay-300">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="h-px bg-sand/30 flex-1" />
            <span className="text-xs text-muted-foreground">或者</span>
            <div className="h-px bg-sand/30 flex-1" />
          </div>
          <button
            onClick={handleGuest}
            className="text-sm text-muted-foreground hover:text-ink transition-colors"
          >
            游客体验 → 仅可浏览首页Demo和发现页
          </button>
        </div>
      </div>
    </div>
  )
}