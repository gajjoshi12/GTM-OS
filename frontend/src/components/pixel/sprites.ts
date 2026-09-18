/**
 * Pixel-art avatar system for the AI agents.
 *
 * Every agent gets a distinct little character, derived deterministically from
 * its key — so the Paid Media Agent looks the same every time you open the app,
 * on every machine, with no image assets to ship.
 *
 * A sprite is a stack of 32x32 layers. Each layer is 32 strings of 32 chars,
 * one char per pixel, painted in order. '.' is transparent.
 *
 *   o outline   k skin      d skin shadow   w eye white   p pupil
 *   m mouth     b blush     H hair          h hair light  C cloth
 *   c cloth accent          W cloth panel   G gold        S sweat
 *
 * 32x32 rather than 24x24 specifically so the eyes get four rows — at 24 they
 * collapse into featureless white blocks and the faces stop reading as faces.
 */

export const GRID = 32

export type Layer = readonly string[]

/* ------------------------------------------------------------------ base body */
//        0         1         2         3
//        0123456789012345678901234567890 1
const BASE: Layer = [
  '................................',
  '................................',
  '................................',
  '...........oooooooooo...........',
  '.........okkkkkkkkkkkko.........',
  '........okkkkkkkkkkkkkko........',
  '.......okkkkkkkkkkkkkkkko.......',
  '.......okkkkkkkkkkkkkkkko.......',
  '.......okkkkkkkkkkkkkkkko.......',
  '.......okkkkkkkkkkkkkkkko.......',
  '.......okkwwwwkkkkwwwwkko.......',
  '.......okkwwpwkkkkwwpwkko.......',
  '.......okkwppwkkkkwppwkko.......',
  '.......okkwwwwkkkkwwwwkko.......',
  '.......okkkkkkkkkkkkkkkko.......',
  '.......okbbkkkkkkkkkkbbko.......',
  '.......okkkkkkkmmkkkkkkko.......',
  '........okkkkkkkkkkkkkko........',
  '.........okkkkkkkkkkkko.........',
  '.............okkkko.............',
  '..........oCCCCCCCCCCo..........',
  '........oCCCCCCCCCCCCCCo........',
  '........oCCCCCCCCCCCCCCo........',
  '........oCCCCCkkkkCCCCCo........',
  '........oCCCCWWkkWWCCCCo........',
  '........oCCCWWWWWWWWCCCo........',
  '........oCCCWWcWWcWWCCCo........',
  '........oCCCCWWWWWWCCCCo........',
  '........oCCCCCCCCCCCCCCo........',
  '........oCGGGGGGGGGGGGCo........',
  '........oCCCCCCCCCCCCCCo........',
  '........oooooooooooooooo........',
]

/** Eyes shut — the blink frame. */
const BASE_BLINK: Layer = BASE.map((row, i) => {
  if (i === 10 || i === 11 || i === 13) return '.......okkkkkkkkkkkkkkkko.......'
  if (i === 12) return '.......okkppppkkkkppppkko.......'
  return row
})

/** Eyes dropped to the keyboard — used while an agent is working. */
const BASE_FOCUS: Layer = BASE.map((row, i) => {
  if (i === 10 || i === 11) return '.......okkwwwwkkkkwwwwkko.......'
  if (i === 12 || i === 13) return '.......okkwppwkkkkwppwkko.......'
  return row
})

/* ------------------------------------------------------------------ hair */

const blank = (): string[] => Array.from({ length: GRID }, () => '.'.repeat(GRID))

function layer(rows: Record<number, string>): Layer {
  const g = blank()
  for (const [i, s] of Object.entries(rows)) g[Number(i)] = s
  return g
}

const HAIR: Record<string, Layer> = {
  // Big curly volume — closest to the reference avatar.
  afro: layer({
    0: '........HHHHHHHHHHHHHHHH........',
    1: '......HHHHHHHHHHHHHHHHHHHH......',
    2: '.....HHHHHHHHHHHHHHHHHHHHHH.....',
    3: '....HHHHHHHHHHHHHHHHHHHHHHHH....',
    4: '....HHHHHHHhhhhhhhhhhHHHHHHH....',
    5: '...HHHHHh..............hHHHHH...',
    6: '...HHHHH................HHHHH...',
    7: '...HHHH..................HHHH...',
    8: '...HHHH..................HHHH...',
    9: '...HHH....................HHH...',
    10: '...HHH....................HHH...',
    11: '...HHH....................HHH...',
    12: '...HHH....................HHH...',
    13: '...HHH....................HHH...',
    14: '...HHH....................HHH...',
    15: '...HHHH..................HHHH...',
    16: '....HHH..................HHH....',
    17: '....HHH..................HHH....',
    18: '.....HH..................HH.....',
    19: '.....H....................H.....',
  }),
  long: layer({
    0: '..........HHHHHHHHHHHH..........',
    1: '........HHHHHHHHHHHHHHHH........',
    2: '.......HHHHHHHHHHHHHHHHHH.......',
    3: '......HHHHHHHHHHHHHHHHHHHH......',
    4: '......HHHHHhhhhhhhhhhHHHHH......',
    5: '.....HHHH..............HHHH.....',
    6: '.....HHHH..............HHHH.....',
    7: '.....HHHH..............HHHH.....',
    8: '.....HHHH..............HHHH.....',
    9: '.....HHHH..............HHHH.....',
    10: '.....HHHH..............HHHH.....',
    11: '.....HHHH..............HHHH.....',
    12: '.....HHHH..............HHHH.....',
    13: '.....HHHH..............HHHH.....',
    14: '.....HHHH..............HHHH.....',
    15: '.....HHHH..............HHHH.....',
    16: '.....HHHH..............HHHH.....',
    17: '.....HHHH..............HHHH.....',
    18: '.....HHHH..............HHHH.....',
    19: '.....HHHH..............HHHH.....',
    20: '.....HHHH..............HHHH.....',
    21: '.....HHHH..............HHHH.....',
    22: '......HHH..............HHH......',
    23: '......HH................HH......',
  }),
  bob: layer({
    0: '........HHHHHHHHHHHHHHHH........',
    1: '......HHHHHHHHHHHHHHHHHHHH......',
    2: '.....HHHHHHHHHHHHHHHHHHHHHH.....',
    3: '....HHHHHHHHHHHHHHHHHHHHHHHH....',
    4: '....HHHHHHHhhhhhhhhhhHHHHHHH....',
    5: '...HHHH..................HHHH...',
    6: '...HHHH..................HHHH...',
    7: '...HHHH..................HHHH...',
    8: '...HHHH..................HHHH...',
    9: '...HHHH..................HHHH...',
    10: '...HHHH..................HHHH...',
    11: '...HHHH..................HHHH...',
    12: '...HHHH..................HHHH...',
    13: '...HHHH..................HHHH...',
    14: '...HHHH..................HHHH...',
    15: '...HHHH..................HHHH...',
    16: '...HHHHH................HHHHH...',
    17: '...HHHHH................HHHHH...',
    18: '....HHHH................HHHH....',
    19: '.....HH..................HH.....',
  }),
  ponytail: layer({
    0: '........HHHHHHHHHHHHHHHH........',
    1: '......HHHHHHHHHHHHHHHHHHHH......',
    2: '.....HHHHHHHHHHHHHHHHHHHHHH.....',
    3: '....HHHHHHHHHHHHHHHHHHHHHHHH....',
    4: '....HHHHHHHhhhhhhhhhhHHHHHHH....',
    5: '...HHHH..................HHHH...',
    6: '...HHHH..................HHHHHH.',
    7: '...HHHH..................HHHHHHH',
    8: '...HHHH..................HHHHHHH',
    9: '...HHHH..................HHHHHHH',
    10: '...HHHH..................HHHHHHH',
    11: '...HHHH..................HHHHHHH',
    12: '...HHHH..................HHHHHH.',
    13: '...HHHH..................HHHHH..',
    14: '...HHHH..................HHHH...',
    15: '...HHHH..................HHHH...',
    16: '....HHH..................HHH....',
    17: '.....HH..................HH.....',
  }),
  crop: layer({
    2: '.......HHHHHHHHHHHHHHHHHH.......',
    3: '.....HHHHHHHHHHHHHHHHHHHHHH.....',
    4: '.....HHHHHHhhhhhhhhhhHHHHHH.....',
    5: '.....HHHH..............HHHH.....',
    6: '.....HHH................HHH.....',
    7: '.....HHH................HHH.....',
    8: '......HH................HH......',
    9: '......H..................H......',
  }),
  bun: layer({
    0: '.............HHHHHH.............',
    1: '............HHHHHHHH............',
    2: '...........HHHHHHHHHH...........',
    3: '........HHHHHHHHHHHHHHHH........',
    4: '......HHHHHHHHHHHHHHHHHHHH......',
    5: '.....HHHHHHhhhhhhhhhhHHHHHH.....',
    6: '....HHHH................HHHH....',
    7: '....HHH..................HHH....',
    8: '....HHH..................HHH....',
    9: '....HHH..................HHH....',
    10: '....HHH..................HHH....',
    11: '....HHH..................HHH....',
    12: '....HHH..................HHH....',
    13: '....HHH..................HHH....',
    14: '....HHH..................HHH....',
    15: '.....HH..................HH.....',
    16: '.....H....................H.....',
  }),
}
export const HAIR_STYLES = Object.keys(HAIR)

/* ------------------------------------------------------------------ accessories */

const ACCESSORY: Record<string, Layer> = {
  none: blank(),
  // Gold hoops, like the reference.
  earrings: layer({
    14: '......G..................G......',
    15: '......G..................G......',
    16: '.......G................G.......',
  }),
  glasses: layer({
    9: '.........oooooo..oooooo.........',
    10: '.........o....oooo....o.........',
    11: '.........o....o..o....o.........',
    12: '.........o....o..o....o.........',
    13: '.........o....o..o....o.........',
    14: '.........oooooo..oooooo.........',
  }),
  // Headset for the agents that talk to people.
  headset: layer({
    2: '..........oooooooooooo..........',
    3: '........ooo..........ooo........',
    4: '.......oo..............oo.......',
    10: '.....GGG................GGG.....',
    11: '.....GGG................GGG.....',
    12: '.....GGG................GGG.....',
    13: '.....GGG................GGG.....',
    14: '.....GGG................GGG.....',
    15: '.....GG.........................',
    16: '......GG........................',
    17: '.......GG.......................',
  }),
  collar: layer({ 20: '..........oGGGGGGGGGGo..........' }),
}
export const ACCESSORIES = Object.keys(ACCESSORY)

/* ------------------------------------------------------------------ arms */

const ARMS = {
  rest: layer({
    23: '......CC................CC......',
    24: '......kk................kk......',
    25: '......oo................oo......',
  }),
  typeA: layer({
    21: '......CC................CC......',
    22: '......kk................kk......',
    23: '......oo................oo......',
  }),
  typeB: layer({
    20: '......CC................CC......',
    21: '......kk................kk......',
    22: '......oo................oo......',
  }),
}

/** A little sweat bead for the error state. */
const SWEAT: Layer = layer({
  6: '.........................SS.....',
  7: '.........................SS.....',
})

/* ------------------------------------------------------------------ palettes */

const SKIN: [string, string][] = [
  ['#f7d7bb', '#e3b795'], ['#efc59b', '#d4a175'], ['#dba26a', '#bb8450'],
  ['#b67c4d', '#94603a'], ['#8d5524', '#6d3f18'], ['#5f3719', '#452510'],
]
const HAIR_COLOR: [string, string][] = [
  ['#241c18', '#40332b'], ['#3d2b1f', '#5c4331'], ['#6b4226', '#8c5b36'],
  ['#a9682f', '#c98748'], ['#d9a441', '#efc46a'], ['#2b3a67', '#43578f'],
  ['#6d4bd6', '#8f72e8'], ['#b33a2e', '#d15a4a'],
]
/** Cloth colours reuse the chart series slots so the team matches the brand. */
const CLOTH: [string, string][] = [
  ['#3987e5', '#2a6bb8'], ['#d95926', '#b3441c'], ['#199e70', '#127a56'],
  ['#c98500', '#a06a00'], ['#d55181', '#ad3e66'], ['#9085e9', '#7268c7'],
  ['#e66767', '#bf5050'], ['#2f3b52', '#232d3f'],
]

export type Palette = Record<string, string>

function paletteFor(skin: number, hair: number, cloth: number): Palette {
  const [k, d] = SKIN[skin % SKIN.length]
  const [H, h] = HAIR_COLOR[hair % HAIR_COLOR.length]
  const [C, c] = CLOTH[cloth % CLOTH.length]
  return {
    o: '#20191a', k, d, w: '#ffffff', p: '#241d20', m: '#8c4038', b: '#e58b8b',
    H, h, C, c, W: '#efe6d2', G: '#e8b13f', S: '#7fd3ef',
  }
}

/* ------------------------------------------------------------------ the character */

export type Look = {
  hair: string
  accessory: string
  skin: number
  hairColor: number
  cloth: number
  palette: Palette
}

/** FNV-1a — small, fast, stable across machines. */
function hash(s: string): number {
  let h = 2166136261
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619) }
  return h >>> 0
}
const pick = <T,>(arr: readonly T[], seed: string, salt: string): T => arr[hash(seed + salt) % arr.length]

/** Agents whose job involves talking to people get a headset, and so on. */
const FORCED_ACCESSORY: Record<string, string> = {
  sdr: 'headset', reply_intelligence: 'headset', cmo: 'collar',
  analytics: 'glasses', attribution: 'glasses', revenue_intelligence: 'glasses',
  compliance: 'glasses', brand_manager: 'earrings',
}

export function lookFor(seed: string): Look {
  const hair = pick(HAIR_STYLES, seed, 'hair')
  const accessory = FORCED_ACCESSORY[seed] ?? pick(ACCESSORIES, seed, 'acc')
  const skin = hash(seed + 'skin') % SKIN.length
  const hairColor = hash(seed + 'hc') % HAIR_COLOR.length
  const cloth = hash(seed + 'cl') % CLOTH.length
  return { hair, accessory, skin, hairColor, cloth, palette: paletteFor(skin, hairColor, cloth) }
}

/* ------------------------------------------------------------------ frames */

export type FrameName = 'idle' | 'blink' | 'work1' | 'work2' | 'error'

function stack(look: Look, frame: FrameName): Layer[] {
  const hair = HAIR[look.hair] ?? HAIR.bob
  const acc = ACCESSORY[look.accessory] ?? ACCESSORY.none
  switch (frame) {
    case 'blink': return [BASE_BLINK, ARMS.rest, hair, acc]
    case 'work1': return [BASE_FOCUS, ARMS.typeA, hair, acc]
    case 'work2': return [BASE_FOCUS, ARMS.typeB, hair, acc]
    case 'error': return [BASE_BLINK, ARMS.rest, hair, acc, SWEAT]
    default: return [BASE, ARMS.rest, hair, acc]
  }
}

const cache = new Map<string, string>()

/** Paint one frame to a data URL. Memoised — 38 agents share a handful of canvases. */
export function frameUrl(seed: string, frame: FrameName): string {
  const key = `${seed}:${frame}`
  const hit = cache.get(key)
  if (hit) return hit

  const look = lookFor(seed)
  const canvas = document.createElement('canvas')
  canvas.width = GRID
  canvas.height = GRID
  const ctx = canvas.getContext('2d')
  if (!ctx) return ''

  for (const l of stack(look, frame)) {
    for (let y = 0; y < GRID; y++) {
      const row = l[y] ?? ''
      for (let x = 0; x < GRID; x++) {
        const ch = row[x]
        if (!ch || ch === '.') continue
        const colour = look.palette[ch]
        if (!colour) continue
        ctx.fillStyle = colour
        ctx.fillRect(x, y, 1, 1)
      }
    }
  }
  const url = canvas.toDataURL()
  cache.set(key, url)
  return url
}

/* Dev guard: every row of every layer must be exactly GRID wide, or the art skews. */
if (import.meta.env?.DEV) {
  const check = (name: string, l: Layer) =>
    l.forEach((r, i) => {
      if (r.length !== GRID) console.error(`[pixel] ${name} row ${i} is ${r.length}px, expected ${GRID}`)
    })
  check('BASE', BASE)
  Object.entries(HAIR).forEach(([n, l]) => check(`hair:${n}`, l))
  Object.entries(ACCESSORY).forEach(([n, l]) => check(`acc:${n}`, l))
  Object.entries(ARMS).forEach(([n, l]) => check(`arms:${n}`, l))
}
