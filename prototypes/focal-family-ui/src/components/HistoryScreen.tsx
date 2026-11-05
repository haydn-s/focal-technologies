import React from 'react';
import {
  FICTIONAL_EXAMPLE_RECORDS,
  type ActivityRecord,
  type ScreenId,
} from '../utils/focalLogic';

interface HistoryScreenProps {
  sessionRecords: ActivityRecord[];
  onNavigate: (screen: ScreenId) => void;
  onStartCheck: () => void;
}

export const HistoryScreen: React.FC<HistoryScreenProps> = ({
  sessionRecords,
  onNavigate,
  onStartCheck,
}) => {
  const [selectedBarId, setSelectedBarId] = React.useState<string | null>(null);

  // Combine chart series clearly separating Fictional Example Data from current session
  const chartItems: ActivityRecord[] = [
    ...FICTIONAL_EXAMPLE_RECORDS,
    ...sessionRecords,
  ];
  const activeBarItem =
    chartItems.find((item) => item.id === selectedBarId) ?? null;

  return (
    <div className="mx-auto max-w-[1060px] px-6 py-10">
      {/* Header */}
      <div className="animate-reveal-up flex flex-wrap items-end justify-between gap-4 border-b border-[#20304D]/12 pb-6">
        <div>
          <p className="text-xs font-semibold tracking-wider text-[#286D65] uppercase">
            Activity & observation log
          </p>
          <h1 className="mt-1 text-2xl font-semibold text-[#20304D] sm:text-3xl">
            Previous activities and observations
          </h1>
          <p className="mt-1.5 max-w-[68ch] text-sm text-[#20304D]/80">
            Review activity responses recorded during this browser session
            alongside clearly labeled fictional example entries that illustrate
            how a family can log observations before an appointment.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={() => onNavigate('note')}
            className="min-h-[44px] whitespace-nowrap shrink-0 rounded-full border border-[#20304D]/25 bg-white px-5 py-2 text-xs font-semibold text-[#20304D] transition-all hover:bg-[#F7F5F0]"
          >
            Open parent note
          </button>
          <button
            type="button"
            onClick={onStartCheck}
            className="btn-sheen min-h-[44px] whitespace-nowrap shrink-0 rounded-full bg-[#286D65] px-5 py-2 text-xs font-semibold text-white transition-all hover:bg-[#1f5650]"
          >
            Start new activity
          </button>
        </div>
      </div>

      {/* Session vs Fictional Notice + Chart Section */}
      <section
        aria-labelledby="activity-chart-heading"
        className="animate-reveal-up animate-reveal-delay-1 mt-8 rounded-2xl border border-[#20304D]/12 bg-white p-6 shadow-xs sm:p-8"
      >
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <div>
            <h2
              id="activity-chart-heading"
              className="text-lg font-semibold text-[#20304D]"
            >
              Directional activity responses per session (out of 12 trials)
            </h2>
            <p className="mt-1 text-xs text-[#20304D]/75">
              Values show how many directional E shapes the child pointed to in
              each 12-trial activity — not clinical visual acuity measurements.
              Click any bar to inspect session details.
            </p>
          </div>
          <span className="text-xs font-medium text-[#20304D]/70">
            Fictional example data + current session
          </span>
        </div>

        {/* Inline SVG Bar & Point Chart */}
        <div className="mt-6 rounded-xl bg-[#F7F5F0] p-4 sm:p-6">
          <svg
            viewBox="0 0 720 230"
            role="img"
            aria-label="Chart of directional activity responses out of 12 trials across fictional examples and current browser session"
            className="h-auto w-full"
          >
            {/* Horizontal reference lines (0, 4, 8, 12 trials) */}
            {[0, 4, 8, 12].map((val) => {
              const y = 175 - (val / 12) * 130;
              return (
                <g key={val}>
                  <line
                    x1="65"
                    y1={y}
                    x2="680"
                    y2={y}
                    stroke="#20304D"
                    strokeOpacity="0.12"
                    strokeDasharray={val === 0 ? undefined : '4 4'}
                    strokeWidth="1"
                  />
                  <text
                    x="52"
                    y={y + 4}
                    textAnchor="end"
                    fill="#20304D"
                    fillOpacity="0.7"
                    fontSize="11"
                  >
                    {val}/12
                  </text>
                </g>
              );
            })}

            {/* Bars for each record */}
            {chartItems.map((item, idx) => {
              const slotWidth = 580 / Math.max(chartItems.length, 1);
              const xCenter = 85 + idx * slotWidth + slotWidth * 0.4;
              const barWidth = Math.min(64, slotWidth * 0.55);
              const barHeight = (item.matchedCount / 12) * 130;
              const yTop = 175 - barHeight;
              const isSelected = selectedBarId === item.id;
              const fill = item.isFictional
                ? isSelected
                  ? '#F2CDAE'
                  : '#E5EEE8'
                : '#286D65';
              const stroke = item.isFictional ? '#20304D' : '#286D65';

              return (
                <g
                  key={item.id}
                  onClick={() =>
                    setSelectedBarId((prev) =>
                      prev === item.id ? null : item.id
                    )
                  }
                  className="cursor-pointer"
                >
                  <rect
                    x={xCenter - barWidth / 2}
                    y={yTop}
                    width={barWidth}
                    height={Math.max(barHeight, 4)}
                    rx="6"
                    fill={fill}
                    stroke={stroke}
                    strokeOpacity={item.isFictional && !isSelected ? 0.35 : 1}
                    strokeWidth={isSelected ? '2.5' : '1.5'}
                    className="animate-bar-grow"
                    style={{ animationDelay: `${idx * 90}ms` }}
                  />
                  <text
                    x={xCenter}
                    y={yTop - 8}
                    textAnchor="middle"
                    fill="#20304D"
                    fontSize="12"
                    fontWeight="700"
                  >
                    {item.matchedCount}/{item.totalTrials}
                  </text>
                  <text
                    x={xCenter}
                    y="196"
                    textAnchor="middle"
                    fill="#20304D"
                    fontSize="11"
                    fontWeight="600"
                  >
                    {item.isFictional
                      ? `Example ${idx + 1}`
                      : `This session`}
                  </text>
                  <text
                    x={xCenter}
                    y="212"
                    textAnchor="middle"
                    fill="#20304D"
                    fillOpacity="0.7"
                    fontSize="10"
                  >
                    {item.childLabel.slice(0, 18)}
                  </text>
                </g>
              );
            })}
          </svg>

          {activeBarItem && (
            <div className="animate-scale-in mt-3 flex flex-wrap items-center justify-between gap-2 rounded-xl border border-[#286D65]/25 bg-white px-4 py-2.5 text-xs text-[#20304D]">
              <div>
                <span className="font-semibold text-[#286D65]">
                  {activeBarItem.isFictional
                    ? 'Fictional example: '
                    : 'Current session: '}
                </span>
                <strong>{activeBarItem.childLabel}</strong> ·{' '}
                {activeBarItem.dateLabel} · {activeBarItem.distancePreset} ·{' '}
                {activeBarItem.matchedCount}/{activeBarItem.totalTrials} matched
              </div>
              <button
                type="button"
                onClick={() => setSelectedBarId(null)}
                className="font-semibold text-[#286D65] underline"
              >
                Clear selection
              </button>
            </div>
          )}

          <div className="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-[#20304D]/10 pt-3 text-xs text-[#20304D]/75">
            <div className="flex flex-wrap items-center gap-4">
              <span className="flex items-center gap-2">
                <span className="inline-block h-3 w-3 rounded-xs border border-[#20304D]/40 bg-[#E5EEE8]" />
                <span>Fictional example data</span>
              </span>
              <span className="flex items-center gap-2">
                <span className="inline-block h-3 w-3 rounded-xs bg-[#286D65]" />
                <span>Recorded in this browser session</span>
              </span>
            </div>
            <span>
              Differences between sessions can reflect room lighting, fatigue,
              or attention — not improved or deteriorating vision.
            </span>
          </div>
        </div>
      </section>

      {/* Section 1: Records Created in This Browser Session */}
      <section
        aria-labelledby="session-records-heading"
        className="mt-8 rounded-xl border border-[#20304D]/12 bg-white p-6 shadow-xs"
      >
        <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-[#20304D]/10 pb-4">
          <div>
            <h2
              id="session-records-heading"
              className="text-base font-semibold text-[#20304D]"
            >
              Records created in this browser session
            </h2>
            <p className="mt-0.5 text-xs text-[#20304D]/70">
              Stored in memory only. Refreshing the page clears these records
              unless you download your parent note.
            </p>
          </div>
          <span className="font-tabular text-xs font-semibold text-[#286D65]">
            {sessionRecords.length}{' '}
            {sessionRecords.length === 1 ? 'record' : 'records'}
          </span>
        </div>

        {sessionRecords.length === 0 ? (
          <div className="mt-4 rounded-lg bg-[#F7F5F0] p-5 text-sm text-[#20304D]/80">
            <p>
              No activity records completed in this browser session yet. When
              you finish the guided letter activity, your session summary will
              appear here.
            </p>
            <button
              type="button"
              onClick={onStartCheck}
              className="mt-3 min-h-[44px] rounded-lg bg-[#286D65] px-4 py-2 text-xs font-semibold text-white hover:bg-[#1f5650]"
            >
              Start a check together
            </button>
          </div>
        ) : (
          <div className="mt-4 divide-y divide-[#20304D]/10">
            {sessionRecords.map((rec) => (
              <article key={rec.id} className="py-4 first:pt-0 last:pb-0">
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <h3 className="text-sm font-semibold text-[#20304D]">
                    {rec.childLabel} ({rec.ageGroup}){' '}
                    <span aria-hidden="true">·</span>{' '}
                    <span className="font-normal text-[#20304D]/75">
                      {rec.dateLabel}
                    </span>
                  </h3>
                  <span className="font-tabular text-xs font-semibold text-[#286D65]">
                    Activity responses: {rec.matchedCount} of {rec.totalTrials}{' '}
                    matched ({rec.unsureCount} unsure)
                  </span>
                </div>
                <p className="mt-1 text-xs text-[#20304D]/75">
                  {rec.distancePreset} <span aria-hidden="true">·</span>{' '}
                  {rec.glassesStatus} <span aria-hidden="true">·</span>{' '}
                  {rec.reason}
                </p>
                {rec.observations.length > 0 && (
                  <ul className="mt-2 list-inside list-disc text-xs text-[#20304D]/85">
                    {rec.observations.map((obs) => (
                      <li key={obs}>{obs}</li>
                    ))}
                  </ul>
                )}
              </article>
            ))}
          </div>
        )}
      </section>

      {/* Section 2: Pre-populated Fictional Example Data (kept strictly separate) */}
      <section
        aria-labelledby="fictional-records-heading"
        className="mt-8 rounded-xl border border-[#20304D]/12 bg-white p-6 shadow-xs"
      >
        <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-[#20304D]/10 pb-4">
          <div>
            <h2
              id="fictional-records-heading"
              className="text-base font-semibold text-[#20304D]"
            >
              Pre-populated example records
            </h2>
            <p className="mt-0.5 text-xs text-[#20304D]/70">
              Shown for demonstration so you can see how multiple observations
              look over time.
            </p>
          </div>
          <span className="text-xs font-semibold text-[#20304D]/75">
            Fictional example data
          </span>
        </div>

        <div className="mt-4 divide-y divide-[#20304D]/10">
          {FICTIONAL_EXAMPLE_RECORDS.map((rec) => (
            <article key={rec.id} className="py-4 first:pt-0 last:pb-0">
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <h3 className="text-sm font-semibold text-[#20304D]">
                  {rec.childLabel} <span aria-hidden="true">·</span>{' '}
                  <span className="font-normal text-[#20304D]/70">
                    {rec.dateLabel} (Fictional example data)
                  </span>
                </h3>
                <span className="font-tabular text-xs font-medium text-[#20304D]/80">
                  Activity responses: {rec.matchedCount} of {rec.totalTrials}{' '}
                  matched ({rec.unsureCount} unsure)
                </span>
              </div>
              <p className="mt-1 text-xs text-[#20304D]/70">
                {rec.distancePreset} <span aria-hidden="true">·</span>{' '}
                {rec.glassesStatus} <span aria-hidden="true">·</span>{' '}
                {rec.reason}
              </p>
              <ul className="mt-2 list-inside list-disc text-xs text-[#20304D]/80">
                {rec.observations.map((obs) => (
                  <li key={obs}>{obs}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
};
