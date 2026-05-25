import { Bookmark, ChevronRight, Sparkles } from 'lucide-react'

interface Outfit {
  id: string
  name: string
  items: string[]
  matchScore: number
  reason: string
  tags: string[]
}

export default function OutfitCard({ outfit }: { outfit: Outfit }) {
  return (
    <div className="bg-white rounded-2xl ring-1 ring-sand/30 overflow-hidden outfit-card-lift">
      {/* Score badge */}
      <div className="flex items-center justify-between px-4 pt-4 pb-2">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 px-2.5 py-1 bg-forest/10 rounded-full">
            <Sparkles size={12} className="text-forest" />
            <span className="text-xs font-bold text-forest">{outfit.matchScore}%适配</span>
          </div>
          <h3 className="text-base font-bold text-ink">{outfit.name}</h3>
        </div>
        <button className="p-1.5 hover:bg-forest/5 rounded-lg transition-colors">
          <Bookmark size={16} className="text-muted-foreground hover:text-forest" />
        </button>
      </div>

      {/* Items row - visual representation */}
      <div className="px-4 py-3">
        <div className="flex gap-2.5">
          {outfit.items.map((item, idx) => (
            <div
              key={idx}
              className="flex-1 bg-cream/80 rounded-xl p-3 text-center"
            >
              {/* Placeholder clothing icon */}
              <div className="w-full aspect-square bg-sand/30 rounded-lg mb-2 flex items-center justify-center">
                <span className="font-handwritten text-lg text-forest/40">
                  {idx === 0 ? '衫' : idx === 1 ? '裤' : idx === 2 ? '鞋' : '饰'}
                </span>
              </div>
              <p className="text-xs text-ink font-medium truncate">{item}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Reason */}
      <div className="px-4 pb-3">
        <p className="text-xs text-muted-foreground leading-relaxed">{outfit.reason}</p>
      </div>

      {/* Tags & Actions */}
      <div className="px-4 pb-4 flex items-center justify-between">
        <div className="flex gap-1.5">
          {outfit.tags.map((tag) => (
            <span
              key={tag}
              className="px-2 py-0.5 text-xs bg-sand/40 text-ink/70 rounded-full"
            >
              {tag}
            </span>
          ))}
        </div>
        <button className="flex items-center gap-1 px-3 py-1.5 bg-forest text-white rounded-xl text-sm font-medium hover:bg-forest-deep transition-colors">
          一键记录
          <ChevronRight size={14} />
        </button>
      </div>
    </div>
  )
}