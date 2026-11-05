import React, { useRef, useState } from 'react';
import {
  NEXT_STEP_OPTIONS,
  OBSERVATION_OPTIONS,
  generateParentNoteText,
  type NoteRecipient,
  type OnsetTiming,
  type ParentNoteConfig,
  type SetupState,
  type TrialResponse,
} from '../utils/focalLogic';

interface ParentNoteScreenProps {
  setup: SetupState;
  noteConfig: ParentNoteConfig;
  responses: TrialResponse[];
  manualNoteOverride: string | null;
  onUpdateNoteConfig: (updater: (prev: ParentNoteConfig) => ParentNoteConfig) => void;
  onSetManualNoteOverride: (val: string | null) => void;
  onStartCheck: () => void;
  onShowToast?: (msg: string) => void;
}

const RECIPIENTS: NoteRecipient[] = [
  'Pediatric Optometrist or Ophthalmologist',
  'School Nurse',
  'Pediatrician',
];

const ONSET_OPTIONS: OnsetTiming[] = [
  'After a recent school screening letter (last 1–2 weeks)',
  'Noticed gradually over the past 1–3 months',
  'Noticed for more than 3 months',
  'Unsure of exact timing',
];

export const ParentNoteScreen: React.FC<ParentNoteScreenProps> = ({
  setup,
  noteConfig,
  responses,
  manualNoteOverride,
  onUpdateNoteConfig,
  onSetManualNoteOverride,
  onStartCheck,
  onShowToast,
}) => {
  const [copyFeedback, setCopyFeedback] = useState<string | null>(null);
  const [downloadFeedback, setDownloadFeedback] = useState<string | null>(null);
  const [noteFlashKey, setNoteFlashKey] = useState<number>(0);
  const [checklistState, setChecklistState] = useState<{
    findProvider: boolean;
    chooseAppointment: boolean;
    bringSchoolLetter: boolean;
  }>({
    findProvider: false,
    chooseAppointment: false,
    bringSchoolLetter: false,
  });

  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  const detailLevel = noteConfig.noteDetailLevel ?? 50;
  const detailLabel =
    detailLevel < 35
      ? 'Concise summary'
      : detailLevel > 65
        ? 'Detailed + Doctor questions'
        : 'Balanced family note';

  const generatedNote = generateParentNoteText(setup, noteConfig, responses);
  const activeNoteText =
    manualNoteOverride !== null ? manualNoteOverride : generatedNote;
  const wordCount = activeNoteText
    .trim()
    .split(/\s+/)
    .filter(Boolean).length;

  const toggleObservation = (obs: string) => {
    onSetManualNoteOverride(null);
    setNoteFlashKey((k) => k + 1);
    onUpdateNoteConfig((prev) => {
      const exists = prev.selectedObservations.includes(obs);
      onShowToast?.(
        exists
          ? 'Removed observation from parent note'
          : 'Added observation to parent note'
      );
      return {
        ...prev,
        selectedObservations: exists
          ? prev.selectedObservations.filter((item) => item !== obs)
          : [...prev.selectedObservations, obs],
      };
    });
  };

  const toggleNextStep = (stepText: string) => {
    onSetManualNoteOverride(null);
    setNoteFlashKey((k) => k + 1);
    onUpdateNoteConfig((prev) => {
      const exists = prev.selectedNextSteps.includes(stepText);
      onShowToast?.('Updated planned next steps in note');
      return {
        ...prev,
        selectedNextSteps: exists
          ? prev.selectedNextSteps.filter((item) => item !== stepText)
          : [...prev.selectedNextSteps, stepText],
      };
    });
  };

  const handleCopyNote = async () => {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(activeNoteText);
        setCopyFeedback('Copied note to clipboard.');
        onShowToast?.('Copied parent note to clipboard');
        setTimeout(() => setCopyFeedback(null), 4000);
        return;
      }
    } catch {
      // Fallback below when opened locally or clipboard permission blocked
    }

    if (textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.select();
      try {
        const ok = document.execCommand('copy');
        if (ok) {
          setCopyFeedback('Copied note using local browser fallback.');
          onShowToast?.('Copied parent note to clipboard');
        } else {
          setCopyFeedback(
            'Note text is highlighted — press Ctrl+C (or Cmd+C) to copy.'
          );
        }
      } catch {
        setCopyFeedback(
          'Note text is highlighted — press Ctrl+C (or Cmd+C) to copy.'
        );
      }
      setTimeout(() => setCopyFeedback(null), 5000);
    }
  };

  const handleDownloadTxt = () => {
    const blob = new Blob([activeNoteText], {
      type: 'text/plain;charset=utf-8',
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    const safeChild =
      setup.childLabel
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-|-$/g, '') || 'child';
    link.href = url;
    link.download = `focal-family-parent-note-${safeChild}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    setDownloadFeedback('Downloaded .txt note to your device.');
    onShowToast?.('Downloaded .txt parent note');
    setTimeout(() => setDownloadFeedback(null), 4000);
  };

  return (
    <div className="mx-auto max-w-[1160px] px-6 py-10">
      {/* Page Header */}
      <div className="animate-reveal-up flex flex-wrap items-end justify-between gap-4 border-b border-[#20304D]/12 pb-6">
        <div>
          <p className="text-xs font-semibold tracking-wider text-[#286D65] uppercase">
            Parent note builder <span aria-hidden="true">·</span> Next-step plan
          </p>
          <h1 className="mt-1 text-2xl font-semibold text-[#20304D] sm:text-3xl">
            Prepare your editable note for the school nurse or eye doctor
          </h1>
          <p className="mt-1.5 max-w-[68ch] text-sm text-[#20304D]/80">
            Select what you have noticed and who you are meeting with. The note
            preview updates immediately and can be edited word-for-word before
            you copy or download it.
          </p>
        </div>

        <button
          type="button"
          onClick={onStartCheck}
          className="inline-flex min-h-[44px] whitespace-nowrap shrink-0 items-center gap-2 rounded-full border border-[#20304D]/20 bg-white px-5 py-2 text-xs font-semibold text-[#20304D] transition-all hover:border-[#286D65] hover:bg-[#E5EEE8] active:scale-[0.98]"
        >
          <span>Run or update letter activity</span>
        </button>
      </div>

      {/* Interactive Note Detail Tuner Bar (inspired by UI demo slider bar) */}
      <section
        aria-label="Note detail level tuner"
        className="animate-reveal-up animate-reveal-delay-1 mt-6 rounded-2xl border border-[#20304D]/12 bg-white/90 p-5 shadow-xs backdrop-blur-xs"
      >
        <div className="flex flex-col justify-between gap-5 md:flex-row md:items-center">
          <div>
            <h2 className="flex items-center gap-2 text-sm font-bold text-[#20304D]">
              <svg
                className="h-4 w-4 text-[#286D65]"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                aria-hidden="true"
              >
                <line x1="4" y1="21" x2="4" y2="14" />
                <line x1="4" y1="10" x2="4" y2="3" />
                <line x1="12" y1="21" x2="12" y2="12" />
                <line x1="12" y1="8" x2="12" y2="3" />
                <line x1="20" y1="21" x2="20" y2="16" />
                <line x1="20" y1="12" x2="20" y2="3" />
                <line x1="1" y1="14" x2="7" y2="14" />
                <line x1="9" y1="8" x2="15" y2="8" />
                <line x1="17" y1="16" x2="23" y2="16" />
              </svg>
              <span>Tune Note Detail Level</span>
            </h2>
            <p className="mt-0.5 text-xs text-[#20304D]/70">
              Slide to switch between a quick school nurse summary and a full
              eye-exam note with questions.
            </p>
          </div>

          <div className="w-full max-w-md space-y-2">
            <div className="flex justify-between text-xs font-medium text-[#20304D]/80">
              <span>Concise summary</span>
              <span className="font-semibold text-[#286D65]">
                {detailLabel}
              </span>
              <span>Detailed + Questions</span>
            </div>
            <input
              type="range"
              aria-label="Note detail level"
              min={1}
              max={100}
              value={detailLevel}
              onChange={(e) => {
                onSetManualNoteOverride(null);
                setNoteFlashKey((k) => k + 1);
                onUpdateNoteConfig((prev) => ({
                  ...prev,
                  noteDetailLevel: Number(e.target.value),
                }));
              }}
              className="focal-slider w-full"
            />
          </div>
        </div>
      </section>

      {/* Main Two-Column Builder (Stacks controls above preview on mobile) */}
      <div className="animate-reveal-up animate-reveal-delay-2 mt-7 grid grid-cols-1 items-start gap-8 lg:grid-cols-12">
        {/* Left Column: Controls */}
        <div className="space-y-6 rounded-2xl border border-[#20304D]/12 bg-white p-6 shadow-xs lg:col-span-6">
          {/* Intended Recipient */}
          <fieldset>
            <legend className="text-sm font-semibold text-[#20304D]">
              1. Intended recipient
            </legend>
            <div className="mt-2.5 flex flex-wrap gap-2">
              {RECIPIENTS.map((rec) => {
                const selected = noteConfig.recipient === rec;
                return (
                  <button
                    key={rec}
                    type="button"
                    aria-pressed={selected}
                    onClick={() => {
                      onSetManualNoteOverride(null);
                      setNoteFlashKey((k) => k + 1);
                      onUpdateNoteConfig((prev) => ({
                        ...prev,
                        recipient: rec,
                      }));
                      onShowToast?.(`Recipient set to ${rec}`);
                    }}
                    className={`min-h-[44px] whitespace-nowrap shrink-0 rounded-full border px-4 py-2 text-left text-xs font-medium transition-all ${
                      selected
                        ? 'border-[#286D65] bg-[#286D65] font-semibold text-white shadow-xs'
                        : 'border-[#20304D]/15 bg-white text-[#20304D]/85 hover:border-[#286D65]/40 hover:bg-[#F7F5F0]'
                    }`}
                  >
                    {rec}
                  </button>
                );
              })}
            </div>
          </fieldset>

          {/* Approximate Onset */}
          <div className="border-t border-[#20304D]/10 pt-5">
            <label
              htmlFor="onset-select"
              className="block text-sm font-semibold text-[#20304D]"
            >
              2. Approximate timing / onset
            </label>
            <select
              id="onset-select"
              value={noteConfig.onset}
              onChange={(e) => {
                onSetManualNoteOverride(null);
                setNoteFlashKey((k) => k + 1);
                onUpdateNoteConfig((prev) => ({
                  ...prev,
                  onset: e.target.value as OnsetTiming,
                }));
                onShowToast?.('Updated approximate timing');
              }}
              className="mt-2 min-h-[44px] w-full rounded-xl border border-[#20304D]/25 bg-[#F7F5F0]/60 px-3.5 py-2.5 text-sm text-[#20304D] focus:border-[#286D65] focus:bg-white focus:outline-2 focus:outline-[#286D65]"
            >
              {ONSET_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>

          {/* Observation Controls */}
          <fieldset className="border-t border-[#20304D]/10 pt-5">
            <legend className="text-sm font-semibold text-[#20304D]">
              3. Observations to include in note
            </legend>
            <p className="mt-1 text-xs text-[#20304D]/70">
              Toggle observations from home, school, or the directional letter
              activity.
            </p>
            <div className="mt-3 space-y-2">
              {OBSERVATION_OPTIONS.map((obs) => {
                const active = noteConfig.selectedObservations.includes(obs);
                return (
                  <label
                    key={obs}
                    className={`flex min-h-[44px] cursor-pointer items-start gap-3 rounded-xl border p-3 text-xs sm:text-sm transition-colors ${
                      active
                        ? 'border-[#286D65] bg-[#E5EEE8]/70 font-medium text-[#20304D]'
                        : 'border-[#20304D]/15 bg-white text-[#20304D]/85 hover:bg-[#F7F5F0]/60'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={active}
                      onChange={() => toggleObservation(obs)}
                      className="mt-0.5 h-4 w-4 shrink-0 cursor-pointer accent-[#286D65]"
                    />
                    <span>{obs}</span>
                  </label>
                );
              })}
            </div>

            <div className="mt-3">
              <label
                htmlFor="custom-obs-input"
                className="block text-xs font-semibold text-[#20304D]/85"
              >
                Additional specific detail (optional)
              </label>
              <input
                id="custom-obs-input"
                type="text"
                value={noteConfig.customObservationNote}
                onChange={(e) => {
                  onSetManualNoteOverride(null);
                  onUpdateNoteConfig((prev) => ({
                    ...prev,
                    customObservationNote: e.target.value,
                  }));
                }}
                placeholder="e.g., Sits close to the TV or squints at distant street signs"
                className="mt-1.5 min-h-[44px] w-full rounded-xl border border-[#20304D]/20 bg-[#F7F5F0]/50 px-3.5 py-2 text-sm text-[#20304D] focus:border-[#286D65] focus:bg-white focus:outline-2 focus:outline-[#286D65]"
              />
            </div>
          </fieldset>

          {/* Editable Next-Step Selection */}
          <fieldset className="border-t border-[#20304D]/10 pt-5">
            <legend className="text-sm font-semibold text-[#20304D]">
              4. Planned next steps in your note
            </legend>
            <div className="mt-2.5 space-y-2">
              {NEXT_STEP_OPTIONS.map((stepText) => {
                const active = noteConfig.selectedNextSteps.includes(stepText);
                return (
                  <label
                    key={stepText}
                    className={`flex min-h-[44px] cursor-pointer items-start gap-3 rounded-xl border p-3 text-xs sm:text-sm transition-colors ${
                      active
                        ? 'border-[#286D65] bg-[#E5EEE8]/70 font-medium text-[#20304D]'
                        : 'border-[#20304D]/15 bg-white text-[#20304D]/85 hover:bg-[#F7F5F0]/60'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={active}
                      onChange={() => toggleNextStep(stepText)}
                      className="mt-0.5 h-4 w-4 shrink-0 cursor-pointer accent-[#286D65]"
                    />
                    <span>{stepText}</span>
                  </label>
                );
              })}
            </div>
          </fieldset>
        </div>

        {/* Right Column: Live Editable Note Preview + Action Checklist */}
        <div className="space-y-6 lg:col-span-6">
          <section
            key={noteFlashKey}
            aria-labelledby="live-note-heading"
            className="animate-note-flash rounded-2xl border border-[#20304D]/15 bg-white p-6 shadow-xs"
          >
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#20304D]/10 pb-4">
              <div>
                <h2
                  id="live-note-heading"
                  className="text-base font-semibold text-[#20304D]"
                >
                  Live parent note preview
                </h2>
                <p className="mt-0.5 text-xs font-medium text-[#286D65]">
                  Draft only — nothing has been sent ·{' '}
                  <span className="font-tabular">{wordCount} words</span>
                </p>
              </div>

              {manualNoteOverride !== null && (
                <button
                  type="button"
                  onClick={() => onSetManualNoteOverride(null)}
                  className="min-h-[36px] rounded-full border border-[#20304D]/20 px-3.5 py-1 text-xs font-medium text-[#20304D] hover:bg-[#F7F5F0]"
                >
                  Reset to auto-generated text
                </button>
              )}
            </div>

            <div className="mt-4">
              <label
                htmlFor="editable-parent-note"
                className="block text-xs font-semibold text-[#20304D]/75"
              >
                Editable note text (you can type directly in this box)
              </label>
              <textarea
                id="editable-parent-note"
                ref={textareaRef}
                rows={15}
                value={activeNoteText}
                onChange={(e) => onSetManualNoteOverride(e.target.value)}
                className="mt-2 w-full rounded-xl border border-[#20304D]/25 bg-[#F7F5F0]/60 p-4 text-sm leading-relaxed text-[#20304D] focus:border-[#286D65] focus:bg-white focus:outline-2 focus:outline-[#286D65]"
              />
            </div>

            {/* Modern Pill Action Buttons: Copy note & Download .txt */}
            <div className="mt-4 flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={handleCopyNote}
                className="btn-sheen inline-flex min-h-[48px] whitespace-nowrap shrink-0 items-center gap-2 rounded-full bg-[#286D65] px-6 py-2.5 text-sm font-semibold text-white shadow-xs transition-all hover:bg-[#1f5650] active:scale-[0.98]"
              >
                <svg
                  className="h-4 w-4"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  aria-hidden="true"
                >
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                </svg>
                <span>Copy note</span>
              </button>

              <button
                type="button"
                onClick={handleDownloadTxt}
                className="inline-flex min-h-[48px] whitespace-nowrap shrink-0 items-center gap-2 rounded-full border border-[#20304D]/25 bg-white px-6 py-2.5 text-sm font-semibold text-[#20304D] transition-all hover:border-[#286D65] hover:bg-[#F7F5F0] active:scale-[0.98]"
              >
                <svg
                  className="h-4 w-4 text-[#286D65]"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  aria-hidden="true"
                >
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="7 10 12 15 17 10" />
                  <line x1="12" y1="15" x2="12" y2="3" />
                </svg>
                <span>Download .txt</span>
              </button>
            </div>

            {(copyFeedback || downloadFeedback) && (
              <p
                role="status"
                aria-live="polite"
                className="mt-3 text-xs font-semibold text-[#286D65]"
              >
                {copyFeedback || downloadFeedback}
              </p>
            )}

            <p className="mt-4 border-t border-[#20304D]/10 pt-3 text-xs leading-relaxed text-[#20304D]/70">
              <strong>Session privacy notice:</strong> Information entered here
              is kept in memory for this browser session only. Refreshing or
              closing the page clears your session information unless you have
              copied or downloaded your note.
            </p>
          </section>

          {/* Brief Action Checklist for the Parent */}
          <section
            aria-labelledby="family-checklist-heading"
            className="rounded-2xl border border-[#20304D]/12 bg-[#E5EEE8] p-6"
          >
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <h2
                id="family-checklist-heading"
                className="text-base font-semibold text-[#20304D]"
              >
                Personal follow-up checklist
              </h2>
              <span className="text-xs text-[#20304D]/75">
                For your own tracking — no appointment is booked here
              </span>
            </div>
            <p className="mt-1 text-xs text-[#20304D]/80">
              Focal Family does not send messages or schedule visits. Use this
              checklist as you arrange your child’s care:
            </p>

            <div className="mt-3 space-y-2.5">
              {[
                {
                  key: 'findProvider' as const,
                  title:
                    'Find a local pediatric optometrist or ophthalmologist who sees children aged 4–10',
                },
                {
                  key: 'chooseAppointment' as const,
                  title:
                    'Choose an appointment time when your child is well-rested (mornings often work well)',
                },
                {
                  key: 'bringSchoolLetter' as const,
                  title:
                    'Bring the school vision referral form, any current glasses, and your downloaded parent note',
                },
              ].map((item) => (
                <label
                  key={item.key}
                  className="flex min-h-[44px] cursor-pointer items-start gap-3 rounded-xl bg-white/90 p-3 text-xs sm:text-sm text-[#20304D]"
                >
                  <input
                    type="checkbox"
                    checked={checklistState[item.key]}
                    onChange={() =>
                      setChecklistState((prev) => ({
                        ...prev,
                        [item.key]: !prev[item.key],
                      }))
                    }
                    className="mt-0.5 h-4 w-4 shrink-0 cursor-pointer accent-[#286D65]"
                  />
                  <span>{item.title}</span>
                </label>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};
