import React from 'react';

interface DmvConceptModalProps {
  open: boolean;
  onClose: () => void;
}

export const DmvConceptModal: React.FC<DmvConceptModalProps> = ({
  open,
  onClose,
}) => {
  if (!open) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="dmv-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-[#20304D]/45 p-4"
    >
      <div className="w-full max-w-lg rounded-xl border border-[#20304D]/15 bg-white p-6 shadow-lg sm:p-7">
        <div className="flex items-baseline justify-between gap-4 border-b border-[#20304D]/10 pb-3">
          <h2
            id="dmv-modal-title"
            className="text-lg font-semibold text-[#10265F]"
          >
            Focal DMV readiness concept (secondary exploration)
          </h2>
          <span className="text-xs text-[#20304D]/65">Student prototype</span>
        </div>

        <p className="mt-4 text-sm leading-relaxed text-[#20304D]/85">
          Alongside <strong>Focal Family</strong> (designed for parents of
          children aged 4–10), our student team explored a secondary concept for
          adults preparing for an upcoming driver’s license vision renewal test
          at the DMV.
        </p>

        <div className="mt-4 rounded-lg bg-[#F7F5F0] p-4 text-xs leading-relaxed text-[#20304D]/85">
          <p className="font-semibold text-[#10265F]">
            Why Focal Family is our primary focus:
          </p>
          <p className="mt-1">
            Parents receiving a school vision screening letter often feel
            uncertain about what the letter means and what to share at an eye
            exam. Focal Family turns a calm at-home activity and parent
            observations into a concrete, editable note for a school nurse or
            pediatric eye doctor.
          </p>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="min-h-[44px] rounded-lg bg-[#10265F] px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#0B1B46] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#3E9BE0]"
          >
            Return to Focal Family
          </button>
        </div>
      </div>
    </div>
  );
};
