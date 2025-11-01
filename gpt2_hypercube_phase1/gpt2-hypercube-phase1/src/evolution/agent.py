"""
Agent wrapper holding a genome and a generator callable.

Generator callable signature:
    generator(genome: Genome, prompt: str, temperature: float) -> str
For testing a mock generator is provided.
"""
from typing import Callable, Optional
from .genome import Genome


class Agent:
    def __init__(self, genome: Genome, generator: Optional[Callable] = None):
        self.genome = genome
        self.generator = generator

    def generate(self, prompt: str, temperature: float = 1.0) -> str:
        if self.generator is None:
            # deterministic fallback: combine prompt + genome id summary
            return f"{prompt} ||gen:{self.genome.id[:6]}|t{temperature:.2f}"
        return self.generator(self.genome, prompt, temperature)
