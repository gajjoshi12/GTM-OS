/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      colors: {
        ink: { 950: '#07080c', 900: '#0b0d13', 850: '#0f121a', 800: '#141826', 700: '#1c2133', 600: '#262c40' },
        line: 'rgba(255,255,255,0.08)',
        accent: { DEFAULT: '#7c6cff', soft: '#a99cff', cyan: '#22d3ee', mint: '#34d399', amber: '#fbbf24', rose: '#fb7185' },
        s1: '#3987e5', s2: '#d95926', s3: '#199e70', s4: '#c98500', s5: '#d55181', s6: '#9085e9', s7: '#e66767',
      },
      boxShadow: {
        glass: '0 1px 0 rgba(255,255,255,0.06) inset, 0 20px 60px -30px rgba(0,0,0,0.8)',
        glow: '0 0 0 1px rgba(124,108,255,0.35), 0 0 40px -10px rgba(124,108,255,0.6)',
        cyan: '0 0 0 1px rgba(34,211,238,0.35), 0 0 40px -10px rgba(34,211,238,0.6)',
      },
      backgroundImage: {
        'grid-fade': 'linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px)',
      },
      keyframes: {
        float: { '0%,100%': { transform: 'translateY(0px)' }, '50%': { transform: 'translateY(-8px)' } },
        pulseRing: { '0%': { transform: 'scale(0.9)', opacity: '0.8' }, '100%': { transform: 'scale(1.8)', opacity: '0' } },
        shimmer: { '0%': { backgroundPosition: '-200% 0' }, '100%': { backgroundPosition: '200% 0' } },
        aurora: { '0%,100%': { transform: 'translate(0,0) scale(1)' }, '33%': { transform: 'translate(6%, -4%) scale(1.08)' }, '66%': { transform: 'translate(-5%, 5%) scale(0.96)' } },
        orbit: { from: { transform: 'rotate(0deg)' }, to: { transform: 'rotate(360deg)' } },
      },
      animation: {
        float: 'float 6s ease-in-out infinite',
        pulseRing: 'pulseRing 1.8s cubic-bezier(0.2,0.7,0.3,1) infinite',
        shimmer: 'shimmer 2.2s linear infinite',
        aurora: 'aurora 18s ease-in-out infinite',
        orbit: 'orbit 40s linear infinite',
      },
    },
  },
  plugins: [],
}
