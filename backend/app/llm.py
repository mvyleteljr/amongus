"""LLM orchestration for the game."""

import asyncio
import re
import os
import logging
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from google import genai

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

from .prompts import (
    CREWMATE_SYSTEM_PROMPT,
    IMPOSTER_SYSTEM_PROMPT,
    get_coding_prompt,
    get_reveal_prompt,
    get_discussion_prompt,
    get_voting_prompt,
)
from .models import GameState, Submission, Message, Vote


# Provider detection based on model name
def get_provider(model: str) -> str:
    """Determine the provider based on model name."""
    model_lower = model.lower()
    if "claude" in model_lower:
        return "anthropic"
    elif "gpt" in model_lower or "o1" in model_lower or "o3" in model_lower:
        return "openai"
    elif "gemini" in model_lower:
        return "google"
    elif "deepseek" in model_lower:
        return "deepseek"
    else:
        return "anthropic"  # Default fallback


class LLMOrchestrator:
    """Orchestrates LLM calls for all players."""

    def __init__(self):
        self.anthropic_client = AsyncAnthropic()
        self.openai_client = AsyncOpenAI()
        self.deepseek_client = AsyncOpenAI(
            api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
            base_url="https://api.deepseek.com"
        )
        self.google_client = genai.Client()
        self.conversation_histories: dict[str, list[list[dict]]] = {}

    def _get_system_prompt(self, player_index: int, is_imposter: bool) -> str:
        """Get the appropriate system prompt for a player."""
        if is_imposter:
            return IMPOSTER_SYSTEM_PROMPT.format(player_index=player_index + 1)
        return CREWMATE_SYSTEM_PROMPT.format(player_index=player_index + 1)

    def _init_game_histories(self, game_id: str):
        """Initialize conversation histories for a new game."""
        self.conversation_histories[game_id] = [[] for _ in range(4)]

    def _add_to_history(
        self, game_id: str, player_index: int, role: str, content: str
    ):
        """Add a message to a player's conversation history."""
        if game_id not in self.conversation_histories:
            self._init_game_histories(game_id)
        self.conversation_histories[game_id][player_index].append(
            {"role": role, "content": content}
        )

    async def _call_anthropic(
        self,
        model: str,
        system_prompt: str,
        messages: list[dict],
        max_tokens: int = 1024,
    ) -> str:
        """Make an Anthropic API call."""
        response = await self.anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages,
        )
        return response.content[0].text

    async def _call_openai(
        self,
        model: str,
        system_prompt: str,
        messages: list[dict],
        max_tokens: int = 1024,
        client: AsyncOpenAI | None = None,
    ) -> str:
        """Make an OpenAI-compatible API call (works for OpenAI and DeepSeek)."""
        if client is None:
            client = self.openai_client
        
        formatted_messages = [{"role": "system", "content": system_prompt}]
        formatted_messages.extend(messages)
        
        # GPT-5 is a reasoning model, needs more tokens for reasoning + output
        actual_max_tokens = max_tokens * 4 if "gpt-5" in model.lower() else max_tokens
        
        response = await client.chat.completions.create(
            model=model,
            max_completion_tokens=actual_max_tokens,
            messages=formatted_messages,
        )
        logger.debug(f"OpenAI response for {model}: {response}")
        content = response.choices[0].message.content
        if not content:
            logger.error(f"OpenAI returned empty content. Full response: {response}")
            raise ValueError(f"OpenAI API returned empty content for model {model}")
        return content

    async def _call_google(
        self,
        model: str,
        system_prompt: str,
        messages: list[dict],
        max_tokens: int = 1024,
    ) -> str:
        """Make a Google Gemini API call."""
        # Build contents from messages
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(genai.types.Content(
                role=role,
                parts=[genai.types.Part(text=msg["content"])]
            ))
        
        # Run sync client in thread pool
        def sync_call():
            # Gemini 2.5 is a reasoning model, needs more tokens for thinking + output
            actual_max_tokens = max_tokens * 8 if "2.5" in model or "3" in model else max_tokens
            
            response = self.google_client.models.generate_content(
                model=model,
                contents=contents,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=actual_max_tokens,
                ),
            )
            logger.debug(f"Google raw response for {model}: candidates={response.candidates}, text={getattr(response, 'text', None)}")
            
            # Check for blocked content or other issues
            if response.candidates:
                candidate = response.candidates[0]
                logger.debug(f"Google candidate: finish_reason={candidate.finish_reason}, content={candidate.content}")
                if candidate.content and candidate.content.parts:
                    text = candidate.content.parts[0].text
                    if text:
                        return text
            
            logger.error(f"Google returned no usable content. Full response: {response}")
            raise ValueError(f"Google API returned empty content for model {model}. Response: {response}")
        
        return await asyncio.to_thread(sync_call)

    async def _call_llm(
        self,
        model: str,
        system_prompt: str,
        messages: list[dict],
        max_tokens: int = 1024,
    ) -> str:
        """Make an LLM API call to the appropriate provider."""
        provider = get_provider(model)
        
        if provider == "anthropic":
            return await self._call_anthropic(model, system_prompt, messages, max_tokens)
        elif provider == "openai":
            return await self._call_openai(model, system_prompt, messages, max_tokens)
        elif provider == "deepseek":
            return await self._call_openai(model, system_prompt, messages, max_tokens, self.deepseek_client)
        elif provider == "google":
            return await self._call_google(model, system_prompt, messages, max_tokens)
        else:
            # Fallback to Anthropic
            return await self._call_anthropic(model, system_prompt, messages, max_tokens)

    def _extract_code(self, response: str) -> str:
        """Extract code from LLM response, handling markdown formatting."""
        # Try to extract from markdown code blocks
        code_block_match = re.search(r"```(?:python)?\s*\n?(.*?)```", response, re.DOTALL)
        if code_block_match:
            return code_block_match.group(1).strip()
        # Otherwise return the whole response stripped
        return response.strip()

    def _parse_vote(self, response: str, self_index: int, active_players: list[int]) -> tuple[int, int]:
        """Parse voting response to extract solution and suspect votes."""
        solution_match = re.search(r"SOLUTION:\s*(\d)", response)
        suspect_match = re.search(r"SUSPECT:\s*(\d)", response)

        solution_vote = int(solution_match.group(1)) - 1 if solution_match else active_players[0]
        suspect_vote = int(suspect_match.group(1)) - 1 if suspect_match else active_players[0]

        # Clamp values to valid range and ensure they're active players
        if solution_vote not in active_players:
            solution_vote = active_players[0]
        if suspect_vote not in active_players:
            suspect_vote = active_players[0]

        # Prevent voting for self as suspect
        if suspect_vote == self_index:
            other_players = [p for p in active_players if p != self_index]
            suspect_vote = other_players[0] if other_players else active_players[0]

        return solution_vote, suspect_vote

    async def get_code_submissions(
        self, game_state: GameState, task: dict, eliminated_player: int | None = None, last_task_passed: bool | None = None
    ) -> list[Submission]:
        """Get code submissions from all active players in parallel."""
        from datetime import datetime

        game_id = game_state.gameId
        if game_id not in self.conversation_histories:
            self._init_game_histories(game_id)

        coding_prompt = get_coding_prompt(game_state.currentRound, task, eliminated_player, last_task_passed)

        async def get_submission(player_index: int) -> Submission | None:
            player = game_state.players[player_index]
            if player.isEliminated:
                return None

            is_imposter = player_index == game_state.imposterIndex
            system_prompt = self._get_system_prompt(player_index, is_imposter)

            # Add coding prompt to history
            self._add_to_history(game_id, player_index, "user", coding_prompt)

            response = await self._call_llm(
                model=player.model,
                system_prompt=system_prompt,
                messages=self.conversation_histories[game_id][player_index],
            )

            # Add response to history
            self._add_to_history(game_id, player_index, "assistant", response)

            code = self._extract_code(response)
            return Submission(
                playerIndex=player_index,
                code=code,
                timestamp=datetime.now().isoformat(),
            )

        tasks = [get_submission(i) for i in range(4)]
        results = await asyncio.gather(*tasks)
        return [s for s in results if s is not None]

    async def show_code_reveal(
        self, game_state: GameState, task: dict, submissions: list[Submission]
    ):
        """Show all code submissions to all players."""
        game_id = game_state.gameId
        reveal_prompt = get_reveal_prompt(
            task, [s.model_dump() for s in submissions]
        )

        # Add reveal prompt to all active players' histories
        for i, player in enumerate(game_state.players):
            if not player.isEliminated:
                self._add_to_history(game_id, i, "user", reveal_prompt)

    async def get_discussion_messages(
        self,
        game_state: GameState,
        task: dict,
        discussion_round: int,
        previous_messages: list[Message],
    ) -> list[Message]:
        """Get discussion messages from all active players in parallel."""
        game_id = game_state.gameId

        async def get_message(player_index: int) -> Message | None:
            player = game_state.players[player_index]
            if player.isEliminated:
                return None

            is_imposter = player_index == game_state.imposterIndex
            system_prompt = self._get_system_prompt(player_index, is_imposter)

            discussion_prompt = get_discussion_prompt(
                discussion_round, task, [m.model_dump() for m in previous_messages]
            )

            self._add_to_history(game_id, player_index, "user", discussion_prompt)

            response = await self._call_llm(
                model=player.model,
                system_prompt=system_prompt,
                messages=self.conversation_histories[game_id][player_index],
                max_tokens=300,
            )

            self._add_to_history(game_id, player_index, "assistant", response)

            # Truncate if too long
            content = response.strip()[:500]
            return Message(
                playerIndex=player_index,
                content=content,
                discussionRound=discussion_round,
            )

        tasks = [get_message(i) for i in range(4)]
        results = await asyncio.gather(*tasks)
        return [m for m in results if m is not None]

    async def get_votes(
        self, game_state: GameState, task: dict, discussion: list[Message]
    ) -> list[Vote]:
        """Get votes from all active players in parallel."""
        game_id = game_state.gameId
        active_players = [p.index for p in game_state.players if not p.isEliminated]

        async def get_vote(player_index: int) -> Vote | None:
            player = game_state.players[player_index]
            if player.isEliminated:
                return None

            is_imposter = player_index == game_state.imposterIndex
            system_prompt = self._get_system_prompt(player_index, is_imposter)

            voting_prompt = get_voting_prompt(
                task, [m.model_dump() for m in discussion], player_index
            )

            self._add_to_history(game_id, player_index, "user", voting_prompt)

            response = await self._call_llm(
                model=player.model,
                system_prompt=system_prompt,
                messages=self.conversation_histories[game_id][player_index],
                max_tokens=200,
            )

            self._add_to_history(game_id, player_index, "assistant", response)

            solution_vote, suspect_vote = self._parse_vote(response, player_index, active_players)
            return Vote(
                voterIndex=player_index,
                solutionVote=solution_vote,
                suspectVote=suspect_vote,
            )

        tasks = [get_vote(i) for i in range(4)]
        results = await asyncio.gather(*tasks)
        return [v for v in results if v is not None]

    def cleanup_game(self, game_id: str):
        """Clean up conversation histories for a finished game."""
        if game_id in self.conversation_histories:
            del self.conversation_histories[game_id]
