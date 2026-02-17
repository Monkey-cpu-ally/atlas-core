"""
atlas_core/core/demo/demo_run.py

CLI demo for testing persona responses.
"""

from ..memory.memory_store import SimpleMemoryStore
from ..personas.registry import PersonaRegistry
from ..brain.persona_kernel import PersonaKernel
from ..brain.response_pipeline import ResponsePipeline


def main():
    mem = SimpleMemoryStore()
    reg = PersonaRegistry()
    kernel = PersonaKernel(registry=reg)
    pipe = ResponsePipeline(kernel=kernel, memory=mem)

    while True:
        txt = input("You> ").strip()
        if txt.lower() in {"quit", "exit"}:
            break
        out = pipe.run(user_text=txt, persona="ajani", style="blueprint", mode="teach", use_tools=False)
        print("\nAjani>", out["text"], "\n")


if __name__ == "__main__":
    main()
