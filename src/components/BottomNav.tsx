import { NavLink } from 'react-router'
import { Shirt, Sparkles, BookOpen, Compass, User } from 'lucide-react'

const navItems = [
  { path: '/', label: '穿搭', icon: Sparkles },
  { path: '/wardrobe', label: '衣橱', icon: Shirt },
  { path: '/record', label: '记录', icon: BookOpen },
  { path: '/discover', label: '发现', icon: Compass },
  { path: '/profile', label: '我的', icon: User },
]

export default function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 glass-card border-t border-sand/30">
      <div className="max-w-lg mx-auto flex items-center justify-around h-[72px] px-2">
        {navItems.map(({ path, label, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              `flex flex-col items-center gap-1 px-3 py-2 rounded-xl transition-all duration-300 ${
                isActive
                  ? 'text-forest scale-105'
                  : 'text-muted-foreground hover:text-forest/70'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <div className={`p-1.5 rounded-xl transition-all duration-300 ${isActive ? 'bg-forest/10' : ''}`}>
                  <Icon size={20} strokeWidth={isActive ? 2.2 : 1.5} />
                </div>
                <span className={`text-xs font-medium ${isActive ? 'font-semibold' : ''}`}>
                  {label}
                </span>
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  )
}