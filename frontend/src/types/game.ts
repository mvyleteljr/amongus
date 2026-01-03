export interface Example {
  input: string;
  output: string;
}

export interface TestCase {
  input: unknown[];
  expected: unknown;
}

export interface Task {
  id: string;
  title: string;
  functionName: string;
  description: string;
  examples: Example[];
  test_cases: TestCase[];
}

export interface Player {
  index: number;
  name: string;
  model: string;
  isEliminated: boolean;
}

export interface Submission {
  playerIndex: number;
  code: string;
  timestamp: string;
}

export interface Message {
  playerIndex: number;
  content: string;
  discussionRound: number;
}

export interface Vote {
  voterIndex: number;
  solutionVote: number;
  suspectVote: number;
}

export interface FailedTest {
  testIndex: number;
  input: unknown;
  expected: unknown;
  actual?: unknown;
  error?: string;
}

export interface TestResult {
  passed: boolean;
  totalTests: number;
  passedTests: number;
  failedTests: FailedTest[];
  error?: string;
}

export interface Round {
  roundNumber: number;
  task: Task;
  submissions: Submission[];
  discussion: Message[];
  votes: Vote[];
  chosenSubmission: number | null;
  testResults: TestResult | null;
  suspectVotes: Record<number, number>;
}

export type GamePhase = 'lobby' | 'coding' | 'reveal' | 'discussion' | 'voting' | 'results' | 'finished';
export type GameStatus = 'lobby' | 'in_progress' | 'finished';
export type Winner = 'crewmates' | 'imposter' | null;

export interface GameState {
  gameId: string;
  status: GameStatus;
  currentRound: number;
  currentPhase: GamePhase;
  players: Player[];
  imposterIndex: number | null;
  rounds: Round[];
  winner: Winner;
  eliminatedPlayer: number | null;
  failedTaskCount: number;
  discussionRoundNumber: number;
}

export interface WebSocketMessage {
  type: string;
  data?: GameState;
}
