import test from 'node:test';
import assert from 'node:assert/strict';
import {
  INITIAL_SETUP_STATE,
  INITIAL_NOTE_CONFIG,
  TRIAL_SEQUENCE,
  isSetupStepReady,
  summarizeTrialResponses,
  generateParentNoteText,
  FICTIONAL_EXAMPLE_RECORDS,
  type SetupState,
  type TrialResponse,
} from './focalLogic';

test('INITIAL_SETUP_STATE does not pre-check any readiness acknowledgments', () => {
  assert.equal(INITIAL_SETUP_STATE.readinessChecks.roomLit, false);
  assert.equal(INITIAL_SETUP_STATE.readinessChecks.distanceMarked, false);
  assert.equal(INITIAL_SETUP_STATE.readinessChecks.prototypeUnderstood, false);
  assert.equal(INITIAL_SETUP_STATE.readinessChecks.keepFollowUpUnderstood, false);
  const step3Unchecked: SetupState = { ...INITIAL_SETUP_STATE, step: 3 };
  assert.equal(isSetupStepReady(step3Unchecked), false);
});

test('isSetupStepReady requires all four readiness checkboxes on step 3', () => {
  const step3Ready: SetupState = {
    ...INITIAL_SETUP_STATE,
    step: 3,
    readinessChecks: {
      roomLit: true,
      distanceMarked: true,
      prototypeUnderstood: true,
      keepFollowUpUnderstood: true,
    },
  };
  assert.equal(isSetupStepReady(step3Ready), true);
});

test('summarizeTrialResponses counts matches and unsure responses without clinical claims', () => {
  const sampleResponses: TrialResponse[] = [
    {
      trialNumber: 1,
      expectedDirection: 'right',
      selectedDirection: 'right',
      matched: true,
      sizeTier: 'Large',
      eyeUsed: 'Both eyes',
    },
    {
      trialNumber: 5,
      expectedDirection: 'right',
      selectedDirection: 'unsure',
      matched: false,
      sizeTier: 'Medium',
      eyeUsed: 'Left eye covered',
    },
  ];

  const summary = summarizeTrialResponses(sampleResponses);
  assert.equal(summary.totalCompleted, 2);
  assert.equal(summary.matchedCount, 1);
  assert.equal(summary.unsureCount, 1);
  assert.equal(summary.byTier.Large.matched, 1);
  assert.equal(summary.byTier.Medium.matched, 0);
});

test('generateParentNoteText produces structured, non-diagnostic note reflecting controls', () => {
  const note = generateParentNoteText(INITIAL_SETUP_STATE, INITIAL_NOTE_CONFIG, []);
  assert.ok(note.includes('Dear Eye Care Provider,'));
  assert.ok(note.includes('Child A (Age 7)'));
  assert.ok(note.includes('not a clinical visual acuity test or medical diagnosis'));
});

test('TRIAL_SEQUENCE has 12 fixed-size trials and fictional records are explicitly marked', () => {
  assert.equal(TRIAL_SEQUENCE.length, 12);
  assert.ok(FICTIONAL_EXAMPLE_RECORDS.every((r) => r.isFictional === true));
});

test('generateParentNoteText adapts output when noteDetailLevel slider is adjusted', () => {
  const conciseNote = generateParentNoteText(
    INITIAL_SETUP_STATE,
    { ...INITIAL_NOTE_CONFIG, noteDetailLevel: 20 },
    []
  );
  const detailedNote = generateParentNoteText(
    INITIAL_SETUP_STATE,
    { ...INITIAL_NOTE_CONFIG, noteDetailLevel: 85 },
    []
  );
  assert.ok(conciseNote.includes('Sharing a quick summary'));
  assert.ok(detailedNote.includes('Questions we would like to ask at the visit:'));
});
