import { useRef, useState } from 'react';
import { ActivityScreen } from './components/ActivityScreen';
import { CompletionScreen } from './components/CompletionScreen';
import { DmvConceptModal } from './components/DmvConceptModal';
import { FocalLogo } from './components/FocalLogo';
import { HistoryScreen } from './components/HistoryScreen';
import { ParentNoteScreen } from './components/ParentNoteScreen';
import { SessionRadarDrawer } from './components/SessionRadarDrawer';
import { SetupScreen } from './components/SetupScreen';
import { WelcomeScreen } from './components/WelcomeScreen';
import {
  INITIAL_NOTE_CONFIG,
  INITIAL_SETUP_STATE,
  TRIAL_SEQUENCE,
  summarizeTrialResponses,
  type ActivityRecord,
  type ParentNoteConfig,
  type ScreenId,
  type SetupState,
  type TrialDirection,
  type TrialResponse,
} from './utils/focalLogic';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<ScreenId>(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      if (params.get('autostart') === '1') {
        return 'setup';
      }
    }
    return 'welcome';
  });

  const [setup, setSetup] = useState<SetupState>(INITIAL_SETUP_STATE);
  const [trialIndex, setTrialIndex] = useState<number>(0);
  const [responses, setResponses] = useState<TrialResponse[]>([]);
  const [noteConfig, setNoteConfig] =
    useState<ParentNoteConfig>(INITIAL_NOTE_CONFIG);
  const [manualNoteOverride, setManualNoteOverride] = useState<string | null>(
    null
  );
  const [sessionRecords, setSessionRecords] = useState<ActivityRecord[]>([]);
  const [dmvModalOpen, setDmvModalOpen] = useState<boolean>(false);
  const [radarDrawerOpen, setRadarDrawerOpen] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const toastTimerRef = useRef<number | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    if (toastTimerRef.current) {
      window.clearTimeout(toastTimerRef.current);
    }
    toastTimerRef.current = window.setTimeout(() => {
      setToastMessage(null);
    }, 3200);
  };

  const navigateTo = (screen: ScreenId) => {
    setCurrentScreen(screen);
    window.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior });
  };

  const handleStartCheck = () => {
    navigateTo('setup');
  };

  const handleBeginActivityFromSetup = () => {
    setTrialIndex(0);
    setResponses([]);
    showToast('Started 12-trial directional E activity');
    navigateTo('activity');
  };

  const finalizeSessionRecord = (finalResponses: TrialResponse[]) => {
    const summary = summarizeTrialResponses(finalResponses);
    const newRecord: ActivityRecord = {
      id: `session-${Date.now()}`,
      dateLabel: 'Today · Current browser session',
      childLabel: setup.childLabel.trim() || 'Child A',
      ageGroup: setup.ageGroup,
      glassesStatus: setup.glassesStatus,
      distancePreset: setup.distancePreset,
      matchedCount: summary.matchedCount,
      totalTrials: TRIAL_SEQUENCE.length,
      unsureCount: summary.unsureCount,
      observations: [...noteConfig.selectedObservations],
      reason: setup.reason,
      isFictional: false,
    };
    setSessionRecords((prev) => [newRecord, ...prev]);
    setManualNoteOverride(null);
    showToast('Activity logged · Ready to prepare parent note');
    navigateTo('completion');
  };

  const handleRecordAnswer = (selectedDirection: TrialDirection | 'unsure') => {
    const currentTrial = TRIAL_SEQUENCE[trialIndex];
    if (!currentTrial) return;

    const newResponse: TrialResponse = {
      trialNumber: currentTrial.trialNumber,
      expectedDirection: currentTrial.direction,
      selectedDirection,
      matched: selectedDirection === currentTrial.direction,
      sizeTier: currentTrial.sizeTier,
      eyeUsed: currentTrial.eyeUsed,
    };

    const updated = [
      ...responses.filter((r) => r.trialNumber !== currentTrial.trialNumber),
      newResponse,
    ];
    setResponses(updated);

    if (trialIndex + 1 < TRIAL_SEQUENCE.length) {
      setTrialIndex(trialIndex + 1);
    } else {
      finalizeSessionRecord(updated);
    }
  };

  const handleStepBackTrial = () => {
    if (trialIndex > 0) {
      setTrialIndex(trialIndex - 1);
    }
  };

  const handleToggleObservation = (obs: string) => {
    setManualNoteOverride(null);
    setNoteConfig((prev) => {
      const exists = prev.selectedObservations.includes(obs);
      showToast(
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

  return (
    <div className="flex min-h-screen flex-col bg-[#F7F5F0] text-[#20304D]">
      {/* Strict 3-Zone Top Navigation Bar with Official Focal Technologies Logo */}
      <header className="sticky top-0 z-30 border-b border-[#20304D]/10 bg-white/90 px-4 py-3 backdrop-blur-md sm:px-6 sm:py-3.5">
        <div className="mx-auto flex max-w-[1160px] items-center justify-between gap-3 md:gap-8">
          {/* Zone 1: Official Focal Technologies Logo Lockup */}
          <a
            href="#welcome"
            onClick={(e) => {
              e.preventDefault();
              navigateTo('welcome');
            }}
            aria-label="Focal Family Home"
            className="inline-flex items-center whitespace-nowrap shrink-0 rounded-lg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#286D65]"
          >
            <FocalLogo className="h-9 sm:h-10 w-auto" />
          </a>

          {/* Zone 2: Concise single-line navigation links */}
          <nav
            aria-label="Primary navigation"
            className="flex items-center gap-4 sm:gap-7 text-xs sm:text-sm font-medium text-[#20304D]/80"
          >
            <a
              href="#welcome"
              onClick={(e) => {
                e.preventDefault();
                navigateTo('welcome');
              }}
              aria-current={currentScreen === 'welcome' ? 'page' : undefined}
              className={`whitespace-nowrap shrink-0 py-1 transition-colors hover:text-[#20304D] hover:underline hover:underline-offset-4 ${
                currentScreen === 'welcome'
                  ? 'font-semibold text-[#20304D] underline decoration-[#286D65] decoration-2 underline-offset-4'
                  : ''
              }`}
            >
              Welcome
            </a>
            <a
              href="#setup"
              onClick={(e) => {
                e.preventDefault();
                navigateTo('setup');
              }}
              aria-current={currentScreen === 'setup' ? 'page' : undefined}
              className={`hidden md:inline whitespace-nowrap shrink-0 py-1 transition-colors hover:text-[#20304D] hover:underline hover:underline-offset-4 ${
                currentScreen === 'setup'
                  ? 'font-semibold text-[#20304D] underline decoration-[#286D65] decoration-2 underline-offset-4'
                  : ''
              }`}
            >
              Guided setup
            </a>
            <a
              href="#note"
              onClick={(e) => {
                e.preventDefault();
                navigateTo('note');
              }}
              aria-current={currentScreen === 'note' ? 'page' : undefined}
              className={`whitespace-nowrap shrink-0 py-1 transition-colors hover:text-[#20304D] hover:underline hover:underline-offset-4 ${
                currentScreen === 'note'
                  ? 'font-semibold text-[#20304D] underline decoration-[#286D65] decoration-2 underline-offset-4'
                  : ''
              }`}
            >
              Parent note
            </a>
            <a
              href="#history"
              onClick={(e) => {
                e.preventDefault();
                navigateTo('history');
              }}
              aria-current={currentScreen === 'history' ? 'page' : undefined}
              className={`whitespace-nowrap shrink-0 py-1 transition-colors hover:text-[#20304D] hover:underline hover:underline-offset-4 ${
                currentScreen === 'history'
                  ? 'font-semibold text-[#20304D] underline decoration-[#286D65] decoration-2 underline-offset-4'
                  : ''
              }`}
            >
              History
            </a>
          </nav>

          {/* Zone 3: 1 Primary Action */}
          <div className="hidden md:flex items-center shrink-0">
            <button
              type="button"
              onClick={handleStartCheck}
              className="inline-flex min-h-[42px] whitespace-nowrap shrink-0 items-center gap-2 rounded-lg bg-[#1F5C55] px-4 py-2 text-sm font-semibold text-white shadow-2xs transition-colors duration-[180ms] hover:bg-[#174741] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#1F5C55]"
            >
              <span>Start a check together</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area with Smooth 260ms Fade + Vertical Lift Page Transition */}
      <main className="flex-1">
        <div key={currentScreen} className="animate-reveal-up">
          {currentScreen === 'welcome' && (
            <WelcomeScreen
              onNavigate={navigateTo}
              onStartCheck={handleStartCheck}
            />
          )}

          {currentScreen === 'setup' && (
            <SetupScreen
              setup={setup}
              onUpdateSetup={setSetup}
              onCancelToWelcome={() => navigateTo('welcome')}
              onStartActivity={handleBeginActivityFromSetup}
            />
          )}

          {currentScreen === 'activity' && (
            <ActivityScreen
              setup={setup}
              currentIndex={trialIndex}
              responses={responses}
              selectedObservations={noteConfig.selectedObservations}
              onRecordAnswer={handleRecordAnswer}
              onStepBackTrial={handleStepBackTrial}
              onToggleObservation={handleToggleObservation}
              onExitToSetup={() => navigateTo('setup')}
              onFinishEarly={() => finalizeSessionRecord(responses)}
            />
          )}

          {currentScreen === 'completion' && (
            <CompletionScreen
              setup={setup}
              responses={responses}
              selectedObservations={noteConfig.selectedObservations}
              onToggleObservation={handleToggleObservation}
              onPrepareParentNote={() => navigateTo('note')}
              onViewHistory={() => navigateTo('history')}
              onRestartActivity={handleBeginActivityFromSetup}
            />
          )}

          {currentScreen === 'note' && (
            <ParentNoteScreen
              setup={setup}
              noteConfig={noteConfig}
              responses={responses}
              manualNoteOverride={manualNoteOverride}
              onUpdateNoteConfig={setNoteConfig}
              onSetManualNoteOverride={setManualNoteOverride}
              onStartCheck={handleStartCheck}
              onShowToast={showToast}
            />
          )}

          {currentScreen === 'history' && (
            <HistoryScreen
              sessionRecords={sessionRecords}
              onNavigate={navigateTo}
              onStartCheck={handleStartCheck}
            />
          )}
        </div>
      </main>

      {/* Quiet Footer with Logo, Prototype Notice, Prep Snapshot Trigger, and Small DMV Concept Link */}
      <footer className="border-t border-[#20304D]/10 bg-white px-6 py-6 text-xs text-[#20304D]/75">
        <div className="mx-auto flex max-w-[1160px] flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-4">
            <FocalLogo className="h-8 w-auto" />
            <div className="space-y-0.5">
              <p className="font-semibold text-[#20304D]">
                Focal Family · Student Prototype (Non-diagnostic)
              </p>
              <p>
                Session-only memory: refreshing clears entered information
                unless you download your parent note (.txt). No accounts,
                analytics, or camera access.
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-4 shrink-0">
            <button
              type="button"
              onClick={() => setRadarDrawerOpen(true)}
              className="group inline-flex min-h-[38px] items-center gap-2 rounded-full border border-[#20304D]/18 bg-[#F7F5F0] px-4 py-1.5 text-xs font-semibold text-[#20304D] transition-all hover:border-[#286D65] hover:bg-[#E5EEE8]"
            >
              <svg
                className="h-3.5 w-3.5 text-[#286D65] transition-transform duration-500 group-hover:rotate-90"
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
              <span>Prep Snapshot</span>
            </button>

            <button
              type="button"
              onClick={() => setDmvModalOpen(true)}
              className="min-h-[36px] text-xs font-medium text-[#20304D]/75 underline decoration-[#20304D]/30 underline-offset-4 hover:text-[#20304D]"
            >
              Explore the DMV concept
            </button>
          </div>
        </div>
      </footer>

      {/* Slide-Over Prep Snapshot Drawer */}
      <SessionRadarDrawer
        open={radarDrawerOpen}
        onClose={() => setRadarDrawerOpen(false)}
        setup={setup}
        responses={responses}
        noteConfig={noteConfig}
        onNavigate={navigateTo}
      />

      {/* DMV Concept Modal */}
      <DmvConceptModal
        open={dmvModalOpen}
        onClose={() => setDmvModalOpen(false)}
      />

      {/* Modern Toast Feedback Notification */}
      <div
        role="status"
        aria-live="polite"
        className={`fixed right-6 bottom-6 z-50 flex items-center gap-3 rounded-full border border-[#286D65]/35 bg-[#20304D] px-4 py-2.5 text-xs font-medium text-white shadow-xl transition-all duration-300 ${
          toastMessage
            ? 'translate-y-0 opacity-100'
            : 'pointer-events-none translate-y-12 opacity-0'
        }`}
      >
        <svg
          className="h-4 w-4 text-[#E5EEE8]"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.2"
          aria-hidden="true"
        >
          <polyline points="20 6 9 17 4 12" />
        </svg>
        <span>{toastMessage}</span>
      </div>
    </div>
  );
}
