import React from 'react';
import {
  TRIAL_SEQUENCE,
  type ParentNoteConfig,
  type ScreenId,
  type SetupState,
  type TrialResponse,
} from '../utils/focalLogic';

interface SessionRadarDrawerProps {
  open: boolean;
  onClose: () => void;
  setup: SetupState;
  responses: TrialResponse[];
  noteConfig: ParentNoteConfig;
  onNavigate: (screen: ScreenId) => void;
}

export const SessionRadarDrawer: React.FC<SessionRadarDrawerProps> = ({
  open,
  onClose,
  setup,
  responses,
  noteConfig,
  onNavigate,
}) => {
  // Compute 5-axis preparation profile (non-diagnostic readiness indicators, radius 20..80 from center 100,100)
  const checksCount = Object.values(setup.readinessChecks).filter(Boolean).length;
  const setupRatio = 0.35 + (checksCount / 4) * 0.65;
  const activityRatio =
    0.25 + (Math.min(responses.length, TRIAL_SEQUENCE.length) / TRIAL_SEQUENCE.length) * 0.75;
  const obsRatio =
    0.3 + (Math.min(noteConfig.selectedObservations.length, 5) / 5) * 0.7;
  const stepsRatio =
    0.35 + (Math.min(noteConfig.selectedNextSteps.length, 4) / 4) * 0.65;
  const contextRatio = setup.childLabel.trim().length > 0 ? 0.88 : 0.4;

  // 5 Pentagon vertices around (100, 100) with max radius 76
  const pt = (angleDeg: number, ratio: number) => {
    const rad = ((angleDeg - 90) * Math.PI) / 180;
    const r = 76 * ratio;
    const x = Math.round(100 + r * Math.cos(rad));
    const y = Math.round(100 + r * Math.sin(rad));
    return `${x},${y}`;
  };

  const polygonPoints = [
    pt(0, setupRatio),
    pt(72, activityRatio),
    pt(144, obsRatio),
    pt(216, stepsRatio),
    pt(288, contextRatio),
  ].join(' ');

  return (
    <div
      aria-hidden={!open}
      className={`fixed inset-0 z-50 transition-opacity duration-300 ${
        open
          ? 'pointer-events-auto opacity-100'
          : 'pointer-events-none opacity-0'
      }`}
    >
      {/* Backdrop */}
      <div
        onClick={onClose}
        className="absolute inset-0 bg-[#20304D]/25 backdrop-blur-xs"
      />

      {/* Slide-Over Panel */}
      <aside
        aria-label="Session Preparation Profile"
        className={`fixed inset-y-0 right-0 z-50 flex w-85 flex-col justify-between border-l border-[#20304D]/12 bg-white/95 p-6 shadow-2xl backdrop-blur-xl transition-transform duration-300 ease-in-out sm:w-96 ${
          open ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div>
          <div className="flex items-center justify-between border-b border-[#20304D]/10 pb-4">
            <div className="flex items-center gap-2.5">
              <svg
                className="h-5 w-5 text-[#286D65]"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                aria-hidden="true"
              >
                <circle cx="12" cy="12" r="9" />
                <circle cx="12" cy="12" r="4" />
                <path d="M12 3v3M12 18v3M3 12h3M18 12h3" />
              </svg>
              <h2 className="text-base font-bold text-[#20304D]">
                Family Prep Snapshot
              </h2>
            </div>

            <button
              type="button"
              onClick={onClose}
              aria-label="Close session snapshot drawer"
              className="flex h-9 w-9 items-center justify-center rounded-full border border-[#20304D]/12 text-[#20304D]/70 transition-colors hover:bg-[#F7F5F0] hover:text-[#20304D]"
            >
              <svg
                className="h-4 w-4"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>

          <p className="mt-3 text-xs leading-relaxed text-[#20304D]/75">
            This live preparation map updates as you complete setup checks, log
            directional E trials, and select home observations for your parent
            note.
          </p>

          {/* Dynamic SVG Radar Chart */}
          <div className="my-6 flex items-center justify-center">
            <svg
              viewBox="0 0 220 210"
              className="h-56 w-56 overflow-visible"
              role="img"
              aria-label="Five-axis preparation radar chart"
            >
              {/* Concentric Pentagon Web */}
              <polygon
                points="100,24 172,76 145,161 55,161 28,76"
                fill="#F7F5F0"
                stroke="#20304D"
                strokeOpacity="0.14"
                strokeWidth="1"
              />
              <polygon
                points="100,50 148,85 130,140 70,140 52,85"
                fill="none"
                stroke="#20304D"
                strokeOpacity="0.12"
                strokeWidth="1"
              />
              <polygon
                points="100,75 124,92 115,120 85,120 76,92"
                fill="none"
                stroke="#20304D"
                strokeOpacity="0.12"
                strokeWidth="1"
              />

              {/* Axis Lines */}
              <line
                x1="100"
                y1="100"
                x2="100"
                y2="24"
                stroke="#20304D"
                strokeOpacity="0.14"
              />
              <line
                x1="100"
                y1="100"
                x2="172"
                y2="76"
                stroke="#20304D"
                strokeOpacity="0.14"
              />
              <line
                x1="100"
                y1="100"
                x2="145"
                y2="161"
                stroke="#20304D"
                strokeOpacity="0.14"
              />
              <line
                x1="100"
                y1="100"
                x2="55"
                y2="161"
                stroke="#20304D"
                strokeOpacity="0.14"
              />
              <line
                x1="100"
                y1="100"
                x2="28"
                y2="76"
                stroke="#20304D"
                strokeOpacity="0.14"
              />

              {/* Dynamic Morphing Polygon */}
              <polygon
                points={polygonPoints}
                fill="rgba(40, 109, 101, 0.24)"
                stroke="#286D65"
                strokeWidth="2.2"
                className="transition-all duration-500 ease-out"
              />

              {/* Labels */}
              <text
                x="100"
                y="12"
                fill="#20304D"
                fontSize="10"
                fontWeight="600"
                textAnchor="middle"
              >
                Setup ({checksCount}/4)
              </text>
              <text
                x="180"
                y="78"
                fill="#20304D"
                fontSize="10"
                fontWeight="600"
                textAnchor="start"
              >
                Trials ({responses.length}/12)
              </text>
              <text
                x="152"
                y="178"
                fill="#20304D"
                fontSize="10"
                fontWeight="600"
                textAnchor="middle"
              >
                Observations ({noteConfig.selectedObservations.length})
              </text>
              <text
                x="48"
                y="178"
                fill="#20304D"
                fontSize="10"
                fontWeight="600"
                textAnchor="middle"
              >
                Next steps ({noteConfig.selectedNextSteps.length})
              </text>
              <text
                x="20"
                y="78"
                fill="#20304D"
                fontSize="10"
                fontWeight="600"
                textAnchor="end"
              >
                Child info
              </text>
            </svg>
          </div>

          {/* Live Session Summary Cards */}
          <div className="space-y-2.5">
            <div className="rounded-xl border border-[#20304D]/10 bg-[#F7F5F0] p-3.5 text-xs">
              <div className="flex items-center justify-between font-semibold text-[#20304D]">
                <span>Current child & distance</span>
                <span className="text-[#286D65]">{setup.ageGroup}</span>
              </div>
              <p className="mt-1 text-[#20304D]/75">
                {setup.childLabel} · {setup.distancePreset} ·{' '}
                {setup.glassesStatus}
              </p>
            </div>

            <div className="rounded-xl border border-[#20304D]/10 bg-[#F7F5F0] p-3.5 text-xs">
              <div className="flex items-center justify-between font-semibold text-[#20304D]">
                <span>Note recipient</span>
                <span className="text-[#286D65]">Draft ready</span>
              </div>
              <p className="mt-1 text-[#20304D]/75">{noteConfig.recipient}</p>
            </div>
          </div>
        </div>

        {/* Quick-Jump Pill Actions */}
        <div className="space-y-2 border-t border-[#20304D]/10 pt-4">
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => {
                onClose();
                onNavigate('setup');
              }}
              className="min-h-[42px] flex-1 rounded-full border border-[#20304D]/20 bg-white px-4 py-2 text-xs font-semibold text-[#10265F] transition-all hover:border-[#3E9BE0] hover:bg-[#F7F5F0] focus-visible:outline-2 focus-visible:outline-[#3E9BE0]"
            >
              Guided setup
            </button>
            <button
              type="button"
              onClick={() => {
                onClose();
                onNavigate('note');
              }}
              className="min-h-[42px] flex-1 rounded-full bg-[#10265F] px-4 py-2 text-xs font-semibold text-white transition-all hover:bg-[#0B1B46] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#3E9BE0]"
            >
              Open parent note
            </button>
          </div>
          <p className="text-center text-[11px] text-[#20304D]/60">
            Interact with observations or steps to watch the chart morph.
          </p>
        </div>
      </aside>
    </div>
  );
};
