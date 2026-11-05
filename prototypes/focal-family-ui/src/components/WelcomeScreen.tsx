import React from 'react';
import type { ScreenId } from '../utils/focalLogic';
import { OpticalHeroBackground } from './OpticalHeroBackground';

interface WelcomeScreenProps {
  onNavigate: (screen: ScreenId) => void;
  onStartCheck: () => void;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({
  onNavigate,
  onStartCheck,
}) => {
  return (
    <div className="relative isolate overflow-hidden bg-[#F7F5F0]">
      {/* Smooth flowing pale teal & apricot gradient strictly behind the right column */}
      <OpticalHeroBackground />

      <div className="relative z-10 mx-auto max-w-[1120px] px-6 py-12 md:py-16">
        {/* Two-Column Hero */}
        <div className="grid grid-cols-1 items-center gap-10 lg:grid-cols-12 lg:gap-12">
          {/* Left Column: Clean warm off-white background with initial reveal */}
          <div className="animate-reveal-up flex flex-col justify-center lg:col-span-7">
            <p className="text-xs font-semibold tracking-wider text-[#10265F] uppercase">
              FOR PARENTS OF CHILDREN 4–10
            </p>

            <h1
              className="mt-3 text-4xl font-semibold leading-[1.12] tracking-tight text-[#20304D] sm:text-5xl lg:text-[3.25rem]"
              style={{ textWrap: 'balance' }}
            >
              Got a school vision letter?{' '}
              <span className="text-[#10265F] underline decoration-[#3E9BE0]/45 decoration-2 underline-offset-[6px]">
                Make the next step easy.
              </span>
            </h1>

            <p className="mt-5 max-w-[54ch] text-base leading-relaxed text-[#20304D]/85 sm:text-lg">
              Try a calm, 3-minute directional letter activity together at home,
              note what you observe, and prepare a clear, editable summary for
              your school nurse or eye doctor.
            </p>

            {/* Primary & Secondary Actions (180ms color transition, Logo deep blue primary button & bright blue link accent) */}
            <div className="mt-8 flex flex-wrap items-center gap-4">
              <button
                type="button"
                onClick={onStartCheck}
                className="inline-flex min-h-[48px] shrink-0 items-center justify-center whitespace-nowrap rounded-lg bg-[#10265F] px-6 py-3 text-base font-semibold text-white shadow-xs transition-colors duration-[180ms] hover:bg-[#0B1B46] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#3E9BE0]"
              >
                Start a check together
              </button>

              <button
                type="button"
                onClick={() => onNavigate('note')}
                className="inline-flex min-h-[48px] shrink-0 items-center justify-center whitespace-nowrap rounded-lg px-3 py-3 text-base font-semibold text-[#10265F] underline decoration-[#3E9BE0] decoration-2 underline-offset-4 transition-colors duration-[180ms] hover:text-[#3E9BE0] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#3E9BE0]"
              >
                Preview a parent note
              </button>
            </div>

            <p className="mt-6 text-sm font-medium text-[#20304D]/75">
              Free for families <span aria-hidden="true">·</span> No account{' '}
              <span aria-hidden="true">·</span> No camera
            </p>
          </div>

          {/* Right Column: Concise, refined "Your next-step plan" preview card */}
          <div className="animate-reveal-up animate-reveal-delay-1 lg:col-span-5">
            <section
              aria-label="Illustrative example of Your next-step plan"
              className="refined-card refined-card-hover rounded-2xl bg-white p-6 sm:p-7"
            >
              {/* Card Header with small document icon (auxiliary teal accent) */}
              <div className="flex items-center justify-between gap-3 border-b border-[#20304D]/10 pb-4">
                <div className="flex items-center gap-2.5">
                  <span
                    aria-hidden="true"
                    className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[#E5EEE8] text-[#1F5C55]"
                  >
                    <svg
                      className="h-4 w-4"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                      <line x1="16" y1="13" x2="8" y2="13" />
                      <line x1="16" y1="17" x2="8" y2="17" />
                    </svg>
                  </span>
                  <h2 className="text-base font-semibold text-[#10265F]">
                    Your next-step plan
                  </h2>
                </div>
                <span className="rounded-md bg-[#F7F5F0] px-2.5 py-1 text-xs font-medium text-[#20304D]/65">
                  Illustrative example
                </span>
              </div>

              {/* 1. Two concise observations */}
              <div className="mt-5">
                <h3 className="text-xs font-semibold tracking-wide text-[#20304D]/60 uppercase">
                  Observations
                </h3>
                <ul className="mt-2.5 space-y-2 text-sm text-[#20304D]/90">
                  <li className="flex items-start gap-2.5">
                    <span
                      aria-hidden="true"
                      className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[#1F5C55]"
                    />
                    <span>Received a school vision referral letter</span>
                  </li>
                  <li className="flex items-start gap-2.5">
                    <span
                      aria-hidden="true"
                      className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[#1F5C55]"
                    />
                    <span>Squints slightly when reading distant signs</span>
                  </li>
                </ul>
              </div>

              {/* 2. Two concise checklist items */}
              <div className="mt-5 border-t border-[#20304D]/8 pt-4">
                <h3 className="text-xs font-semibold tracking-wide text-[#20304D]/60 uppercase">
                  Follow-up checklist
                </h3>
                <ul className="mt-2.5 space-y-2 text-sm text-[#20304D]/90">
                  <li className="flex items-center gap-2.5">
                    <svg
                      className="h-4 w-4 shrink-0 text-[#1F5C55]"
                      viewBox="0 0 20 20"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      aria-hidden="true"
                    >
                      <rect x="3" y="3" width="14" height="14" rx="2.5" />
                      <path d="M6.5 10.5l2.2 2.2 4.8-5" />
                    </svg>
                    <span>Book a pediatric eye exam</span>
                  </li>
                  <li className="flex items-center gap-2.5">
                    <svg
                      className="h-4 w-4 shrink-0 text-[#1F5C55]"
                      viewBox="0 0 20 20"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      aria-hidden="true"
                    >
                      <rect x="3" y="3" width="14" height="14" rx="2.5" />
                      <path d="M6.5 10.5l2.2 2.2 4.8-5" />
                    </svg>
                    <span>Bring the school referral letter and this note</span>
                  </li>
                </ul>
              </div>

              {/* 3. Three-line parent-note excerpt */}
              <div className="mt-5 rounded-xl bg-[#F7F5F0] p-3.5">
                <p className="text-xs font-semibold text-[#10265F]">
                  Prepared parent note
                </p>
                <p className="mt-1 text-sm leading-relaxed text-[#20304D]/85">
                  “We are scheduling an eye exam after receiving Leo’s school
                  vision letter. He reads well up close, but hesitated on
                  smaller E shapes at 10 feet.”
                </p>
              </div>
            </section>
          </div>
        </div>

        {/* Three Concise Steps — Stable 3-Column Grid (max 2px lift on hover, no height/width shift) */}
        <section
          aria-labelledby="how-it-works-heading"
          className="animate-reveal-up animate-reveal-delay-2 mt-14 border-t border-[#20304D]/10 pt-10"
        >
          <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-baseline">
            <h2
              id="how-it-works-heading"
              className="text-lg font-semibold text-[#10265F]"
            >
              How Focal Family works
            </h2>
            <p className="text-sm text-[#20304D]/75">
              Set up together → Try the letter activity → Prepare your next step
            </p>
          </div>

          <div className="mt-5 grid grid-cols-1 gap-5 md:grid-cols-3">
            {[
              {
                step: 'Step 1',
                title: 'Set up together',
                description:
                  'Choose your child’s age group, note whether they wear glasses, and mark a standing spot in a well-lit room.',
                actionLabel: 'Start setup →',
                onClick: onStartCheck,
              },
              {
                step: 'Step 2',
                title: 'Try the letter activity',
                description:
                  'Your child points the way the tumbling E opens while you record their responses on a calm, static screen.',
                actionLabel: 'Try activity →',
                onClick: onStartCheck,
              },
              {
                step: 'Step 3',
                title: 'Prepare your next step',
                description:
                  'Review a neutral summary of observations and copy or download an editable note for your visit.',
                actionLabel: 'Preview note →',
                onClick: () => onNavigate('note'),
              },
            ].map((item) => (
              <div
                key={item.step}
                className="refined-card refined-card-hover flex flex-col justify-between rounded-xl bg-white p-6"
              >
                <div>
                  <span className="text-xs font-semibold tracking-wider text-[#10265F] uppercase">
                    {item.step}
                  </span>
                  <h3 className="mt-2 text-base font-semibold text-[#10265F]">
                    {item.title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-[#20304D]/80">
                    {item.description}
                  </p>
                </div>

                <div className="mt-5 pt-2">
                  <button
                    type="button"
                    onClick={item.onClick}
                    className="rounded-xs text-sm font-semibold text-[#10265F] underline decoration-[#3E9BE0] decoration-1 underline-offset-4 transition-colors duration-[180ms] hover:text-[#3E9BE0] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#3E9BE0]"
                  >
                    {item.actionLabel}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Concise, visible statement that this is a prototype and not a diagnosis (auxiliary light teal prompt) */}
        <section
          aria-label="Prototype and non-diagnostic notice"
          className="animate-reveal-up animate-reveal-delay-3 mt-10 rounded-xl border border-[#286D65]/20 bg-[#E5EEE8]/85 px-5 py-4 sm:px-6"
        >
          <p className="text-sm leading-relaxed text-[#20304D]/90">
            <strong className="font-semibold text-[#10265F]">
              Student prototype — not a medical diagnosis:
            </strong>{' '}
            Focal Family helps parents organize observations and prepare
            questions before a professional eye exam. It does not diagnose
            conditions, replace professional screening, or establish that a
            child’s vision is normal.
          </p>
        </section>
      </div>
    </div>
  );
};
