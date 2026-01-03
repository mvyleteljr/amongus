"""Pydantic models for the LLM Among Us game."""

from typing import Any
from pydantic import BaseModel


class Example(BaseModel):
    input: str
    output: str


class TestCase(BaseModel):
    input: list[Any]
    expected: Any


class Task(BaseModel):
    id: str
    title: str
    functionName: str
    description: str
    examples: list[Example]
    test_cases: list[TestCase]


class Player(BaseModel):
    index: int
    name: str
    model: str
    isEliminated: bool = False


class Submission(BaseModel):
    playerIndex: int
    code: str
    timestamp: str


class Message(BaseModel):
    playerIndex: int
    content: str
    discussionRound: int


class Vote(BaseModel):
    voterIndex: int
    solutionVote: int
    suspectVote: int


class FailedTest(BaseModel):
    testIndex: int
    input: Any
    expected: Any
    actual: Any | None = None
    error: str | None = None


class TestResult(BaseModel):
    passed: bool
    totalTests: int
    passedTests: int
    failedTests: list[FailedTest]
    error: str | None = None


class Round(BaseModel):
    roundNumber: int
    task: Task
    submissions: list[Submission] = []
    discussion: list[Message] = []
    votes: list[Vote] = []
    chosenSubmission: int | None = None
    testResults: TestResult | None = None
    suspectVotes: dict[int, int] = {}


class GameState(BaseModel):
    gameId: str
    status: str  # 'lobby' | 'in_progress' | 'finished'
    currentRound: int
    currentPhase: str  # 'coding' | 'reveal' | 'discussion' | 'voting' | 'results'
    players: list[Player]
    imposterIndex: int
    rounds: list[Round] = []
    winner: str | None = None  # 'crewmates' | 'imposter' | None
    eliminatedPlayer: int | None = None
    failedTaskCount: int = 0
    discussionRoundNumber: int = 1


class CreateGameRequest(BaseModel):
    models: list[str] | None = None


class GameStateResponse(BaseModel):
    """Game state response that hides imposter until game is over."""

    gameId: str
    status: str
    currentRound: int
    currentPhase: str
    players: list[Player]
    imposterIndex: int | None  # Only revealed when game is finished
    rounds: list[Round]
    winner: str | None
    eliminatedPlayer: int | None
    failedTaskCount: int
    discussionRoundNumber: int
