import React from 'react';

/**
 * Ambient flowing gradient localized strictly behind the right-hand hero card:
 * - Warm off-white (#F7F5F0) base across the page and left text column
 * - Soft, pale teal-sage gradient behind the upper-right card
 * - Subtle warm apricot accent behind the lower-right corner of the card
 * - GPU-composited smooth flowing motion (no tiles, no mouse tracking, no frame drops)
 * - Respects prefers-reduced-motion via CSS
 */
export const OpticalHeroBackground: React.FC = () => {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none absolute inset-0 z-0 overflow-hidden"
    >
      {/* Right-side pale teal-sage flowing gradient aura behind the hero card */}
      <div className="ambient-teal-flow absolute top-2 right-[-4%] h-[420px] w-[500px] rounded-full lg:right-[2%] lg:h-[460px] lg:w-[540px]" />

      {/* Bottom-right soft apricot flowing accent behind the lower-right of the hero card */}
      <div className="ambient-apricot-flow absolute top-[230px] right-[-6%] h-[340px] w-[380px] rounded-full lg:top-[250px] lg:right-[-1%] lg:h-[360px] lg:w-[420px]" />
    </div>
  );
};
