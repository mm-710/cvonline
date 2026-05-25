import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface UserProfile {
  name: string
  phone: string
  email: string
  bodyType: string
  skinTone: string
  preference: string
  scenes: string[]
  height: string
  weight: string
}

interface AuthState {
  isLoggedIn: boolean
  isGuest: boolean
  hasCompletedOnboarding: boolean
  profile: UserProfile
  login: (method: 'phone' | 'wechat' | 'email', identifier: string) => void
  loginAsGuest: () => void
  logout: () => void
  completeOnboarding: (profile: Partial<UserProfile>) => void
  updateProfile: (updates: Partial<UserProfile>) => void
}

const DEFAULT_PROFILE: UserProfile = {
  name: '',
  phone: '',
  email: '',
  bodyType: '',
  skinTone: '',
  preference: '',
  scenes: [],
  height: '',
  weight: '',
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isLoggedIn: false,
      isGuest: false,
      hasCompletedOnboarding: false,
      profile: DEFAULT_PROFILE,

      login: (method, identifier) =>
        set({
          isLoggedIn: true,
          isGuest: false,
          profile: {
            ...DEFAULT_PROFILE,
            name: method === 'wechat' ? '微信用户' : identifier,
            phone: method === 'phone' ? identifier : '',
            email: method === 'email' ? identifier : '',
          },
        }),

      loginAsGuest: () => set({ isGuest: true, isLoggedIn: false }),

      logout: () =>
        set({
          isLoggedIn: false,
          isGuest: false,
          hasCompletedOnboarding: false,
          profile: DEFAULT_PROFILE,
        }),

      completeOnboarding: (profileUpdates) =>
        set((state) => ({
          hasCompletedOnboarding: true,
          profile: { ...state.profile, ...profileUpdates },
        })),

      updateProfile: (updates) =>
        set((state) => ({
          profile: { ...state.profile, ...updates },
        })),
    }),
    {
      name: 'jianda-auth',
    }
  )
)