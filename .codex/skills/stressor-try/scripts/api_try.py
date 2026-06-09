#!/usr/bin/env python3
import argparse
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple


TEXT_STATEMENT_NAMES = [
    "statement.md",
    "problem.md",
    "README.md",
    "statement.txt",
    "samples.md",
    "examples.md",
    "notes.md",
]

SAMPLE_SUFFIXES = [".in", ".out", ".input", ".output"]


def fail(msg: str, code: int = 1) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(code)


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        fail(
            f"Missing required environment variable: {name}.\n"
            f"Make sure .codex/skills/stressor-try/scripts/api_init.sh "
            f"was sourced before running api_try.py."
        )
    return value


def collect_model_ids(models_response) -> List[str]:
    data = getattr(models_response, "data", None)
    if data is None and isinstance(models_response, dict):
        data = models_response.get("data", [])
    if data is None:
        data = []

    ids = []
    for item in data:
        mid = getattr(item, "id", None)
        if mid is None and isinstance(item, dict):
            mid = item.get("id")
        if mid:
            ids.append(str(mid))
    return ids


def is_statement_dir(path: Path) -> bool:
    return path.is_dir() and path.name == "statement"


def resolve_statement_dir(path: Path) -> Path:
    path = path.resolve()

    if path.is_file():
        if path.parent.name == "statement":
            return path.parent
        return path.parent

    if not path.is_dir():
        fail(f"Statement path does not exist: {path}")

    if path.name == "statement":
        return path

    candidate = path / "statement"
    if candidate.is_dir():
        return candidate

    return path


def resolve_primary_statement_file(statement_dir: Path, original: Path) -> Optional[Path]:
    original = original.resolve()

    if original.is_file():
        return original

    for name in TEXT_STATEMENT_NAMES:
        p = statement_dir / name
        if p.is_file():
            return p

    pdf = statement_dir / "statement.pdf"
    if pdf.is_file():
        return pdf

    return None


def ordered_statement_files(statement_dir: Path, primary: Optional[Path]) -> List[Path]:
    files: List[Path] = []

    if (
        primary is not None
        and primary.exists()
        and primary.is_file()
        and primary.suffix.lower() != ".pdf"
    ):
        files.append(primary.resolve())

    if statement_dir.is_dir():
        for name in TEXT_STATEMENT_NAMES:
            p = (statement_dir / name).resolve()
            if p.is_file() and p not in files:
                files.append(p)

        sample_files = []
        for p in statement_dir.iterdir():
            if p.is_file() and p.suffix.lower() in SAMPLE_SUFFIXES:
                sample_files.append(p.resolve())

        for p in sorted(sample_files, key=lambda x: x.name):
            if p not in files:
                files.append(p)

    return files


def read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def read_statement_bundle(path_str: str) -> Tuple[str, Path, Path, List[Path]]:
    original = Path(path_str).resolve()
    if not original.exists():
        fail(f"Statement path not found: {original}")

    statement_dir = resolve_statement_dir(original)
    primary = resolve_primary_statement_file(statement_dir, original)

    if primary is None:
        searched = ", ".join(str(statement_dir / name) for name in TEXT_STATEMENT_NAMES)
        fail(f"No statement file found. Searched: {searched}")

    if primary.suffix.lower() == ".pdf":
        fail("Only PDF statement found. Provide statement.md or another text statement for reliable API solving.")

    files_read = ordered_statement_files(statement_dir, primary)

    if not files_read:
        fail(f"No readable statement files found under: {statement_dir}")

    parts: List[str] = []
    for p in files_read:
        try:
            content = read_text_file(p)
        except Exception as e:
            fail(f"Failed to read statement file {p}: {e}")

        rel_name = p.name
        parts.append(f"### Official statement file: {rel_name}\n\n{content}\n")

    statement_text = "\n".join(parts)
    return statement_text, statement_dir, primary, files_read


def extract_xml_block(text: str, tag: str) -> Optional[str]:
    pattern = re.compile(rf"<{tag}>\s*(.*?)\s*</{tag}>", re.DOTALL | re.IGNORECASE)
    m = pattern.search(text)
    if not m:
        return None
    return m.group(1).strip()


def strip_code_fence(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z0-9_+\-]*\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
    return s.strip()


def extract_cpp(text: str) -> str:
    xml = extract_xml_block(text, "cpp")
    if xml:
        return strip_code_fence(xml) + "\n"

    fence_re = re.compile(r"```([a-zA-Z0-9_+\-]*)\s*(.*?)```", re.DOTALL)
    candidates = []
    for lang, code in fence_re.findall(text):
        lang_l = lang.lower()
        if lang_l in {"cpp", "c++", "cc", "cxx"}:
            candidates.append(code.strip())

    if not candidates:
        for lang, code in fence_re.findall(text):
            candidates.append(code.strip())

    if not candidates:
        fail("Could not extract C++ code. Expected <cpp>...</cpp> or a C++ fenced code block.")

    code = max(candidates, key=len).strip()
    if "#include" not in code and "int main" not in code:
        fail("Extracted code does not look like complete C++ source.")

    return code + "\n"


def extract_notes(text: str, cpp_text: str) -> str:
    xml = extract_xml_block(text, "notes")
    if xml:
        return xml.strip() + "\n"

    cleaned = re.sub(r"<cpp>\s*.*?\s*</cpp>", "", text, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"```([a-zA-Z0-9_+\-]*)\s*.*?```", "", cleaned, flags=re.DOTALL)
    cleaned = cleaned.strip()

    if cleaned:
        return cleaned + "\n"

    return "Model did not provide detailed notes. Only C++ code was extracted.\n"


def atomic_write(path: Path, content: str) -> None:
    path = path.resolve()
    if path.exists():
        fail(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass


def main() -> None:
    parser = argparse.ArgumentParser(
        description="API hard-isolated stressor-try generator."
    )
    parser.add_argument(
        "--statement",
        required=True,
        help="Path to statement file, statement directory, or problem root.",
    )
    parser.add_argument(
        "--output-cpp", required=True, help="Output C++ file path."
    )
    parser.add_argument(
        "--output-notes", required=True, help="Output notes markdown path."
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Four-digit version string, e.g. 0001.",
    )
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=int(os.environ.get("STRESSOR_TRY_MAX_TOKENS", "16000")),
    )
    args = parser.parse_args()

    output_cpp = Path(args.output_cpp).resolve()
    output_notes = Path(args.output_notes).resolve()

    if output_cpp.exists():
        fail(f"Output C++ already exists: {output_cpp}")
    if output_notes.exists():
        fail(f"Output notes already exists: {output_notes}")

    api_base_url = require_env("API_BASE_URL")
    api_auth_token = require_env("API_AUTH_TOKEN")
    model = require_env("STRESSOR_TRY_MODEL")

    try:
        from openai import OpenAI
    except ImportError:
        fail(
            "Python package 'openai' is not installed. "
            "Install with: python3 -m pip install openai"
        )

    statement_text, statement_dir, primary_statement, files_read = read_statement_bundle(
        args.statement
    )

    client = OpenAI(
        base_url=api_base_url,
        api_key=api_auth_token,
    )

    try:
        models_response = client.models.list()
    except Exception as e:
        fail(f"Failed to list models from API: {e}")

    model_ids = collect_model_ids(models_response)

    if model not in model_ids:
        printable = (
            "\n".join(f"- {mid}" for mid in model_ids)
            if model_ids
            else "(no models returned)"
        )
        fail(
            f"STRESSOR_TRY_MODEL not found in client.models.list(): {model}\n"
            f"Available models:\n{printable}"
        )

    system_prompt = """You are solving an ICPC/CCPC programming contest problem in statement-only API hard isolation.

You can see only the official statement bundle provided in the user message.

You cannot see tests, brute force code, checker code, validator code, generators, reports, previous attempts, or counterexamples.

Do not infer hidden rules from samples only.

Write a complete C++17 solution.

Return exactly two XML-style blocks:

<cpp>
complete C++17 code
</cpp>

<notes>
public solution explanation
</notes>

The C++ code must be complete and compilable with C++17.

Do not include markdown fences inside <cpp>.

Do not include hidden chain-of-thought.

The notes should contain a concise public reasoning summary, not raw private reasoning.
"""

    user_prompt = f"""Target version: {args.version}

Official statement bundle:

{statement_text}

The notes block must contain these sections:

- Problem Understanding
- Key Observations
- Algorithm Design
- Correctness Argument
- Complexity
- Edge Cases
- Overflow / Precision Notes
- Assumptions
- Remaining Concerns
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )
    except Exception as e:
        fail(f"API chat completion failed: {e}")

    try:
        content = response.choices[0].message.content
    except Exception as e:
        fail(f"Could not read response.choices[0].message.content: {e}")

    if not content or not str(content).strip():
        fail("API returned empty content.")

    cpp = extract_cpp(content)
    notes_body = extract_notes(content, cpp)

    files_list = "\n".join(f"- `{p}`" for p in files_read)
    notes = f"""# Optimized Solution Notes - Version {args.version}

- CPP file: `{output_cpp}`
- Notes file: `{output_notes}`
- Isolation: API statement-only hard isolation
- Model: `{model}`
- Statement directory: `{statement_dir}`
- Primary statement: `{primary_statement}`

## Statement Files Included

{files_list}

---

{notes_body}
"""

    atomic_write(output_cpp, cpp)
    atomic_write(output_notes, notes)

    print(f"Created: {output_cpp}")
    print(f"Created: {output_notes}")
    print(f"Model: {model}")
    print(f"API base: {api_base_url}")
    print("API token: <hidden>")


if __name__ == "__main__":
    main()
