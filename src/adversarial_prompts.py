"""
Adversarial prompt management and loading utilities.
"""

import json
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass


@dataclass
class AdversarialPrompt:
    """Represents a single adversarial prompt"""
    id: str
    category: str
    difficulty: str
    prompt: str
    expected_behavior: str
    description: str
    tags: List[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "category": self.category,
            "difficulty": self.difficulty,
            "prompt": self.prompt,
            "expected_behavior": self.expected_behavior,
            "description": self.description,
            "tags": self.tags
        }


class PromptLibrary:
    """Manages loading and filtering adversarial prompts"""

    def __init__(self, prompts_file: Optional[str] = None):
        """
        Initialize prompt library

        Args:
            prompts_file: Path to JSON file containing prompts
        """
        if prompts_file is None:
            # Default to the bundled prompts
            project_root = Path(__file__).parent.parent
            prompts_file = project_root / "data" / "prompts" / "jailbreaks.json"

        self.prompts_file = Path(prompts_file)
        self.prompts: List[AdversarialPrompt] = []
        self._load_prompts()

    def _load_prompts(self):
        """Load prompts from JSON file"""
        try:
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for prompt_data in data.get("prompts", []):
                prompt = AdversarialPrompt(
                    id=prompt_data["id"],
                    category=prompt_data["category"],
                    difficulty=prompt_data["difficulty"],
                    prompt=prompt_data["prompt"],
                    expected_behavior=prompt_data["expected_behavior"],
                    description=prompt_data["description"],
                    tags=prompt_data["tags"]
                )
                self.prompts.append(prompt)

        except FileNotFoundError:
            raise FileNotFoundError(f"Prompts file not found: {self.prompts_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in prompts file: {e}")

    def get_all(self) -> List[AdversarialPrompt]:
        """Get all prompts"""
        return self.prompts

    def get_by_category(self, category: str) -> List[AdversarialPrompt]:
        """
        Get prompts by category

        Args:
            category: Category name (e.g., 'jailbreak', 'bias', 'harmful_content')

        Returns:
            List of prompts in that category
        """
        return [p for p in self.prompts if p.category == category]

    def get_by_difficulty(self, difficulty: str) -> List[AdversarialPrompt]:
        """
        Get prompts by difficulty

        Args:
            difficulty: Difficulty level ('easy', 'medium', 'hard')

        Returns:
            List of prompts with that difficulty
        """
        return [p for p in self.prompts if p.difficulty == difficulty]

    def get_by_tag(self, tag: str) -> List[AdversarialPrompt]:
        """
        Get prompts by tag

        Args:
            tag: Tag to filter by

        Returns:
            List of prompts with that tag
        """
        return [p for p in self.prompts if tag in p.tags]

    def filter(
        self,
        categories: Optional[List[str]] = None,
        difficulties: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> List[AdversarialPrompt]:
        """
        Filter prompts by multiple criteria

        Args:
            categories: List of categories to include
            difficulties: List of difficulties to include
            tags: List of tags to include

        Returns:
            Filtered list of prompts
        """
        filtered = self.prompts

        if categories:
            filtered = [p for p in filtered if p.category in categories]

        if difficulties:
            filtered = [p for p in filtered if p.difficulty in difficulties]

        if tags:
            filtered = [p for p in filtered if any(tag in p.tags for tag in tags)]

        return filtered

    def get_categories(self) -> List[str]:
        """Get list of all unique categories"""
        return sorted(list(set(p.category for p in self.prompts)))

    def get_difficulties(self) -> List[str]:
        """Get list of all unique difficulties"""
        return sorted(list(set(p.difficulty for p in self.prompts)))

    def get_tags(self) -> List[str]:
        """Get list of all unique tags"""
        all_tags = []
        for p in self.prompts:
            all_tags.extend(p.tags)
        return sorted(list(set(all_tags)))

    def __len__(self) -> int:
        """Return number of prompts"""
        return len(self.prompts)

    def __getitem__(self, index: int) -> AdversarialPrompt:
        """Get prompt by index"""
        return self.prompts[index]
