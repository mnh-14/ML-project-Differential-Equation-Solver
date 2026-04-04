from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SYSTEM_PROMPT = (
    "You are a mathematical routing agent. Analyze the provided LaTeX equation. "
    "Currently, you only support:['Separable', 'Linear First-Order', 'Exact']. "
    "If the equation belongs to these, output the required steps. If it belongs to an unsupported family, "
    "set 'equation_family' to 'Unsupported' and leave 'steps' empty."
)

SYSTEM_PROMPT = """
You are a highly constrained mathematical routing agent. Your task is to analyze LaTeX ordinary differential equations (ODEs), categorize them, and generate a strict JSON execution plan.

SUPPORTED FAMILIES: ['Separable', 'Linear First-Order', 'Exact']
If the equation does NOT belong to one of these exact families, you must set "equation_family" to "Unsupported" and "steps" to[].

ALLOWED ACTIONS AND PARAMETER SCHEMA:
You are STRICTLY FORBIDDEN from using any action names other than:
1. "identify": params: {"expression": "latex_expression_or_result_name", "result_as": "unique_result_name"}
2. "integrate": params: {"expression": "latex_expression_or_result_name", "wrt": "variable", "result_as": "unique_result_name"}
3. "differentiate": params: {"expression": "latex_expression_or_result_name", "wrt": "variable", "result_as": "unique_result_name"}
4. "IF Calc": params: {"expression": "result_name_of_P(x)", "wrt": "variable", "result_as": "unique_result_name"}
5. "multiply": params: {"operand1": "latex_expression_or_result_name", "operand2": "latex_expression_or_result_name_or_variable_name", "operand_type": ["expression_name", "expression_name_or_variable_name"], "result_as": "unique_result_name"}
6. "solve": params: {"equation": "latex_equation/name of equation", "wrt": "variable", "result_as": "unique_result_name"}
7. "add": params: {"operand1": "latex_expression_or_result_name", "operand2": "latex_expression_or_result_name_or_variable_name", "operand_type": ["expression_name", "expression_name_or_variable_name"], "result_as": "unique_result_name"}

RULES:
1. Output ONLY valid JSON.
2. Do not invent, capitalize, or modify the allowed action names.
3. All mathematical expressions and variable references inside the "params" keys must follow these rules: Raw mathematical terms must be in pure LaTeX format (e.g., x^2, \frac{1}{x}, \sin(x)). If you are referring to a previously defined result, use the exact name you assigned to it in the "result_as" field. Do NOT use Python programming syntax (e.g., no ** for exponents).
4. Do not add outside conversational text.
"""


SUPPORTED_FAMILIES = {
    "separable": "Separable ODE",
    "separable ode": "Separable ODE",
    "first-order linear": "Linear First-Order ODE",
    "linear first-order": "Linear First-Order ODE",
    "linear first-order ode": "Linear First-Order ODE",
    "bernoulli": "Bernoulli ODE",
    "bernoulli ode": "Bernoulli ODE",
}


def normalize_action_name(value: str) -> str:
    """Convert step labels into the lowercase snake_case format used by the target dataset."""
    cleaned = []
    previous_was_separator = False

    for character in value.strip():
        if character.isalnum():
            cleaned.append(character.lower())
            previous_was_separator = False
        else:
            if not previous_was_separator:
                cleaned.append("_")
                previous_was_separator = True

    result = "".join(cleaned).strip("_")
    while "__" in result:
        result = result.replace("__", "_")
    return result


def map_equation_family(raw_family: Any) -> str:
    if raw_family is None:
        return "Unsupported"

    family_text = str(raw_family).strip().lower()
    return SUPPORTED_FAMILIES.get(family_text, "Unsupported")


def load_json_array(file_path: Path) -> list[dict[str, Any]]:
    with file_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON array in {file_path.name}")

    records: list[dict[str, Any]] = []
    for item in data:
        if isinstance(item, dict):
            records.append(item)
    return records


def build_assistant_payload(record: dict[str, Any]) -> str:
    family = record.get("equation_family", "") or record.get("family", "")
    raw_steps = record.get("steps") or []

    steps = []
    for step in raw_steps:
        if not isinstance(step, dict):
            continue
        steps.append(
            {
                "action": step.get("action", ""),
                "params": step.get("params", {}),
            }
        )

    assistant_payload = {
        "reasoning": record.get("reasoning", ""),
        "equation_family": family,
        "steps": steps,
    }
    return f"```json\n{json.dumps(assistant_payload, indent=2, ensure_ascii=False)}\n```"


def build_messages(record: dict[str, Any]) -> dict[str, Any]:
    equation = record.get("equation", "")
    return {
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": f"Solve the equation: {equation}",
            },
            {
                "role": "assistant",
                "content": build_assistant_payload(record),
            },
        ]
    }


def merge_json_files(input_dir: Path, output_path: Path) -> int:
    json_files = sorted(
        file_path
        for file_path in input_dir.glob("*.json")
        if file_path.is_file() and file_path.resolve() != output_path.resolve()
    )

    merged_records: list[dict[str, Any]] = []
    for file_path in json_files:
        merged_records.extend(load_json_array(file_path))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in merged_records:
            handle.write(json.dumps(build_messages(record), ensure_ascii=False))
            handle.write("\n")

    return len(merged_records)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge final dataset JSON files into a JSONL chat dataset")
    parser.add_argument(
        "--input-dir",
        default="final_datasets",
        help="Folder containing the source JSON files",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSONL file path. Defaults to <input-dir>/merged_data.jsonl",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_path = Path(args.output) if args.output else input_dir / "merged_data.jsonl"

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

    count = merge_json_files(input_dir, output_path)
    print(f"Successfully merged {count} records into {output_path}")


if __name__ == "__main__":
    main()
