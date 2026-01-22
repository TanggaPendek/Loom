/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // The "Creamy Cotton" Foundation
        cotton: "#FCFDFB",
        
        // "Vibrant Sage" (Growth & Primary) - emerald-500
        sage: {
          50: "#ecfdf5",
          100: "#d1fae5",
          200: "#a7f3d0",
          500: "#10b981", // Brand Primary
          600: "#059669",
        },

        // "Vibrant Rose" (Destructive & Highlights) - pink-500
        rose: {
          50: "#fdf2f8",
          100: "#fce7f3",
          500: "#ec4899", // High-Contrast Accent
          600: "#db2777",
        },
      },
      
      borderRadius: {
        // "Squircle" Geometry Logic
        'squircle-lg': '32px', // Main containers
        'squircle-sm': '20px', // Internal elements (buttons, inputs)
      },

      letterSpacing: {
        // High-Contrast CTA Typography logic (0.2em)
        'cta': '0.2em',
      },

      boxShadow: {
        // Botanical "Glow" instead of neutral grays
        'botanical': '0 10px 30px -5px rgba(16, 185, 129, 0.15)',
        'botanical-rose': '0 10px 30px -5px rgba(236, 72, 153, 0.2)',
      },

      // Backdrop blur for overlays (backdrop-blur-md)
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  plugins: [
    // Helper to inject the fractal noise texture via utility class
    function ({ addUtilities }) {
      addUtilities({
        '.bg-cotton-texture': {
          position: 'relative',
          '&::before': {
            content: '""',
            position: 'absolute',
            inset: '0',
            opacity: '0.05',
            pointerEvents: 'none',
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
          },
        },
      });
    },
  ],
};