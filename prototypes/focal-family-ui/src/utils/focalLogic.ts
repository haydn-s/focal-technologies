export type ScreenId = 'welcome' | 'setup' | 'activity' | 'completion' | 'note' | 'history';

export type AgeGroup = '4–5 years' | '6–7 years' | '8–10 years';

export type CheckReason =
  | 'Received a school vision referral letter'
  | 'Noticed squinting or sitting close to screens'
  | 'Routine preparation before an eye appointment'
  | 'Following up after a change in glasses';

export type GlassesStatus =
  | 'Does not wear glasses'
  | 'Wears glasses (wearing them now)'
  | 'Wears glasses (not available right now)';

export type DistancePreset = '10 ft (3 meters)' | '6 ft (1.8 meters)';

export type TrialDirection = 'up' | 'right' | 'down' | 'left';

export interface ReadinessChecks {
  roomLit: boolean;
  distanceMarked: boolean;
  prototypeUnderstood: boolean;
  keepFollowUpUnderstood: boolean;
}

export interface SetupState {
  step: 1 | 2 | 3;
  childLabel: string;
  ageGroup: AgeGroup;
  reason: CheckReason;
  glassesStatus: GlassesStatus;
  distancePreset: DistancePreset;
  cardSliderWidthPx: number;
  readinessChecks: ReadinessChecks;
}

export interface TrialSpec {
  trialNumber: number;
  direction: TrialDirection;
  sizeTier: 'Large' | 'Medium' | 'Smaller';
  pixelSize: number;
  eyeUsed: 'Both eyes' | 'Left eye covered' | 'Right eye covered';
}

export interface TrialResponse {
  trialNumber: number;
  expectedDirection: TrialDirection;
  selectedDirection: TrialDirection | 'unsure';
  matched: boolean;
  sizeTier: 'Large' | 'Medium' | 'Smaller';
  eyeUsed: 'Both eyes' | 'Left eye covered' | 'Right eye covered';
}

export type NoteRecipient =
  | 'Pediatric Optometrist or Ophthalmologist'
  | 'School Nurse'
  | 'Pediatrician';

export type OnsetTiming =
  | 'After a recent school screening letter (last 1–2 weeks)'
  | 'Noticed gradually over the past 1–3 months'
  | 'Noticed for more than 3 months'
  | 'Unsure of exact timing';

export interface ParentNoteConfig {
  recipient: NoteRecipient;
  onset: OnsetTiming;
  selectedObservations: string[];
  customObservationNote: string;
  selectedNextSteps: string[];
  noteDetailLevel?: number;
}

export interface ActivityRecord {
  id: string;
  dateLabel: string;
  childLabel: string;
  ageGroup: AgeGroup;
  glassesStatus: GlassesStatus;
  distancePreset: DistancePreset;
  matchedCount: number;
  totalTrials: number;
  unsureCount: number;
  observations: string[];
  reason: CheckReason;
  isFictional: boolean;
}

export const OBSERVATION_OPTIONS: string[] = [
  'School screening letter noted a vision referral',
  'Squinting when looking at distant signs or the classroom board',
  'Tilting head or covering one eye during reading or TV',
  'Moving closer to the television, tablet, or book',
  'Rubbing eyes or mentioning tired eyes after school',
  'Hesitating on smaller directional shapes during the home activity',
];

export const NEXT_STEP_OPTIONS: string[] = [
  'Schedule a comprehensive pediatric eye exam with an optometrist or ophthalmologist',
  'Bring the school vision referral letter and this observation note to the visit',
  'Share scheduling updates with the school nurse so classroom seating can be supported',
  'If glasses are prescribed or updated, ask about transition tips for school and reading',
];

export const INITIAL_SETUP_STATE: SetupState = {
  step: 1,
  childLabel: 'Child A (Age 7)',
  ageGroup: '6–7 years',
  reason: 'Received a school vision referral letter',
  glassesStatus: 'Does not wear glasses',
  distancePreset: '10 ft (3 meters)',
  cardSliderWidthPx: 240,
  readinessChecks: {
    roomLit: false,
    distanceMarked: false,
    prototypeUnderstood: false,
    keepFollowUpUnderstood: false,
  },
};

export const INITIAL_NOTE_CONFIG: ParentNoteConfig = {
  recipient: 'Pediatric Optometrist or Ophthalmologist',
  onset: 'After a recent school screening letter (last 1–2 weeks)',
  selectedObservations: [
    'School screening letter noted a vision referral',
    'Squinting when looking at distant signs or the classroom board',
    'Hesitating on smaller directional shapes during the home activity',
  ],
  customObservationNote: 'Reads comfortably up close, but asks what distant street signs say when riding in the car.',
  selectedNextSteps: [
    'Schedule a comprehensive pediatric eye exam with an optometrist or ophthalmologist',
    'Bring the school vision referral letter and this observation note to the visit',
    'Share scheduling updates with the school nurse so classroom seating can be supported',
  ],
};

export const TRIAL_SEQUENCE: TrialSpec[] = [
  { trialNumber: 1, direction: 'right', sizeTier: 'Large', pixelSize: 96, eyeUsed: 'Both eyes' },
  { trialNumber: 2, direction: 'down', sizeTier: 'Large', pixelSize: 96, eyeUsed: 'Both eyes' },
  { trialNumber: 3, direction: 'left', sizeTier: 'Large', pixelSize: 96, eyeUsed: 'Both eyes' },
  { trialNumber: 4, direction: 'up', sizeTier: 'Large', pixelSize: 96, eyeUsed: 'Both eyes' },
  { trialNumber: 5, direction: 'right', sizeTier: 'Medium', pixelSize: 64, eyeUsed: 'Left eye covered' },
  { trialNumber: 6, direction: 'up', sizeTier: 'Medium', pixelSize: 64, eyeUsed: 'Left eye covered' },
  { trialNumber: 7, direction: 'down', sizeTier: 'Medium', pixelSize: 64, eyeUsed: 'Right eye covered' },
  { trialNumber: 8, direction: 'left', sizeTier: 'Medium', pixelSize: 64, eyeUsed: 'Right eye covered' },
  { trialNumber: 9, direction: 'up', sizeTier: 'Smaller', pixelSize: 44, eyeUsed: 'Left eye covered' },
  { trialNumber: 10, direction: 'right', sizeTier: 'Smaller', pixelSize: 44, eyeUsed: 'Left eye covered' },
  { trialNumber: 11, direction: 'left', sizeTier: 'Smaller', pixelSize: 44, eyeUsed: 'Right eye covered' },
  { trialNumber: 12, direction: 'down', sizeTier: 'Smaller', pixelSize: 44, eyeUsed: 'Right eye covered' },
];

export const FICTIONAL_EXAMPLE_RECORDS: ActivityRecord[] = [
  {
    id: 'fictional-1',
    dateLabel: 'Oct 14 · Example entry',
    childLabel: 'Maya (Example, Age 6)',
    ageGroup: '6–7 years',
    glassesStatus: 'Does not wear glasses',
    distancePreset: '10 ft (3 meters)',
    matchedCount: 9,
    totalTrials: 12,
    unsureCount: 2,
    observations: [
      'School screening letter noted a vision referral',
      'Squinting when looking at distant signs or the classroom board',
    ],
    reason: 'Received a school vision referral letter',
    isFictional: true,
  },
  {
    id: 'fictional-2',
    dateLabel: 'Oct 28 · Example entry',
    childLabel: 'Maya (Example, Age 6)',
    ageGroup: '6–7 years',
    glassesStatus: 'Does not wear glasses',
    distancePreset: '10 ft (3 meters)',
    matchedCount: 10,
    totalTrials: 12,
    unsureCount: 1,
    observations: [
      'Hesitating on smaller directional shapes during the home activity',
      'Moving closer to the television, tablet, or book',
    ],
    reason: 'Routine preparation before an eye appointment',
    isFictional: true,
  },
  {
    id: 'fictional-3',
    dateLabel: 'Nov 02 · Example entry',
    childLabel: 'Leo (Example, Age 8)',
    ageGroup: '8–10 years',
    glassesStatus: 'Wears glasses (wearing them now)',
    distancePreset: '10 ft (3 meters)',
    matchedCount: 11,
    totalTrials: 12,
    unsureCount: 1,
    observations: [
      'Rubbing eyes or mentioning tired eyes after school',
    ],
    reason: 'Following up after a change in glasses',
    isFictional: true,
  },
];

export function isSetupStepReady(state: SetupState): boolean {
  if (state.step === 1) {
    return state.childLabel.trim().length > 0;
  }
  if (state.step === 2) {
    return state.cardSliderWidthPx >= 180 && state.cardSliderWidthPx <= 320;
  }
  if (state.step === 3) {
    const { roomLit, distanceMarked, prototypeUnderstood, keepFollowUpUnderstood } = state.readinessChecks;
    return Boolean(roomLit && distanceMarked && prototypeUnderstood && keepFollowUpUnderstood);
  }
  return false;
}

export function summarizeTrialResponses(responses: TrialResponse[]): {
  totalCompleted: number;
  matchedCount: number;
  unsureCount: number;
  byTier: Record<'Large' | 'Medium' | 'Smaller', { matched: number; total: number }>;
} {
  const byTier: Record<'Large' | 'Medium' | 'Smaller', { matched: number; total: number }> = {
    Large: { matched: 0, total: 0 },
    Medium: { matched: 0, total: 0 },
    Smaller: { matched: 0, total: 0 },
  };

  let matchedCount = 0;
  let unsureCount = 0;

  for (const r of responses) {
    byTier[r.sizeTier].total += 1;
    if (r.matched) {
      matchedCount += 1;
      byTier[r.sizeTier].matched += 1;
    }
    if (r.selectedDirection === 'unsure') {
      unsureCount += 1;
    }
  }

  return {
    totalCompleted: responses.length,
    matchedCount,
    unsureCount,
    byTier,
  };
}

export function generateParentNoteText(
  setup: SetupState,
  noteConfig: ParentNoteConfig,
  responses: TrialResponse[]
): string {
  const summary = summarizeTrialResponses(responses);
  const childDescriptor = setup.childLabel.trim() || 'My child';
  const detailLevel = noteConfig.noteDetailLevel ?? 50;
  const greeting =
    noteConfig.recipient === 'School Nurse'
      ? 'Dear School Nurse,'
      : noteConfig.recipient === 'Pediatrician'
        ? 'Dear Pediatric Care Team,'
        : 'Dear Eye Care Provider,';

  const obsLines =
    noteConfig.selectedObservations.length > 0
      ? noteConfig.selectedObservations.map((obs) => `- ${obs}`).join('\n')
      : '- No specific day-to-day visual behaviors checked yet.';

  const customLine = noteConfig.customObservationNote.trim()
    ? `\nAdditional parent observation:\n- ${noteConfig.customObservationNote.trim()}\n`
    : '';

  const activityLine =
    summary.totalCompleted > 0
      ? `At-home orientation activity (uncalibrated interaction preview at ${setup.distancePreset}):\n- Completed ${summary.totalCompleted} of ${TRIAL_SEQUENCE.length} directional E trials (${summary.matchedCount} matched directions, ${summary.unsureCount} marked unsure/hesitant).\n- Responses by display size: Large (${summary.byTier.Large.matched}/${summary.byTier.Large.total}), Medium (${summary.byTier.Medium.matched}/${summary.byTier.Medium.total}), Smaller (${summary.byTier.Smaller.matched}/${summary.byTier.Smaller.total}).`
      : `At-home orientation activity:\n- Prepared note prior to completing full 12-trial sequence (${setup.distancePreset} setup selected).`;

  const nextStepsLines =
    noteConfig.selectedNextSteps.length > 0
      ? noteConfig.selectedNextSteps.map((step) => `[ ] ${step}`).join('\n')
      : '[ ] Follow up with an eye care professional as recommended.';

  const questionsBlock =
    detailLevel > 65
      ? `\nQuestions we would like to ask at the visit:\n- Does ${childDescriptor} need glasses for distance, classroom board work, or reading?\n- Should we share any seating or visual accommodations with the teacher or school nurse?\n`
      : '';

  if (detailLevel < 35) {
    return `${greeting}

Sharing a quick summary for ${childDescriptor} (${setup.ageGroup}) ahead of our vision follow-up:
- Reason: ${setup.reason} (${noteConfig.onset})
- Glasses: ${setup.glassesStatus}

Observations noticed at home / school:
${obsLines}

Planned next steps:
${nextStepsLines}

Note: Prepared with Focal Family (student prototype — uncalibrated family preparation activity, not a clinical visual acuity test or medical diagnosis).`;
  }

  return `${greeting}

I am sharing these notes to help prepare for ${childDescriptor}'s vision follow-up (${setup.ageGroup}).

Reason for preparing this note:
- ${setup.reason}
- Approximate timing: ${noteConfig.onset}
- Glasses status: ${setup.glassesStatus}

What we have noticed at home / school:
${obsLines}${customLine}
${activityLine}${questionsBlock}

Planned next steps for our family:
${nextStepsLines}

Note: Prepared with Focal Family (student prototype). The at-home letter activity is an uncalibrated family preparation exercise and is not a clinical visual acuity test or medical diagnosis.`;
}
