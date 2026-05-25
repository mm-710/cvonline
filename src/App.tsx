import { Routes, Route, Navigate } from 'react-router'
import HomePage from '@/pages/HomePage'
import WardrobePage from '@/pages/WardrobePage'
import RecordPage from '@/pages/RecordPage'
import DiscoverPage from '@/pages/DiscoverPage'
import ProfilePage from '@/pages/ProfilePage'
import OnboardingPage from '@/pages/OnboardingPage'
import BottomNav from '@/components/BottomNav'

function App() {
  return (
    <div className="min-h-screen bg-cream pb-nav-safe">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/wardrobe" element={<WardrobePage />} />
        <Route path="/record" element={<RecordPage />} />
        <Route path="/discover" element={<DiscoverPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <BottomNav />
    </div>
  )
}

export default App