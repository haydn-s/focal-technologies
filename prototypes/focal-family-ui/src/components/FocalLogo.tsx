import React from 'react';

interface FocalLogoProps {
  className?: string;
  showFamilyTag?: boolean;
}

/**
 * Renders the official Focal Technologies horizontal lockup from
 * /assets/aistudio/focal-lockup_aebb44cd.svg as crisp inline SVG.
 */
export const FocalLogo: React.FC<FocalLogoProps> = ({
  className = 'h-10 w-auto',
  showFamilyTag = false,
}) => {
  return (
    <div className="inline-flex items-center gap-2.5 shrink-0">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 232 96"
        role="img"
        aria-label="Focal Technologies"
        className={className}
      >
        <title>Focal Technologies — horizontal lockup</title>
        <circle
          cx="40"
          cy="46"
          r="28"
          fill="none"
          stroke="#10265F"
          strokeWidth="4.4"
          strokeDasharray="23.2 6.12"
          transform="rotate(15 40 46)"
        />
        <circle cx="40" cy="46" r="21.2" fill="#FFFFFF" />
        <circle cx="40" cy="46" r="14.5" fill="#3E9BE0" />
        <circle cx="40" cy="46" r="6.3" fill="#071634" />
        <text
          x="88"
          y="50"
          fontFamily="Archivo, 'Plus Jakarta Sans', 'Helvetica Neue', Arial, sans-serif"
          fontSize="42"
          fontWeight="700"
          letterSpacing="-0.8"
          fill="#10265F"
        >
          Focal
        </text>
        <text
          x="90"
          y="73"
          fontFamily="Archivo, 'Plus Jakarta Sans', 'Helvetica Neue', Arial, sans-serif"
          fontSize="13"
          fontWeight="500"
          letterSpacing="3.1"
          fill="#3E9BE0"
        >
          Technologies
        </text>
      </svg>
      {showFamilyTag && (
        <span className="text-xs font-semibold tracking-wider text-[#286D65] uppercase">
          Family
        </span>
      )}
    </div>
  );
};
