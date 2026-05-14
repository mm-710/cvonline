import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'
import { account, loginWithKuaishou } from '@/lib/appwrite'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function LoginPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // 兑换 OAuth2 token（SSO 回调后 URL 携带 userId/secret）
    const params = new URLSearchParams(window.location.search)
    const userId = params.get('userId')
    const secret = params.get('secret')

    if (userId && secret) {
      account
        .createSession({ userId, secret })
        .then(() => navigate('/', { replace: true }))
        .catch(() => setLoading(false))
      return
    }

    // 检查是否已登录
    account
      .get()
      .then(() => navigate('/', { replace: true }))
      .catch(() => setLoading(false))
  }, [navigate])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted-foreground text-sm">正在验证登录状态…</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center">
          <CardTitle>登录</CardTitle>
          <CardDescription>使用快手账号登录</CardDescription>
        </CardHeader>
        <CardContent>
          <button className="w-full" onClick={loginWithKuaishou}>
            快手 SSO 登录
          </button>
        </CardContent>
      </Card>
    </div>
  )
}
