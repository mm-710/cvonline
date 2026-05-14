# Prompt-Reference — UI/UX Image Generation Prompt Guide

> A reference handbook for expanding vague user intents into high-quality natural language prompts for AI image generation (Gemini, Midjourney, Stable Diffusion, etc.)  
> Fused from: [FelipeOFF/design-advisor-skill](https://github.com/FelipeOFF/design-advisor-skill) + [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) ⭐ ~69.5k

---

## How to Use This Document

1. **Parse** the user intent → extract 4 dimensions using **Part 1**
2. **Look up** the industry → find recommended style + color mood in **Part 2**
3. **Select** visual style → grab AI Prompt Keywords from **Part 3**
4. **Colors** → copy the **Palette Description** from **Part 4** directly (HEX + fixed descriptions provided)
5. **Add** typography mood → choose heading/body style from **Part 5**
6. **Compose** the layout → use composition keywords from **Part 6**
7. **Combine** all elements into the final prompt

---

## Table of Contents

1. [Intent Parsing Framework](#part-1--intent-parsing-framework)
2. [Industry → Design Rule Index](#part-2--industry--design-rule-index)
3. [Visual Style Prompt Keyword Library](#part-3--visual-style-prompt-keyword-library)
4. [Industry Color Palette → Natural Language](#part-4--industry-color-palette--natural-language)
5. [Typography Mood Keywords](#part-5--typography-mood-keywords)
6. [Layout & Composition Reference](#part-6--layout--composition-reference)

---

## Part 1 — Intent Parsing Framework

> When a user provides a vague image generation intent, extract the following 4 signal dimensions before expanding the prompt. If a dimension is missing, infer it from the industry rules in Part 2.

### 4 Signal Dimensions

| Dimension | Description | Examples |
|---|---|---|
| **Industry / Product Type** | What sector or product is this for? | SaaS, healthcare, gaming, e-commerce, restaurant, fitness |
| **Content Purpose** | What kind of image is needed? | UI screenshot, poster/banner, hero image, product mockup, infographic, illustration |
| **Style Preference** | Any explicit style cues from the user? | "minimal", "dark", "vibrant", "luxury", "retro", "playful" |
| **Emotional Tone** | Desired feeling / atmosphere | professional, playful, trustworthy, energetic, calm, romantic, futuristic |

### Inference Rules

- If **industry** is stated → look up Part 2 for recommended style, colors, and anti-patterns
- If **style** is stated → look up Part 3 for the AI Prompt Keywords of that style
- If **no style or industry** → use the user's emotional tone words to select the closest match from Part 3
- If **colors** are needed → use Part 4 to convert palette to natural language
- If **layout/composition** is needed → use Part 6 for layout keywords

### Output Format for Expanded Prompt

```
[Subject] [Content Purpose] — [Composition/Layout] — [Visual Style] — [Color Palette in natural language] — [Lighting & Atmosphere] — [Typography Style] — [Avoid]
```

**Example:**
> User intent: "AI assistant app home screen"
>
> Expanded: A clean mobile app UI screenshot showing an AI chat assistant home screen — centered content layout with card-based modules — glassmorphism style with frosted glass panels and translucent overlays — deep violet primary, soft cyan accent, near-white purple background, light lavender borders — soft ambient glow lighting, layered depth, subtle reflections — modern sans-serif clean typography — avoid heavy chrome, slow-feedback indicators, dark mode by default


---

## Part 2 — Industry → Design Rule Index

> Use this table to identify the recommended visual style, palette reference, and patterns to avoid for a given industry.

| # | Industry / Product Type | Recommended Visual Style | Color Mood | Typography Mood | Key Visual Effects | Avoid (Anti-Patterns) |
|---|---|---|---|---|---|---|
| 1 | SaaS (General) | Glassmorphism + Flat Design | Trust blue + Accent contrast | Professional + Hierarchy | Subtle hover (200-250ms) + Smooth transitions | Excessive animation + Dark mode by default |
| 2 | Micro SaaS | Motion-Driven + Vibrant & Block | Bold primaries + Accent contrast | Modern + Energetic typography | Scroll-triggered animations + Parallax | Static design + No video + Poor mobile |
| 3 | E-commerce | Vibrant & Block-based | Brand primary + Success green | Engaging + Clear hierarchy | Card hover lift (200ms) + Scale effect | Flat design without depth + Text-heavy pages |
| 4 | E-commerce Luxury | Liquid Glass + Glassmorphism | Premium colors + Minimal accent | Elegant + Refined typography | Chromatic aberration + Fluid animations (400-600ms) | Vibrant & Block-based + Playful colors |
| 5 | B2B Service | Trust & Authority + Minimalism | Professional blue + Neutral grey | Formal + Clear typography | Section transitions + Feature reveals | Playful design + Hidden credentials + AI purple/pink gradients |
| 6 | Financial Dashboard | Dark Mode (OLED) + Data-Dense | Dark bg + Red/Green alerts + Trust blue | Clear + Readable typography | Real-time number animations + Alert pulse | Light mode default + Slow rendering |
| 7 | Analytics Dashboard | Data-Dense + Heat Map | Cool→Hot gradients + Neutral grey | Clear + Functional typography | Hover tooltips + Chart zoom + Filter animations | Ornate design + No filtering |
| 8 | Healthcare App | Neumorphism + Accessible & Ethical | Calm blue + Health green | Readable + Large type (16px+) | Soft box-shadow + Smooth press (150ms) | Bright neon colors + Motion-heavy animations + AI purple/pink gradients |
| 9 | Educational App | Claymorphism + Micro-interactions | Playful colors + Clear hierarchy | Friendly + Engaging typography | Soft press (200ms) + Fluffy elements | Dark modes + Complex jargon |
| 10 | Creative Agency | Brutalism + Motion-Driven | Bold primaries + Artistic freedom | Bold + Expressive typography | CRT scanlines + Neon glow + Glitch effects | Corporate minimalism + Hidden portfolio |
| 11 | Portfolio/Personal | Motion-Driven + Minimalism | Brand primary + Artistic | Expressive + Variable typography | Parallax (3-5 layers) + Scroll-triggered reveals | Corporate templates + Generic layouts |
| 12 | Gaming | 3D & Hyperrealism + Retro-Futurism | Vibrant + Neon + Immersive | Bold + Impactful typography | WebGL 3D rendering + Glitch effects | Minimalist design + Static assets |
| 13 | Government/Public Service | Accessible & Ethical + Minimalism | Professional blue + High contrast | Clear + Large typography | Clear focus rings (3-4px) + Skip links | Ornate design + Low contrast + Motion effects + AI purple/pink gradients |
| 14 | Fintech/Crypto | Minimalism + Accessible & Ethical | Navy + Trust Blue + Gold | Professional + Trustworthy | Smooth state transitions + Number animations | Playful design + Unclear fees + AI purple/pink gradients |
| 15 | Social Media App | Vibrant & Block-based + Motion-Driven | Vibrant + Engagement colors | Modern + Bold typography | Large scroll animations + Icon animations | Heavy skeuomorphism + Accessibility ignored |
| 16 | Productivity Tool | Flat Design + Micro-interactions | Clear hierarchy + Functional colors | Clean + Efficient typography | Quick actions (150ms) + Task animations | Complex onboarding + Slow performance |
| 17 | Design System/Component Library | Minimalism + Accessible & Ethical | Clear hierarchy + Code-like structure | Monospace + Clear typography | Code copy animations + Component previews | Poor documentation + No live preview |
| 18 | AI/Chatbot Platform | AI-Native UI + Minimalism | Neutral + AI Purple (#6366F1) | Modern + Clear typography | Streaming text + Typing indicators + Fade-in | Heavy chrome + Slow response feedback |
| 19 | NFT/Web3 Platform | Cyberpunk UI + Glassmorphism | Dark + Neon + Gold (#FFD700) | Bold + Modern typography | Wallet connect animations + Transaction feedback | Light mode default + No transaction status |
| 20 | Creator Economy Platform | Vibrant & Block-based + Bento Box Grid | Vibrant + Brand colors | Modern + Bold typography | Engagement counter animations + Profile reveals | Generic layout + Hidden earnings |
| 21 | Remote Work/Collaboration Tool | Soft UI Evolution + Minimalism | Calm Blue + Neutral grey | Clean + Readable typography | Real-time presence indicators + Notification badges | Cluttered interface + No presence |
| 22 | Mental Health App | Neumorphism + Accessible & Ethical | Calm Pastels + Trust colors | Calming + Readable typography | Soft press + Breathing animations | Bright neon + Motion overload |
| 23 | Pet Tech App | Claymorphism + Vibrant & Block-based | Playful + Warm colors | Friendly + Playful typography | Pet profile animations + Health tracking charts | Generic design + No personality |
| 24 | Smart Home/IoT Dashboard | Glassmorphism + Dark Mode (OLED) | Dark + Status indicator colors | Clear + Functional typography | Device status pulse + Quick action animations | Slow updates + No automation |
| 25 | EV/Charging Ecosystem | Minimalism + Aurora UI | Electric Blue (#009CD1) + Green | Modern + Clear typography | Range estimation animations + Map interactions | Poor map UX + Hidden costs |
| 26 | Subscription Box Service | Vibrant & Block-based + Motion-Driven | Brand + Excitement colors | Engaging + Clear typography | Unboxing reveal animations + Product carousel | Confusing pricing + No unboxing preview |
| 27 | Podcast Platform | Dark Mode (OLED) + Minimalism | Dark + Audio waveform accents | Modern + Clear typography | Waveform visualizations + Episode transitions | Poor audio player + Cluttered layout |
| 28 | Dating App | Vibrant & Block-based + Motion-Driven | Warm + Romantic (Pink/Red gradients) | Modern + Friendly typography | Profile card swipe + Match animations | Generic profiles + No safety |
| 29 | Micro-Credentials/Badges Platform | Minimalism + Flat Design | Trust Blue + Gold (#FFD700) | Professional + Clear typography | Badge reveal animations + Progress tracking | No verification + Hidden progress |
| 30 | Knowledge Base/Documentation | Minimalism + Accessible & Ethical | Clean hierarchy + Minimal color | Clear + Readable typography | Search highlight + Smooth scrolling | Poor navigation + No search |
| 31 | Hyperlocal Services | Minimalism + Vibrant & Block-based | Location markers + Trust colors | Clear + Functional typography | Map hover + Provider card reveals | No map + Hidden reviews |
| 32 | Beauty/Spa/Wellness Service | Soft UI Evolution + Neumorphism | Soft pastels (Pink Sage Cream) + Gold accents | Elegant + Calming typography | Soft shadows + Smooth transitions (200-300ms) + Gentle hover | Bright neon colors + Harsh animations + Dark mode |
| 33 | Luxury/Premium Brand | Liquid Glass + Glassmorphism | Black + Gold (#FFD700) + White | Elegant + Refined typography | Slow parallax + Premium reveals (400-600ms) | Cheap visuals + Fast animations |
| 34 | Restaurant/Food Service | Vibrant & Block-based + Motion-Driven | Warm colors (Orange Red Brown) | Appetizing + Clear typography | Food image reveal + Menu hover effects | Low-quality imagery + Outdated hours |
| 35 | Fitness/Gym App | Vibrant & Block-based + Dark Mode (OLED) | Energetic (Orange #FF6B35) + Dark bg | Bold + Motivational typography | Progress ring animations + Achievement unlocks | Static design + No gamification |
| 36 | Real Estate/Property | Glassmorphism + Minimalism | Trust Blue + Gold + White | Professional + Confident | 3D property tour zoom + Map hover | Poor photos + No virtual tours |
| 37 | Travel/Tourism Agency | Aurora UI + Motion-Driven | Vibrant destination + Sky Blue | Inspirational + Engaging | Destination parallax + Itinerary animations | Generic photos + Complex booking |
| 38 | Hotel/Hospitality | Liquid Glass + Minimalism | Warm neutrals + Gold (#D4AF37) | Elegant + Welcoming typography | Room gallery + Amenity reveals | Poor photos + Complex booking |
| 39 | Wedding/Event Planning | Soft UI Evolution + Aurora UI | Soft Pink (#FFD6E0) + Gold + Cream | Elegant + Romantic typography | Gallery reveals + Timeline animations | Generic templates + No portfolio |
| 40 | Legal Services | Trust & Authority + Minimalism | Navy Blue (#1E3A5F) + Gold + White | Professional + Authoritative typography | Practice area reveal + Attorney profile animations | Outdated design + Hidden credentials + AI purple/pink gradients |
| 41 | Insurance Platform | Trust & Authority + Flat Design | Trust Blue (#0066CC) + Green + Neutral | Clear + Professional typography | Quote calculator animations + Policy comparison | Confusing pricing + No trust signals + AI purple/pink gradients |
| 42 | Banking/Traditional Finance | Minimalism + Accessible & Ethical | Navy (#0A1628) + Trust Blue + Gold | Professional + Trustworthy typography | Smooth number animations + Security indicators | Playful design + Poor security UX + AI purple/pink gradients |
| 43 | Online Course/E-learning | Claymorphism + Vibrant & Block-based | Vibrant learning colors + Progress green | Friendly + Engaging typography | Progress bar animations + Certificate reveals | Boring design + No gamification |
| 44 | Non-profit/Charity | Accessible & Ethical + Organic Biophilic | Cause-related colors + Trust + Warm | Heartfelt + Readable typography | Impact counter animations + Story reveals | No impact data + Hidden financials |
| 45 | Music Streaming | Dark Mode (OLED) + Vibrant & Block-based | Dark (#121212) + Vibrant accents + Album art colors | Modern + Bold typography | Waveform visualization + Playlist animations | Cluttered layout + Poor audio player UX |
| 46 | Video Streaming/OTT | Dark Mode (OLED) + Motion-Driven | Dark bg + Poster colors + Brand accent | Bold + Engaging typography | Video player animations + Content carousel (parallax) | Static layout + Slow video player |
| 47 | Job Board/Recruitment | Flat Design + Minimalism | Professional Blue + Success Green + Neutral | Clear + Professional typography | Search/filter animations + Application flow | Outdated forms + Hidden filters |
| 48 | Marketplace (P2P) | Vibrant & Block-based + Flat Design | Trust colors + Category colors + Success green | Modern + Engaging typography | Review star animations + Listing hover effects | Low trust signals + Confusing layout |
| 49 | Logistics/Delivery | Minimalism + Flat Design | Blue (#2563EB) + Orange (tracking) + Green | Clear + Functional typography | Real-time tracking animation + Status pulse | Static tracking + No map integration + AI purple/pink gradients |
| 50 | Agriculture/Farm Tech | Organic Biophilic + Flat Design | Earth Green (#4A7C23) + Brown + Sky Blue | Clear + Informative typography | Data visualization + Weather animations | Generic design + Ignored accessibility + AI purple/pink gradients |
| 51 | Construction/Architecture | Minimalism + 3D & Hyperrealism | Grey (#4A4A4A) + Orange (safety) + Blueprint Blue | Professional + Bold typography | 3D model viewer + Timeline animations | 2D-only layouts + Poor image quality + AI purple/pink gradients |
| 52 | Automotive/Car Dealership | Motion-Driven + 3D & Hyperrealism | Brand colors + Metallic + Dark/Light | Bold + Confident typography | 360 product view + Configurator animations | Static product pages + Poor UX |
| 53 | Photography Studio | Motion-Driven + Minimalism | Black + White + Minimal accent | Elegant + Minimal typography | Full-bleed gallery + Before/after reveal | Heavy text + Poor image showcase |
| 54 | Coworking Space | Vibrant & Block-based + Glassmorphism | Energetic colors + Wood tones + Brand | Modern + Engaging typography | Space tour video + Amenity reveal animations | Outdated photos + Confusing layout |
| 55 | Home Services (Plumber/Electrician) | Flat Design + Trust & Authority | Trust Blue + Safety Orange + Grey | Professional + Clear typography | Emergency contact highlight + Service menu animations | Hidden contact info + No certifications |
| 56 | Childcare/Daycare | Claymorphism + Vibrant & Block-based | Playful pastels + Safe colors + Warm | Friendly + Playful typography | Parent portal animations + Activity gallery reveal | Generic design + Hidden safety info |
| 57 | Senior Care/Elderly | Accessible & Ethical + Soft UI Evolution | Calm Blue + Warm neutrals + Large text | Large + Clear typography (18px+) | Large touch targets + Clear navigation | Small text + Complex navigation + AI purple/pink gradients |
| 58 | Medical Clinic | Accessible & Ethical + Minimalism | Medical Blue (#0077B6) + Trust White | Professional + Readable typography | Online booking flow + Doctor profile reveals | Outdated interface + Confusing booking + AI purple/pink gradients |
| 59 | Pharmacy/Drug Store | Flat Design + Accessible & Ethical | Pharmacy Green + Trust Blue + Clean White | Clear + Functional typography | Prescription upload flow + Refill reminders | Confusing layout + Privacy concerns + AI purple/pink gradients |
| 60 | Dental Practice | Soft UI Evolution + Minimalism | Fresh Blue + White + Smile Yellow | Friendly + Professional typography | Before/after gallery + Patient testimonial carousel | Poor imagery + No testimonials |
| 61 | Veterinary Clinic | Claymorphism + Accessible & Ethical | Caring Blue + Pet colors + Warm | Friendly + Welcoming typography | Pet profile management + Service animations | Generic design + Hidden services |
| 62 | Florist/Plant Shop | Organic Biophilic + Vibrant & Block-based | Natural Green + Floral pinks/purples | Elegant + Natural typography | Product reveal + Seasonal transitions | Poor imagery + No seasonal content |
| 63 | Bakery/Cafe | Vibrant & Block-based + Soft UI Evolution | Warm Brown + Cream + Appetizing accents | Warm + Inviting typography | Menu hover + Order animations | Poor food photos + Hidden hours |
| 64 | Brewery/Winery | Motion-Driven + Storytelling-Driven | Deep amber/burgundy + Gold + Craft | Artisanal + Heritage typography | Tasting note reveals + Heritage timeline | Generic product pages + No story |
| 65 | Airline | Minimalism + Glassmorphism | Sky Blue + Brand colors + Trust | Clear + Professional typography | Flight search animations + Boarding pass reveals | Complex booking + Poor mobile |
| 66 | News/Media Platform | Minimalism + Flat Design | Brand colors + High contrast | Clear + Readable typography | Breaking news badge + Article reveal animations | Cluttered layout + Slow loading |
| 67 | Magazine/Blog | Swiss Modernism 2.0 + Motion-Driven | Editorial colors + Brand + Clean white | Editorial + Elegant typography | Article transitions + Category reveals | Poor typography + Slow loading |
| 68 | Freelancer Platform | Flat Design + Minimalism | Professional Blue + Success Green | Clear + Professional typography | Skill match animations + Review reveals | Poor profiles + No reviews |
| 69 | Marketing Agency | Brutalism + Motion-Driven | Bold brand colors + Creative freedom | Bold + Expressive typography | Portfolio reveals + Results animations | Boring design + Hidden work |
| 70 | Event Management | Vibrant & Block-based + Motion-Driven | Event theme colors + Excitement accents | Bold + Engaging typography | Countdown timer + Registration flow | Confusing registration + No countdown |
| 71 | Membership/Community | Vibrant & Block-based + Soft UI Evolution | Community brand colors + Engagement | Friendly + Engaging typography | Member counter + Benefit reveals | Hidden benefits + No community proof |
| 72 | Newsletter Platform | Minimalism + Flat Design | Brand primary + Clean white + CTA | Clean + Readable typography | Subscribe form + Archive reveals | Complex signup + No preview |
| 73 | Digital Products/Downloads | Vibrant & Block-based + Motion-Driven | Product colors + Brand + Success green | Modern + Clear typography | Product preview + Instant delivery animations | No preview + Slow delivery |
| 74 | Church/Religious Organization | Accessible & Ethical + Soft UI Evolution | Warm Gold + Deep Purple/Blue + White | Welcoming + Clear typography | Service time highlights + Event calendar | Outdated design + Hidden info |
| 75 | Sports Team/Club | Vibrant & Block-based + Motion-Driven | Team colors + Energetic accents | Bold + Impactful typography | Score animations + Schedule reveals | Static content + Poor fan engagement |
| 76 | Museum/Gallery | Minimalism + Motion-Driven | Art-appropriate neutrals + Exhibition accents | Elegant + Minimal typography | Virtual tour + Collection reveals | Cluttered layout + No online access |
| 77 | Theater/Cinema | Dark Mode (OLED) + Motion-Driven | Dark + Spotlight accents + Gold | Dramatic + Bold typography | Seat selection + Trailer reveals | Poor booking UX + No trailers |
| 78 | Language Learning App | Claymorphism + Vibrant & Block-based | Playful colors + Progress indicators | Friendly + Clear typography | Progress animations + Achievement unlocks | Boring design + No motivation |
| 79 | Coding Bootcamp | Dark Mode (OLED) + Minimalism | Code editor colors + Brand + Success | Technical + Clear typography | Terminal animations + Career outcome reveals | Light mode only + Hidden results |
| 80 | Cybersecurity Platform | Cyberpunk UI + Dark Mode (OLED) | Matrix Green (#00FF00) + Deep Black | Technical + Clear typography | Threat visualization + Alert animations | Light mode + Poor data viz |
| 81 | Developer Tool / IDE | Dark Mode (OLED) + Minimalism | Dark syntax theme + Blue focus | Monospace + Functional typography | Syntax highlighting + Command palette | Light mode default + Slow performance |
| 82 | Biotech / Life Sciences | Glassmorphism + Clean Science | Sterile White + DNA Blue + Life Green | Scientific + Clear typography | Data visualization + Research reveals | Cluttered data + Poor credibility |
| 83 | Space Tech / Aerospace | Holographic/HUD + Dark Mode | Deep Space Black + Star White + Metallic | Futuristic + Precise typography | Telemetry animations + 3D renders | Generic design + No immersion |
| 84 | Architecture / Interior | Exaggerated Minimalism + High Imagery | Monochrome + Gold Accent + High Imagery | Architectural + Elegant typography | Project gallery + Blueprint reveals | Poor imagery + Cluttered layout |
| 85 | Quantum Computing Interface | Holographic/HUD + Dark Mode | Quantum Blue (#00FFFF) + Deep Black | Futuristic + Scientific typography | Probability visualizations + Qubit state animations | Generic tech design + No viz |
| 86 | Biohacking / Longevity App | Biomimetic/Organic 2.0 + Minimalism | Cellular Pink/Red + DNA Blue + White | Scientific + Clear typography | Biological data viz + Progress animations | Generic health app + No privacy |
| 87 | Autonomous Drone Fleet Manager | HUD/Sci-Fi FUI + Real-Time | Tactical Green + Alert Red + Map Dark | Technical + Functional typography | Telemetry animations + 3D spatial awareness | Slow updates + Poor spatial viz |
| 88 | Generative Art Platform | Minimalism + Gen Z Chaos | Neutral (#F5F5F5) + User Content | Minimal + Content-focused typography | Gallery masonry + Minting animations | Heavy chrome + Slow loading |
| 89 | Spatial Computing OS / App | Spatial UI (VisionOS) + Glassmorphism | Frosted Glass + System Colors + Depth | Spatial + Readable typography | Depth hierarchy + Gaze interactions | 2D design + No spatial depth |
| 90 | Sustainable Energy / Climate Tech | Organic Biophilic + E-Ink/Paper | Earth Green + Sky Blue + Solar Yellow | Clear + Informative typography | Impact viz + Progress animations | Greenwashing + No real data |
| 91 | Personal Finance Tracker | Glassmorphism + Dark Mode (OLED) | Calm blue + success green + alert red + chart accents | Modern + Clear hierarchy | Backdrop blur (10-20px) + Translucent overlays | Pure white backgrounds |
| 92 | Chat & Messaging App | Minimalism + Micro-interactions | Brand primary + bubble contrast (sender/receiver) + typing grey | Professional + Clean hierarchy | Subtle hover 200ms + Smooth transitions + Clean | Excessive decoration |
| 93 | Notes & Writing App | Minimalism + Flat Design | Clean white/cream + minimal accent + editor syntax colors | Professional + Clean hierarchy | Color shift hover + Fast 150ms transitions + No shadows | Excessive decoration + Complex shadows + 3D effects |
| 94 | Habit Tracker | Claymorphism + Vibrant & Block-based | Streak warm (amber/orange) + progress green + motivational accents | Playful + Rounded + Friendly | Multi-layer shadows + Spring bounce + Soft press 200ms | Muted colors + Low energy |
| 95 | Food Delivery / On-Demand | Vibrant & Block-based + Motion-Driven | Appetizing warm (orange/red) + trust blue + map accent | Energetic + Bold + Large | Scroll animations + Parallax + Page transitions | Muted colors + Low energy |
| 96 | Ride Hailing / Transportation | Minimalism + Glassmorphism | Brand primary + map neutral + status indicator colors | Professional + Clean hierarchy | Backdrop blur (10-20px) + Translucent overlays | Excessive decoration |
| 97 | Recipe & Cooking App | Claymorphism + Vibrant & Block-based | Warm food tones (terracotta/sage/cream) + appetizing imagery | Playful + Rounded + Friendly | Multi-layer shadows + Spring bounce + Soft press 200ms | Muted colors + Low energy |
| 98 | Meditation & Mindfulness | Neumorphism + Soft UI Evolution | Ultra-calm pastels (lavender/sage/sky) + breathing animation gradient | Subtle + Soft + Monochromatic | Dual shadows (light+dark) + Soft press 150ms | Inconsistent styling + Poor contrast ratios |
| 99 | Weather App | Glassmorphism + Aurora UI | Atmospheric gradients (sky blue → sunset → storm grey) + temp scale | Modern + Clear hierarchy | Backdrop blur (10-20px) + Translucent overlays | Inconsistent styling + Poor contrast ratios |
| 100 | Diary & Journal App | Soft UI Evolution + Minimalism | Warm paper tones (cream/linen) + muted ink + mood-coded accents | Professional + Clean hierarchy | Subtle hover 200ms + Smooth transitions + Clean | Excessive decoration |
| 101 | CRM & Client Management | Flat Design + Minimalism | Professional blue + pipeline stage colors + closed-won green | Professional + Clean hierarchy | Color shift hover + Fast 150ms transitions + No shadows | Excessive decoration + Complex shadows + 3D effects |
| 102 | Inventory & Stock Management | Flat Design + Minimalism | Functional neutral + status traffic-light (green/amber/red) + scanner accent | Professional + Clean hierarchy | Color shift hover + Fast 150ms transitions + No shadows | Excessive decoration + Complex shadows + 3D effects |
| 103 | Flashcard & Study Tool | Claymorphism + Micro-interactions | Playful primary + correct green + incorrect red + progress blue | Playful + Rounded + Friendly | Multi-layer shadows + Spring bounce + Soft press 200ms | Inconsistent styling + Poor contrast ratios |
| 104 | Booking & Appointment App | Soft UI Evolution + Flat Design | Trust blue + available green + booked grey + confirm accent | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | Complex shadows + 3D effects |
| 105 | Invoice & Billing Tool | Minimalism + Flat Design | Professional navy + paid green + overdue red + neutral grey | Professional + Clean hierarchy | Color shift hover + Fast 150ms transitions + No shadows | Excessive decoration + Complex shadows + 3D effects |
| 106 | Grocery & Shopping List | Flat Design + Vibrant & Block-based | Fresh green + food-category colors + checkmark accent | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | Complex shadows + 3D effects + Muted colors + Low energy |
| 107 | Timer & Pomodoro | Minimalism + Neumorphism | High-contrast on dark + focus red/amber + break green | Professional + Clean hierarchy | Dual shadows (light+dark) + Soft press 150ms | Excessive decoration |
| 108 | Parenting & Baby Tracker | Claymorphism + Soft UI Evolution | Soft pastels (baby pink/sky blue/mint/peach) + warm accents | Playful + Rounded + Friendly | Multi-layer shadows + Spring bounce + Soft press 200ms | Inconsistent styling + Poor contrast ratios |
| 109 | Scanner & Document Manager | Minimalism + Flat Design | Clean white + camera viewfinder accent + file-type color coding | Professional + Clean hierarchy | Color shift hover + Fast 150ms transitions + No shadows | Excessive decoration + Complex shadows + 3D effects |
| 110 | Calendar & Scheduling App | Flat Design + Micro-interactions | Clean blue + event category accent colors + success green | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | Complex shadows + 3D effects |
| 111 | Password Manager | Minimalism + Accessible & Ethical | Trust blue + security green + dark neutral | Professional + Clean hierarchy | Subtle hover 200ms + Smooth transitions + Clean | Excessive decoration + Color-only indicators |
| 112 | Expense Splitter / Bill Split | Flat Design + Vibrant & Block-based | Success green + alert red + neutral grey + avatar accent colors | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | Complex shadows + 3D effects + Muted colors + Low energy |
| 113 | Voice Recorder & Memo | Minimalism + AI-Native UI | Clean white + recording red + waveform accent | Professional + Clean hierarchy | Subtle hover 200ms + Smooth transitions + Clean | Excessive decoration |
| 114 | Bookmark & Read-Later | Minimalism + Flat Design | Paper warm white + ink neutral + minimal accent + tag colors | Professional + Clean hierarchy | Color shift hover + Fast 150ms transitions + No shadows | Excessive decoration + Complex shadows + 3D effects |
| 115 | Translator App | Flat Design + AI-Native UI | Global blue + neutral grey + language flag accent | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | Complex shadows + 3D effects |
| 116 | Calculator & Unit Converter | Neumorphism + Minimalism | Dark functional + orange operation keys + clear button hierarchy | Professional + Clean hierarchy | Dual shadows (light+dark) + Soft press 150ms | Excessive decoration |
| 117 | Alarm & World Clock | Dark Mode (OLED) + Minimalism | Deep dark + ambient glow accent + timezone gradient | Professional + Clean hierarchy | Subtle glow + Neon accents + High contrast | Excessive decoration + Pure white backgrounds |
| 118 | File Manager & Transfer | Flat Design + Minimalism | Functional neutral + file type color coding (PDF orange, doc blue, image purple) | Professional + Clean hierarchy | Color shift hover + Fast 150ms transitions + No shadows | Excessive decoration + Complex shadows + 3D effects |
| 119 | Email Client | Flat Design + Minimalism | Clean white + brand primary + priority red + snooze amber | Professional + Clean hierarchy | Color shift hover + Fast 150ms transitions + No shadows | Excessive decoration + Complex shadows + 3D effects |
| 120 | Casual Puzzle Game | Claymorphism + Vibrant & Block-based | Cheerful pastels + progression gradient + reward gold + bright accent | Playful + Rounded + Friendly | Multi-layer shadows + Spring bounce + Soft press 200ms | Muted colors + Low energy |
| 121 | Trivia & Quiz Game | Vibrant & Block-based + Micro-interactions | Energetic blue + correct green + incorrect red + leaderboard gold | Energetic + Bold + Large | Haptic feedback + Small 50-100ms animations | Muted colors + Low energy |
| 122 | Card & Board Game | 3D & Hyperrealism + Flat Design | Game-theme felt green + dark wood + card back patterns | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | Complex shadows + 3D effects |
| 123 | Idle & Clicker Game | Vibrant & Block-based + Motion-Driven | Coin gold + upgrade blue + prestige purple + progress green | Energetic + Bold + Large | Scroll animations + Parallax + Page transitions | Muted colors + Low energy |
| 124 | Word & Crossword Game | Minimalism + Flat Design | Clean white + warm letter tiles + success green + shake red | Professional + Clean hierarchy | Color shift hover + Fast 150ms transitions + No shadows | Excessive decoration + Complex shadows + 3D effects |
| 125 | Arcade & Retro Game | Pixel Art + Retro-Futurism | Neon on black + pixel palette + score gold + danger red | Nostalgic + Monospace + Neon | Subtle hover (200ms) + Smooth transitions | Inconsistent styling + Poor contrast ratios |
| 126 | Photo Editor & Filters | Minimalism + Dark Mode (OLED) | Dark editor background + vibrant filter preview strip + tool icon accent | Professional + Clean hierarchy | Subtle glow + Neon accents + High contrast | Excessive decoration + Pure white backgrounds |
| 127 | Short Video Editor | Dark Mode (OLED) + Motion-Driven | Dark background + timeline track accent colors + effect preview vivid | High contrast + Light on dark | Subtle glow + Neon accents + High contrast | Pure white backgrounds |
| 128 | Drawing & Sketching Canvas | Minimalism + Dark Mode (OLED) | Neutral canvas + full-spectrum color picker + tool panel dark | Professional + Clean hierarchy | Subtle glow + Neon accents + High contrast | Excessive decoration + Pure white backgrounds |
| 129 | Music Creation & Beat Maker | Dark Mode (OLED) + Motion-Driven | Dark studio background + track colors rainbow + waveform accent + BPM pulse | High contrast + Light on dark | Subtle glow + Neon accents + High contrast | Pure white backgrounds |
| 130 | Meme & Sticker Maker | Vibrant & Block-based + Flat Design | Bold primary + comedic yellow + viral red + high saturation accent | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | Complex shadows + 3D effects + Muted colors + Low energy |
| 131 | AI Photo & Avatar Generator | AI-Native UI + Aurora UI | AI purple + aurora gradients + before/after neutral | Elegant + Gradient-friendly | Flowing gradients 8-12s + Color morphing | Inconsistent styling + Poor contrast ratios |
| 132 | Link-in-Bio Page Builder | Vibrant & Block-based + Bento Box Grid | Brand-customizable + accent link color + clean white canvas | Energetic + Bold + Large | Large section gaps 48px+ + Color shift hover + Scroll-snap | Muted colors + Low energy |
| 133 | Wardrobe & Outfit Planner | Minimalism + Motion-Driven | Clean fashion neutral + full clothes color palette + accent | Professional + Clean hierarchy | Subtle hover 200ms + Smooth transitions + Clean | Excessive decoration |
| 134 | Plant Care Tracker | Organic Biophilic + Soft UI Evolution | Nature greens + earth brown + sunny yellow reminder + water blue | Warm + Humanist + Natural | Rounded 16-24px + Natural shadows + Flowing SVG | Inconsistent styling + Poor contrast ratios |
| 135 | Book & Reading Tracker | Swiss Modernism 2.0 + Minimalism | Warm paper white + ink brown + reading progress green + book cover colors | Professional + Clean hierarchy | Subtle hover 200ms + Smooth transitions + Clean | Excessive decoration |
| 136 | Couple & Relationship App | Aurora UI + Soft UI Evolution | Warm romantic pink/rose + soft gradient + memory photo tones | Elegant + Gradient-friendly | Flowing gradients 8-12s + Color morphing | Inconsistent styling + Poor contrast ratios |
| 137 | Family Calendar & Chores | Flat Design + Claymorphism | Warm playful + member color coding + chore completion green | Playful + Rounded + Friendly | Multi-layer shadows + Spring bounce + Soft press 200ms | Complex shadows + 3D effects |
| 138 | Mood Tracker | Soft UI Evolution + Minimalism | Emotion gradient (blue sad to yellow happy) + pastel per mood + insight accent | Professional + Clean hierarchy | Subtle hover 200ms + Smooth transitions + Clean | Excessive decoration |
| 139 | Gift & Wishlist | Vibrant & Block-based + Soft UI Evolution | Celebration warm pink/gold/red + category colors + surprise accent | Energetic + Bold + Large | Large section gaps 48px+ + Color shift hover + Scroll-snap | Muted colors + Low energy |
| 140 | Running & Cycling GPS | Dark Mode (OLED) + Vibrant & Block-based | Energetic orange + map accent + pace zones (green/yellow/red) | High contrast + Light on dark | Subtle glow + Neon accents + High contrast | Pure white backgrounds + Muted colors + Low energy |
| 141 | Yoga & Stretching Guide | Organic Biophilic + Soft UI Evolution | Earth calming sage/terracotta/cream + breathing gradient + warm accent | Warm + Humanist + Natural | Rounded 16-24px + Natural shadows + Flowing SVG | Inconsistent styling + Poor contrast ratios |
| 142 | Sleep Tracker | Dark Mode (OLED) + Neumorphism | Deep midnight blue + stars/moon accent + sleep quality gradient (poor red to great green) | High contrast + Light on dark | Dual shadows (light+dark) + Soft press 150ms | Pure white backgrounds |
| 143 | Calorie & Nutrition Counter | Flat Design + Vibrant & Block-based | Healthy green + macro colors (protein blue, carb orange, fat yellow) + progress circle | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | Complex shadows + 3D effects + Muted colors + Low energy |
| 144 | Period & Cycle Tracker | Soft UI Evolution + Aurora UI | Rose/blush + lavender + fertility green + soft calendar tones | Elegant + Gradient-friendly | Flowing gradients 8-12s + Color morphing | Inconsistent styling + Poor contrast ratios |
| 145 | Medication & Pill Reminder | Accessible & Ethical + Flat Design | Medical trust blue + missed alert red + taken green + clean white | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | Complex shadows + 3D effects + Color-only indicators |
| 146 | Water & Hydration Reminder | Claymorphism + Vibrant & Block-based | Refreshing blue + water wave animation + goal progress accent | Playful + Rounded + Friendly | Multi-layer shadows + Spring bounce + Soft press 200ms | Muted colors + Low energy |
| 147 | Fasting & Intermittent Timer | Minimalism + Dark Mode (OLED) | Fasting deep blue/purple + eating window green + timeline neutral | Professional + Clean hierarchy | Subtle glow + Neon accents + High contrast | Excessive decoration + Pure white backgrounds |
| 148 | Anonymous Community / Confession | Dark Mode (OLED) + Minimalism | Dark protective + subtle gradient + upvote green + empathy warm accent | Professional + Clean hierarchy | Subtle glow + Neon accents + High contrast | Excessive decoration + Pure white backgrounds |
| 149 | Local Events & Discovery | Vibrant & Block-based + Motion-Driven | City vibrant + event category colors + map accent + date highlight | Energetic + Bold + Large | Scroll animations + Parallax + Page transitions | Muted colors + Low energy |
| 150 | Study Together / Virtual Coworking | Minimalism + Soft UI Evolution | Calm focus blue + session progress indicator + ambient warm neutrals | Professional + Clean hierarchy | Subtle hover 200ms + Smooth transitions + Clean | Excessive decoration |
| 151 | Coding Challenge & Practice | Dark Mode (OLED) + Cyberpunk UI | Code editor dark + success green + difficulty gradient (easy green / medium amber / hard red) | High contrast + Light on dark | Subtle glow + Neon accents + High contrast | Pure white backgrounds |
| 152 | Kids Learning (ABC & Math) | Claymorphism + Vibrant & Block-based | Bright primary + child-safe pastels + reward gold + interactive accent | Playful + Rounded + Friendly | Multi-layer shadows + Spring bounce + Soft press 200ms | Muted colors + Low energy |
| 153 | Music Instrument Learning | Vibrant & Block-based + Motion-Driven | Musical warm deep red/brown + note color system + skill progress bar | Energetic + Bold + Large | Scroll animations + Parallax + Page transitions | Muted colors + Low energy |
| 154 | Parking Finder | Minimalism + Glassmorphism | Trust blue + available green + occupied red + map neutral | Professional + Clean hierarchy | Backdrop blur (10-20px) + Translucent overlays | Excessive decoration |
| 155 | Public Transit Guide | Flat Design + Accessible & Ethical | Transit brand line colors + real-time indicator green/red + map neutral | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | Complex shadows + 3D effects + Color-only indicators |
| 156 | Road Trip Planner | Aurora UI + Organic Biophilic | Adventure warm sunset orange + map teal + stop markers + road neutral | Elegant + Gradient-friendly | Flowing gradients 8-12s + Color morphing | Inconsistent styling + Poor contrast ratios |
| 157 | VPN & Privacy Tool | Minimalism + Dark Mode (OLED) | Dark shield blue + connected green + disconnected red + trust accent | Professional + Clean hierarchy | Subtle glow + Neon accents + High contrast | Excessive decoration + Pure white backgrounds |
| 158 | Emergency SOS & Safety | Accessible & Ethical + Flat Design | Alert red + safety blue + location green + high contrast critical | Bold + Clean + Sans-serif | Color shift hover + Fast 150ms transitions + No shadows | Complex shadows + 3D effects + Color-only indicators |
| 159 | Wallpaper & Theme App | Vibrant & Block-based + Aurora UI | Content-driven + trending aesthetic palettes + download accent | Energetic + Bold + Large | Large section gaps 48px+ + Color shift hover + Scroll-snap | Muted colors + Low energy |
| 160 | White Noise & Ambient Sound | Minimalism + Dark Mode (OLED) | Calming dark + ambient texture visual + subtle sound wave + sleep blue | Professional + Clean hierarchy | Subtle glow + Neon accents + High contrast | Excessive decoration + Pure white backgrounds |
| 161 | Home Decoration & Interior Design | Minimalism + 3D Product Preview | Neutral interior palette + material texture accent + AR blue | Professional + Clean hierarchy | Subtle hover 200ms + Smooth transitions + Clean | Excessive decoration |

---

## Part 3 — Visual Style Prompt Keyword Library

> Each style entry contains ready-to-use AI Prompt Keywords — copy directly into your image prompt.

### Minimalism & Swiss Style *(type: General, era: 1950s Swiss)*

**Prompt Keywords:**  
> Design a minimalist landing page. Use: white space, geometric layouts, sans-serif fonts, high contrast, grid-based structure, essential elements only. Avoid shadows and gradients. Focus on clarity and functionality.

**Best for:** Enterprise apps, dashboards, documentation sites, SaaS platforms, professional tools  
**Avoid for:** Creative portfolios, entertainment, playful brands, artistic experiments

---

### Neumorphism *(type: General, era: 2020s Modern)*

**Prompt Keywords:**  
> Create a neumorphic UI with soft 3D effects. Use light pastels, rounded corners (12-16px), subtle soft shadows (multiple layers), no hard lines, monochromatic color scheme with light/dark variations. Embossed/debossed effect on interactive elements.

**Best for:** Health/wellness apps, meditation platforms, fitness trackers, minimal interaction UIs  
**Avoid for:** Complex apps, critical accessibility, data-heavy dashboards, high-contrast required

---

### Glassmorphism *(type: General, era: 2020s Modern)*

**Prompt Keywords:**  
> Design a glassmorphic interface with frosted glass effect. Use backdrop blur (10-20px), translucent overlays (rgba 10-30% opacity), vibrant background colors, subtle borders, light source reflection, layered depth. Perfect for modern overlays and cards.

**Best for:** Modern SaaS, financial dashboards, high-end corporate, lifestyle apps, modal overlays, navigation  
**Avoid for:** Low-contrast backgrounds, critical accessibility, performance-limited, dark text on dark

---

### Brutalism *(type: General, era: 1950s Brutalist)*

**Prompt Keywords:**  
> Create a brutalist design with raw, unpolished, stark aesthetic. Use pure primary colors (red, blue, yellow), black & white, no smooth transitions (instant), sharp corners, bold large typography, visible grid lines, default system fonts, intentional 'broken' design elements.

**Best for:** Design portfolios, artistic projects, counter-culture brands, editorial/media sites, tech blogs  
**Avoid for:** Corporate environments, conservative industries, critical accessibility, customer-facing professional

---

### 3D & Hyperrealism *(type: General, era: 2020s Modern)*

**Prompt Keywords:**  
> Build an immersive 3D interface using realistic textures, 3D models (Three.js/Babylon.js), complex shadows, realistic lighting, parallax scrolling (3-5 layers), physics-based motion. Include skeuomorphic elements with tactile detail.

**Best for:** Gaming, product showcase, immersive experiences, high-end e-commerce, architectural viz, VR/AR  
**Avoid for:** Low-end mobile, performance-limited, critical accessibility, data tables/forms

---

### Vibrant & Block-based *(type: General, era: 2020s Modern)*

**Prompt Keywords:**  
> Design an energetic, vibrant interface with bold block layouts, geometric shapes, high color contrast, large typography (32px+), animated background patterns, duotone effects. Perfect for startups and youth-focused apps. Use 4-6 contrasting colors from complementary/triadic schemes.

**Best for:** Startups, creative agencies, gaming, social media, youth-focused, entertainment, consumer  
**Avoid for:** Financial institutions, healthcare, formal business, government, conservative, elderly

---

### Dark Mode (OLED) *(type: General, era: 2020s Modern)*

**Prompt Keywords:**  
> Create an OLED-optimized dark interface with deep black (#000000), dark grey (#121212), midnight blue accents. Use minimal glow effects, vibrant neon accents (green, blue, gold, purple), high contrast text. Optimize for eye comfort and OLED power saving.

**Best for:** Night-mode apps, coding platforms, entertainment, eye-strain prevention, OLED devices, low-light  
**Avoid for:** Print-first content, high-brightness outdoor, color-accuracy-critical

---

### Accessible & Ethical *(type: General, era: Universal)*

**Prompt Keywords:**  
> Design with WCAG AAA compliance. Include: high contrast (7:1+), large text (16px+), keyboard navigation, screen reader compatibility, focus states visible (3-4px ring), semantic HTML, ARIA labels, skip links, reduced motion support (prefers-reduced-motion), 44x44px touch targets.

**Best for:** Government, healthcare, education, inclusive products, large audience, legal compliance, public  
**Avoid for:** None - accessibility universal

---

### Claymorphism *(type: General, era: 2020s Modern)*

**Prompt Keywords:**  
> Design a playful, toy-like interface with soft 3D, chunky elements, bubbly aesthetic, rounded edges (16-24px), thick borders (3-4px), double shadows (inner + outer), pastel colors, smooth animations. Perfect for children's apps and creative tools.

**Best for:** Educational apps, children's apps, SaaS platforms, creative tools, fun-focused, onboarding, casual games  
**Avoid for:** Formal corporate, professional services, data-critical, serious/medical, legal apps, finance

---

### Aurora UI *(type: General, era: 2020s Modern)*

**Prompt Keywords:**  
> Create a vibrant gradient interface inspired by Northern Lights with mesh gradients, smooth color blends, flowing animations. Use complementary color pairs (blue-orange, purple-yellow), flowing background gradients, subtle continuous animations (8-12s loops), iridescent effects.

**Best for:** Modern SaaS, creative agencies, branding, music platforms, lifestyle, premium products, hero sections  
**Avoid for:** Data-heavy dashboards, critical accessibility, content-heavy where distraction issues

---

### Retro-Futurism *(type: General, era: 1980s Retro)*

**Prompt Keywords:**  
> Build a retro-futuristic (cyberpunk/vaporwave) interface with neon colors (blue, pink, cyan), deep black background, 80s aesthetic, CRT scanlines, glitch effects, neon glow text/borders, monospace fonts, geometric patterns. Use neon text-shadow and animated glitch effects.

**Best for:** Gaming, entertainment, music platforms, tech brands, artistic projects, nostalgic, cyberpunk  
**Avoid for:** Conservative industries, critical accessibility, professional/corporate, elderly, legal/finance

---

### Flat Design *(type: General, era: 2010s Modern)*

**Prompt Keywords:**  
> Create a flat, 2D interface with bold colors, no shadows/gradients, clean lines, simple geometric shapes, icon-heavy, typography-focused, minimal ornamentation. Use 4-6 solid, bright colors in a limited palette with high saturation.

**Best for:** Web apps, mobile apps, cross-platform, startup MVPs, user-friendly, SaaS, dashboards, corporate  
**Avoid for:** Complex 3D, premium/luxury, artistic portfolios, immersive experiences, high-detail

---

### Skeuomorphism *(type: General, era: 2007-2012 iOS)*

**Prompt Keywords:**  
> Design a realistic, textured interface with 3D depth, real-world metaphors (leather, wood, metal), complex gradients (8-12 stops), realistic shadows, grain/texture overlays, tactile press animations. Perfect for premium/luxury products.

**Best for:** Legacy apps, gaming, immersive storytelling, premium products, luxury, realistic simulations, education  
**Avoid for:** Modern enterprise, critical accessibility, low-performance, web (use Flat/Modern)

---

### Liquid Glass *(type: General, era: 2020s Modern)*

**Prompt Keywords:**  
> Create a premium liquid glass effect with morphing shapes, flowing animations, chromatic aberration, iridescent gradients, smooth 400-600ms transitions. Use SVG morphing for shape changes, dynamic blur, smooth color transitions creating a fluid, premium feel.

**Best for:** Premium SaaS, high-end e-commerce, creative platforms, branding experiences, luxury portfolios  
**Avoid for:** Performance-limited, critical accessibility, complex data, budget projects

---

### Motion-Driven *(type: General, era: 2020s Modern)*

**Prompt Keywords:**  
> Build an animation-heavy interface with scroll-triggered animations, microinteractions, parallax scrolling (3-5 layers), smooth transitions (300-400ms), entrance animations, page transitions. Use Intersection Observer for scroll effects, transform for performance, GPU acceleration.

**Best for:** Portfolio sites, storytelling platforms, interactive experiences, entertainment apps, creative, SaaS  
**Avoid for:** Data dashboards, critical accessibility, low-power devices, content-heavy, motion-sensitive

---

### Micro-interactions *(type: General, era: 2020s Modern)*

**Prompt Keywords:**  
> Design with delightful micro-interactions: small 50-100ms animations, gesture-based responses, tactile feedback, loading spinners, success/error states, subtle hover effects, haptic feedback triggers for mobile. Focus on responsive, contextual interactions.

**Best for:** Mobile apps, touchscreen UIs, productivity tools, user-friendly, consumer apps, interactive components  
**Avoid for:** Desktop-only, critical performance, accessibility-first (alternatives needed)

---

### Inclusive Design *(type: General, era: Universal)*

**Prompt Keywords:**  
> Design for universal accessibility: high contrast (7:1+), large text (16px+), keyboard-only navigation, screen reader optimization, WCAG AAA compliance, symbol-based color indicators (not color-only), haptic feedback, voice interaction support, reduced motion options.

**Best for:** Public services, education, healthcare, finance, government, accessible consumer, inclusive  
**Avoid for:** None - accessibility universal

---

### Zero Interface *(type: General, era: 2020s AI-Era)*

**Prompt Keywords:**  
> Create a voice-first, gesture-based, AI-driven interface with minimal visible UI, progressive disclosure, voice recognition UI, gesture detection, AI predictions, smart suggestions, context-aware actions. Hide controls until needed.

**Best for:** Voice assistants, AI platforms, future-forward UX, smart home, contextual computing, ambient experiences  
**Avoid for:** Complex workflows, data-entry heavy, traditional systems, legacy support, explicit control

---

### Soft UI Evolution *(type: General, era: 2020s Modern)*

**Prompt Keywords:**  
> Design evolved neumorphism with improved contrast (WCAG AA+), modern aesthetics, subtle depth, accessibility focus. Use soft shadows (softer than flat but clearer than pure neumorphism), better color hierarchy, improved focus states, modern 200-300ms animations.

**Best for:** Modern enterprise apps, SaaS platforms, health/wellness, modern business tools, professional, hybrid  
**Avoid for:** Extreme minimalism, critical performance, systems without modern OS

---

### Hero-Centric Design *(type: Landing Page, era: 2020s Modern)*

**Prompt Keywords:**  
> Design a hero-centric landing page. Use: full-width hero section, compelling headline (60-80 chars), high-contrast CTA button, product screenshot or video, value proposition above fold, gradient or image background, clear visual hierarchy.

**Best for:** SaaS landing pages, product launches, service landing pages, B2B platforms, tech companies  
**Avoid for:** Complex navigation, multi-page experiences, data-heavy applications

---

### Conversion-Optimized *(type: Landing Page, era: 2020s Modern)*

**Prompt Keywords:**  
> Design a conversion-optimized landing page. Use: single primary CTA, minimal distractions, trust badges, urgency elements (limited time), social proof (testimonials), clear value proposition, form above fold, progress indicators.

**Best for:** E-commerce product pages, free trial signups, lead generation, SaaS pricing pages, limited-time offers  
**Avoid for:** Complex feature explanations, multi-product showcases, technical documentation

---

### Feature-Rich Showcase *(type: Landing Page, era: 2020s Modern)*

**Prompt Keywords:**  
> Design a feature showcase landing page. Use: grid layout for features (3-4 columns), feature cards with icons, benefit-focused copy, alternating sections, comparison tables, interactive demos, problem-solution pairs.

**Best for:** Enterprise SaaS, software tools landing pages, platform services, complex product explanations, B2B products  
**Avoid for:** Simple product pages, early-stage startups with few features, entertainment landing pages

---

### Minimal & Direct *(type: Landing Page, era: 2020s Modern)*

**Prompt Keywords:**  
> Design a minimal direct landing page. Use: single column layout, maximum white space, essential content only, one CTA, clean typography, no decorative elements, fast loading, direct messaging.

**Best for:** Simple service landing pages, indie products, consulting services, micro SaaS, freelancer portfolios  
**Avoid for:** Feature-heavy products, complex explanations, multi-product showcases

---

### Social Proof-Focused *(type: Landing Page, era: 2020s Modern)*

**Prompt Keywords:**  
> Design a social proof landing page. Use: testimonials with photos, client logos grid, case study cards, review ratings (stars), user count metrics, success stories, trust indicators, before/after comparisons.

**Best for:** B2B SaaS, professional services, premium products, e-commerce conversion pages, established brands  
**Avoid for:** Startup MVPs, products without users, niche/experimental products

---

### Interactive Product Demo *(type: Landing Page, era: 2020s Modern)*

**Prompt Keywords:**  
> Design an interactive demo landing page. Use: embedded product mockup, video walkthrough, step-by-step guide, hover-to-reveal features, live demo button, screenshot carousel, feature highlights on interaction.

**Best for:** SaaS platforms, tool/software products, productivity apps landing pages, developer tools, productivity software  
**Avoid for:** Simple services, consulting, non-digital products, complexity-averse audiences

---

### Trust & Authority *(type: Landing Page, era: 2020s Modern)*

**Prompt Keywords:**  
> Design a trust-focused landing page. Use: certification badges, security indicators, expert credentials, industry awards, case study metrics, compliance logos (GDPR, SOC2), guarantee badges, professional photography.

**Best for:** Healthcare/medical landing pages, financial services, enterprise software, premium/luxury products, legal services  
**Avoid for:** Casual products, entertainment, viral/social-first products

---

### Storytelling-Driven *(type: Landing Page, era: 2020s Modern)*

**Prompt Keywords:**  
> Design a storytelling landing page. Use: narrative flow sections, scroll-triggered reveals, chapter-like structure, emotional imagery, brand journey visualization, founder story, mission statement, timeline progression.

**Best for:** Brand/startup stories, mission-driven products, premium/lifestyle brands, documentary-style products, educational  
**Avoid for:** Technical/complex products (unless narrative-driven), traditional enterprise software

---

### Data-Dense Dashboard *(type: BI/Analytics, era: 2020s Modern)*

**Prompt Keywords:**  
> Design a data-dense dashboard. Use: multiple chart widgets, KPI cards row, data tables with sorting, minimal padding (8-12px), efficient grid layout, filter sidebar, dense but readable typography, maximum information density.

**Best for:** Business intelligence dashboards, financial analytics, enterprise reporting, operational dashboards, data warehousing  
**Avoid for:** Marketing dashboards, consumer-facing analytics, simple reporting

---

### Heat Map & Heatmap Style *(type: BI/Analytics, era: 2020s Modern)*

**Prompt Keywords:**  
> Design a heatmap visualization. Use: color gradient scale (cool to hot), cell-based grid, intensity legend, hover tooltips, geographic or matrix layout, divergent color scheme for +/- values, accessible color alternatives.

**Best for:** Geographical analysis, performance matrices, correlation analysis, user behavior heatmaps, temperature/intensity data  
**Avoid for:** Linear data representation, categorical comparisons (use bar charts), small datasets

---

### Executive Dashboard *(type: BI/Analytics, era: 2020s Modern)*

**Prompt Keywords:**  
> Design an executive dashboard. Use: large KPI cards (4-6 max), trend sparklines, high-level summary only, clean layout with white space, traffic light indicators (red/yellow/green), at-a-glance insights, minimal detail.

**Best for:** C-suite dashboards, business summary reports, decision-maker dashboards, strategic planning views  
**Avoid for:** Detailed analyst dashboards, technical deep-dives, operational monitoring

---

### Real-Time Monitoring *(type: BI/Analytics, era: 2020s Modern)*

**Prompt Keywords:**  
> Design a real-time monitoring dashboard. Use: live status indicators (pulsing), streaming charts, alert notifications, connection status, auto-refresh indicators, critical alerts prominent, system health overview.

**Best for:** System monitoring dashboards, DevOps dashboards, real-time analytics, stock market dashboards, live event tracking  
**Avoid for:** Historical analysis, long-term trend reports, archived data dashboards

---

### Drill-Down Analytics *(type: BI/Analytics, era: 2020s Modern)*

**Prompt Keywords:**  
> Design a drill-down analytics dashboard. Use: breadcrumb navigation, expandable sections, summary-to-detail flow, back button prominent, level indicators, context preservation, hierarchical data display.

**Best for:** Sales analytics, product analytics, funnel analysis, multi-dimensional data exploration, business intelligence  
**Avoid for:** Simple linear data, single-metric dashboards, streaming real-time dashboards

---

### Comparative Analysis Dashboard *(type: BI/Analytics, era: 2020s Modern)*

**Prompt Keywords:**  
> Design a comparison dashboard. Use: side-by-side metrics, period selectors (vs last month), delta indicators (+/-), benchmark lines, A/B comparison tables, winning/losing highlights, percentage change badges.

**Best for:** Period-over-period reporting, A/B test dashboards, market comparison, competitive analysis, regional performance  
**Avoid for:** Single metric dashboards, future projections (use forecasting), real-time only (no historical)

---

### Predictive Analytics *(type: BI/Analytics, era: 2020s Modern)*

**Prompt Keywords:**  
> Design a predictive analytics dashboard. Use: forecast lines (dashed), confidence intervals (shaded bands), trend projections, anomaly highlights, scenario toggles, AI insight cards, probability indicators.

**Best for:** Forecasting dashboards, anomaly detection systems, trend prediction dashboards, AI-powered analytics, budget planning  
**Avoid for:** Historical-only dashboards, simple reporting, real-time operational dashboards

---

### User Behavior Analytics *(type: BI/Analytics, era: 2020s Modern)*

**Prompt Keywords:**  
> Design a user behavior analytics dashboard. Use: funnel visualization, user flow diagrams (Sankey), conversion metrics, engagement heatmaps, cohort tables, retention curves, session replay indicators.

**Best for:** Conversion funnel analysis, user journey tracking, engagement analytics, cohort analysis, retention tracking  
**Avoid for:** Real-time operational metrics, technical system monitoring, financial transactions

---

### Financial Dashboard *(type: BI/Analytics, era: 2020s Modern)*

**Prompt Keywords:**  
> Design a financial dashboard. Use: revenue/expense charts, profit margins, budget vs actual, cash flow waterfall, financial ratios, audit trail table, currency formatting, period comparisons.

**Best for:** Financial reporting, accounting dashboards, portfolio tracking, budget monitoring, banking analytics  
**Avoid for:** Simple business dashboards, entertainment/social metrics, non-financial data

---

### Sales Intelligence Dashboard *(type: BI/Analytics, era: 2020s Modern)*

**Prompt Keywords:**  
> Design a sales intelligence dashboard. Use: pipeline funnel, deal cards (kanban), quota gauges, leaderboard table, territory map, win/loss ratios, forecast accuracy, activity timeline.

**Best for:** CRM dashboards, sales management, opportunity tracking, performance management, quota planning  
**Avoid for:** Marketing analytics, customer support metrics, HR dashboards

---

### Neubrutalism *(type: General, era: 2020s Modern)*

**Prompt Keywords:**  
> Design a neubrutalist interface. Use: high contrast, hard black borders (3px+), bright pop colors, no blur, sharp or slightly rounded corners, bold typography, hard shadows (offset 4px 4px), raw aesthetic but functional.

**Best for:** Gen Z brands, startups, creative agencies, Figma-style apps, Notion-style interfaces, tech blogs  
**Avoid for:** Luxury brands, finance, healthcare, conservative industries (too playful)

---

### Bento Box Grid *(type: General, era: 2020s Apple)*

**Prompt Keywords:**  
> Design a Bento Box grid layout. Use: modular cards with varied sizes (1x1, 2x1, 2x2), Apple-style aesthetic, rounded corners (16-24px), soft shadows, clean hierarchy, asymmetric grid, neutral backgrounds (#F5F5F7), hover effects.

**Best for:** Dashboards, product pages, portfolios, Apple-style marketing, feature showcases, SaaS  
**Avoid for:** Dense data tables, text-heavy content, real-time monitoring

---

### Y2K Aesthetic *(type: General, era: Y2K 2000s)*

**Prompt Keywords:**  
> Design a Y2K aesthetic interface. Use: neon pink/cyan colors, chrome/metallic textures, bubblegum gradients, glossy buttons, iridescent effects, 2000s futurism, star/sparkle decorations, bubble shapes, tech-optimistic vibe.

**Best for:** Fashion brands, music platforms, Gen Z brands, nostalgia marketing, entertainment, youth-focused  
**Avoid for:** B2B enterprise, healthcare, finance, conservative industries, elderly users

---

### Cyberpunk UI *(type: General, era: 2020s Cyberpunk)*

**Prompt Keywords:**  
> Design a cyberpunk interface. Use: neon colors on dark (#0D0D0D), terminal/HUD aesthetic, glitch effects, scanlines overlay, matrix green accents, monospace fonts, angular shapes, dystopian tech feel.

**Best for:** Gaming platforms, tech products, crypto apps, sci-fi applications, developer tools, entertainment  
**Avoid for:** Corporate enterprise, healthcare, family apps, conservative brands, elderly users

---

### Organic Biophilic *(type: General, era: 2020s Sustainable)*

**Prompt Keywords:**  
> Design a biophilic organic interface. Use: nature-inspired colors (greens, browns), organic curved shapes, rounded corners (16-24px), natural textures (wood, stone), flowing SVG elements, wellness aesthetic, earthy palette.

**Best for:** Wellness apps, sustainability brands, eco products, health apps, meditation, organic food brands  
**Avoid for:** Tech-focused products, gaming, industrial, urban brands

---

### AI-Native UI *(type: General, era: 2020s AI-Era)*

**Prompt Keywords:**  
> Design an AI-native interface. Use: minimal chrome, conversational layout, streaming text area, typing indicators (3-dot pulse), context cards, subtle AI accent color (#6366F1), clean input field, response bubbles.

**Best for:** AI products, chatbots, voice assistants, copilots, AI-powered tools, conversational interfaces  
**Avoid for:** Traditional forms, data-heavy dashboards, print-first content

---

### Memphis Design *(type: General, era: 1980s Postmodern)*

**Prompt Keywords:**  
> Design a Memphis style interface. Use: bold geometric shapes (triangles, squiggles, circles), bright clashing colors, 80s postmodern aesthetic, playful patterns, dotted textures, asymmetric layouts, decorative elements.

**Best for:** Creative agencies, music sites, youth brands, event promotion, artistic portfolios, entertainment  
**Avoid for:** Corporate finance, healthcare, legal, elderly users, conservative brands

---

### Vaporwave *(type: General, era: 1980s-90s Retro)*

**Prompt Keywords:**  
> Design a vaporwave aesthetic interface. Use: sunset gradients (pink/cyan/purple), 80s-90s nostalgia, glitch effects, Greek statue imagery, palm trees, grid patterns, neon glow, retro-futuristic feel, dreamy atmosphere.

**Best for:** Music platforms, gaming, creative portfolios, tech startups, entertainment, artistic projects  
**Avoid for:** Business apps, e-commerce, education, healthcare, enterprise software

---

### Dimensional Layering *(type: General, era: 2020s Modern)*

**Prompt Keywords:**  
> Design with dimensional layering. Use: z-index depth (multiple layers), overlapping cards, elevation shadows (4 levels), floating elements, parallax depth, backdrop blur for hierarchy, spatial UI feel.

**Best for:** Dashboards, card layouts, modals, navigation, product showcases, SaaS interfaces  
**Avoid for:** Print-style layouts, simple blogs, low-end devices, flat design requirements

---

### Exaggerated Minimalism *(type: General, era: 2020s Modern)*

**Prompt Keywords:**  
> Design with exaggerated minimalism. Use: oversized typography (clamp 3rem-12rem), extreme negative space, black/white primary, single accent color only, bold statements, minimal elements, dramatic contrast.

**Best for:** Fashion, architecture, portfolios, agency landing pages, luxury brands, editorial  
**Avoid for:** E-commerce catalogs, dashboards, forms, data-heavy, elderly users, complex apps

---

### Kinetic Typography *(type: General, era: 2020s Modern)*

**Prompt Keywords:**  
> Design with kinetic typography. Use: animated text, scroll-triggered reveals, typing effects, letter-by-letter animations, morphing text, gradient text fills, oversized hero text, text as the main visual element.

**Best for:** Hero sections, marketing sites, video platforms, storytelling, creative portfolios, landing pages  
**Avoid for:** Long-form content, accessibility-critical, data interfaces, forms, elderly users

---

### Parallax Storytelling *(type: General, era: 2020s Modern)*

**Prompt Keywords:**  
> Design a parallax storytelling page. Use: scroll-driven narrative, layered backgrounds (3-5 layers), fixed/sticky sections, cinematic transitions, progressive disclosure, full-screen chapters, depth perception.

**Best for:** Brand storytelling, product launches, case studies, portfolios, annual reports, marketing campaigns  
**Avoid for:** E-commerce, dashboards, mobile-first, SEO-critical, accessibility-required

---

### Swiss Modernism 2.0 *(type: General, era: 1950s Swiss + 2020s)*

**Prompt Keywords:**  
> Design with Swiss Modernism 2.0. Use: strict grid system (12 columns), Helvetica/Inter fonts, mathematical spacing, asymmetric balance, high contrast, minimal decoration, clean hierarchy, single accent color.

**Best for:** Corporate sites, architecture, editorial, SaaS, museums, professional services, documentation  
**Avoid for:** Playful brands, children's sites, entertainment, gaming, emotional storytelling

---

### HUD / Sci-Fi FUI *(type: General, era: 2010s Sci-Fi)*

**Prompt Keywords:**  
> Design a futuristic HUD (Heads Up Display) or FUI. Use: thin lines (1px), neon cyan/blue on black, technical markers, decorative brackets, data visualization, monospaced tech fonts, glowing elements, transparency.

**Best for:** Sci-fi games, space tech, cybersecurity, movie props, immersive dashboards  
**Avoid for:** Standard corporate, reading heavy content, accessible public services

---

### Pixel Art *(type: General, era: 1980s Arcade)*

**Prompt Keywords:**  
> Design a pixel art inspired interface. Use: pixelated fonts, 8-bit or 16-bit aesthetic, sharp edges (image-rendering: pixelated), limited color palette, blocky UI elements, retro gaming feel.

**Best for:** Indie games, retro tools, creative portfolios, nostalgia marketing, Web3/NFT  
**Avoid for:** Professional corporate, modern SaaS, high-res photography sites

---

### Bento Grids *(type: General, era: 2020s Apple/Linear)*

**Prompt Keywords:**  
> Design a Bento Grid layout. Use: modular grid system, rounded corners (16-24px), different card sizes (1x1, 2x1, 2x2), card-based hierarchy, soft backgrounds (#F5F5F7), subtle borders, content-first, Apple-style aesthetic.

**Best for:** Product features, dashboards, personal sites, marketing summaries, galleries  
**Avoid for:** Long-form reading, data tables, complex forms

---

### Spatial UI (VisionOS) *(type: General, era: 2024 Spatial Era)*

**Prompt Keywords:**  
> Design a VisionOS-style spatial interface. Use: frosted glass panels, depth layers, translucent backgrounds (15-30% opacity), vibrant colors for active states, gaze-hover effects, floating windows, immersive feel.

**Best for:** Spatial computing apps, VR/AR interfaces, immersive media, futuristic dashboards  
**Avoid for:** Text-heavy documents, high-contrast requirements, non-3D capable devices

---

### E-Ink / Paper *(type: General, era: 2020s Digital Well-being)*

**Prompt Keywords:**  
> Design an e-ink/paper style interface. Use: high contrast black on off-white, paper texture, no animations (instant transitions), reading-focused, minimal UI chrome, distraction-free, calm aesthetic, monochrome.

**Best for:** Reading apps, digital newspapers, minimal journals, distraction-free writing, slow-living brands  
**Avoid for:** Gaming, video platforms, high-energy marketing, dark mode dependent apps

---

### Gen Z Chaos / Maximalism *(type: General, era: 2023+ Internet Core)*

**Prompt Keywords:**  
> Design a Gen Z chaos maximalist interface. Use: clashing bright colors, sticker overlays, collage aesthetic, raw/unpolished feel, mixed media, ironic elements, loud typography, GIF-heavy, internet culture references.

**Best for:** Gen Z lifestyle brands, music artists, creative portfolios, viral marketing, fashion  
**Avoid for:** Corporate, government, healthcare, banking, serious tools

---

### Biomimetic / Organic 2.0 *(type: General, era: 2024+ Generative)*

**Prompt Keywords:**  
> Design a biomimetic organic interface. Use: cellular/fluid shapes, breathing animations, generative patterns, bioluminescent colors, physics-based movement, nature algorithms, life-like elements, flowing gradients.

**Best for:** Sustainability tech, biotech, advanced health, meditation, generative art platforms  
**Avoid for:** Standard SaaS, data grids, strict corporate, accounting

---

### Anti-Polish / Raw Aesthetic *(type: General, era: 2025+ Anti-Digital)*

**Prompt Keywords:**  
> Design with anti-polish raw aesthetic. Use: hand-drawn elements, scanned textures, unfinished look, paper/pencil textures, collage style, authentic imperfection, sketch marks, tape/sticker overlays, human touch.

**Best for:** Creative portfolios, artist sites, indie brands, handmade products, authentic storytelling, editorial  
**Avoid for:** Corporate enterprise, fintech, healthcare, government, polished SaaS

---

### Tactile Digital / Deformable UI *(type: General, era: 2025+ Tactile Era)*

**Prompt Keywords:**  
> Design a tactile deformable interface. Use: jelly/squishy buttons, press deformation effect, bounce-back animations, chrome/clay materials, spring physics, haptic-like feedback, material response, 3D depth on interaction.

**Best for:** Modern mobile apps, playful brands, entertainment, gaming UI, consumer products, interactive demos  
**Avoid for:** Enterprise software, data dashboards, accessibility-critical, professional tools

---

### Nature Distilled *(type: General, era: 2025+ Handmade Warmth)*

**Prompt Keywords:**  
> Design with nature distilled aesthetic. Use: muted earthy colors (terracotta, sand, olive), organic materials feel, warm tones, handmade warmth, natural textures, artisan quality, sustainable vibe, soft gradients.

**Best for:** Wellness brands, sustainable products, artisan goods, organic food, spa/beauty, home decor  
**Avoid for:** Tech startups, gaming, nightlife, corporate finance, high-energy brands

---

### Interactive Cursor Design *(type: General, era: 2025+ Interactive)*

**Prompt Keywords:**  
> Design with interactive cursor effects. Use: custom cursor, cursor morphing on hover, magnetic cursor pull, cursor trails, blend mode cursors, click feedback animations, cursor as interaction tool, pointer transformation.

**Best for:** Creative portfolios, interactive experiences, agency sites, product showcases, gaming, entertainment  
**Avoid for:** Mobile-first (no cursor), accessibility-critical, data-heavy dashboards, forms

---

### Voice-First Multimodal *(type: General, era: 2025+ Voice Era)*

**Prompt Keywords:**  
> Design a voice-first multimodal interface. Use: voice waveform visualization, listening state indicator, speaking animation, minimal visible UI, audio feedback cues, hands-free optimized, conversational flow, ambient design.

**Best for:** Voice assistants, accessibility apps, hands-free tools, smart home, automotive UI, cooking apps  
**Avoid for:** Visual-heavy content, data entry, complex forms, noisy environments

---

### 3D Product Preview *(type: General, era: 2025+ E-commerce 3D)*

**Prompt Keywords:**  
> Design a 3D product preview interface. Use: 360° rotation, drag-to-spin, pinch-to-zoom, AR preview button, material/color switcher, hotspot annotations, orbit controls, product configurator, smooth rendering.

**Best for:** E-commerce, furniture, fashion, automotive, electronics, jewelry, product configurators  
**Avoid for:** Content-heavy sites, blogs, dashboards, low-bandwidth, accessibility-critical

---

### Gradient Mesh / Aurora Evolved *(type: General, era: 2025+ Gradient Evolution)*

**Prompt Keywords:**  
> Design with gradient mesh aurora effect. Use: multi-color mesh gradients, flowing color transitions, aurora/northern lights feel, iridescent overlays, holographic shimmer, prismatic effects, smooth color morphing.

**Best for:** Hero sections, backgrounds, creative brands, music platforms, fashion, lifestyle, premium products  
**Avoid for:** Data interfaces, text-heavy content, accessibility-critical, conservative brands

---

### Editorial Grid / Magazine *(type: General, era: 2020s Editorial Digital)*

**Prompt Keywords:**  
> Design an editorial magazine layout. Use: asymmetric grid, pull quotes, drop caps, multi-column text, large imagery, bylines, section dividers, print-inspired typography, article hierarchy, white space balance.

**Best for:** News sites, blogs, magazines, editorial content, long-form articles, journalism, publishing  
**Avoid for:** Dashboards, apps, e-commerce catalogs, real-time data, short-form content

---

### Chromatic Aberration / RGB Split *(type: General, era: 2020s Retro-Tech)*

**Prompt Keywords:**  
> Design with chromatic aberration RGB split effect. Use: color channel offset (R/G/B), glitch aesthetic, retro tech feel, VHS error look, lens distortion, scan lines, noise overlay, analog imperfection.

**Best for:** Music platforms, gaming, tech brands, creative portfolios, nightlife, entertainment, video platforms  
**Avoid for:** Corporate, healthcare, finance, accessibility-critical, elderly users

---

### Vintage Analog / Retro Film *(type: General, era: 1970s-90s Analog Revival)*

**Prompt Keywords:**  
> Design with vintage analog film aesthetic. Use: film grain overlay, faded/desaturated colors, warm sepia tones, light leaks, VHS tracking effect, polaroid frame, analog warmth, nostalgic photography feel.

**Best for:** Photography portfolios, music/vinyl brands, vintage fashion, nostalgia marketing, film industry, cafes  
**Avoid for:** Modern tech, SaaS, healthcare, children's apps, corporate enterprise

---

### Bauhaus (包豪斯) *(type: Mobile, era: 1919 Bauhaus Movement)*

**Prompt Keywords:**  
> Design a Bauhaus mobile app. Use strict geometric shapes (circles and squares only), primary color blocking (Red #D02020, Blue #1040C0, Yellow #F0C020), hard 4px offset black shadows, OFF-WHITE canvas (#F0F0F0), massive bold uppercase headlines (Outfit Black 900), rectangular full-width buttons with mechanical press animation. No gradients. No rounded cards. No soft transitions.

**Best for:** Mobile-first apps needing high personality, onboarding flows, branding-forward product screens, artisan/design brands, editorial mobile experiences  
**Avoid for:** Enterprise dashboards, accessibility-critical contexts (requires extra a11y work), data-heavy screens, conservative industries

---

### Minimalist Monochrome *(type: Mobile, era: 2020s Editorial Mobile)*

**Prompt Keywords:**  
> Design a minimalist monochrome mobile app. Use ONLY black (#000000) and white (#FFFFFF). Zero border-radius on every element. No shadows — depth is created by 1–4px black borders and color inversion only. Typography is the primary visual: Playfair Display for heroes (text-5xl–text-6xl, tracking-tighter, leading-[0.9]), Source Serif 4 for body, JetBrains Mono for labels/tags. Tap states instantly invert (bg-black text-white). Full-width horizontal rules separate sections. Use the word 'MENU' instead of hamburger icon.

**Best for:** Luxury fashion e-commerce mobile, editorial publications, high-end portfolio apps, experimental/avant-garde brands, digital exhibitions  
**Avoid for:** Entertainment, colorful brands, friendly consumer apps, anything requiring visual warmth or gradient

---

### Modern Dark (Cinema Mobile) *(type: Mobile, era: 2020s Cinematic Mobile)*

**Prompt Keywords:**  
> Design a cinematic dark mobile app. Background: LinearGradient from #0a0a0f (top) to #020203 (bottom). Add 2–3 absolute animated 'blob' views: circular, blurRadius 30–50, opacity 0.08–0.12, slow Reanimated oscillation. Cards: borderRadius 16, border rgba(255,255,255,0.08) hairline, subtle top-edge shine gradient. Primary button: #5E6AD2, scale press 0.97, haptic on press. BlurView (intensity 20, tint dark) for tab bar and headers. Typography: Inter 700 for headers, 400 for body. Never use pure #000000. Accent glow: rgba(94,106,210,0.2) behind primary actions.

**Best for:** Developer tools, pro productivity apps, fintech/trading dashboards, media/streaming platforms, AI tool interfaces, high-end gaming companion apps  
**Avoid for:** Consumer apps needing warmth, children's apps, health/medical contexts where dark feels harsh, high-accessibility contexts needing maximum contrast

---

### SaaS Mobile (High-Tech Boutique) *(type: Mobile, era: 2020s SaaS Mobile)*

**Prompt Keywords:**  
> Design a high-tech boutique SaaS mobile app. Primary canvas: #FAFAFA (warm off-white). Cards: #FFFFFF with 1pt Slate-200 border, iOS shadow (shadowOpacity:0.1, shadowRadius:10, offset y:4), Android elevation:4, padding 24px, borderRadius 16. Buttons: LinearGradient #0052FF→#4D7CFF, height 56px, borderRadius 16, scale press 0.96 + haptic. Section badges: rounded pill with rgba(0,82,255,0.05) bg and rgba(0,82,255,0.2) border + PulseDot + JetBrains Mono text. Typography: Calistoga for heroes (36–42pt), Inter for body (16–18pt), JetBrains Mono for data labels. All screen transitions: spring (mass:1 damping:15 stiffness:120). Always include SafeAreaView.

**Best for:** B2B SaaS mobile dashboards, fintech apps, developer tool mobile companions, marketing analytics apps, HR/operations apps, modern business productivity  
**Avoid for:** Pure consumer entertainment, children's apps, highly decorative lifestyle apps, contexts where Electric Blue feels too corporate

---

### Terminal CLI (Mobile) *(type: Mobile, era: Retro-Future 1980s–2020s)*

**Prompt Keywords:**  
> Design a Mobile Terminal CLI app. Background: #050505 OLED black. ALL text in Matrix Green #33FF00. Font: JetBrains Mono or SpaceMono ONLY — zero border-radius everywhere. ASCII borders using +, -, ｜, * characters instead of standard containers. Buttons displayed as [ EXECUTE ] or > PROCEED. On press: instantly inverts to green bg + black text + haptic. Cursor: blinking View opacity 0→1 at 500ms. Show boot sequence on launch (fake log scroll). Progress bars as [#####-----] text. Status bar footer: [BATTERY:88%] [NET:CONNECTED]. Scanline overlay: absolute View with repeating 1px horizontal lines at opacity 0.05. Typewriter effect on new data.

**Best for:** Developer tools, Web3/blockchain apps, geek-culture apps, ARG games, sci-fi/noir gaming companions, hacker/security tools, creative studio portfolios  
**Avoid for:** Consumer products, health apps, anything requiring approachability or warmth, children's apps, standard enterprise contexts

---

### Kinetic Brutalism (Mobile) *(type: Mobile, era: 2020s Mobile Brutalism)*

**Prompt Keywords:**  
> Design a Kinetic Brutalism mobile app. Canvas: #09090B. Primary accent: Acid Yellow #DFE104 (text: #000000). Typography: Space Grotesk BOLD. Display text: 60–120pt, uppercase, letterSpacing -1, lineHeight 0.9–1.1x. Body: 18–20pt. Labels: 12pt uppercase letterSpacing +2. Add infinite marquee rows (Reanimated, no easing, hard edge clip). Hero text parallax on scroll (Interpolate: scale 1.0→1.3, opacity 1→0). Card press: instantly flood to #DFE104 + flip text to #000. Haptic Medium on every press. 0px radius. 2px solid borders. NO shadows. No gradients. Scale all fonts by (windowWidth / 375 * size) for responsiveness.

**Best for:** Immersive storytelling apps, brand flagship mobile, music/culture platforms, sports apps, underground zines, limited-edition product drops, performance dashboards  
**Avoid for:** Calm informational apps, healthcare, finance contexts needing trust, children's, any context where aggressive typography feels inappropriate

---

### Flat Design Mobile (Touch-First) *(type: Mobile, era: 2010s–2020s Flat Mobile)*

**Prompt Keywords:**  
> Design a Flat Mobile app. NO shadows (shadowOpacity: 0, elevation: 0). Color creates all hierarchy. Sections: full-width View blocks alternating contrasting bg colors (Blue Hero → White Content → Gray Block). Buttons: solid #3B82F6, borderRadius 8, height 56. Cards: backgroundColor #FFFFFF (on gray bg) or #DBEAFE (blue tint) — no shadow. Text: fontWeight 800 letterSpacing -0.5 (heads), 600 (sub), 400 (body). Inputs: #F3F4F6 bg, focused: borderWidth 2 borderColor #3B82F6. Icons: Lucide strokeWidth 2.5 inside solid colored square/circle. Press feedback: scale 0.97 Pressable. Use position absolute low-opacity geometric shapes (circles, rotated squares) as background decoration.

**Best for:** Cross-platform apps (iOS+Android parity), information-dense dashboards, system UI, brand illustration, onboarding flows, marketing pages, icon design  
**Avoid for:** Ultra-premium contexts needing depth/shadow, dark-mode-first products, contexts where flat design reads as unfinished or sterile

---

### Material You (MD3 Mobile) *(type: Mobile, era: Material Design 3)*

**Prompt Keywords:**  
> Design a Material You (MD3) mobile app. Use #FFFBFE background, #6750A4 primary, #E8DEF8 secondary container, #F3EDF7 surface container. All interactive elements are pill-shaped (borderRadius: 999). Buttons use Pressable with scale: 0.95 on press and state-layer overlays (black 10% or primary 12%). Inputs use filled M3 style: background #E7E0EC with floating label animation on focus. Elevation is tonal (layering containers) plus light shadow/elevation on Android. Animations use emphasized easing (0.2,0,0,1) at 100–400ms. FABs are tertiary-colored rounded squares/circles with level 3 elevation.

**Best for:** Android ecosystem apps, cross-platform productivity tools, MD3-based admin panels, data-heavy back-office UI with Material UI  
**Avoid for:** Ultra-minimal brutalist brands, terminal/hacker aesthetics, monochrome editorial apps

---

### Neo Brutalism (Mobile) *(type: Mobile, era: 2020s Neo-Brutalism)*

**Prompt Keywords:**  
> Design a Mobile Neo-Brutalist app. Background: Cream #FFFDF5. All content blocks: white or violet with borderWidth 4 borderColor #000. Shadows are solid offset blocks (no blur) using an extra View behind offset by 4px or 8px. Typography: Space Grotesk Bold/Black only (700–900). Buttons: 56px tall, 4px border, 0 radius; press animation translates button to cover the shadow. Cards slightly rotated (-1deg, 2deg). Colors: Hot Red #FF6B6B for primary, Yellow #FFD93D for focus/badges, Soft Violet #C4B5FD as tertiary. Animation: spring/linear only, no ease-out luxury motion.

**Best for:** Creative tools, collab platforms, Gen Z marketing & e-commerce, portfolio sites, sticker-book style content apps  
**Avoid for:** Serious enterprise apps, conservative industries, sober fintech, accessibility-first contexts (must tune contrast)

---

### Bold Typography (Mobile Poster) *(type: Mobile, era: Editorial 2020s)*

**Prompt Keywords:**  
> Design a Bold Typography mobile screen. Background #0A0A0A, text #FAFAFA, accent #FF3D00. Use Inter Tight/Inter 600+ for all type; JetBrains Mono for labels. Headline: 56–72px, tracking -1.5, lineHeight 1.1, full-bleed width with slight bleed off-screen. Body: 16–18px, leading 1.6. Buttons: underline CTA (accent text + 2px underline block), or inverted box with 0 radius. No shadows, no rounded corners. Layout: single column, paddingHorizontal 24, vertical gaps 64 between sections. Animation: 200ms, Easing.bezier(0.25,0,0,1), slight slide-up 10px + fade on mount.

**Best for:** Creative brand heroes, reading-focused apps, event/exhibition pages, editorial mobile experiences, landing hero sections  
**Avoid for:** Utility dashboards, kids apps, playful consumer products, contexts needing many icons or heavy imagery

---

### Academia (Scholarly Mobile) *(type: Mobile, era: Timeless Scholarly)*

**Prompt Keywords:**  
> Design a Scholarly Academia mobile app. Background #1C1714 (mahogany), alt surfaces #251E19 (oak), text #E8DFD4 (parchment). Accent brass #C9A962 for CTAs + borders; crimson #8B2635 for wax seals. Typography: Cormorant Garamond (headings), Crimson Pro (body), Cinzel (labels/overlines). Use arch-top hero containers (borderTopRadius 100). Cards: oak bg, 1px wood-grain border. Inputs: worn-leather background, brass focus border. Global vignette overlay and ornate brass dividers (Unicode glyph + gradient line). Animations: no spring, only Timing with Easing.out(Easing.poly(4)).

**Best for:** Knowledge management apps, deep reading tools, ritual-heavy personal brands, lore-heavy RPG/roleplay apps, culture-specific community platforms  
**Avoid for:** Hyper-modern tech dashboards, neon/glassmorphism, playful Gen Z branding

---

### Cyberpunk Mobile HUD *(type: Mobile, era: Cyber-Noir)*

**Prompt Keywords:**  
> Design a Cyberpunk mobile HUD. Background #0A0A0F, card #12121A. Accents: #00FF88 (primary), #FF00FF, #00D4FF. Typography: Orbitron for headings, JetBrains Mono for data. All shapes use chamfered corners via SVG or Skia clipPath. Buttons: neon glow shadows, scale 0.98 + haptic on press, optional glitch jitter on active. Global scanline overlay (semi-transparent horizontal lines) and CRT flicker (root opacity 0.98–1). Inputs: prompt style with '>' in accent, custom blinking block cursor. HUD cards use corner brackets and subtle gradients.

**Best for:** Gaming dashboards, crypto/cyberpunk apps, sci-fi companion tools, hacker OS skins, data-heavy monitoring HUDs  
**Avoid for:** Serious enterprise, health/finance requiring calm trust, minimal editorial apps

---

### Bitcoin DeFi (Mobile) *(type: Mobile, era: Fintech/Web3)*

**Prompt Keywords:**  
> Design a Bitcoin DeFi mobile app. Background #030304, cards #0F1115, text #FFFFFF, muted #94A3B8. Primary CTA: LinearGradient #EA580C→#F7931A with orange glow shadow. Typography: Space Grotesk Bold for headings, Inter for body, JetBrains Mono for prices/hashes. Use BlurView (intensity 20) for nav bars and floating panels. Cards as 'blocks' with hairline borders and light orange glow on active. Use grid background (low-opacity 50px grid). Gradient text for key balances via MaskedView and LinearGradient orange→gold. Status indicators pulse using Reanimated. Ledger timelines drawn as vertical gradient line with pulsing dots.

**Best for:** DeFi dashboards, wallets, NFT marketplaces, Web3 social, metaverse utilities, high-tech fintech brands  
**Avoid for:** Playful casual apps, low-tech brands, ultra-minimal editorial apps

---

### Claymorphism (Mobile) *(type: Mobile, era: Consumer/Education)*

**Prompt Keywords:**  
> Design a high-fidelity Claymorphism mobile app. Background #F4F1FA (cool lavender-white, never pure white). Primary CTA: LinearGradient #A78BFA to #7C3AED, borderRadius 20, height 56. Cards: borderRadius 32, backgroundColor rgba(255,255,255,0.7) with BlurView. Multi-layer shadow: outer offset(12,12) rgba(160,150,180,0.2) + highlight offset(-8,-8) white. Typography: Nunito Black 900 for headings (48px hero, 32px section, 22px card), DM Sans Medium 500 for body 16px. Spring animations: scale 0.92 on press, spring back damping 10. Background blobs drift ±20px over 8–10s. Bento 2-column grid with hero card spanning full width. Haptics.impactAsync Light on every button press.

**Best for:** Children education apps, teen social products, crypto gamification, creative tools, brand mascot-led apps  
**Avoid for:** Serious enterprise, high-density data, editorial reading apps, fintech trust signals

---

### Enterprise SaaS (Mobile) *(type: Mobile, era: Enterprise/SaaS)*

**Prompt Keywords:**  
> Design a Modern Enterprise SaaS mobile app. Background #F8FAFC, surfaces #FFFFFF, primary #4F46E5 (Indigo), secondary #7C3AED (Violet). Typography: Plus Jakarta Sans, ExtraBold 800 for screen titles, Bold 700 for section headers, SemiBold 600 for buttons, Regular 400 for body. Line height 1.1–1.2 for titles, 1.4–1.5 for body. Primary button: full-width, LinearGradient Indigo→Violet, pill-shaped or radius 12, scale 0.95 on press with medium haptic. Cards: white bg, 16pt radius, hairline border, shadow rgba(79,70,229,0.08). Inputs: white bg, 8pt radius, floating label, Indigo border on focus. Bottom Tab Navigation (3–5 items), gradient active tab icon. Screen padding 16–20pt. Vertical rhythm 24pt between sections, 12pt between items. Shared Element Transition for hero cards opening to detail.

**Best for:** B2B backend management, productivity tools, government and finance mobile apps, SaaS companion apps, enterprise dashboards  
**Avoid for:** Pure consumer entertainment, Gen-Z youth apps, gaming UI, ultra-minimal editorial

---

### Sketch Hand-Drawn (Mobile) *(type: Mobile, era: Creative/Education)*

**Prompt Keywords:**  
> Design a Hand-Drawn (Sketch) mobile app. Background #FDFBF7 (warm paper texture). Typography: Kalam Bold for headings (high weight, felt-tip style), PatrickHand Regular for body (human but legible). Colors: Pencil Black #2D2D2D for all text and borders, Red Marker #FF4D4D for accents, Blue Ballpoint #2D5DA1for input focus. Cards: white background, wobbly corner radii (e.g., 15/25/20/10), borderWidth 3, rotate -1deg or +1deg. Hard offset shadow implemented as a second View behind the card offset 4px right and 4px down. Buttons: Post-it yellow #FFF9C4 for primary CTA, press state shifts the button (translateX 4, translateY 4) to cover the shadow. Inputs: PatrickHand font, wobbly border, focus changes to Blue Ballpoint. Add absolute SVG tape and tack decorations. Error: jiggle animation -2deg to +2deg. All touch targets minimum 48x48.

**Best for:** Low-fidelity prototyping, creative brands, children/picturebook apps, education tools, journaling apps, gamified puzzles  
**Avoid for:** Enterprise dashboards, high-density data tables, fintech precision tools, medical or legal apps

---

### Neumorphism (Mobile) *(type: Mobile, era: Tools/Lifestyle)*

**Prompt Keywords:**  
> Design a Neumorphism (Soft UI) mobile app. Entire background is a single color #E0E5EC (Cool Clay). No other background colors. Dual shadows: outer dark shadowColor rgba(163,177,198,0.7) offset(6,6) radius 10 + outer light #FFFFFF offset(-6,-6) radius 10 using nested View or react-native-shadow-2. Extruded (convex) for resting buttons and cards. Inset (concave) for inputs and pressed states. Buttons: height 56, borderRadius 16, scale 0.97 on press with shadow opacity→0.4, Haptics.impactAsync Light. Cards: padding 24, borderRadius 32, nested inner icon container uses inset style. Inputs: height 50, borderRadius 16, backgroundColor #E0E5EC (NOT white), inset depth effect, focus borderColor #6C63FF width 1.5. Typography: Plus Jakarta Sans Bold or System. Heading 24–32pt, body 16pt, caption 12pt, letterSpacing -0.5 for headings. Animation: 250ms Bezier(0.4,0,0.2,1). No black shadows, no pure white backgrounds.

**Best for:** Minimal hardware controls, smart home apps, aesthetic utility tools, health monitors, brand showcase pages  
**Avoid for:** High-density data, bright multi-color apps, apps needing strong visual hierarchy via color, dark-mode-only products

---


---

## Part 4 — Industry Color Palette Reference

> Each row shows the Primary / Accent / Background HEX values paired with their fixed natural-language description.
> Use the **Palette Description** column directly in your image prompt.

| # | Industry | Primary | Accent | Background | Palette Description |
|---|---|---|---|---|---|
| 1 | SaaS (General) | `#2563EB` | `#EA580C` | `#F8FAFC` | Trust blue + orange CTA contrast |
| 2 | Micro SaaS | `#6366F1` | `#059669` | `#F5F3FF` | Indigo primary + emerald CTA |
| 3 | E-commerce | `#059669` | `#EA580C` | `#ECFDF5` | Success green + urgency orange |
| 4 | E-commerce Luxury | `#1C1917` | `#A16207` | `#FAFAF9` | Premium dark + gold accent |
| 5 | B2B Service | `#0F172A` | `#0369A1` | `#F8FAFC` | Professional navy + blue CTA |
| 6 | Financial Dashboard | `#0F172A` | `#22C55E` | `#020617` | Dark bg + green positive indicators |
| 7 | Analytics Dashboard | `#1E40AF` | `#D97706` | `#F8FAFC` | Blue data + amber highlights |
| 8 | Healthcare App | `#0891B2` | `#059669` | `#ECFEFF` | Calm cyan + health green |
| 9 | Educational App | `#4F46E5` | `#EA580C` | `#EEF2FF` | Playful indigo + energetic orange |
| 10 | Creative Agency | `#EC4899` | `#0891B2` | `#FDF2F8` | Bold pink + cyan accent |
| 11 | Portfolio/Personal | `#18181B` | `#2563EB` | `#FAFAFA` | Monochrome + blue accent |
| 12 | Gaming | `#7C3AED` | `#F43F5E` | `#0F0F23` | Neon purple + rose action |
| 13 | Government/Public Service | `#0F172A` | `#0369A1` | `#F8FAFC` | High contrast navy + blue |
| 14 | Fintech/Crypto | `#F59E0B` | `#8B5CF6` | `#0F172A` | Gold trust + purple tech |
| 15 | Social Media App | `#E11D48` | `#2563EB` | `#FFF1F2` | Vibrant rose + engagement blue |
| 16 | Productivity Tool | `#0D9488` | `#EA580C` | `#F0FDFA` | Teal focus + action orange |
| 17 | Design System/Component Library | `#4F46E5` | `#EA580C` | `#EEF2FF` | Indigo brand + doc hierarchy |
| 18 | AI/Chatbot Platform | `#7C3AED` | `#0891B2` | `#FAF5FF` | AI purple + cyan interactions |
| 19 | NFT/Web3 Platform | `#8B5CF6` | `#FBBF24` | `#0F0F23` | Purple tech + gold value |
| 20 | Creator Economy Platform | `#EC4899` | `#EA580C` | `#FDF2F8` | Creator pink + engagement orange |
| 21 | Remote Work/Collaboration Tool | `#6366F1` | `#059669` | `#F5F3FF` | Calm indigo + success green |
| 22 | Mental Health App | `#8B5CF6` | `#059669` | `#FAF5FF` | Calming lavender + wellness green |
| 23 | Pet Tech App | `#F97316` | `#2563EB` | `#FFF7ED` | Playful orange + trust blue |
| 24 | Smart Home/IoT Dashboard | `#1E293B` | `#22C55E` | `#0F172A` | Dark tech + status green |
| 25 | EV/Charging Ecosystem | `#0891B2` | `#16A34A` | `#ECFEFF` | Electric cyan + eco green |
| 26 | Subscription Box Service | `#D946EF` | `#EA580C` | `#FDF4FF` | Excitement purple + urgency orange |
| 27 | Podcast Platform | `#1E1B4B` | `#F97316` | `#0F0F23` | Dark audio + warm accent |
| 28 | Dating App | `#E11D48` | `#EA580C` | `#FFF1F2` | Romantic rose + warm orange |
| 29 | Micro-Credentials/Badges Platform | `#0369A1` | `#A16207` | `#F0F9FF` | Trust blue + achievement gold |
| 30 | Knowledge Base/Documentation | `#475569` | `#2563EB` | `#F8FAFC` | Neutral grey + link blue |
| 31 | Hyperlocal Services | `#059669` | `#EA580C` | `#ECFDF5` | Location green + action orange |
| 32 | Beauty/Spa/Wellness Service | `#EC4899` | `#8B5CF6` | `#FDF2F8` | Soft pink + lavender luxury |
| 33 | Luxury/Premium Brand | `#1C1917` | `#A16207` | `#FAFAF9` | Premium black + gold accent |
| 34 | Restaurant/Food Service | `#DC2626` | `#A16207` | `#FEF2F2` | Appetizing red + warm gold |
| 35 | Fitness/Gym App | `#F97316` | `#22C55E` | `#1F2937` | Energy orange + success green |
| 36 | Real Estate/Property | `#0F766E` | `#0369A1` | `#F0FDFA` | Trust teal + professional blue |
| 37 | Travel/Tourism Agency | `#0EA5E9` | `#EA580C` | `#F0F9FF` | Sky blue + adventure orange |
| 38 | Hotel/Hospitality | `#1E3A8A` | `#A16207` | `#F8FAFC` | Luxury navy + gold service |
| 39 | Wedding/Event Planning | `#DB2777` | `#A16207` | `#FDF2F8` | Romantic pink + elegant gold |
| 40 | Legal Services | `#1E3A8A` | `#B45309` | `#F8FAFC` | Authority navy + trust gold |
| 41 | Insurance Platform | `#0369A1` | `#16A34A` | `#F0F9FF` | Security blue + protected green |
| 42 | Banking/Traditional Finance | `#0F172A` | `#A16207` | `#F8FAFC` | Trust navy + premium gold |
| 43 | Online Course/E-learning | `#0D9488` | `#EA580C` | `#F0FDFA` | Progress teal + achievement orange |
| 44 | Non-profit/Charity | `#0891B2` | `#EA580C` | `#ECFEFF` | Compassion blue + action orange |
| 45 | Music Streaming | `#1E1B4B` | `#22C55E` | `#0F0F23` | Dark audio + play green |
| 46 | Video Streaming/OTT | `#0F0F23` | `#E11D48` | `#000000` | Cinema dark + play red |
| 47 | Job Board/Recruitment | `#0369A1` | `#16A34A` | `#F0F9FF` | Professional blue + success green |
| 48 | Marketplace (P2P) | `#7C3AED` | `#16A34A` | `#FAF5FF` | Trust purple + transaction green |
| 49 | Logistics/Delivery | `#2563EB` | `#EA580C` | `#EFF6FF` | Tracking blue + delivery orange |
| 50 | Agriculture/Farm Tech | `#15803D` | `#A16207` | `#F0FDF4` | Earth green + harvest gold |
| 51 | Construction/Architecture | `#64748B` | `#EA580C` | `#F8FAFC` | Industrial grey + safety orange |
| 52 | Automotive/Car Dealership | `#1E293B` | `#DC2626` | `#F8FAFC` | Premium dark + action red |
| 53 | Photography Studio | `#18181B` | `#F8FAFC` | `#000000` | Pure black + white contrast |
| 54 | Coworking Space | `#F59E0B` | `#2563EB` | `#FFFBEB` | Energetic amber + booking blue |
| 55 | Home Services (Plumber/Electrician) | `#1E40AF` | `#EA580C` | `#EFF6FF` | Professional blue + urgent orange |
| 56 | Childcare/Daycare | `#F472B6` | `#16A34A` | `#FDF2F8` | Soft pink + safe green |
| 57 | Senior Care/Elderly | `#0369A1` | `#16A34A` | `#F0F9FF` | Calm blue + reassuring green |
| 58 | Medical Clinic | `#0891B2` | `#16A34A` | `#F0FDFA` | Medical teal + health green |
| 59 | Pharmacy/Drug Store | `#15803D` | `#0369A1` | `#F0FDF4` | Pharmacy green + trust blue |
| 60 | Dental Practice | `#0EA5E9` | `#0EA5E9` | `#F0F9FF` | Fresh blue + smile yellow |
| 61 | Veterinary Clinic | `#0D9488` | `#EA580C` | `#F0FDFA` | Caring teal + warm orange |
| 62 | Florist/Plant Shop | `#15803D` | `#EC4899` | `#F0FDF4` | Natural green + floral pink |
| 63 | Bakery/Cafe | `#92400E` | `#92400E` | `#FEF3C7` | Warm brown + cream white |
| 64 | Brewery/Winery | `#7C2D12` | `#A16207` | `#FEF2F2` | Deep burgundy + craft gold |
| 65 | Airline | `#1E3A8A` | `#EA580C` | `#EFF6FF` | Sky blue + booking orange |
| 66 | News/Media Platform | `#DC2626` | `#1E40AF` | `#FEF2F2` | Breaking red + link blue |
| 67 | Magazine/Blog | `#18181B` | `#EC4899` | `#FAFAFA` | Editorial black + accent pink |
| 68 | Freelancer Platform | `#6366F1` | `#16A34A` | `#EEF2FF` | Creative indigo + hire green |
| 69 | Marketing Agency | `#EC4899` | `#0891B2` | `#FDF2F8` | Bold pink + creative cyan |
| 70 | Event Management | `#7C3AED` | `#EA580C` | `#FAF5FF` | Excitement purple + action orange |
| 71 | Membership/Community | `#7C3AED` | `#16A34A` | `#FAF5FF` | Community purple + join green |
| 72 | Newsletter Platform | `#0369A1` | `#EA580C` | `#F0F9FF` | Trust blue + subscribe orange |
| 73 | Digital Products/Downloads | `#6366F1` | `#16A34A` | `#EEF2FF` | Digital indigo + buy green |
| 74 | Church/Religious Organization | `#7C3AED` | `#A16207` | `#FAF5FF` | Spiritual purple + warm gold |
| 75 | Sports Team/Club | `#DC2626` | `#DC2626` | `#FEF2F2` | Team red + championship gold |
| 76 | Museum/Gallery | `#18181B` | `#18181B` | `#FAFAFA` | Gallery black + white space |
| 77 | Theater/Cinema | `#1E1B4B` | `#CA8A04` | `#0F0F23` | Dramatic dark + spotlight gold |
| 78 | Language Learning App | `#4F46E5` | `#16A34A` | `#EEF2FF` | Learning indigo + progress green |
| 79 | Coding Bootcamp | `#0F172A` | `#22C55E` | `#020617` | Terminal dark + success green |
| 80 | Cybersecurity Platform | `#00FF41` | `#FF3333` | `#000000` | Matrix green + alert red |
| 81 | Developer Tool / IDE | `#1E293B` | `#22C55E` | `#0F172A` | Code dark + run green |
| 82 | Biotech / Life Sciences | `#0EA5E9` | `#059669` | `#F0F9FF` | DNA blue + life green |
| 83 | Space Tech / Aerospace | `#F8FAFC` | `#3B82F6` | `#0B0B10` | Star white + launch blue |
| 84 | Architecture / Interior | `#171717` | `#A16207` | `#FFFFFF` | Minimal black + accent gold |
| 85 | Quantum Computing Interface | `#00FFFF` | `#FF00FF` | `#050510` | Quantum cyan + interference purple |
| 86 | Biohacking / Longevity App | `#FF4D4D` | `#059669` | `#F5F5F7` | Bio red/blue + vitality green |
| 87 | Autonomous Drone Fleet Manager | `#00FF41` | `#FF3333` | `#0D1117` | Terminal green + alert red |
| 88 | Generative Art Platform | `#18181B` | `#EC4899` | `#FAFAFA` | Canvas neutral + creative pink |
| 89 | Spatial Computing OS / App | `#FFFFFF` | `#FFFFFF` | `#888888` | Glass white + system blue |
| 90 | Sustainable Energy / Climate Tech | `#059669` | `#059669` | `#ECFDF5` | Nature green + solar gold |
| 91 | Personal Finance Tracker | `#1E40AF` | `#059669` | `#0F172A` | Trust blue + profit green on dark |
| 92 | Chat & Messaging App | `#2563EB` | `#059669` | `#FFFFFF` | Messenger blue + online green |
| 93 | Notes & Writing App | `#78716C` | `#D97706` | `#FFFBEB` | Warm ink + amber accent on cream |
| 94 | Habit Tracker | `#D97706` | `#059669` | `#FFFBEB` | Streak amber + habit green |
| 95 | Food Delivery / On-Demand | `#EA580C` | `#2563EB` | `#FFF7ED` | Appetizing orange + trust blue |
| 96 | Ride Hailing / Transportation | `#1E293B` | `#2563EB` | `#0F172A` | Map dark + route blue |
| 97 | Recipe & Cooking App | `#9A3412` | `#059669` | `#FFFBEB` | Warm terracotta + fresh green |
| 98 | Meditation & Mindfulness | `#7C3AED` | `#059669` | `#FAF5FF` | Calm lavender + mindful green |
| 99 | Weather App | `#0284C7` | `#F59E0B` | `#F0F9FF` | Sky blue + sun amber |
| 100 | Diary & Journal App | `#92400E` | `#6366F1` | `#FFFBEB` | Warm journal brown + ink violet |
| 101 | CRM & Client Management | `#2563EB` | `#059669` | `#F8FAFC` | Professional blue + deal green |
| 102 | Inventory & Stock Management | `#334155` | `#059669` | `#F8FAFC` | Industrial slate + stock green |
| 103 | Flashcard & Study Tool | `#7C3AED` | `#059669` | `#FAF5FF` | Study purple + correct green |
| 104 | Booking & Appointment App | `#0284C7` | `#059669` | `#F0F9FF` | Calendar blue + available green |
| 105 | Invoice & Billing Tool | `#1E3A5F` | `#059669` | `#F8FAFC` | Navy professional + paid green |
| 106 | Grocery & Shopping List | `#059669` | `#D97706` | `#ECFDF5` | Fresh green + food amber |
| 107 | Timer & Pomodoro | `#DC2626` | `#059669` | `#0F172A` | Focus red on dark + break green |
| 108 | Parenting & Baby Tracker | `#EC4899` | `#0284C7` | `#FDF2F8` | Soft pink + trust blue |
| 109 | Scanner & Document Manager | `#1E293B` | `#2563EB` | `#F8FAFC` | Document grey + scan blue |
| 110 | Calendar & Scheduling App | `#2563EB` | `#059669` | `#F8FAFC` | Calendar blue + event green |
| 111 | Password Manager | `#1E3A5F` | `#059669` | `#0F172A` | Vault dark blue + secure green |
| 112 | Expense Splitter / Bill Split | `#059669` | `#DC2626` | `#F8FAFC` | Balance green + owe red |
| 113 | Voice Recorder & Memo | `#DC2626` | `#2563EB` | `#FFFFFF` | Recording red + waveform blue |
| 114 | Bookmark & Read-Later | `#D97706` | `#2563EB` | `#FFFBEB` | Warm amber + link blue |
| 115 | Translator App | `#2563EB` | `#EA580C` | `#F8FAFC` | Global blue + teal + accent orange |
| 116 | Calculator & Unit Converter | `#EA580C` | `#2563EB` | `#1C1917` | Operation orange on dark |
| 117 | Alarm & World Clock | `#D97706` | `#6366F1` | `#0F172A` | Time amber + night indigo on dark |
| 118 | File Manager & Transfer | `#2563EB` | `#D97706` | `#F8FAFC` | Folder blue + file amber |
| 119 | Email Client | `#2563EB` | `#DC2626` | `#FFFFFF` | Inbox blue + priority red |
| 120 | Casual Puzzle Game | `#EC4899` | `#F59E0B` | `#FDF2F8` | Cheerful pink + reward gold |
| 121 | Trivia & Quiz Game | `#2563EB` | `#F59E0B` | `#EFF6FF` | Quiz blue + gold leaderboard |
| 122 | Card & Board Game | `#15803D` | `#D97706` | `#0F172A` | Felt green + gold on dark |
| 123 | Idle & Clicker Game | `#D97706` | `#7C3AED` | `#FFFBEB` | Coin gold + prestige purple |
| 124 | Word & Crossword Game | `#15803D` | `#D97706` | `#FFFFFF` | Word green + letter amber |
| 125 | Arcade & Retro Game | `#DC2626` | `#22C55E` | `#0F172A` | Neon red+blue on dark + score green |
| 126 | Photo Editor & Filters | `#7C3AED` | `#0891B2` | `#0F172A` | Editor violet + filter cyan on dark |
| 127 | Short Video Editor | `#EC4899` | `#2563EB` | `#0F172A` | Video pink on dark + timeline blue |
| 128 | Drawing & Sketching Canvas | `#7C3AED` | `#0891B2` | `#1C1917` | Canvas purple + tool teal on dark |
| 129 | Music Creation & Beat Maker | `#7C3AED` | `#22C55E` | `#0F172A` | Studio purple + waveform green on dark |
| 130 | Meme & Sticker Maker | `#EC4899` | `#2563EB` | `#FFFFFF` | Viral pink + comedy yellow + share blue |
| 131 | AI Photo & Avatar Generator | `#7C3AED` | `#EC4899` | `#FAF5FF` | AI purple + generation pink |
| 132 | Link-in-Bio Page Builder | `#2563EB` | `#EC4899` | `#FFFFFF` | Brand blue + creator purple |
| 133 | Wardrobe & Outfit Planner | `#BE185D` | `#D97706` | `#FDF2F8` | Fashion rose + gold accent |
| 134 | Plant Care Tracker | `#15803D` | `#D97706` | `#F0FDF4` | Nature green + sun yellow |
| 135 | Book & Reading Tracker | `#78716C` | `#D97706` | `#FFFBEB` | Book brown + page amber |
| 136 | Couple & Relationship App | `#BE185D` | `#DC2626` | `#FDF2F8` | Romance rose + love red |
| 137 | Family Calendar & Chores | `#2563EB` | `#D97706` | `#F8FAFC` | Family blue + chore green |
| 138 | Mood Tracker | `#7C3AED` | `#D97706` | `#FAF5FF` | Mood purple + insight amber |
| 139 | Gift & Wishlist | `#DC2626` | `#EC4899` | `#FFF1F2` | Gift red + gold + surprise pink |
| 140 | Running & Cycling GPS | `#EA580C` | `#059669` | `#0F172A` | Energetic orange + pace green on dark |
| 141 | Yoga & Stretching Guide | `#6B7280` | `#0891B2` | `#F5F5F0` | Sage neutral + calm teal |
| 142 | Sleep Tracker | `#4338CA` | `#7C3AED` | `#0F172A` | Night indigo + dream violet on dark |
| 143 | Calorie & Nutrition Counter | `#059669` | `#EA580C` | `#ECFDF5` | Healthy green + macro orange |
| 144 | Period & Cycle Tracker | `#BE185D` | `#7C3AED` | `#FDF2F8` | Blush rose + fertility lavender |
| 145 | Medication & Pill Reminder | `#0284C7` | `#DC2626` | `#F0F9FF` | Medical blue + alert red |
| 146 | Water & Hydration Reminder | `#0284C7` | `#0891B2` | `#F0F9FF` | Refreshing blue + water cyan |
| 147 | Fasting & Intermittent Timer | `#6366F1` | `#059669` | `#0F172A` | Fasting indigo on dark + eating green |
| 148 | Anonymous Community / Confession | `#475569` | `#0891B2` | `#0F172A` | Protective grey + subtle teal on dark |
| 149 | Local Events & Discovery | `#EA580C` | `#2563EB` | `#FFF7ED` | Event orange + map blue |
| 150 | Study Together / Virtual Coworking | `#2563EB` | `#059669` | `#F8FAFC` | Focus blue + session green |
| 151 | Coding Challenge & Practice | `#22C55E` | `#D97706` | `#0F172A` | Code green + difficulty amber on dark |
| 152 | Kids Learning (ABC & Math) | `#2563EB` | `#EC4899` | `#EFF6FF` | Learning blue + play yellow + fun pink |
| 153 | Music Instrument Learning | `#DC2626` | `#D97706` | `#FFFBEB` | Musical red + warm amber |
| 154 | Parking Finder | `#2563EB` | `#DC2626` | `#F0F9FF` | Available blue/green + occupied red |
| 155 | Public Transit Guide | `#2563EB` | `#EA580C` | `#F8FAFC` | Transit blue + line colors |
| 156 | Road Trip Planner | `#EA580C` | `#D97706` | `#FFF7ED` | Adventure orange + map teal |
| 157 | VPN & Privacy Tool | `#1E3A5F` | `#22C55E` | `#0F172A` | Shield dark + connected green |
| 158 | Emergency SOS & Safety | `#DC2626` | `#2563EB` | `#FFF1F2` | Alert red + safety blue |
| 159 | Wallpaper & Theme App | `#7C3AED` | `#2563EB` | `#FAF5FF` | Aesthetic purple + trending pink |
| 160 | White Noise & Ambient Sound | `#475569` | `#4338CA` | `#0F172A` | Ambient grey + deep indigo on dark |
| 161 | Home Decoration & Interior Design | `#78716C` | `#D97706` | `#FAF5F2` | Interior warm grey + gold accent |

---

## Part 5 — Typography Mood Keywords

> Font names are irrelevant to image generation. Use the mood/style keywords and the heading/body style descriptions instead.

| # | Pairing Name | Category | Heading Style | Body Style | Mood Keywords | Best For |
|---|---|---|---|---|---|---|
| 1 | Classic Elegant | Serif + Sans | elegant serif heading | clean sans-serif body | elegant, luxury, sophisticated, timeless, premium, editorial | Luxury brands, fashion, spa, beauty, editorial, magazines, high-end e- |
| 2 | Modern Professional | Sans + Sans | geometric sans heading | modern sans body | modern, professional, clean, corporate, friendly, approachable | SaaS, corporate sites, business apps, startups, professional services |
| 3 | Tech Startup | Sans + Sans | geometric sans heading | modern sans body | tech, startup, modern, innovative, bold, futuristic | Tech companies, startups, SaaS, developer tools, AI products |
| 4 | Editorial Classic | Serif + Serif | Cormorant Garamond | Libre Baskerville | editorial, classic, literary, traditional, refined, bookish | Publishing, blogs, news sites, literary magazines, book covers |
| 5 | Minimal Swiss | Sans + Sans | geometric sans heading | modern sans body | minimal, clean, swiss, functional, neutral, professional | Dashboards, admin panels, documentation, enterprise apps, design syste |
| 6 | Playful Creative | Display + Sans | bold display heading | clean body | playful, friendly, fun, creative, warm, approachable | Children's apps, educational, gaming, creative tools, entertainment |
| 7 | Bold Statement | Display + Sans | bold display heading | clean body | bold, impactful, strong, dramatic, modern, headlines | Marketing sites, portfolios, agencies, event pages, sports |
| 8 | Wellness Calm | Serif + Sans | elegant serif heading | clean sans-serif body | calm, wellness, health, relaxing, natural, organic | Health apps, wellness, spa, meditation, yoga, organic brands |
| 9 | Developer Mono | Mono + Sans | monospace technical heading | monospace body | code, developer, technical, precise, functional, hacker | Developer tools, documentation, code editors, tech blogs, CLI apps |
| 10 | Retro Vintage | Display + Serif | bold display heading | clean body | retro, vintage, nostalgic, dramatic, decorative, bold | Vintage brands, breweries, restaurants, creative portfolios, posters |
| 11 | Geometric Modern | Sans + Sans | geometric sans heading | modern sans body | geometric, modern, clean, balanced, contemporary, versatile | General purpose, portfolios, agencies, modern brands, landing pages |
| 12 | Luxury Serif | Serif + Sans | elegant serif heading | clean sans-serif body | luxury, high-end, fashion, elegant, refined, premium | Fashion brands, luxury e-commerce, jewelry, high-end services |
| 13 | Friendly SaaS | Sans + Sans | geometric sans heading | modern sans body | friendly, modern, saas, clean, approachable, professional | SaaS products, web apps, dashboards, B2B, productivity tools |
| 14 | News Editorial | Serif + Sans | elegant serif heading | clean sans-serif body | news, editorial, journalism, trustworthy, readable, informative | News sites, blogs, magazines, journalism, content-heavy sites |
| 15 | Handwritten Charm | Script + Sans | handwritten script accent | soft rounded body | handwritten, personal, friendly, casual, warm, charming | Personal blogs, invitations, creative portfolios, lifestyle brands |
| 16 | Corporate Trust | Sans + Sans | geometric sans heading | modern sans body | corporate, trustworthy, accessible, readable, professional, clean | Enterprise, government, healthcare, finance, accessibility-focused |
| 17 | Brutalist Raw | Mono + Mono | monospace technical heading | monospace body | brutalist, raw, technical, monospace, minimal, stark | Brutalist designs, developer portfolios, experimental, tech art |
| 18 | Fashion Forward | Sans + Sans | geometric sans heading | modern sans body | fashion, avant-garde, creative, bold, artistic, edgy | Fashion brands, creative agencies, art galleries, design studios |
| 19 | Soft Rounded | Sans + Sans | geometric sans heading | modern sans body | soft, rounded, friendly, approachable, warm, gentle | Children's products, pet apps, friendly brands, wellness, soft UI |
| 20 | Premium Sans | Sans + Sans | geometric sans heading | modern sans body | premium, modern, clean, sophisticated, versatile, balanced | Premium brands, modern agencies, SaaS, portfolios, startups |
| 21 | Vietnamese Friendly | Sans + Sans | geometric sans heading | modern sans body | vietnamese, international, readable, clean, multilingual, accessible | Vietnamese sites, multilingual apps, international products |
| 22 | Japanese Elegant | Serif + Sans | elegant serif heading | clean sans-serif body | japanese, elegant, traditional, modern, multilingual, readable | Japanese sites, Japanese restaurants, cultural sites, anime/manga |
| 23 | Korean Modern | Sans + Sans | geometric sans heading | modern sans body | korean, modern, clean, professional, multilingual, readable | Korean sites, K-beauty, K-pop, Korean businesses, multilingual |
| 24 | Chinese Traditional | Serif + Sans | elegant serif heading | clean sans-serif body | chinese, traditional, elegant, cultural, multilingual, readable | Traditional Chinese sites, cultural content, Taiwan/Hong Kong markets |
| 25 | Chinese Simplified | Sans + Sans | geometric sans heading | modern sans body | chinese, simplified, modern, professional, multilingual, readable | Simplified Chinese sites, mainland China market, business apps |
| 26 | Arabic Elegant | Serif + Sans | elegant serif heading | clean sans-serif body | arabic, elegant, traditional, cultural, RTL, readable | Arabic sites, Middle East market, Islamic content, bilingual sites |
| 27 | Thai Modern | Sans + Sans | geometric sans heading | modern sans body | thai, modern, readable, clean, multilingual, accessible | Thai sites, Southeast Asia, tourism, Thai restaurants |
| 28 | Hebrew Modern | Sans + Sans | geometric sans heading | modern sans body | hebrew, modern, RTL, clean, professional, readable | Hebrew sites, Israeli market, Jewish content, bilingual sites |
| 29 | Legal Professional | Serif + Sans | elegant serif heading | clean sans-serif body | legal, professional, traditional, trustworthy, formal, authoritative | Law firms, legal services, contracts, formal documents, government |
| 30 | Medical Clean | Sans + Sans | geometric sans heading | modern sans body | medical, clean, accessible, professional, healthcare, trustworthy | Healthcare, medical clinics, pharma, health apps, accessibility |
| 31 | Financial Trust | Sans + Sans | geometric sans heading | modern sans body | financial, trustworthy, professional, corporate, banking, serious | Banks, finance, insurance, investment, fintech, enterprise |
| 32 | Real Estate Luxury | Serif + Sans | elegant serif heading | clean sans-serif body | real estate, luxury, elegant, sophisticated, property, premium | Real estate, luxury properties, architecture, interior design |
| 33 | Restaurant Menu | Serif + Sans | elegant serif heading | clean sans-serif body | restaurant, menu, culinary, elegant, foodie, hospitality | Restaurants, cafes, food blogs, culinary, hospitality |
| 34 | Art Deco | Display + Sans | bold display heading | clean body | art deco, vintage, 1920s, elegant, decorative, gatsby | Vintage events, art deco themes, luxury hotels, classic cocktails |
| 35 | Magazine Style | Serif + Sans | elegant serif heading | clean sans-serif body | magazine, editorial, publishing, refined, journalism, print | Magazines, online publications, editorial content, journalism |
| 36 | Crypto/Web3 | Sans + Sans | geometric sans heading | modern sans body | crypto, web3, futuristic, tech, blockchain, digital | Crypto platforms, NFT, blockchain, web3, futuristic tech |
| 37 | Gaming Bold | Display + Sans | bold display heading | clean body | gaming, bold, action, esports, competitive, energetic | Gaming, esports, action games, competitive sports, entertainment |
| 38 | Indie/Craft | Display + Sans | bold display heading | clean body | indie, craft, handmade, artisan, organic, creative | Craft brands, indie products, artisan, handmade, organic products |
| 39 | Startup Bold | Sans + Sans | geometric sans heading | modern sans body | startup, bold, modern, innovative, confident, dynamic | Startups, pitch decks, product launches, bold brands |
| 40 | E-commerce Clean | Sans + Sans | geometric sans heading | modern sans body | ecommerce, clean, shopping, product, retail, conversion | E-commerce, online stores, product pages, retail, shopping |
| 41 | Academic/Research | Serif + Sans | elegant serif heading | clean sans-serif body | academic, research, scholarly, accessible, readable, educational | Universities, research papers, academic journals, educational |
| 42 | Dashboard Data | Mono + Sans | monospace technical heading | monospace body | dashboard, data, analytics, code, technical, precise | Dashboards, analytics, data visualization, admin panels |
| 43 | Music/Entertainment | Display + Sans | bold display heading | clean body | music, entertainment, fun, energetic, bold, performance | Music platforms, entertainment, events, festivals, performers |
| 44 | Minimalist Portfolio | Sans + Sans | geometric sans heading | modern sans body | minimal, portfolio, designer, creative, clean, artistic | Design portfolios, creative professionals, minimalist brands |
| 45 | Kids/Education | Display + Sans | bold display heading | clean body | kids, education, playful, friendly, colorful, learning | Children's apps, educational games, kid-friendly content |
| 46 | Wedding/Romance | Script + Serif | handwritten script accent | soft rounded body | wedding, romance, elegant, script, invitation, feminine | Wedding sites, invitations, romantic brands, bridal |
| 47 | Science/Tech | Sans + Sans | geometric sans heading | modern sans body | science, technology, research, data, futuristic, precise | Science, research, tech documentation, data-heavy sites |
| 48 | Accessibility First | Sans + Sans | geometric sans heading | modern sans body | accessible, readable, inclusive, WCAG, dyslexia-friendly, clear | Accessibility-critical sites, government, healthcare, inclusive design |
| 49 | Sports/Fitness | Sans + Sans | geometric sans heading | modern sans body | sports, fitness, athletic, energetic, condensed, action | Sports, fitness, gyms, athletic brands, competition |
| 50 | Luxury Minimalist | Serif + Sans | elegant serif heading | clean sans-serif body | luxury, minimalist, high-end, sophisticated, refined, premium | Luxury minimalist brands, high-end fashion, premium products |
| 51 | Tech/HUD Mono | Mono + Mono | monospace technical heading | monospace body | tech, futuristic, hud, sci-fi, data, monospaced, precise | Sci-fi interfaces, developer tools, cybersecurity, dashboards |
| 52 | Pixel Retro | Display + Sans | bold display heading | clean body | pixel, retro, gaming, 8-bit, nostalgic, arcade | Pixel art games, retro websites, creative portfolios |
| 53 | Neubrutalist Bold | Display + Sans | bold display heading | clean body | bold, neubrutalist, loud, strong, geometric, quirky | Neubrutalist designs, Gen Z brands, bold marketing |
| 54 | Academic/Archival | Serif + Serif | EB Garamond | Crimson Text | academic, old-school, university, research, serious, traditional | University sites, archives, research papers, history |
| 55 | Spatial Clear | Sans + Sans | geometric sans heading | modern sans body | spatial, legible, glass, system, clean, neutral | Spatial computing, AR/VR, glassmorphism interfaces |
| 56 | Kinetic Motion | Display + Mono | monospace technical heading | monospace body | kinetic, motion, futuristic, speed, wide, tech | Music festivals, automotive, high-energy brands |
| 57 | Gen Z Brutal | Display + Sans | bold display heading | clean body | brutal, loud, shouty, meme, internet, bold | Gen Z marketing, streetwear, viral campaigns |
| 58 | Minimalist Monochrome Editorial | Serif + Serif + Mono (Triple Stack) | monospace technical heading | monospace body | monochrome, editorial, austere, typographic, pocket manifesto, luxury, high contrast, brutalist mobile | Luxury fashion mobile apps, editorial publications, digital exhibition |
| 59 | Modern Dark Cinema (Inter System) | Sans + Mono | geometric sans heading | modern sans body | dark, cinematic, technical, precision, clean, premium, developer, professional, high-end utility | Developer tools, fintech/trading, AI dashboards, streaming platforms,  |
| 60 | SaaS Mobile Boutique (Calistoga + Inter) | Display Serif + Sans + Mono | elegant serif heading | clean sans-serif body | saas, boutique, electric, warm, editorial, bold, premium, fintech, business, dual font, human warmth | B2B SaaS mobile, fintech apps, analytics dashboards, marketing tools,  |
| 61 | Terminal CLI Monospace | Mono + Mono (Single Family) | monospace technical heading | monospace body | terminal, cli, hacker, monospace, matrix, developer, retro-future, command line, precision, OLED | Developer tools, Web3/blockchain apps, hacker aesthetic, sci-fi games, |
| 62 | Kinetic Brutalism (Space Grotesk) | Geometric Sans (Single Dominant) | Space Grotesk | Space Grotesk | kinetic, brutalist, aggressive, uppercase, oversized, display, motion, street, bold, high-energy, zine | Music/culture apps, sports platforms, brand flagship mobile, performan |
| 63 | Flat Design Mobile (System Bold) | Sans + Sans | geometric sans heading | modern sans body | flat, clean, system, bold, geometric, cross-platform, icon, poster, minimal, functional, responsive | Cross-platform apps, dashboards, system UI, onboarding, marketing page |
| 64 | Material You MD3 (Roboto System) | Sans (System Default) | geometric sans heading | modern sans body | material design 3, md3, android, google, tonal, friendly, rounded, accessible, adaptive | Android apps, cross-platform tools, productivity software, data-heavy  |
| 65 | Neo Brutalism Mobile (Space Grotesk Heavy) | Geometric Sans (Bold-Only) | Space Grotesk | Space Grotesk | neo brutalism, pop art, loud, bold, heavy, stickers, mechanical, high contrast, cream, gen-z | Creative tools, Gen-Z marketing, e-commerce for youth culture, content |
| 66 | Bold Typography Mobile (Inter-Tight Poster) | Sans + Serif (Display) + Mono | elegant serif heading | clean sans-serif body | bold typography, editorial, poster, near-black, vermillion, luxury, type-as-hero, manifesto, high-contrast | Creative brand flagships, reading platforms, event apps, flash pages,  |
| 67 | Academia Mobile (Cormorant + Crimson + Cinzel) | Serif + Book Serif + Engraved (Triple Stack) | Cormorant Garamond | Crimson Pro | academia, library, mahogany, parchment, brass, scholarly, prestige, antique, victorian, leather | Knowledge management apps, scholarly reading tools, personal brand por |
| 68 | Cyberpunk Mobile (Orbitron + JetBrains Mono) | Tech Display + Mono | monospace technical heading | monospace body | cyberpunk, neon, glitch, hud, sci-fi, dark, matrix green, magenta, chamfered, tactical | Gaming companion apps, fintech/crypto, data visualization, dark brand  |
| 69 | Web3 Bitcoin DeFi (Space Grotesk + Inter + Mono) | Geometric Sans + Sans + Mono (Triple) | monospace technical heading | monospace body | web3, bitcoin, defi, digital gold, fintech, crypto, trustless, luminescent, precision, dark | DeFi protocols and wallets, NFT platforms, metaverse social apps, high |
| 70 | Claymorphism Mobile (Nunito + DM Sans) | Display Rounded + Geometric Sans | bold display heading | clean body | claymorphism, clay, rounded, playful, candy, bubbly, soft, 3d, children, education, tactile, spring, nunito, dm sans | Children education apps, teen social, brand mascot apps, creative tool |
| 71 | Enterprise SaaS Mobile (Plus Jakarta Sans) | Geometric Sans (Single Family) | Plus Jakarta Sans | Plus Jakarta Sans | enterprise, saas, b2b, professional, indigo, modern, approachable, legible, ios dynamic type, android scaling | B2B SaaS apps, productivity tools, government and finance mobile apps, |
| 72 | Sketch Hand-Drawn Mobile (Kalam + Patrick Hand) | Handwritten + Handwritten (Dual) | Kalam | Patrick Hand | sketch, hand-drawn, handwriting, human, imperfect, organic, paper, kalam, patrick hand, education, journal, creative | Journaling apps, prototype tools, children's picturebook apps, creativ |
| 73 | Neumorphism Mobile (Plus Jakarta Sans + System) | Geometric Sans (System Fallback) | Plus Jakarta Sans | Plus Jakarta Sans | neumorphism, soft ui, monochromatic, cool grey, minimal, physical, depth, ceramic, system font, utility | Smart home controls, minimal tools, aesthetic dashboards, health monit |

---

## Part 6 — Layout & Composition Reference

> Use these composition keywords to describe the structural arrangement of the image.  
> Source: FelipeOFF/design-advisor-skill Landing Page patterns.

### Hero-Centric
**Composition:** full-width hero section filling the viewport, large compelling headline centered above fold, high-contrast call-to-action button, product screenshot or illustration as central focus, gradient or cinematic background  
**Best for:** SaaS, product launches, travel, real estate

---

### Conversion-Optimized
**Composition:** single-column centered layout, dominant CTA button at top, minimal surrounding elements, trust badges below headline, clean white space, form or sign-up component visible without scrolling  
**Best for:** e-commerce product pages, free trial sign-ups, lead generation

---

### Feature-Rich Showcase
**Composition:** multi-column grid of feature cards (3–4 columns), icon + headline + short description per card, alternating content sections, comparison table section, product benefit tiles  
**Best for:** enterprise SaaS, software tools, B2B platforms

---

### Minimal & Direct
**Composition:** single narrow centered column, abundant white space, sparse essential content only, one clear focal element, no decorative imagery, pure typographic hierarchy  
**Best for:** micro SaaS, consulting, indie products, freelancers

---

### Social Proof-Focused
**Composition:** testimonial cards with avatar photos, client logo grid strip, star rating badges, success metric counters, before/after comparison panels, case study cards  
**Best for:** B2B SaaS, professional services, established brands

---

### Interactive Product Demo
**Composition:** embedded product mockup in center stage, step-by-step numbered guide below, hover-reveal feature callouts, screenshot carousel or video player, live demo button overlay  
**Best for:** SaaS platforms, developer tools, productivity apps

---

### Trust & Authority
**Composition:** certification badge grid, security shield icons, expert credential cards, industry award logos, case study metrics with large numbers, professional photography of team/office  
**Best for:** healthcare, financial services, enterprise software, legal

---

### Storytelling-Driven
**Composition:** chapter-like vertical sections with alternating image and text, narrative progress indicators, timeline visualization, emotional full-bleed imagery between sections, founder story panel  
**Best for:** brand stories, mission-driven products, premium lifestyle

---

### Data-Dense Dashboard
**Composition:** compact 12-column grid of widgets, KPI metric cards in top row, chart panels in center, data table in lower section, filter sidebar on left, minimal padding between elements  
**Best for:** business intelligence, financial analytics, enterprise reporting

---

### Bento Box Grid
**Composition:** asymmetric modular card grid with varied sizes (1×1, 2×1, 2×2 tiles), Apple-style clean layout, rounded card corners, negative space between tiles, featured card prominently larger  
**Best for:** portfolios, product marketing, Apple-style feature showcases

---

### Executive Dashboard
**Composition:** 4–6 large KPI cards across the top, trend sparklines inside each card, traffic-light status indicators, clean single-page layout with generous white space, print-friendly structure  
**Best for:** C-suite summary views, business decision dashboards

---

### Real-Time Monitoring
**Composition:** status indicator dots (pulsing green/red), streaming line charts in center, alert notification panel on side, connection status badge in header, auto-refresh counter visible  
**Best for:** DevOps, system monitoring, live event tracking

---

### Comparative Analysis
**Composition:** side-by-side metric columns, period selector at top, delta indicator arrows (↑↓), benchmark lines on charts, color-coded winning vs losing metrics (green/red), percentage badges  
**Best for:** A/B testing, period-over-period reporting, market comparison

---

### Predictive Analytics
**Composition:** dashed forecast lines extending from solid historical data, shaded confidence interval bands, anomaly highlight markers (circles), scenario toggle switches, AI insight summary card  
**Best for:** forecasting dashboards, trend prediction, AI-powered analytics

---

### Storytelling Landing Page (Scroll-Driven)
**Composition:** scroll-snap sections with full-height chapters, parallax background imagery, section transition dividers, timeline progression bar, alternating image-text blocks, emotional quote callouts  
**Best for:** brand/startup stories, mission-driven products, premium lifestyle brands

---

## Part 7 — Gemini/Imagen 专项生图提示词词库

> ⚠️ **适用范围：仅用于 Route B（风格锚点版本）的风格句生成，不影响 Route A（叙事流版本）。**  
> Route A 不指定任何风格、配色、材质参数；本章节所有词汇仅在 Route B 的「视觉风格：」行中使用。  
> 覆盖写实摄影、游戏概念艺术、材质质感、光影效果等维度。  
> **核心原则：用叙事性段落替代关键词堆砌，Gemini 对段落描述的理解显著优于 comma-separated 关键词列表。**

---

### Part 7.1 — Gemini 提示词结构模板

**官方推荐 6 要素公式：**
```
[主体 Subject] + [构图 Composition] + [动作 Action] + [场景 Location] + [风格 Style] + [约束 Constraints]
```

**写实摄影通用模板：**
```
A photorealistic [shot type] of [subject], [action/expression], set in [environment].
The scene is illuminated by [lighting description], creating a [mood] atmosphere.
Captured with a [camera/lens details], emphasizing [key textures and details].
The image should be in a [aspect ratio] format.
```

**产品摄影模板：**
```
A high-resolution, studio-lit product photograph of a [product] on a [background].
The lighting is a three-point softbox setup to [purpose].
The camera angle is a [angle type] to showcase [specific feature].
Ultra-realistic, with sharp focus on [key detail].
```

**电影概念艺术模板：**
```
A cinematic still from an imaginary [GENRE] film, shot on Kodak Vision3 500T 35mm film stock.
The frame shows [SUBJECT + ACTION] in a [LOCATION] during [TIME OF DAY].
Color palette: teal shadows and orange highlights, slight halation around bright areas,
organic film grain, anamorphic 2.39:1 widescreen aspect ratio.
Camera: 40mm lens at f/2, slight motion blur on foreground, deep focus on subject's face.
Mood: [MOOD ADJECTIVES].
```

> ⚠️ **Gemini 特有注意事项：**
> - 使用"语义负向提示"而非直接否定：不说 `no cars`，说 `an empty street with no signs of traffic`
> - 避免无效关键词：`masterpiece`、`4k`、`trending on ArtStation` 已失效，模型默认高质量
> - 明确说明材质名称与光源类型，而非笼统说"真实感"

---

### Part 7.2 — 写实摄影风格词库

#### 核心写实关键词
- `photorealistic` / `RAW photo` / `hyperrealistic`
- `high-resolution` / `ultra-sharp focus`
- `editorial photography` / `commercial photography quality`
- `documentary photo` / `candid moment` / `unposed`

#### 相机与镜头参数

| 用途 | 关键词 |
|------|--------|
| 人像特写 | `85mm portrait lens, f/1.8 aperture, shallow depth of field, bokeh` |
| 风景广角 | `21mm lens, f/11 aperture, deep depth of field` |
| 微距特写 | `100mm macro lens, extreme close-up` |
| 广角叙事 | `35mm lens, wide-angle shot` |
| 俯拍/低角 | `low-angle shot` / `aerial view` / `Dutch angle` |

**专业相机型号（提升写实质量）：**

| 相机型号 | 风格质感 |
|---------|---------|
| `Hasselblad medium format camera` | 超高细节，商业摄影 |
| `Leica M11` / `Leica M6` | 经典街拍质感 |
| `Canon EOS R5` / `Nikon Z9` | 现代数码写实 |
| `Sony A7 IV` | 色彩准确 |
| `RED Komodo camera` | 电影感 |
| `Fujifilm X100V` / `Ricoh GR III` | 胶片感街拍 |

#### 胶片模拟关键词

| 关键词 | 效果 |
|--------|------|
| `shot on 35mm film` / `120 film` | 胶片质感通用 |
| `Kodak Portra 400` | 暖色调，肤色自然 |
| `Kodak Gold 200` | 温暖复古 |
| `Cinestill 800T` | 夜间电影感，红色晕光 |
| `Fujifilm Superia` | 清爽色调 |
| `Ilford HP5` | 黑白高对比 |
| `film grain` / `heavy grain` | 胶片颗粒感 |
| `light-leak` | 漏光效果 |
| `halation around bright areas` | 亮区光晕 |
| `analog imperfections` | 模拟瑕疵 |

#### 避免 AI 感的关键词（应加入）
- `imperfect skin` / `natural skin texture`（不完美肌肤纹理）
- `freckles` / `slight asymmetry`（雀斑/轻微不对称）
- `subtle smile lines`（细微笑纹）
- `weathered face`（风化感面孔）
- `candid, unaware of the camera`（坦率，不知道镜头存在）
- `slightly messy hair`（略显凌乱头发）
- `subtle color grading`（微妙色彩分级）

#### 应排除的负向提示
```
--no plastic skin, glossy surfaces, artificial lighting,
oversaturated colors, unnatural symmetry,
drawing, illustration, 3D render, waxy skin, airbrushed
```

---

### Part 7.3 — 光影效果词库

#### 自然光 / 大气光

| 关键词 | 效果描述 |
|--------|---------|
| `golden hour` | 日出日落黄金时刻，暖橙色调 |
| `blue hour` | 日出前/日落后蓝调时刻 |
| `soft window light` | 窗光，柔和漫射 |
| `dappled sunlight filtering through leaves` | 树叶间斑驳阳光 |
| `overcast day` | 阴天均匀柔光，无硬阴影 |
| `afternoon light streaming through dusty windows` | 午后光穿透尘埃窗户 |
| `moonlight` | 月光，冷色调柔光 |

#### 工作室/戏剧性灯光

| 关键词 | 效果描述 |
|--------|---------|
| `three-point lighting` | 三点布光（主光+补光+轮廓光） |
| `three-point softbox setup` | 三点柔光箱，消除硬质阴影 |
| `rim light` | 轮廓光，边缘发光 |
| `chiaroscuro` | 明暗强对比，伦勃朗风格 |
| `Rembrandt lighting` | 伦勃朗光，单侧三角形高光 |
| `dramatic directional spotlight from above` | 强烈方向性顶光 |
| `deep shadows with warm highlights` | 深阴影配暖色高光 |
| `softbox lighting` | 柔光箱，均匀软化光 |

#### 特殊/环境光效

| 关键词 | 效果描述 |
|--------|---------|
| `volumetric lighting` | 体积光，光柱效果 |
| `god rays` | 丁达尔效应光线 |
| `lens flare` | 镜头光晕 |
| `bioluminescent` | 生物发光 |
| `ambient occlusion` | 环境遮蔽，接触阴影 |
| `soft global illumination` | 柔和全局光照 |
| `teal shadows and orange highlights` | 青橙色调（电影标准） |
| `bloom effect` / `glow` | 泛光效果 |
| `reflections on wet pavement` | 湿地面倒影 |
| `dust particles in light beam` | 光束中尘埃粒子 |

#### 不同场景专用光照方案

| 场景 | 推荐光效关键词 |
|------|--------------|
| 神秘洞穴 | `crystal cave glow, bioluminescent, deep shadow, moody blue-green tones, soft specular highlights on wet rock` |
| 外太空 | `harsh directional starlight, deep vacuum black, planet rim light, nebula ambient glow` |
| 末世废土 | `overcast diffuse light, desaturated ochre palette, industrial haze, volumetric dust, corroded metal reflections` |
| 魔幻森林 | `dappled golden sunlight through canopy, ethereal mist, bioluminescent flora, soft diffuse green ambient` |
| 赛博朋克城市 | `neon wet-street reflections, rain bokeh, teal-orange color grading, flicker effect, overhead rain streaks` |
| 电影棚拍 | `warm rim light from behind, soft diffused key light on face, subtle fill from reflector` |
| 奇幻史诗场景 | `dramatic golden hour, volumetric mist, magical particle effects, atmospheric depth haze` |

---

### Part 7.4 — 材质质感词库

#### 金属类

| 关键词 | 效果描述 |
|--------|---------|
| `brushed stainless steel finish` | 拉丝不锈钢 |
| `anisotropic highlights on metal` | 金属各向异性高光 |
| `high-gloss polish` | 高光泽抛光 |
| `matte metallic` | 哑光金属 |
| `anodized aluminum` | 阳极氧化铝 |
| `tarnished brass` | 氧化黄铜，做旧感 |
| `corroded metal texture` | 腐蚀金属纹理 |
| `carbon fiber composites` | 碳纤维复合材料 |
| `worn metal with scratches` | 磨损划痕金属 |
| `chrome finish` | 镀铬表面 |

#### 皮革类

| 关键词 | 效果描述 |
|--------|---------|
| `full-grain leather with visible grain texture` | 全粒面皮革，可见纹理 |
| `leather seams and stitching detail` | 皮革缝合线细节 |
| `weathered aged leather` | 风化做旧皮革 |
| `suede texture` | 麂皮质感 |
| `rich tactile leather with pore detail` | 有毛孔细节的皮革 |
| `scuffed patent leather` | 磨损漆皮 |

#### 玻璃 / 透明材质

| 关键词 | 效果描述 |
|--------|---------|
| `glass refraction` | 玻璃折射 |
| `frosted glass` | 磨砂玻璃 |
| `partial internal reflections` | 部分内部反射 |
| `specular highlights on glass surface` | 玻璃镜面高光 |
| `condensation on glass` | 玻璃上水珠凝结 |
| `high-gloss transparency` | 高光泽透明感 |

#### 有机材质（皮肤/蜡质）

| 关键词 | 效果描述 |
|--------|---------|
| `subsurface scattering on skin` | 皮肤次表面散射（SSS） |
| `smooth subsurface scattering` | 光滑次表面散射 |
| `visible pores` / `natural skin texture` | 毛孔可见/自然皮肤 |
| `translucent skin` | 半透明皮肤 |
| `waxy subsurface` | 蜡质次表面散射 |

#### 石材 / 混凝土 / 木材

| 关键词 | 效果描述 |
|--------|---------|
| `polished concrete surface` | 抛光混凝土 |
| `moss-covered stone` | 青苔覆盖石头 |
| `weathered wood with visible grain` | 风化木材，木纹可见 |
| `sun-bleached texture` | 日晒褪色质感 |
| `hand-hewn logs with rough bark` | 手砍原木，粗糙树皮 |
| `basalt volcanic texture` | 玄武岩火山纹理 |
| `rough porous surfaces with chipped edges` | 粗糙多孔，碎裂边缘 |

#### 布料 / 纤维

| 关键词 | 效果描述 |
|--------|---------|
| `heavy cotton twill` | 厚棉斜纹布料 |
| `sheer silk chiffon` | 透明丝绸雪纺 |
| `linen fabric with natural wrinkles` | 亚麻布，自然皱纹 |
| `fabric weave detail` | 布料编织细节 |
| `fabric folds and drape` | 布料折痕与垂感 |
| `fluffy hair with stray strands` | 毛茸茸头发与散落发丝 |

---

### Part 7.5 — 游戏/概念艺术词库

#### 通用概念艺术必备词汇
- `concept art` / `environment design` / `character concept` / `key art`
- `visual development` / `production design`
- `AAA game quality` / `film production art`
- `matte painting style` / `cinematic wide shot composition`
- `Unreal Engine 5 render quality`

#### 武器/装备描述词汇
- `ornate elven plate armor, etched with silver leaf patterns`（精灵板甲，银叶蚀刻）
- `pauldrons shaped like falcon wings`（鹰翼护肩）
- `glowing magical runes on blade`（刀刃上的发光魔法符文）
- `hard surface design style`（硬表面设计风格）
- `worn battle-damaged armor`（战损做旧盔甲）
- `technical callouts and details`（技术标注细节图）
- `multiple angle orthographic views`（多角度正交视图）

#### 角色设计词汇
- `clear readable silhouette`（清晰可读剪影）
- `front side back turnaround view`（前侧后三视图）
- `neutral pose reference sheet`（中性姿势参考图）
- `anatomically believable structure`（解剖合理结构）
- `detailed costume breakdown`（服装细节分解）

#### 场景环境关键词

| 场景类型 | 关键词 |
|---------|--------|
| 奇幻环境 | `ancient elven city in giant trees, magical glowing crystals, waterfalls, atmospheric fog` |
| 科幻飞船 | `sci-fi spaceship concept art, sleek fighter spacecraft, detailed hull and engine components, glowing thruster effects` |
| 末世废土 | `post-apocalyptic ruins, corroded metal structures, overgrown vegetation, overcast harsh light` |
| 赛博朋克 | `cyberpunk cityscape, neon sign reflections in rain puddles, holographic advertisements, steam vents` |
| 地下洞穴 | `crystal caves, bioluminescent flora, underground river, stalactite formations, moody blue-green ambient` |
| 蒸汽朋克 | `steampunk factory, exposed brass gears, steam pipes, industrial Victorian architecture` |
| 外太空站 | `space station hub, cool fluorescent lights, mixed color temperatures, zero-gravity floating debris` |

#### 电影风格列表

| 风格 | 关键词 |
|------|--------|
| Film Noir | `high contrast black and white, Venetian blind shadow patterns, smoky atmosphere, harsh side lighting` |
| Cyberpunk | `neon blue and purple, rainy wet night reflections, teal-orange color grading, rain bokeh` |
| 科幻军事 | `desaturated industrial greys, dirty orange, olive drab, cold hangar lighting, gritty texture` |
| 奇幻史诗 | `golden hour, volumetric mist, magical particle effects, sweeping landscape, dramatic rim lighting` |
| 末世废土 | `overcast diffuse light, dust haze, corroded textures, desaturated ochre palette` |
| 吉卜力风格 | `Ghibli Studios style, hand-painted watercolor background, soft pastel tones, whimsical natural scene` |
| 皮克斯3D | `Pixar 3D style, soft cinematic key light, smooth subsurface scattering, creamy bokeh background, feature-film polish` |

#### 完整概念艺术示例提示词

**奇幻环境：**
```
epic fantasy environment concept art, ancient elven city built into giant ancient trees,
magical glowing crystals embedded in bark, cascading waterfalls between platforms,
dramatic golden hour lighting, atmospheric fog and mist rising from below,
intricate wooden architectural details with silver inlays,
AAA game quality production art, highly detailed matte painting style,
cinematic wide shot composition
```

**游戏角色（太空海军）：**
```
character concept art sheet, female space marine soldier in futuristic powered armor
with glowing blue energy elements, front side back turnaround view,
clear readable silhouette, detailed armor breakdown with panel lines and weathering,
weapon and equipment designs alongside, professional game art quality,
neutral pose reference sheet, clean white background
```

**3D 等距微缩场景：**
```
A 45° top-down isometric miniature 3D scene of [SCENE THEME] diorama on a wooden display base.
Soft refined PBR textures, realistic materials, clean unified composition.
Tiny props integrated into the architecture.
Studio softbox lighting, subtle ambient occlusion, pastel color palette.
Square 1:1 frame, centered subject, plenty of negative space.
```

---

### Part 7.6 — 快速参考速查表

| 用途 | 推荐关键词 |
|------|-----------|
| 写实人像 | `85mm portrait lens, shallow DOF, bokeh, subsurface scattering on skin, natural skin texture, candid` |
| 产品摄影 | `studio softbox lighting, polished concrete surface, 3/4 perspective, Hasselblad medium format` |
| 胶片质感 | `shot on 35mm film, Kodak Portra 400, film grain, halation, analog imperfections` |
| 游戏概念艺术 | `AAA game quality, concept art, cinematic lighting, production design, matte painting style` |
| 金属武器道具 | `brushed metal, anisotropic highlights, scratched worn, corroded patina, specular highlight` |
| 皮革装备 | `full-grain leather, stitching detail, aged leather, pore detail, worn tactile realism` |
| 皮肤渲染 | `subsurface scattering, visible pores, translucent skin, imperfect natural texture` |
| 奇幻光效 | `volumetric lighting, bioluminescent, ethereal mist, magical particle effects, god rays` |
| 赛博朋克 | `neon wet-street reflections, teal-orange color grading, holographic, rain bokeh` |
| 末世场景 | `overcast diffuse, desaturated ochre, volumetric dust, corroded metal, industrial haze` |
| 电影级写实 | `cinematic anamorphic, Kodak Vision3 500T, teal shadows orange highlights, film grain` |
| 3D 等距场景 | `isometric miniature, PBR textures, ambient occlusion, studio softbox, 45° top-down` |
| 食物摄影 | `steam rising, droplets of condensation, glossy sheen, appetizing, editorial food photography, shallow DOF` |
| 时尚人像 | `editorial, high fashion, dewy skin, natural skin texture, Rembrandt lighting, 85mm f/1.4, creamy bokeh` |
| 建筑外观 | `archdaily style, golden hour, warm light from windows, cinematic wide-angle, hyperrealistic, lens flare` |
| 室内设计 | `soft morning light, hygge vibes, interplay of light and shadow, wide-angle f/8, Architectural Digest style` |
| 自然风景 | `golden hour, leading lines, foreground interest, misty atmosphere, telephoto lens, Turner-esque drama` |
| 野生动物 | `ultra-realistic wildlife photography, telephoto lens, high-speed shutter, intense gaze, detailed fur, bokeh` |
| 抽象艺术 | `minimalist modern art, geometric shapes, intentional negative space, vibrant saturated colors, gallery quality` |

---

## Part 8 — 通用场景专项词库（食物/时尚/建筑/自然）

> ⚠️ **适用范围：仅用于 Route B（风格锚点版本）的风格句生成，不影响 Route A（叙事流版本）。**  
> Route A 不使用任何来自本章节的风格词汇；本章节关键词仅追加在 Route B「视觉风格：」行，以及图生图（模式B）的 prompt 扩写中。  
> 补充 Part 7 的通用高频生图场景。

---

### Part 8.1 — 食物摄影（Food Photography）

#### 光线类
| 关键词 | 效果 |
|--------|------|
| `soft natural daylight` | 柔和自然日光 |
| `backlighting` | 逆光，突出轮廓与透光感 |
| `dramatic side lighting` | 戏剧性侧光，强调质感 |
| `golden hour warmth` | 黄金时段暖光 |
| `warm studio lighting` | 温暖影棚灯光 |

#### 质感/写实类
| 关键词 | 效果 |
|--------|------|
| `steam rising` | 升腾的蒸汽，传达热度与新鲜感 |
| `droplets of condensation` | 凝露水珠 |
| `glossy sheen` | 光泽感 |
| `melting cheese dripping` | 融化的芝士流淌 |
| `individual crumbs visible` | 细腻碎屑可见 |
| `crisp edges` | 清晰边缘 |
| `appetizing` | 令人垂涎 |
| `fresh ingredient garnish` | 新鲜装饰配料 |

#### 构图/角度类
| 关键词 | 效果 |
|--------|------|
| `overhead flat lay` | 俯视平铺构图 |
| `45-degree angle` | 45度角，展示层次 |
| `close-up shot` | 特写，强调质感 |
| `shallow depth of field` | 浅景深，虚化背景 |
| `styled but natural` | 摆拍但自然 |
| `food magazine style` | 食物杂志风格 |

#### 场景/背景类
| 关键词 | 效果 |
|--------|------|
| `rustic wooden board` | 粗糙木板，乡村感 |
| `dark moody background` | 深色忧郁背景，高端感 |
| `marble table` | 大理石桌面 |
| `fine dining plating` | 高档餐厅摆盘 |
| `editorial food photography` | 编辑式食物摄影 |

#### 完整示例提示词
```
Professional food photography of a juicy cheeseburger with melting cheddar dripping down the sides,
brioche bun with sesame seeds, crisp lettuce, shot with 85mm lens,
dramatic side lighting highlighting the textures, steam rising from the patty,
dark moody background, shallow depth of field, appetizing and photorealistic.
```

```
Flat lay top-down shot of a sophisticated breakfast spread with fresh berries, oats, and coffee,
bright airy natural daylight, marble table surface, food magazine editorial style,
individual ingredients clearly visible, slightly overhead perspective.
```

---

### Part 8.2 — 时尚/人像/美妆（Fashion / Portrait / Beauty）

#### 风格类
| 关键词 | 效果 |
|--------|------|
| `editorial` | 编辑风，杂志质感 |
| `high fashion` / `couture` | 高级时装感 |
| `avant-garde` | 先锋派，实验性 |
| `street style` | 街头风，自然随性 |
| `minimalist fashion` | 极简时装 |
| `glamorous` | 魅力四射 |
| `Vogue aesthetic` | Vogue 杂志美学 |

#### 美妆/妆容类
| 关键词 | 效果 |
|--------|------|
| `dewy skin` | 水润肌肤，发光感 |
| `glossy lips` | 水光唇 |
| `bold red lip` | 经典大红唇 |
| `smokey eyes` | 烟熏眼妆 |
| `natural makeup` | 自然妆，无妆感 |
| `wet hair look` | 湿发造型 |
| `intricate hair styling` | 精致发型 |

#### 面料/质感类
| 关键词 | 效果 |
|--------|------|
| `silk` / `satin sheen` | 丝绸/缎面光泽 |
| `velvet` | 天鹅绒质感 |
| `sheer chiffon` | 透明雪纺 |
| `tweed` | 斜纹软呢，经典感 |
| `metallic fabric` | 金属光泽面料 |
| `cashmere` | 羊绒，细腻柔软 |
| `beaded embroidery` | 珠绣装饰 |

#### 技术/灯光类
| 关键词 | 效果 |
|--------|------|
| `softbox key light` | 柔光箱主光 |
| `dramatic hard shadows` | 戏剧性硬阴影 |
| `backlight with rim glow` | 逆光轮廓光晕 |
| `studio strobe` | 闪光灯棚拍 |
| `natural window light` | 自然窗光 |
| `Rembrandt lighting` | 伦勃朗光 |
| `sharp focus on fabric texture` | 面料质感锐利对焦 |
| `creamy bokeh background` | 奶油感背景虚化 |

#### 避免AI感技巧（时尚人像专项）
- `natural skin texture` / `visible pores`（自然肤质/可见毛孔）
- `unedited skin texture`（未修图肤质）
- `subtle imperfections`（细微瑕疵）
- `natural expression`（自然表情）
- **明确手势**：`hand resting on neck`、`fingers loosely holding fabric`（减少手部错误）

**负向提示：** `--no plastic skin, cartoon, illustration, over-smoothed face, waxy skin`

#### 完整示例提示词
```
Close-up editorial portrait, dewy skin with natural texture and subtle freckles,
glossy lips, crystal statement earrings, white satin blouse with subtle sheen,
soft diffused window light with warm rim highlight,
85mm f/1.4 lens, creamy bokeh background, natural expression,
Vogue aesthetic, 8K photorealistic.
```

```
Full-body fashion shot, model in champagne satin dress, three-quarter view,
city lights in background creating warm bokeh, dramatic side lighting,
street style editorial, shot on Canon EOS R5 with 50mm lens.
```

---

### Part 8.3 — 建筑/室内设计（Architecture / Interior Design）

#### 建筑外观类
| 关键词 | 效果 |
|--------|------|
| `archdaily style` | ArchDaily 杂志级别质感 |
| `photorealistic architectural render` | 写实建筑渲染 |
| `warm light spilling from windows` | 窗户透出温暖灯光 |
| `golden hour` | 黄金时段光效 |
| `dramatic lighting with high contrast` | 高对比戏剧性光线 |
| `motion blur walking crowd` | 行人运动模糊，增加生气 |
| `lens flare effect` | 镜头光晕 |
| `cinematic wide-angle` | 电影感广角构图 |

#### 建筑风格类
| 关键词 | 效果 |
|--------|------|
| `minimalist contemporary` | 极简当代风 |
| `brutalism` | 粗野主义，裸露混凝土 |
| `mid-century modern` | 中世纪现代风 |
| `Japanese architecture` | 日式建筑美学 |
| `sustainable biophilic design` | 可持续亲生设计 |

#### 建筑材质类
| 关键词 | 效果 |
|--------|------|
| `exposed concrete` / `polished concrete` | 清水/抛光混凝土 |
| `glass curtain wall` | 玻璃幕墙 |
| `brick facade` | 砖砌立面 |
| `wooden slabs` | 木板条 |
| `calacatta gold marble` | 金色卡拉卡塔大理石 |
| `natural stone cladding` | 天然石材外墙 |
| `cast iron structure` | 铸铁结构 |

#### 室内设计类
| 关键词 | 效果 |
|--------|------|
| `soft morning light` | 柔和晨光 |
| `hygge vibes` | 北欧慵懒温暖感 |
| `interplay of light and shadow` | 光影交织 |
| `large windows flooding natural light` | 大窗自然采光 |
| `herringbone pattern` | 人字纹地板/墙面 |
| `warm ambient glow` | 温暖环境光晕 |
| `Architectural Digest feature quality` | 《建筑文摘》杂志质感 |
| `interior design magazine style` | 室内设计杂志风 |

#### 相机参数（建筑专用）
- `wide-angle lens 24mm`（建筑外观常用）
- `tilt-shift lens`（建筑垂直线校正）
- `narrow aperture f/8`（前后景清晰）
- `full-frame DSLR`（高解析度细节）
- `UHD 8K resolution`（超高清建筑细节）

#### 完整示例提示词
```
Photorealistic architectural render of a minimalist contemporary house at golden hour,
warm light spilling from large floor-to-ceiling windows onto the manicured lawn,
exposed concrete facade with wooden slabs, dramatic sky with scattered clouds,
cinematic wide-angle composition, archdaily style quality, 8K resolution.
```

```
Interior design photograph of a modern Japandi living room,
soft morning light filtering through sheer curtains creating interplay of light and shadow,
polished concrete floor, natural oak furniture, linen fabric sofa,
warm ambient glow from recessed lighting, hygge vibes,
wide-angle 24mm lens f/8, Architectural Digest editorial quality.
```

---

### Part 8.4 — 自然/风景/野生动物（Nature / Landscape / Wildlife）

#### 光线/时段类
| 关键词 | 效果 |
|--------|------|
| `golden hour` | 日出日落黄金时段 |
| `blue hour` | 蓝调时刻，神秘冷静 |
| `sunrise glowing orange clouds` | 日出橙色云彩 |
| `misty moody lighting` | 薄雾朦胧光线 |
| `dramatic backlighting` | 强烈逆光 |
| `diffused overcast light` | 阴天均匀柔光 |
| `twilight` | 黄昏，过渡色调 |
| `long exposure` | 长曝光，流水/星轨效果 |

#### 大气/天气类
| 关键词 | 效果 |
|--------|------|
| `misty atmosphere` | 薄雾氛围 |
| `sun rays breaking through canopy` | 阳光穿透树冠（丁达尔光） |
| `storm clouds building` | 积云涌现，张力感 |
| `Turner-esque drama` | 透纳式戏剧感（英国浪漫主义画风） |
| `blizzard` | 暴风雪 |
| `dewdrops on spider web` | 蜘蛛网上的露珠 |
| `frost crystals on leaf` | 叶片上的霜晶 |
| `reflections on still water` | 静水倒影 |

#### 野生动物专项
| 关键词 | 效果 |
|--------|------|
| `ultra-realistic wildlife photography` | 超写实野生动物摄影 |
| `telephoto lens` | 长焦镜头 |
| `high-speed shutter freezing motion` | 高速快门冻结动作 |
| `intense gaze into camera` | 专注凝视镜头 |
| `detailed fur and whiskers` | 毛发和胡须细节 |
| `intense bokeh background` | 强烈背景虚化 |
| `natural habitat` | 自然栖息地 |
| `behavioral moment` | 自然行为瞬间 |

#### 构图技巧类
| 关键词 | 效果 |
|--------|------|
| `leading lines` | 引导线 |
| `foreground interest` | 前景元素（增加层次） |
| `rule of thirds` | 三分法构图 |
| `tack sharp throughout` | 全程清晰锐利 |
| `wide-angle expansive composition` | 广角开阔构图 |
| `deep depth of field f/11` | 小光圈大景深 |
| `negative space in sky` | 天空留白 |

#### 完整示例提示词
```
Ultra-realistic wildlife photography of a snow leopard walking through a blizzard
on a steep Himalayan mountainside, intense gaze, detailed fur texture with individual hairs,
telephoto lens, high-speed shutter freezing snowflakes mid-air,
dramatic backlighting creating rim light on fur, intense bokeh background,
shot on Canon EOS R5, cinematic atmosphere, 8K.
```

```
Sweeping landscape photograph of Norwegian fjords at golden hour,
long shadows cast by low sun, foreground rocks leading the eye into the scene,
misty atmosphere over distant peaks, reflections on still water,
medium format camera, tack sharp from foreground to background,
Turner-esque dramatic sky with scattered warm clouds.
```

```
Astrophotography of the Milky Way over the Sahara desert at blue hour,
long exposure with pinpoint stars, galaxy visible as luminous band,
subtle moonlight illuminating foreground sand dunes,
wide-angle 21mm lens, deep depth of field, silhouetted lone palm tree.
```

---

### Part 8.5 — 抽象艺术/平面设计（Abstract / Graphic Design）

#### 风格类
| 关键词 | 效果 |
|--------|------|
| `minimalist modern art` | 极简现代艺术 |
| `geometric abstract shapes` | 几何抽象形状 |
| `flat color fields` | 平色块（致敬 Rothko） |
| `intentional negative space` | 刻意留白 |
| `paper cut art style` | 剪纸艺术风格 |
| `vintage travel poster` | 复古旅行海报 |
| `Bauhaus` | 包豪斯风格 |
| `Art Nouveau Mucha style` | 穆夏新艺术风 |
| `low poly 3D` | 低多边形3D |
| `isometric illustration` | 等距插图 |

#### 色彩/渲染类
| 关键词 | 效果 |
|--------|------|
| `vibrant saturated colors` | 鲜艳饱和色彩 |
| `muted earthy palette` | 哑光大地色系 |
| `limited color palette` | 有限色板 |
| `bold color blocks` | 大胆色块 |
| `subtle gradients` | 细腻渐变 |
| `gold accents` | 金色点缀 |
| `neon-drenched` | 霓虹浸透 |
| `monochromatic` | 单色系 |

#### 平面设计质量类
| 关键词 | 效果 |
|--------|------|
| `clean vector style` | 干净矢量风格 |
| `gallery quality` | 画廊级别 |
| `cohesive color palette` | 协调统一色板 |
| `no perspective distortion` | 无透视畸变 |
| `30-degree isometric angles` | 30度等距标准角度 |
| `large-scale wall piece` | 大尺寸墙面作品感 |

---

### Part 8.6 — 通用提升质量的技巧

#### 通用提示词结构公式
```
[What（主体+具体描述）] + [Doing What（动作/姿态）] + [Where（场景/环境）] +
[How It Looks（情绪/光线/色调）] + [Technical Flavor（摄影风格/参数）]
```

**示例对比：**
- ❌ 模糊：`"A chef cooking"`
- ✅ 结构化：`"A middle-aged Italian chef tossing pizza dough in a rustic trattoria kitchen, flour dust visible in warm afternoon light streaming through a window, candid documentary photography style"`

#### 高质量通用关键词
| 类别 | 关键词 |
|------|--------|
| 写实质量 | `photorealistic, hyperrealistic, hyper-detailed, cinematic` |
| 参考风格 | `award-winning photography, National Geographic style, Vogue editorial, ArchDaily quality` |
| 胶片质感 | `film grain, Kodak Portra 400, Kodak Vision3 500T, analog imperfections` |
| 光线通用 | `golden hour, rim lighting, chiaroscuro, three-point lighting, HDR dynamic range` |
| 相机通用 | `Hasselblad medium format, Canon EOS R5, 85mm f/1.4, shallow depth of field` |
| 渲染质感 | `Unreal Engine 5, PBR materials, soft global illumination, ambient occlusion` |

#### 常见错误与修正
| 错误写法 | 正确写法 |
|---------|---------|
| `beautiful, stunning, gorgeous` | 描述具体视觉信息：`sky transitioning from orange to purple at horizon` |
| `minimalist with lots of details` | 明确主次：`minimalist composition, single detailed ceramic object on clean white surface` |
| `no cars` | 语义描述：`an empty deserted street with no signs of traffic` |
| `4k, masterpiece, trending on ArtStation` | 已失效，改用具体镜头/光线/材质描述 |
| `exactly 34 years old` / `Pantone 2728C` | 避免无法精确执行的过度参数 |

#### 情绪优先原则
先写期望的情绪体验，再跟技术参数：
```
"A portrait that makes you feel you've known this person for years"
→ close framing, natural warm window light, soft focus everywhere but the eyes,
   slight smile with laugh lines, 85mm portrait lens, candid unposed moment
```

#### 对话迭代示例
```
第一步: "Generate a cozy cabin interior at dusk"
追加:   "Make it warmer — more firelight, add a dog sleeping by the fire"
继续:   "Pull back camera slightly to see more of the wooden architecture"
```

