import React from 'react';
import {
  OBSERVATION_OPTIONS,
  TRIAL_SEQUENCE,
  summarizeTrialResponses,
  type SetupState,
  type TrialResponse,
} from '../utils/focalLogic';

interface CompletionScreenProps {
  setup: SetupState;
  responses: TrialResponse[];
  selectedObservations: string[];
  onToggleObservation: (obs: string) => void;
  onPrepareParentNote: () => void;
  onViewHistory: () => void;
  onRestartActivity: () => void;
}

export const CompletionScreen: React.FC<CompletionScreenProps> = ({
  setup,
  responses,
  selectedObservations,
  onToggleObservation,
  onPrepareParentNote,
  onViewHistory,
  onRestartActivity,
}) => {
  const summary = summarizeTrialResponses(responses);

  return (
    <div className="mx-auto max-w-[920px] px-6 py-10">
      <div className="animate-reveal-up rounded-2xl border border-[#20304D]/12 bg-white p-6 shadow-xs sm:p-8">
        <p className="text-xs font-semibold tracking-wider text-[#286D65] uppercase">
          Activity complete <span aria-hidden="true">·</span> Next-step preparation
        </p>
        <h1 className="mt-2 text-2xl font-semibold text-[#10265F] sm:text-3xl">
          Activity summary and observations for {setup.childLabel}
        </h1>
        <p className="mt-2 text-sm leading-relaxed text-[#20304D]/80">
          Here is a neutral record of how the directional letter activity went at{' '}
          {setup.distancePreset}. Use these observations to prepare your note
          for an eye doctor or school nurse.
        </p>

        {/* Prominent reminder to keep any professional follow-up already requested (Auxiliary light teal prompt) */}
        <section
          aria-label="Professional follow-up reminder"
          className="animate-reveal-up animate-reveal-delay-1 mt-6 rounded-xl border border-[#286D65]/25 bg-[#E5EEE8] p-5"
        >
          <h2 className="text-sm font-semibold text-[#10265F]">
            Important: Keep any professional follow-up already requested
          </h2>
          <p className="mt-1.5 text-sm leading-relaxed text-[#20304D]/85">
            Even if your child matched most or all directional shapes at home,
            this uncalibrated activity cannot rule out farsightedness,
            astigmatism, eye teaming differences, or other vision needs. Always
            complete any vision referral or comprehensive eye exam recommended
            by your school nurse or pediatrician.
          </p>
        </section>

        {/* Neutral Activity Summary */}
        <section
          aria-labelledby="neutral-summary-heading"
          className="animate-reveal-up animate-reveal-delay-2 mt-7 border-t border-[#20304D]/10 pt-6"
        >
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <h2
              id="neutral-summary-heading"
              className="text-base font-semibold text-[#10265F]"
            >
              Neutral activity log
            </h2>
            <span className="text-xs text-[#20304D]/65">
              Illustrative interaction responses — not a clinical acuity score
            </span>
          </div>

          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-xl bg-[#F7F5F0] p-4 transition-transform duration-200 hover:-translate-y-0.5">
              <span className="text-xs text-[#20304D]/70">
                Trials completed
              </span>
              <p className="mt-1 font-tabular text-xl font-semibold text-[#10265F]">
                {summary.totalCompleted} of {TRIAL_SEQUENCE.length}
              </p>
              <span className="mt-1 block text-xs text-[#20304D]/70">
                {setup.distancePreset} <span aria-hidden="true">·</span>{' '}
                {setup.glassesStatus}
              </span>
            </div>

            <div className="rounded-xl bg-[#F7F5F0] p-4 transition-transform duration-200 hover:-translate-y-0.5">
              <span className="text-xs text-[#20304D]/70">
                Directional responses
              </span>
              <p className="mt-1 font-tabular text-xl font-semibold text-[#10265F]">
                {summary.matchedCount} matched{' '}
                <span className="text-sm font-normal text-[#20304D]/75">
                  ({summary.unsureCount} unsure)
                </span>
              </p>
              <span className="mt-1 block text-xs text-[#20304D]/70">
                Recorded by parent during session
              </span>
            </div>

            <div className="rounded-xl bg-[#F7F5F0] p-4 transition-transform duration-200 hover:-translate-y-0.5">
              <span className="text-xs text-[#20304D]/70">
                Responses by display tier
              </span>
              <p className="mt-1 font-tabular text-sm font-semibold text-[#10265F]">
                Large {summary.byTier.Large.matched}/{summary.byTier.Large.total}{' '}
                <span aria-hidden="true">·</span> Med{' '}
                {summary.byTier.Medium.matched}/{summary.byTier.Medium.total}{' '}
                <span aria-hidden="true">·</span> Smaller{' '}
                {summary.byTier.Smaller.matched}/{summary.byTier.Smaller.total}
              </p>
              <span className="mt-1 block text-xs text-[#20304D]/70">
                Fixed letter size per trial
              </span>
            </div>
          </div>
        </section>

        {/* Observations recorded by the parent */}
        <section
          aria-labelledby="recorded-observations-heading"
          className="animate-reveal-up animate-reveal-delay-3 mt-7 border-t border-[#20304D]/10 pt-6"
        >
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <h2
              id="recorded-observations-heading"
              className="text-base font-semibold text-[#10265F]"
            >
              Observations recorded by parent
            </h2>
            <span className="text-xs text-[#20304D]/70">
              Click any item to include or remove it from your parent note
            </span>
          </div>

          <div className="mt-3 grid grid-cols-1 gap-2.5 sm:grid-cols-2">
            {OBSERVATION_OPTIONS.map((obs) => {
              const checked = selectedObservations.includes(obs);
              return (
                <button
                  key={obs}
                  type="button"
                  aria-pressed={checked}
                  onClick={() => onToggleObservation(obs)}
                  className={`min-h-[48px] rounded-xl border px-4 py-3 text-left text-sm transition-all duration-200 focus-visible:outline-2 focus-visible:outline-[#3E9BE0] ${
                    checked
                      ? 'animate-check-pop border-[#286D65] bg-[#E5EEE8] font-semibold text-[#20304D] shadow-2xs'
                      : 'border-[#20304D]/15 bg-white text-[#20304D]/85 hover:bg-[#F7F5F0]'
                  }`}
                >
                  {checked ? '✓ ' : '+ '}
                  {obs}
                </button>
              );
            })}
          </div>
        </section>

        {/* Primary and Secondary Actions */}
        <div className="mt-8 flex flex-wrap items-center justify-between gap-4 border-t border-[#20304D]/10 pt-6">
          <button
            type="button"
            onClick={onRestartActivity}
            className="min-h-[44px] whitespace-nowrap shrink-0 rounded-full px-3 py-2 text-sm font-medium text-[#10265F] underline decoration-[#3E9BE0] underline-offset-4 hover:text-[#3E9BE0] focus-visible:outline-2 focus-visible:outline-[#3E9BE0]"
          >
            Repeat letter activity
          </button>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={onViewHistory}
              className="min-h-[48px] whitespace-nowrap shrink-0 rounded-full border border-[#20304D]/25 bg-white px-6 py-2.5 text-sm font-semibold text-[#20304D] transition-all hover:border-[#3E9BE0] hover:bg-[#F7F5F0] active:scale-[0.98] focus-visible:outline-2 focus-visible:outline-[#3E9BE0]"
            >
              View history
            </button>

            <button
              type="button"
              onClick={onPrepareParentNote}
              className="btn-sheen min-h-[48px] whitespace-nowrap shrink-0 rounded-full bg-[#10265F] px-7 py-2.5 text-sm font-semibold text-white shadow-xs transition-all hover:bg-[#0B1B46] active:scale-[0.98] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#3E9BE0]"
            >
              Prepare my parent note →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
