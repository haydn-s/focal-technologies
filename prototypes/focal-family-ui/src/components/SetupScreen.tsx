import React from 'react';
import {
  isSetupStepReady,
  type AgeGroup,
  type CheckReason,
  type DistancePreset,
  type GlassesStatus,
  type ReadinessChecks,
  type SetupState,
} from '../utils/focalLogic';

interface SetupScreenProps {
  setup: SetupState;
  onUpdateSetup: (updater: (prev: SetupState) => SetupState) => void;
  onCancelToWelcome: () => void;
  onStartActivity: () => void;
}

const AGE_GROUPS: AgeGroup[] = ['4–5 years', '6–7 years', '8–10 years'];

const REASONS: CheckReason[] = [
  'Received a school vision referral letter',
  'Noticed squinting or sitting close to screens',
  'Routine preparation before an eye appointment',
  'Following up after a change in glasses',
];

const GLASSES_OPTIONS: GlassesStatus[] = [
  'Does not wear glasses',
  'Wears glasses (wearing them now)',
  'Wears glasses (not available right now)',
];

const DISTANCE_PRESETS: DistancePreset[] = [
  '10 ft (3 meters)',
  '6 ft (1.8 meters)',
];

export const SetupScreen: React.FC<SetupScreenProps> = ({
  setup,
  onUpdateSetup,
  onCancelToWelcome,
  onStartActivity,
}) => {
  const stepReady = isSetupStepReady(setup);

  const setStep = (step: 1 | 2 | 3) => {
    onUpdateSetup((prev) => ({ ...prev, step }));
  };

  const toggleReadiness = (key: keyof ReadinessChecks) => {
    onUpdateSetup((prev) => ({
      ...prev,
      readinessChecks: {
        ...prev.readinessChecks,
        [key]: !prev.readinessChecks[key],
      },
    }));
  };

  const checkedCount = Object.values(setup.readinessChecks).filter(Boolean).length;
  const isCompactDistance = setup.distancePreset.startsWith('6');
  const childFloorX = isCompactDistance ? 420 : 535;
  const ringCircumference = 2 * Math.PI * 18;
  const ringDashOffset =
    ringCircumference - (checkedCount / 4) * ringCircumference;

  return (
    <div className="mx-auto max-w-[920px] px-6 py-10">
      {/* Progress Indicator Header */}
      <div className="mb-8 animate-reveal-up">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-xs font-semibold tracking-wider text-[#10265F] uppercase">
              Guided setup <span aria-hidden="true">·</span> Step {setup.step} of 3
            </p>
            <h1 className="mt-1 text-2xl font-semibold text-[#10265F] sm:text-3xl">
              {setup.step === 1 && '1. Child and glasses'}
              {setup.step === 2 && '2. Screen and distance'}
              {setup.step === 3 && '3. Ready to begin'}
            </h1>
          </div>

          <button
            type="button"
            onClick={onCancelToWelcome}
            className="min-h-[44px] whitespace-nowrap shrink-0 rounded-lg px-3 py-2 text-sm font-medium text-[#20304D]/80 underline decoration-[#3E9BE0] underline-offset-4 transition-colors hover:text-[#10265F] focus-visible:outline-2 focus-visible:outline-[#3E9BE0]"
          >
            Return to welcome
          </button>
        </div>

        {/* 3-Step Visual Progress Bar (Active: Logo Deep Blue #10265F, Completed: Auxiliary Teal/Sage) */}
        <nav aria-label="Setup steps" className="mt-6 grid grid-cols-3 gap-3">
          {[
            { num: 1 as const, title: '1. Child & glasses' },
            { num: 2 as const, title: '2. Screen & distance' },
            { num: 3 as const, title: '3. Ready to begin' },
          ].map((item) => {
            const isActive = setup.step === item.num;
            const isDone = setup.step > item.num;
            return (
              <button
                key={item.num}
                type="button"
                onClick={() => setStep(item.num)}
                aria-current={isActive ? 'step' : undefined}
                className={`min-h-[44px] rounded-xl border px-3 py-2.5 text-left transition-all duration-200 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#3E9BE0] ${
                  isActive
                    ? 'border-[#10265F] bg-[#10265F] font-semibold text-white shadow-xs -translate-y-0.5'
                    : isDone
                      ? 'border-[#286D65]/35 bg-[#E5EEE8]/75 font-medium text-[#20304D] hover:border-[#286D65]'
                      : 'border-[#20304D]/12 bg-white/70 text-[#20304D]/65 hover:border-[#3E9BE0]/40 hover:bg-white'
                }`}
              >
                <div className="flex items-center justify-between text-xs sm:text-sm">
                  <span className="truncate">{item.title}</span>
                  {isDone && (
                    <span className="ml-1 inline-flex items-center gap-1 text-xs font-semibold text-[#1F5C55]">
                      <span>✓</span>
                      <span>Saved</span>
                    </span>
                  )}
                </div>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Step Content Card */}
      <div
        key={setup.step}
        className="animate-reveal-up rounded-2xl border border-[#20304D]/12 bg-white p-6 shadow-xs sm:p-8"
      >
        {setup.step === 1 && (
          <div className="space-y-7">
            <div>
              <label
                htmlFor="child-label-input"
                className="block text-sm font-semibold text-[#20304D]"
              >
                Child label (no real full name needed)
              </label>
              <p className="mt-1 text-xs text-[#20304D]/70">
                Use a nickname, initial, or label like “Child A” or “Older
                sibling.” Kept only in memory for this browser session.
              </p>
              <input
                id="child-label-input"
                type="text"
                value={setup.childLabel}
                onChange={(e) =>
                  onUpdateSetup((prev) => ({
                    ...prev,
                    childLabel: e.target.value,
                  }))
                }
                placeholder="e.g., Child A (Age 7)"
                className="mt-2.5 min-h-[44px] w-full max-w-md rounded-xl border border-[#20304D]/25 bg-[#F7F5F0]/50 px-3.5 py-2.5 text-base text-[#20304D] transition-colors focus:border-[#3E9BE0] focus:bg-white focus:outline-2 focus:outline-[#3E9BE0]"
              />
            </div>

            <fieldset>
              <legend className="text-sm font-semibold text-[#20304D]">
                Child’s age group
              </legend>
              <div className="mt-2.5 grid grid-cols-1 gap-3 sm:grid-cols-3">
                {AGE_GROUPS.map((group) => {
                  const selected = setup.ageGroup === group;
                  return (
                    <button
                      key={group}
                      type="button"
                      aria-pressed={selected}
                      onClick={() =>
                        onUpdateSetup((prev) => ({ ...prev, ageGroup: group }))
                      }
                      className={`min-h-[48px] rounded-xl border px-4 py-3 text-left text-sm font-medium transition-all duration-200 focus-visible:outline-2 focus-visible:outline-[#3E9BE0] ${
                        selected
                          ? 'border-[#10265F] bg-[#10265F]/[0.06] ring-1 ring-[#10265F] font-semibold text-[#10265F] shadow-2xs -translate-y-0.5'
                          : 'border-[#20304D]/15 bg-white text-[#20304D]/85 hover:border-[#3E9BE0]/50 hover:bg-[#F7F5F0]'
                      }`}
                    >
                      {group}
                    </button>
                  );
                })}
              </div>
            </fieldset>

            <fieldset>
              <legend className="text-sm font-semibold text-[#20304D]">
                Main reason for checking today
              </legend>
              <div className="mt-2.5 grid grid-cols-1 gap-2.5 sm:grid-cols-2">
                {REASONS.map((reasonOption) => {
                  const selected = setup.reason === reasonOption;
                  return (
                    <button
                      key={reasonOption}
                      type="button"
                      aria-pressed={selected}
                      onClick={() =>
                        onUpdateSetup((prev) => ({
                          ...prev,
                          reason: reasonOption,
                        }))
                      }
                      className={`min-h-[48px] rounded-xl border px-4 py-3 text-left text-sm transition-all duration-200 focus-visible:outline-2 focus-visible:outline-[#3E9BE0] ${
                        selected
                          ? 'border-[#10265F] bg-[#10265F]/[0.06] ring-1 ring-[#10265F] font-semibold text-[#10265F] shadow-2xs -translate-y-0.5'
                          : 'border-[#20304D]/15 bg-white text-[#20304D]/85 hover:border-[#3E9BE0]/50 hover:bg-[#F7F5F0]'
                      }`}
                    >
                      {reasonOption}
                    </button>
                  );
                })}
              </div>
            </fieldset>

            <fieldset>
              <legend className="text-sm font-semibold text-[#20304D]">
                Glasses or corrective lenses
              </legend>
              <p className="mt-1 text-xs text-[#20304D]/70">
                If your child has distance glasses for school, they normally
                wear them during a check.
              </p>
              <div className="mt-2.5 grid grid-cols-1 gap-2.5 sm:grid-cols-3">
                {GLASSES_OPTIONS.map((option) => {
                  const selected = setup.glassesStatus === option;
                  return (
                    <button
                      key={option}
                      type="button"
                      aria-pressed={selected}
                      onClick={() =>
                        onUpdateSetup((prev) => ({
                          ...prev,
                          glassesStatus: option,
                        }))
                      }
                      className={`min-h-[48px] rounded-xl border px-4 py-3 text-left text-sm transition-all duration-200 focus-visible:outline-2 focus-visible:outline-[#3E9BE0] ${
                        selected
                          ? 'border-[#10265F] bg-[#10265F]/[0.06] ring-1 ring-[#10265F] font-semibold text-[#10265F] shadow-2xs -translate-y-0.5'
                          : 'border-[#20304D]/15 bg-white text-[#20304D]/85 hover:border-[#3E9BE0]/50 hover:bg-[#F7F5F0]'
                      }`}
                    >
                      {option}
                    </button>
                  );
                })}
              </div>
            </fieldset>
          </div>
        )}

        {setup.step === 2 && (
          <div className="space-y-8">
            {/* Distance Selection */}
            <fieldset>
              <legend className="text-sm font-semibold text-[#20304D]">
                Choose your room standing distance
              </legend>
              <p className="mt-1 text-xs text-[#20304D]/75">
                Pick a distance where your child can stand comfortably with a
                clear view of the screen at eye level. Watch the room diagram
                adjust below.
              </p>
              <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
                {DISTANCE_PRESETS.map((dist) => {
                  const selected = setup.distancePreset === dist;
                  return (
                    <button
                      key={dist}
                      type="button"
                      aria-pressed={selected}
                      onClick={() =>
                        onUpdateSetup((prev) => ({
                          ...prev,
                          distancePreset: dist,
                        }))
                      }
                      className={`min-h-[48px] rounded-xl border px-4 py-3 text-left text-sm transition-all duration-200 focus-visible:outline-2 focus-visible:outline-[#3E9BE0] ${
                        selected
                          ? 'border-[#10265F] bg-[#10265F]/[0.06] ring-1 ring-[#10265F] font-semibold text-[#10265F] shadow-2xs -translate-y-0.5'
                          : 'border-[#20304D]/15 bg-white text-[#20304D]/85 hover:border-[#3E9BE0]/50 hover:bg-[#F7F5F0]'
                      }`}
                    >
                      <span>{dist}</span>
                      <span className="block text-xs font-normal text-[#20304D]/70">
                        {dist.startsWith('10')
                          ? 'About 5–6 adult heel-to-toe steps'
                          : 'Compact room option (about 3–4 steps)'}
                      </span>
                    </button>
                  );
                })}
              </div>
            </fieldset>

            {/* Inline SVG Diagram: Top-Down / Angled Room Layout Clearly Showing Parent Seated to the Side, Unobstructed Sightline, Child Staying at Mark, and Screen-Relative Left/Right */}
            <div className="border-t border-[#20304D]/10 pt-6">
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <div>
                  <h2 className="text-sm font-semibold text-[#20304D]">
                    Interactive room & seating layout (top-down view)
                  </h2>
                  <p className="mt-0.5 text-xs text-[#20304D]/70">
                    Sit to the side of the laptop so you never block the screen,
                    and record directions relative to the screen.
                  </p>
                </div>
                <span className="inline-flex items-center gap-1.5 rounded-md bg-[#E5EEE8] px-3 py-1 text-xs font-semibold text-[#1F5C55]">
                  <span>Selected distance: {setup.distancePreset}</span>
                </span>
              </div>

              <div className="mt-3 rounded-xl border border-[#20304D]/10 bg-[#F7F5F0] p-4 sm:p-5">
                <svg
                  viewBox="0 0 720 276"
                  role="img"
                  aria-label={`Top-down room layout showing laptop facing child with unobstructed sightline, parent seated to the side operating the laptop, and child standing at the ${setup.distancePreset} mark`}
                  className="h-auto w-full"
                >
                  {/* Subtle Room Floor Grid / Background */}
                  <rect
                    x="12"
                    y="12"
                    width="696"
                    height="252"
                    rx="12"
                    fill="#FFFFFF"
                    stroke="#20304D"
                    strokeOpacity="0.1"
                  />

                  {/* Unobstructed Sightline Corridor (between Laptop Screen and Child) */}
                  <rect
                    x="152"
                    y="68"
                    width={isCompactDistance ? 278 : 393}
                    height="74"
                    rx="8"
                    fill="#E5EEE8"
                    fillOpacity="0.55"
                  />
                  <text
                    x={isCompactDistance ? 290 : 345}
                    y="84"
                    textAnchor="middle"
                    fill="#1F5C55"
                    fontSize="10.5"
                    fontWeight="700"
                    letterSpacing="0.04em"
                  >
                    CLEAR SIGHTLINE — DO NOT BLOCK SCREEN
                  </text>

                  {/* Center Sightline Dashed Line */}
                  <line
                    x1="154"
                    y1="108"
                    x2={childFloorX - 24}
                    y2="108"
                    stroke="#1F5C55"
                    strokeDasharray="6 5"
                    strokeWidth="2"
                  />

                  {/* Screen-Relative Left / Right Reference Labels near Screen */}
                  <g>
                    <rect
                      x="24"
                      y="22"
                      width="156"
                      height="24"
                      rx="6"
                      fill="#F7F5F0"
                      stroke="#20304D"
                      strokeOpacity="0.15"
                    />
                    <text
                      x="102"
                      y="38"
                      textAnchor="middle"
                      fill="#20304D"
                      fontSize="10"
                      fontWeight="600"
                    >
                      ↑ Screen Left (Child’s Left)
                    </text>

                    <rect
                      x="24"
                      y="162"
                      width="162"
                      height="24"
                      rx="6"
                      fill="#F7F5F0"
                      stroke="#20304D"
                      strokeOpacity="0.15"
                    />
                    <text
                      x="105"
                      y="178"
                      textAnchor="middle"
                      fill="#20304D"
                      fontSize="10"
                      fontWeight="600"
                    >
                      ↓ Screen Right (Child’s Right)
                    </text>
                  </g>

                  {/* Desk / Table (Left) */}
                  <rect
                    x="74"
                    y="68"
                    width="68"
                    height="82"
                    rx="8"
                    fill="#F7F5F0"
                    stroke="#20304D"
                    strokeWidth="1.8"
                  />
                  <text
                    x="108"
                    y="61"
                    textAnchor="middle"
                    fill="#20304D"
                    fontSize="10.5"
                    fontWeight="600"
                  >
                    Table / Desk
                  </text>

                  {/* Laptop on Desk with Screen on the Left Facing Right (→) toward Child */}
                  <rect
                    x="98"
                    y="89"
                    width="34"
                    height="40"
                    rx="4"
                    fill="#FFFFFF"
                    stroke="#20304D"
                    strokeWidth="1.6"
                  />
                  {/* Laptop Screen Bar (Left edge / hinge, display facing right toward child) */}
                  <line
                    x1="94"
                    y1="85"
                    x2="94"
                    y2="133"
                    stroke="#1F5C55"
                    strokeWidth="4.5"
                    strokeLinecap="round"
                  />
                  <text
                    x="115"
                    y="113"
                    textAnchor="middle"
                    fill="#20304D"
                    fontSize="10"
                    fontWeight="700"
                  >
                    E
                  </text>

                  {/* Parent Seated to the SIDE (Below the sightline corridor, never blocking screen) */}
                  <g>
                    {/* Chair & Parent */}
                    <circle
                      cx="128"
                      cy="220"
                      r="18"
                      fill="#E5EEE8"
                      stroke="#1F5C55"
                      strokeWidth="1.8"
                    />
                    <circle cx="128" cy="220" r="9" fill="#20304D" />
                    {/* Parent's hand reaching laptop keyboard */}
                    <path
                      d="M 122 202 Q 116 166 116 133"
                      fill="none"
                      stroke="#20304D"
                      strokeWidth="2.2"
                      strokeLinecap="round"
                    />
                    <circle cx="116" cy="133" r="3" fill="#1F5C55" />

                    {/* Parent's visual observation line toward Child */}
                    <path
                      d={`M 146 214 Q 310 198 ${childFloorX - 18} 134`}
                      fill="none"
                      stroke="#20304D"
                      strokeOpacity="0.4"
                      strokeDasharray="4 4"
                      strokeWidth="1.5"
                    />

                    {/* Parent Role Callout Box */}
                    <rect
                      x="156"
                      y="192"
                      width="256"
                      height="58"
                      rx="8"
                      fill="#F7F5F0"
                      stroke="#20304D"
                      strokeOpacity="0.16"
                    />
                    <text
                      x="168"
                      y="211"
                      fill="#20304D"
                      fontSize="11.5"
                      fontWeight="700"
                    >
                      Parent sits to the side (out of sightline)
                    </text>
                    <text
                      x="168"
                      y="227"
                      fill="#20304D"
                      fillOpacity="0.8"
                      fontSize="10.5"
                    >
                      Watches child’s hand &amp; taps screen-relative
                    </text>
                    <text
                      x="168"
                      y="241"
                      fill="#1F5C55"
                      fontSize="10.5"
                      fontWeight="600"
                    >
                      direction on laptop (no hints)
                    </text>
                  </g>

                  {/* Animated Distance Measurement Pill */}
                  <g
                    className="svg-actor-glide"
                    style={{
                      transform: isCompactDistance
                        ? 'translateX(-55px)'
                        : 'translateX(0px)',
                    }}
                  >
                    <rect
                      x="252"
                      y="94"
                      width="162"
                      height="28"
                      rx="6"
                      fill="#FFFFFF"
                      stroke="#1F5C55"
                      strokeWidth="1.4"
                    />
                    <text
                      x="333"
                      y="112"
                      textAnchor="middle"
                      fill="#20304D"
                      fontSize="11.5"
                      fontWeight="700"
                    >
                      {setup.distancePreset}
                    </text>
                  </g>

                  {/* Animated Child Standing at Floor Mark (Stays at mark, points direction) */}
                  <g
                    className="svg-actor-glide"
                    style={{
                      transform: isCompactDistance
                        ? 'translateX(-115px)'
                        : 'translateX(0px)',
                    }}
                  >
                    {/* Floor Tape Line */}
                    <line
                      x1="535"
                      y1="78"
                      x2="535"
                      y2="138"
                      stroke="#1F5C55"
                      strokeWidth="3.5"
                      strokeLinecap="round"
                    />
                    {/* Child Shoulders & Head (Top-Down) */}
                    <rect
                      x="542"
                      y="86"
                      width="24"
                      height="44"
                      rx="10"
                      fill="#F2CDAE"
                      stroke="#20304D"
                      strokeWidth="1.6"
                    />
                    <circle cx="554" cy="108" r="10" fill="#20304D" />
                    {/* Child Pointing Arm toward Screen / Direction */}
                    <line
                      x1="544"
                      y1="94"
                      x2="516"
                      y2="82"
                      stroke="#20304D"
                      strokeWidth="3"
                      strokeLinecap="round"
                    />
                    <circle cx="515" cy="81" r="3" fill="#1F5C55" />

                    {/* Child Role Callout Label */}
                    <rect
                      x="466"
                      y="18"
                      width="228"
                      height="42"
                      rx="8"
                      fill="#F7F5F0"
                      stroke="#20304D"
                      strokeOpacity="0.16"
                    />
                    <text
                      x="478"
                      y="35"
                      fill="#20304D"
                      fontSize="11.5"
                      fontWeight="700"
                    >
                      Child stays at floor mark
                    </text>
                    <text
                      x="478"
                      y="50"
                      fill="#20304D"
                      fillOpacity="0.8"
                      fontSize="10.5"
                    >
                      Points way E opens · Never walks to laptop
                    </text>

                    {/* Screen-Relative Left/Right Reminder by Child */}
                    <text
                      x="554"
                      y="73"
                      textAnchor="middle"
                      fill="#1F5C55"
                      fontSize="10"
                      fontWeight="700"
                    >
                      ↑ Screen Left
                    </text>
                    <text
                      x="554"
                      y="151"
                      textAnchor="middle"
                      fill="#1F5C55"
                      fontSize="10"
                      fontWeight="700"
                    >
                      ↓ Screen Right
                    </text>
                  </g>
                </svg>

                {/* Three Explicit Setup & Recording Rules Below Diagram */}
                <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
                  <div className="rounded-lg border border-[#20304D]/10 bg-white p-3">
                    <p className="text-xs font-semibold text-[#20304D]">
                      1. Sit to the side of the screen
                    </p>
                    <p className="mt-1 text-xs leading-relaxed text-[#20304D]/75">
                      Sit angled to the side so you do not block the screen, can
                      see your child’s hand, and can reach the laptop.
                    </p>
                  </div>

                  <div className="rounded-lg border border-[#20304D]/10 bg-white p-3">
                    <p className="text-xs font-semibold text-[#20304D]">
                      2. Child stays at the floor mark
                    </p>
                    <p className="mt-1 text-xs leading-relaxed text-[#20304D]/75">
                      Your child stands at the mark and points with their hand
                      or arm. They do not walk back to the computer to answer.
                    </p>
                  </div>

                  <div className="rounded-lg border border-[#20304D]/10 bg-white p-3">
                    <p className="text-xs font-semibold text-[#1F5C55]">
                      3. Use screen direction (no hints)
                    </p>
                    <p className="mt-1 text-xs leading-relaxed text-[#20304D]/75">
                      Record the direction relative to the screen (avoid
                      reversing Left and Right when facing your child) and do
                      not hint at answers.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Interactive Card-Width Slider with Explicit Visual Setup Demo Label */}
            <div className="border-t border-[#20304D]/10 pt-6">
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <label
                  htmlFor="card-slider"
                  className="text-sm font-semibold text-[#20304D]"
                >
                  Screen scale reference card
                </label>
                <span className="text-xs font-semibold text-[#286D65]">
                  Visual setup demonstration — not validated optotype calibration
                </span>
              </div>
              <p className="mt-1 text-xs leading-relaxed text-[#20304D]/75">
                In a calibrated clinical tool, matching a standard card width
                helps estimate screen pixel density. This HTML mockup provides
                this slider as a visual setup demonstration and does not
                implement validated optotype calibration.
              </p>

              <div className="mt-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex-1">
                  <input
                    id="card-slider"
                    type="range"
                    min={180}
                    max={320}
                    step={2}
                    value={setup.cardSliderWidthPx}
                    onChange={(e) =>
                      onUpdateSetup((prev) => ({
                        ...prev,
                        cardSliderWidthPx: Number(e.target.value),
                      }))
                    }
                    className="focal-slider w-full cursor-pointer"
                  />
                  <div className="mt-1.5 flex justify-between text-xs text-[#20304D]/70 font-tabular">
                    <span>Smaller screen scale</span>
                    <span>Display width: {setup.cardSliderWidthPx}px</span>
                    <span>Larger screen scale</span>
                  </div>
                </div>

                <div className="flex items-center justify-center rounded-xl bg-[#F7F5F0] p-4">
                  <div
                    style={{
                      width: `${setup.cardSliderWidthPx}px`,
                      height: `${Math.round(setup.cardSliderWidthPx * 0.63)}px`,
                    }}
                    className="flex flex-col justify-between rounded-lg border-2 border-dashed border-[#286D65] bg-white p-3 shadow-2xs transition-all duration-150"
                  >
                    <div className="flex items-center justify-between text-[11px] font-semibold text-[#20304D]">
                      <span>STANDARD CARD OUTLINE</span>
                      <span className="font-tabular">{setup.cardSliderWidthPx}px</span>
                    </div>
                    <div className="h-5 w-8 rounded-xs bg-[#F2CDAE]" />
                    <span className="text-[10px] text-[#20304D]/65">
                      Visual demonstration only
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {setup.step === 3 && (
          <div className="space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <h2 className="text-base font-semibold text-[#20304D]">
                  Confirm your setup before starting
                </h2>
                <p className="mt-1 text-sm text-[#20304D]/75">
                  Please actively check all four boxes below to begin the
                  illustrative letter activity. Your selections on previous steps
                  are saved if you go back.
                </p>
              </div>

              {/* Animated SVG Readiness Progress Ring */}
              <div className="flex items-center gap-3 rounded-xl border border-[#20304D]/10 bg-[#F7F5F0] px-3.5 py-2">
                <svg className="h-11 w-11 -rotate-90" viewBox="0 0 44 44" aria-hidden="true">
                  <circle
                    cx="22"
                    cy="22"
                    r="18"
                    fill="none"
                    stroke="#20304D"
                    strokeOpacity="0.12"
                    strokeWidth="4"
                  />
                  <circle
                    cx="22"
                    cy="22"
                    r="18"
                    fill="none"
                    stroke="#286D65"
                    strokeWidth="4"
                    strokeLinecap="round"
                    strokeDasharray={ringCircumference}
                    strokeDashoffset={ringDashOffset}
                    style={{
                      transition: 'stroke-dashoffset 0.45s cubic-bezier(0.16, 1, 0.3, 1)',
                    }}
                  />
                </svg>
                <div>
                  <span className="block font-tabular text-xs font-bold text-[#20304D]">
                    {checkedCount} of 4 confirmed
                  </span>
                  <span className="block text-[11px] text-[#286D65] font-medium">
                    {stepReady ? 'Ready to begin' : 'Check all 4 items'}
                  </span>
                </div>
              </div>
            </div>

            <div className="rounded-xl bg-[#F7F5F0] p-4 text-sm text-[#20304D]">
              <div className="flex flex-wrap gap-x-6 gap-y-1">
                <span>
                  <strong>Child:</strong> {setup.childLabel} ({setup.ageGroup})
                </span>
                <span>
                  <strong>Glasses:</strong> {setup.glassesStatus}
                </span>
                <span>
                  <strong>Distance:</strong> {setup.distancePreset}
                </span>
              </div>
            </div>

            <div className="space-y-3">
              {[
                {
                  key: 'roomLit' as const,
                  label:
                    'The room is comfortably lit and there is no strong window glare on the screen.',
                },
                {
                  key: 'distanceMarked' as const,
                  label: `We marked a spot about ${setup.distancePreset} from the screen and the screen is near child eye level.`,
                },
                {
                  key: 'prototypeUnderstood' as const,
                  label:
                    'I understand this is a student prototype interaction preview and not a calibrated vision test or diagnosis.',
                },
                {
                  key: 'keepFollowUpUnderstood' as const,
                  label:
                    'I will keep any school vision referral or eye doctor follow-up regardless of how my child responds today.',
                },
              ].map((item) => {
                const checked = setup.readinessChecks[item.key];
                return (
                  <label
                    key={item.key}
                    className={`flex min-h-[52px] cursor-pointer items-start gap-3.5 rounded-xl border p-3.5 text-sm transition-all duration-200 ${
                      checked
                        ? 'animate-check-pop border-[#286D65] bg-[#E5EEE8]/70 font-medium text-[#20304D] shadow-2xs'
                        : 'border-[#20304D]/15 bg-white text-[#20304D]/90 hover:bg-[#F7F5F0]/60'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => toggleReadiness(item.key)}
                      className="mt-0.5 h-5 w-5 shrink-0 cursor-pointer rounded border-[#20304D]/40 accent-[#286D65]"
                    />
                    <span className="leading-snug">{item.label}</span>
                  </label>
                );
              })}
            </div>

            {!stepReady && (
              <p
                role="status"
                className="text-xs font-medium text-[#20304D]/75"
              >
                Check all 4 readiness boxes above to unlock “Begin letter
                activity.”
              </p>
            )}
          </div>
        )}

        {/* Step Navigation Footer */}
        <div className="mt-8 flex flex-wrap items-center justify-between gap-4 border-t border-[#20304D]/10 pt-6">
          <div>
            {setup.step > 1 ? (
              <button
                type="button"
                onClick={() => setStep((setup.step - 1) as 1 | 2)}
                className="min-h-[44px] whitespace-nowrap shrink-0 rounded-full border border-[#20304D]/25 bg-white px-5 py-2.5 text-sm font-semibold text-[#20304D] transition-all hover:border-[#3E9BE0] hover:bg-[#F7F5F0] active:scale-[0.98] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#3E9BE0]"
              >
                ← Back to Step {setup.step - 1}
              </button>
            ) : (
              <button
                type="button"
                onClick={onCancelToWelcome}
                className="min-h-[44px] whitespace-nowrap shrink-0 rounded-full border border-[#20304D]/20 bg-white px-5 py-2.5 text-sm font-medium text-[#20304D]/80 transition-all hover:border-[#3E9BE0] hover:bg-[#F7F5F0] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#3E9BE0]"
              >
                Back to welcome
              </button>
            )}
          </div>

          <div className="flex items-center gap-3">
            {setup.step < 3 ? (
              <button
                type="button"
                disabled={!stepReady}
                onClick={() => setStep((setup.step + 1) as 2 | 3)}
                className="btn-sheen min-h-[48px] whitespace-nowrap shrink-0 rounded-full bg-[#10265F] px-7 py-2.5 text-sm font-semibold text-white shadow-xs transition-all hover:bg-[#0B1B46] active:scale-[0.98] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#3E9BE0] disabled:cursor-not-allowed disabled:opacity-45"
              >
                Continue to Step {setup.step + 1} →
              </button>
            ) : (
              <button
                type="button"
                disabled={!stepReady}
                onClick={onStartActivity}
                className="btn-sheen min-h-[48px] whitespace-nowrap shrink-0 rounded-full bg-[#10265F] px-7 py-2.5 text-sm font-semibold text-white shadow-xs transition-all hover:bg-[#0B1B46] active:scale-[0.98] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#3E9BE0] disabled:cursor-not-allowed disabled:opacity-45"
              >
                Begin letter activity →
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
