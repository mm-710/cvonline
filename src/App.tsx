import { Routes, Route, Navigate, useNavigate } from 'react-router'
import { useAuthStore } from '@/store/authStore'
import HomePage from '@/pages/HomePage'
import WardrobePage from '@/pages/WardrobePage'
import RecordPage from '@/pages/RecordPage'
import DiscoverPage from '@/pages/DiscoverPage'
import ProfilePage from '@/pages/ProfilePage'
import LoginPage from '@/pages/LoginPage'
import OnboardingPage from '@/pages/OnboardingPage'
import BottomNav from '@/components/BottomNav'
import AuthGuardModal from '@/components/AuthGuardModal'
import { useState } from 'react'

/** Routes accessible without login (guest mode) */
const GUEST_ALLOWED = ['/', '/discover']

function AuthGuard({ children, feature }: { children: React.ReactNode; feature: string }) {
  const { isLoggedIn, isGuest } = useAuthStore()
  const [showModal, setShowModal] = useState(false)

  if (isLoggedIn) return <>{children}</>

  if (isGuest) {
    // Guest can only see certain pages
    return (
      <>
        {showModal && <AuthGuardModal feature={feature} onClose={() => setShowModal(false)} />}
        <div onClick={() => setShowModal(true)} className="cursor-pointer">
          {children}
        </div>
      </>
    )
  }

  // Not logged in at all — redirect to login
  return <Navigate to="/login" replace />
}

export default function App() {
  const { isLoggedIn, isGuest, hasCompletedOnboarding } = useAuthStore()
  const navigate = useNavigate()

  // Determine initial route
  const getInitialRoute = () => {
    if (!isLoggedIn && !isGuest) return '/login'
    if (isLoggedIn && !hasCompletedOnboarding) return '/onboarding'
    return '/'
  }

  return (
    <div className="min-h-screen bg-cream">
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/onboarding" element={
          isLoggedIn ? <OnboardingPage /> : <Navigate to="/login" replace />
        } />

        {/* Guest-accessible routes */}
        <Route path="/" element={
          isLoggedIn || isGuest ? (
            <><HomePage /><BottomNav /></>
          ) : <Navigate to="/login" replace />
        } />
        <Route path="/discover" element={
          isLoggedIn || isGuest ? (
            <><DiscoverPage /><BottomNav /></>
          ) : <Navigate to="/login" replace />
        } />

        {/* Auth-required routes with guard */}
        <Route path="/wardrobe" element={
          <AuthGuard feature="wardrobe">
            <><WardrobePage /><BottomNav /></>
          </AuthGuard>
        } />
        <Route path="/record" element={
          <AuthGuard feature="record">
            <><RecordPage /><BottomNav /></>
          </AuthGuard>
        } />
        <Route path="/profile" element={
          isLoggedIn ? (
            <><ProfilePage /><BottomNav /></>
          ) : (
            <AuthGuard feature="vip">
              <><ProfilePage /><BottomNav /></>
            </AuthGuard>
          )
        } />

        {/* Catch-all */}
        <Route path="*" element={<Navigate to={getInitialRoute()} replace />} />
      </Routes>
    </div>
  )
}