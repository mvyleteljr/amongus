"""Game state management and logic."""

import random
import uuid
from collections import Counter

from .models import (
    GameState,
    GameStateResponse,
    Player,
    Round,
    Task,
    Submission,
    Message,
    Vote,
    TestResult,
)
from .tasks import TASKS
from .sandbox import run_tests
from .llm import LLMOrchestrator

DEFAULT_MODELS = [
    "claude-sonnet-4-5-20250929",
    "gpt-5",
    "gemini-2.5-pro",
    "claude-sonnet-4-5-20250929",
]


class GameManager:
    """Manages game state and orchestrates game flow."""

    def __init__(self):
        self.games: dict[str, GameState] = {}
        self.llm = LLMOrchestrator()

    def create_game(self, models: list[str] | None = None) -> GameState:
        """Create a new game with the specified models."""
        if models is None:
            models = DEFAULT_MODELS

        if len(models) != 4:
            raise ValueError("Exactly 4 models are required")

        game_id = str(uuid.uuid4())[:8]
        imposter_index = random.randint(0, 3)

        players = [
            Player(index=i, name=f"Player {i + 1}", model=models[i])
            for i in range(4)
        ]

        game_state = GameState(
            gameId=game_id,
            status="lobby",
            currentRound=0,
            currentPhase="lobby",
            players=players,
            imposterIndex=imposter_index,
            rounds=[],
            winner=None,
            eliminatedPlayer=None,
            failedTaskCount=0,
            discussionRoundNumber=1,
        )

        self.games[game_id] = game_state
        return game_state

    def get_game(self, game_id: str) -> GameState | None:
        """Get game state by ID."""
        return self.games.get(game_id)

    def get_game_response(self, game_id: str) -> GameStateResponse | None:
        """Get game state response, hiding imposter if game not finished."""
        game = self.games.get(game_id)
        if not game:
            return None

        return GameStateResponse(
            gameId=game.gameId,
            status=game.status,
            currentRound=game.currentRound,
            currentPhase=game.currentPhase,
            players=game.players,
            imposterIndex=game.imposterIndex if game.status == "finished" else None,
            rounds=game.rounds,
            winner=game.winner,
            eliminatedPlayer=game.eliminatedPlayer,
            failedTaskCount=game.failedTaskCount,
            discussionRoundNumber=game.discussionRoundNumber,
        )

    def start_game(self, game_id: str) -> GameState | None:
        """Start the game and begin round 1."""
        game = self.games.get(game_id)
        if not game or game.status != "lobby":
            return None

        game.status = "in_progress"
        game.currentRound = 1
        game.currentPhase = "coding"

        # Create first round
        task_dict = TASKS[0]
        task = Task(
            id=task_dict["id"],
            title=task_dict["title"],
            functionName=task_dict["functionName"],
            description=task_dict["description"],
            examples=[{"input": e["input"], "output": e["output"]} for e in task_dict["examples"]],
            test_cases=[{"input": t["input"], "expected": t["expected"]} for t in task_dict["test_cases"]],
        )

        game.rounds.append(
            Round(roundNumber=1, task=task)
        )

        return game

    def _get_current_round(self, game: GameState) -> Round | None:
        """Get the current round object."""
        if not game.rounds or game.currentRound < 1:
            return None
        return game.rounds[game.currentRound - 1]

    def _get_current_task_dict(self, game: GameState) -> dict | None:
        """Get the current task dictionary."""
        if game.currentRound < 1 or game.currentRound > len(TASKS):
            return None
        return TASKS[game.currentRound - 1]

    async def advance_phase(self, game_id: str) -> GameState | None:
        """Advance to the next phase of the game."""
        game = self.games.get(game_id)
        if not game or game.status != "in_progress":
            return None

        current_round = self._get_current_round(game)
        task_dict = self._get_current_task_dict(game)

        if not current_round or not task_dict:
            return None

        if game.currentPhase == "coding":
            # Get context from previous round if applicable
            eliminated_player = None
            last_task_passed = None
            if game.currentRound > 1:
                prev_round = game.rounds[game.currentRound - 2]
                if prev_round.testResults:
                    last_task_passed = prev_round.testResults.passed
                # Check if someone was eliminated in the previous round
                # (eliminatedPlayer is set when elimination happens)
                for player_idx, vote_count in prev_round.suspectVotes.items():
                    active_count = sum(1 for p in game.players if not p.isEliminated or p.index == player_idx)
                    if vote_count >= active_count // 2 + 1:
                        eliminated_player = player_idx
                        break
            
            # Get code submissions from all players
            submissions = await self.llm.get_code_submissions(game, task_dict, eliminated_player, last_task_passed)
            current_round.submissions = submissions
            game.currentPhase = "reveal"

        elif game.currentPhase == "reveal":
            # Show code to all players
            await self.llm.show_code_reveal(
                game, task_dict, current_round.submissions
            )
            game.currentPhase = "discussion"
            game.discussionRoundNumber = 1

        elif game.currentPhase == "discussion":
            # Get discussion messages
            messages = await self.llm.get_discussion_messages(
                game,
                task_dict,
                game.discussionRoundNumber,
                current_round.discussion,
            )
            current_round.discussion.extend(messages)

            if game.discussionRoundNumber >= 3:
                game.currentPhase = "voting"
            else:
                game.discussionRoundNumber += 1

        elif game.currentPhase == "voting":
            # Get votes from all players
            votes = await self.llm.get_votes(
                game, task_dict, current_round.discussion
            )
            current_round.votes = votes

            # Tally solution votes
            solution_votes = Counter(v.solutionVote for v in votes)
            chosen_solution = solution_votes.most_common(1)[0][0]
            current_round.chosenSubmission = chosen_solution

            # Tally suspect votes
            suspect_votes = Counter(v.suspectVote for v in votes)
            current_round.suspectVotes = dict(suspect_votes)

            game.currentPhase = "results"

        elif game.currentPhase == "results":
            # Run tests on chosen solution
            chosen_idx = current_round.chosenSubmission
            if chosen_idx is not None:
                chosen_submission = next(
                    (s for s in current_round.submissions if s.playerIndex == chosen_idx),
                    None,
                )
                if chosen_submission:
                    test_result = run_tests(
                        chosen_submission.code,
                        task_dict["functionName"],
                        task_dict["test_cases"],
                    )
                    current_round.testResults = test_result

                    if not test_result.passed:
                        game.failedTaskCount += 1

            # Check for elimination (majority suspect vote)
            suspect_votes = current_round.suspectVotes
            active_players = sum(1 for p in game.players if not p.isEliminated)
            majority = active_players // 2 + 1

            for player_idx, vote_count in suspect_votes.items():
                if vote_count >= majority:
                    game.players[player_idx].isEliminated = True
                    game.eliminatedPlayer = player_idx
                    break

            # Check win conditions
            if game.eliminatedPlayer == game.imposterIndex:
                game.winner = "crewmates"
                game.status = "finished"
                game.currentPhase = "finished"
            elif game.failedTaskCount >= 3:
                game.winner = "imposter"
                game.status = "finished"
                game.currentPhase = "finished"
            elif game.currentRound >= 5:
                game.winner = "imposter"
                game.status = "finished"
                game.currentPhase = "finished"
            else:
                # Start next round
                game.currentRound += 1
                game.currentPhase = "coding"
                game.discussionRoundNumber = 1

                # Create next round
                next_task_dict = TASKS[game.currentRound - 1]
                next_task = Task(
                    id=next_task_dict["id"],
                    title=next_task_dict["title"],
                    functionName=next_task_dict["functionName"],
                    description=next_task_dict["description"],
                    examples=[{"input": e["input"], "output": e["output"]} for e in next_task_dict["examples"]],
                    test_cases=[{"input": t["input"], "expected": t["expected"]} for t in next_task_dict["test_cases"]],
                )
                game.rounds.append(Round(roundNumber=game.currentRound, task=next_task))

        return game

    def delete_game(self, game_id: str):
        """Delete a game and clean up resources."""
        if game_id in self.games:
            self.llm.cleanup_game(game_id)
            del self.games[game_id]


# Global game manager instance
game_manager = GameManager()
