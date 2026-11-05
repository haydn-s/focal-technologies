import React from 'react';
import {
  OBSERVATION_OPTIONS,
  TRIAL_SEQUENCE,
  type SetupState,
  type TrialDirection,
  type TrialResponse,
} from '../utils/focalLogic';

interface ActivityScreenProps {
  setup: SetupState;
  currentIndex: number;
  responses: TrialResponse[];
  selectedObservations: string[];
  onRecordAnswer: (direction: TrialDirection | 'unsure') => void;
  onStepBackTrial: () => void;
  onToggleObservation: (obs: string) => void;
  onExitToSetup: () => void;
  onFinishEarly: () => void;
}

const ROTATION_DEGREES: Record<TrialDirection, number> = {
  right: 0,
  down: 90,
  left: 180,
  up: 270,
};

export const ActivityScreen: React.FC<ActivityScreenProps> = ({
  setup,
  currentIndex,
  selectedObservations,
  onRecordAnswer,
  onStepBackTrial,
  onToggleObservation,
  onExitToSetup,
  onFinishEarly,
}) => {
  const trial = TRIAL_SEQUENCE[currentIndex] ?? TRIAL_SEQUENCE[0];
  const totalTrials = TRIAL_SEQUENCE.length;
  const rotation = ROTATION_DEGREES[trial.direction];

  return (
    <div className="bg-[#F7F5F0] py-8">
      <div className="mx-auto max-w-[960px] px-6">
        {/* Top Bar for Activity: Label, Progress, Back/Exit */}
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-[#20304D]/12 pb-4">
          <div className="flex flex-wrap items-center gap-2 text-xs font-semibold text-[#20304D]">
            <span>Illustrative activity — not a calibrated vision test</span>
            <span aria-hidden="true">·</span>
            <span className="font-normal text-[#20304D]/75">
              {setup.childLabel} <span aria-hidden="true">·</span> {setup.distancePreset}
            </span>
          </div>

          <div className="flex items-center gap-3">
            <span
              aria-live="polite"
              className="font-tabular text-sm font-semibold text-[#20304D]"
            >
              {trial.trialNumber} of {totalTrials}
            </span>

            {currentIndex > 0 && (
              <button
                type="button"
                onClick={onStepBackTrial}
                className="min-h-[44px] whitespace-nowrap shrink-0 rounded-lg border border-[#20304D]/20 bg-white px-3.5 py-2 text-xs font-semibold text-[#20304D] hover:border-[#3E9BE0] hover:bg-[#F7F5F0] focus-visible:outline-2 focus-visible:outline-[#3E9BE0]"
              >
                Previous letter
              </button>
            )}

            <button
              type="button"
              onClick={onExitToSetup}
              className="min-h-[44px] whitespace-nowrap shrink-0 rounded-lg border border-[#20304D]/20 bg-white px-3.5 py-2 text-xs font-semibold text-[#20304D] transition-colors duration-[180ms] hover:border-[#3E9BE0] hover:bg-[#F7F5F0] focus-visible:outline-2 focus-visible:outline-[#3E9BE0]"
            >
              Exit to setup
            </button>
          </div>
        </div>

        {/* Smooth Progress Bar Glide (Logo Bright Blue #3E9BE0) */}
        <div
          aria-hidden="true"
          className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-[#20304D]/10"
        >
          <div
            className="h-full rounded-full bg-[#3E9BE0] transition-all duration-250 ease-out"
            style={{ width: `${(trial.trialNumber / totalTrials) * 100}%` }}
          />
        </div>

        {/* Role Guidance & Practice Instruction */}
        <div className="mt-5 grid grid-cols-1 gap-4 rounded-xl border border-[#20304D]/12 bg-white p-4 sm:grid-cols-2 sm:p-5">
          <div>
            <p className="text-xs font-semibold tracking-wide text-[#10265F] uppercase">
              Child role ({trial.eyeUsed})
            </p>
            <p className="mt-1 text-sm text-[#20304D]/90">
              Stay at the {setup.distancePreset} mark (do not walk to the
              laptop) and point with your hand or arm in the direction the E
              opens.
            </p>
          </div>
          <div className="border-t border-[#20304D]/10 pt-3 sm:border-t-0 sm:border-l sm:pl-5 sm:pt-0">
            <p className="text-xs font-semibold tracking-wide text-[#20304D]/70 uppercase">
              Parent role (Screen-relative direction · No hints)
            </p>
            <p className="mt-1 text-sm text-[#20304D]/90">
              Sit to the side so you don’t block the screen. Record the
              direction your child points{' '}
              <strong className="font-semibold text-[#10265F]">
                relative to the screen
              </strong>{' '}
              (avoid reversing Left/Right when facing them) without hinting.
            </p>
          </div>
        </div>

        {/* Main Activity Grid: Fixed Optotype Stage + 4 Directional Buttons */}
        <div className="mt-6 grid grid-cols-1 items-center gap-8 rounded-xl border border-[#20304D]/12 bg-white p-6 sm:p-8 lg:grid-cols-12">
          {/* Left: High-Contrast Tumbling E in Fixed Container (No layout shift) */}
          <div className="flex flex-col items-center justify-center lg:col-span-6">
            <div className="mb-3 flex items-center gap-2 text-xs text-[#20304D]/70">
              <span>Display size tier: {trial.sizeTier}</span>
              <span aria-hidden="true">·</span>
              <span>{trial.eyeUsed}</span>
            </div>

            <div
              data-testid="optotype-stage"
              className="flex h-[220px] w-[220px] items-center justify-center rounded-xl border-2 border-[#20304D]/15 bg-white"
            >
              {/* Crisp 5x5 Snellen-proportioned Tumbling E SVG with 220ms trial switch transition */}
              <div
                key={trial.trialNumber}
                className="animate-trial-switch flex items-center justify-center"
              >
                <svg
                  width={trial.pixelSize}
                  height={trial.pixelSize}
                  viewBox="0 0 100 100"
                  role="img"
                  aria-label={`Tumbling E pointing ${trial.direction}`}
                  style={{ transform: `rotate(${rotation}deg)` }}
                >
                  <path
                    fill="#20304D"
                    d="M0 0 H100 V20 H20 V40 H100 V60 H20 V80 H100 V100 H0 Z"
                  />
                </svg>
              </div>
            </div>

            <p className="mt-3 text-xs text-[#20304D]/65">
              Letter size stays fixed during this trial ({trial.pixelSize}px
              preview scale).
            </p>
          </div>

          {/* Right: 4 Large Directional Answer Buttons */}
          <div className="flex flex-col items-center lg:col-span-6">
            <p className="mb-4 text-sm font-semibold text-[#10265F]">
              Which way did your child point?
            </p>

            <div className="grid w-full max-w-[340px] grid-cols-3 gap-3">
              <div />
              <button
                type="button"
                onClick={() => onRecordAnswer('up')}
                aria-label="Pointing Up"
                className="flex min-h-[64px] flex-col items-center justify-center rounded-xl border border-[#20304D]/20 bg-[#F7F5F0] px-4 py-3 text-sm font-semibold text-[#20304D] transition-all duration-[180ms] hover:-translate-y-0.5 hover:border-[#10265F] hover:bg-[#10265F]/[0.05] hover:text-[#10265F] focus-visible:outline-2 focus-visible:outline-[#3E9BE0]"
              >
                <svg
                  className="h-6 w-6"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.2"
                  aria-hidden="true"
                >
                  <path d="M12 19V5M5 12l7-7 7 7" />
                </svg>
                <span className="mt-1">Up</span>
              </button>
              <div />

              <button
                type="button"
                onClick={() => onRecordAnswer('left')}
                aria-label="Pointing Left"
                className="flex min-h-[64px] flex-col items-center justify-center rounded-xl border border-[#20304D]/20 bg-[#F7F5F0] px-4 py-3 text-sm font-semibold text-[#20304D] transition-all duration-[180ms] hover:-translate-y-0.5 hover:border-[#10265F] hover:bg-[#10265F]/[0.05] hover:text-[#10265F] focus-visible:outline-2 focus-visible:outline-[#3E9BE0]"
              >
                <svg
                  className="h-6 w-6"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.2"
                  aria-hidden="true"
                >
                  <path d="M19 12H5M12 19l-7-7 7-7" />
                </svg>
                <span className="mt-1">Left</span>
              </button>

              <div className="flex items-center justify-center rounded-xl border border-dashed border-[#20304D]/15 bg-[#F7F5F0]/40 text-xs font-medium text-[#20304D]/60">
                Trial {trial.trialNumber}/{totalTrials}
              </div>

              <button
                type="button"
                onClick={() => onRecordAnswer('right')}
                aria-label="Pointing Right"
                className="flex min-h-[64px] flex-col items-center justify-center rounded-xl border border-[#20304D]/20 bg-[#F7F5F0] px-4 py-3 text-sm font-semibold text-[#20304D] transition-all duration-[180ms] hover:-translate-y-0.5 hover:border-[#10265F] hover:bg-[#10265F]/[0.05] hover:text-[#10265F] focus-visible:outline-2 focus-visible:outline-[#3E9BE0]"
              >
                <svg
                  className="h-6 w-6"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.2"
                  aria-hidden="true"
                >
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
                <span className="mt-1">Right</span>
              </button>

              <div />
              <button
                type="button"
                onClick={() => onRecordAnswer('down')}
                aria-label="Pointing Down"
                className="flex min-h-[64px] flex-col items-center justify-center rounded-xl border border-[#20304D]/20 bg-[#F7F5F0] px-4 py-3 text-sm font-semibold text-[#20304D] transition-all duration-[180ms] hover:-translate-y-0.5 hover:border-[#10265F] hover:bg-[#10265F]/[0.05] hover:text-[#10265F] focus-visible:outline-2 focus-visible:outline-[#3E9BE0]"
              >
                <svg
                  className="h-6 w-6"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.2"
                  aria-hidden="true"
                >
                  <path d="M12 5v14M19 12l-7 7-7-7" />
                </svg>
                <span className="mt-1">Down</span>
              </button>
              <div />
            </div>

            <div className="mt-4 flex w-full max-w-[340px] flex-wrap items-center justify-between gap-2">
              <button
                type="button"
                onClick={() => onRecordAnswer('unsure')}
                className="min-h-[44px] flex-1 whitespace-nowrap rounded-lg border border-[#20304D]/20 bg-white px-4 py-2 text-xs font-semibold text-[#20304D] hover:border-[#3E9BE0] hover:bg-[#F7F5F0] focus-visible:outline-2 focus-visible:outline-[#3E9BE0]"
              >
                Not sure / hesitated
              </button>

              <button
                type="button"
                onClick={onFinishEarly}
                className="min-h-[44px] whitespace-nowrap rounded-lg px-3 py-2 text-xs font-semibold text-[#10265F] underline decoration-[#3E9BE0] underline-offset-4 hover:text-[#3E9BE0] focus-visible:outline-2 focus-visible:outline-[#3E9BE0]"
              >
                Finish & view summary
              </button>
            </div>
          </div>
        </div>

        {/* Quick Observation Checkboxes during Activity */}
        <section
          aria-label="Record parent observations during activity"
          className="mt-6 rounded-xl border border-[#20304D]/12 bg-white p-5"
        >
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <h2 className="text-sm font-semibold text-[#20304D]">
              What are you noticing right now? (Optional — adds to your parent
              note)
            </h2>
            <span className="text-xs text-[#20304D]/65">
              {selectedObservations.length} selected
            </span>
          </div>

          <div className="mt-3 grid grid-cols-1 gap-2.5 sm:grid-cols-2">
            {OBSERVATION_OPTIONS.slice(1, 5).map((obs) => {
              const active = selectedObservations.includes(obs);
              return (
                <button
                  key={obs}
                  type="button"
                  aria-pressed={active}
                  onClick={() => onToggleObservation(obs)}
                  className={`min-h-[44px] rounded-lg border px-3.5 py-2 text-left text-xs font-medium transition-colors ${
                    active
                      ? 'border-[#286D65] bg-[#E5EEE8] font-semibold text-[#20304D]'
                      : 'border-[#20304D]/15 bg-[#F7F5F0]/50 text-[#20304D]/85 hover:bg-[#F7F5F0]'
                  }`}
                >
                  {active ? '✓ ' : '+ '}
                  {obs}
                </button>
              );
            })}
          </div>
        </section>
      </div>
    </div>
  );
};
