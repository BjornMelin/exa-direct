"""Command-line interface for the exa-direct tool.

This module provides a CLI for interacting with the Exa API,
supporting search, contents retrieval, research tasks, and code context queries.
It handles argument parsing, API key resolution, and output formatting.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import ValidationError

import httpx

from . import client, structured_logging
from .printing import print_json, save_json
from .workflows import registry


def build_parser() -> argparse.ArgumentParser:
    """Construct the top-level argument parser.

    Returns:
        Configured ArgumentParser with all CLI commands and options.
    """
    global_options = argparse.ArgumentParser(add_help=False)
    global_options.add_argument(
        "--api-key",
        dest="api_key",
        help="Override EXA_API_KEY",
        default=argparse.SUPPRESS,
    )
    global_options.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
        default=argparse.SUPPRESS,
    )
    global_options.add_argument(
        "--save",
        dest="save",
        help="Optional file path for the JSON output",
        default=argparse.SUPPRESS,
    )

    parser = argparse.ArgumentParser(
        prog="exa", description="Direct Exa API CLI", parents=[global_options]
    )

    # Command subparsers
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Register all command parsers
    _register_search(subparsers, global_options)
    _register_contents(subparsers, global_options)
    _register_find_similar(subparsers, global_options)
    _register_answer(subparsers, global_options)
    _register_research(subparsers, global_options)
    _register_context(subparsers, global_options)
    _register_agents(subparsers, global_options)
    _register_workflow(subparsers, global_options)

    return parser


def _register_search(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    global_options: argparse.ArgumentParser,
) -> None:
    """Register the `search` command."""
    search_parser = subparsers.add_parser(
        "search", help="Search the web with Exa", parents=[global_options]
    )

    # Required arguments
    search_parser.add_argument(
        "--query", required=True, help="Natural language search query"
    )

    # Search configuration
    search_parser.add_argument(
        "--type",
        dest="type_",
        choices=["auto", "neural", "keyword", "fast", "hybrid", "deep"],
        help="Search type",
    )
    search_parser.add_argument(
        "--num-results",
        type=int,
        dest="num_results",
        help="Number of results to return",
    )

    # Domain filters
    search_parser.add_argument(
        "--include-domains",
        nargs="*",
        dest="include_domains",
        help="Domains to include",
    )
    search_parser.add_argument(
        "--exclude-domains",
        nargs="*",
        dest="exclude_domains",
        help="Domains to exclude",
    )

    # Date filters
    search_parser.add_argument(
        "--start-published-date",
        dest="start_published_date",
        help="Published date lower bound (YYYY-MM-DD)",
    )
    search_parser.add_argument(
        "--end-published-date",
        dest="end_published_date",
        help="Published date upper bound (YYYY-MM-DD)",
    )
    search_parser.add_argument(
        "--start-crawl-date",
        dest="start_crawl_date",
        help="Crawl date lower bound (YYYY-MM-DD)",
    )
    search_parser.add_argument(
        "--end-crawl-date",
        dest="end_crawl_date",
        help="Crawl date upper bound (YYYY-MM-DD)",
    )

    # Text filters
    search_parser.add_argument(
        "--include-text",
        nargs="*",
        dest="include_text",
        help="Terms that must appear in text (<=5 words)",
    )
    search_parser.add_argument(
        "--exclude-text",
        nargs="*",
        dest="exclude_text",
        help="Terms that must not appear in text",
    )
    search_parser.add_argument(
        "--use-autoprompt", action="store_true", dest="use_autoprompt"
    )
    search_parser.add_argument("--category", dest="category")
    search_parser.add_argument("--user-location", dest="user_location")
    search_parser.add_argument("--moderation", action="store_true", dest="moderation")
    search_parser.add_argument("--flags", nargs="*", dest="flags")
    _add_contents_option_flags(search_parser)


def _register_contents(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    global_options: argparse.ArgumentParser,
) -> None:
    """Register the `contents` command."""
    contents_parser = subparsers.add_parser(
        "contents", help="Fetch page contents by URL", parents=[global_options]
    )

    # Required arguments
    contents_parser.add_argument("urls", nargs="+", help="One or more URLs to fetch")
    _add_contents_option_flags(contents_parser)


def _register_find_similar(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    global_options: argparse.ArgumentParser,
) -> None:
    """Register the `find-similar` command."""
    similar_parser = subparsers.add_parser(
        "find-similar",
        help="Find pages similar to the provided URL",
        parents=[global_options],
    )

    # Required arguments
    similar_parser.add_argument("--url", required=True, help="Source URL")

    # Result configuration
    similar_parser.add_argument(
        "--num-results", type=int, dest="num_results", help="Number of similar results"
    )
    similar_parser.add_argument(
        "--exclude-source-domain",
        action="store_true",
        dest="exclude_source_domain",
        help="Exclude source domain",
    )

    # Domain filters
    similar_parser.add_argument("--include-domains", nargs="*", dest="include_domains")
    similar_parser.add_argument("--exclude-domains", nargs="*", dest="exclude_domains")
    similar_parser.add_argument("--include-text", nargs="*", dest="include_text")
    similar_parser.add_argument("--exclude-text", nargs="*", dest="exclude_text")
    similar_parser.add_argument("--start-published-date", dest="start_published_date")
    similar_parser.add_argument("--end-published-date", dest="end_published_date")
    similar_parser.add_argument("--start-crawl-date", dest="start_crawl_date")
    similar_parser.add_argument("--end-crawl-date", dest="end_crawl_date")
    similar_parser.add_argument("--category", dest="category")
    similar_parser.add_argument("--flags", nargs="*", dest="flags")
    _add_contents_option_flags(similar_parser)


def _register_answer(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    global_options: argparse.ArgumentParser,
) -> None:
    """Register the `answer` command."""
    answer_parser = subparsers.add_parser(
        "answer", help="Ask Exa to answer a question", parents=[global_options]
    )

    # Required arguments
    answer_parser.add_argument("--query", required=True, help="Question to answer")

    # Output options
    answer_parser.add_argument(
        "--include-text",
        action="store_true",
        dest="include_text",
        help="Include citation text",
    )
    answer_parser.add_argument(
        "--stream",
        action="store_true",
        dest="stream",
        help="Stream the answer as it is generated",
    )
    answer_parser.add_argument(
        "--json-lines",
        action="store_true",
        dest="json_lines",
        help="When streaming, emit JSON-lines with chunk events",
    )
    answer_parser.add_argument("--model", choices=["exa", "exa-pro"], dest="model")
    answer_parser.add_argument("--system-prompt", dest="system_prompt")
    answer_parser.add_argument("--output-schema", dest="output_schema")
    answer_parser.add_argument("--user-location", dest="user_location")


def _register_research(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    global_options: argparse.ArgumentParser,
) -> None:
    """Register the `research` command group."""
    research = subparsers.add_parser(
        "research", help="Research task operations", parents=[global_options]
    )
    rsubs = research.add_subparsers(dest="research_cmd", required=True)

    # Start research task
    start = rsubs.add_parser("start", help="Create a research task")
    start.add_argument(
        "--instructions", required=True, help="Text or @path to file with instructions"
    )
    start.add_argument(
        "--model",
        choices=["exa-research-fast", "exa-research", "exa-research-pro"],
        help="Research model",
    )
    start.add_argument(
        "--schema", help="Path to JSON Schema file for structured output"
    )

    # Get research task
    getp = rsubs.add_parser("get", help="Get a research task")
    getp.add_argument("--id", required=True, dest="research_id", help="Research ID")
    getp.add_argument("--events", action="store_true", help="Include event log")

    # List research tasks
    listp = rsubs.add_parser("list", help="List research tasks")
    listp.add_argument("--limit", type=int, help="Page size (1-50 or API default)")
    listp.add_argument("--cursor", help="Pagination cursor")

    # Poll research task
    poll = rsubs.add_parser("poll", help="Poll until completion (SDK defaults)")
    poll.add_argument("--id", required=True, dest="research_id", help="Research ID")
    poll.add_argument(
        "--preset",
        choices=["fast", "balanced", "pro"],
        help="Convenience flag for UX; polling uses SDK defaults",
    )

    # Stream research task
    stream = rsubs.add_parser("stream", help="Stream research events as JSON-lines")
    stream.add_argument("--id", required=True, dest="research_id", help="Research ID")


def _register_context(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    global_options: argparse.ArgumentParser,
) -> None:
    """Register the `context` command group."""
    ctx = subparsers.add_parser(
        "context", help="Exa Code context API", parents=[global_options]
    )
    csubs = ctx.add_subparsers(dest="context_cmd", required=True)

    # Query command
    q = csubs.add_parser("query", help="Query for code examples/context")
    q.add_argument("--query", required=True, help="Query text")
    q.add_argument(
        "--tokensNum", dest="tokens_num", help="dynamic or integer token target"
    )


def _register_agents(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    global_options: argparse.ArgumentParser,
) -> None:
    """Register the `agents` command group."""
    agents = subparsers.add_parser(
        "agents", help="OpenAI Agents SDK orchestration", parents=[global_options]
    )
    asubs = agents.add_subparsers(dest="agents_cmd", required=True)

    run = asubs.add_parser("run", help="Run the coordinator over an input prompt")
    run.add_argument("--input", required=True, help="User prompt")
    run.add_argument("--model", dest="model", help="Coordinator model override")
    run.add_argument(
        "--specialist-model", dest="specialist_model", help="Specialist model override"
    )
    run.add_argument(
        "--max-turns", dest="max_turns", type=int, help="Max agent loop turns"
    )
    run.add_argument(
        "--session-id", dest="session_id", help="Conversation/session identifier"
    )
    run.add_argument(
        "--session-backend",
        dest="session_backend",
        choices=["none", "sqlite", "advanced_sqlite"],
        help="Session backend (default derives from --session-id)",
    )
    run.add_argument(
        "--session-db", dest="session_db", help=":memory: or path to SQLite DB"
    )


def _register_workflow(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    global_options: argparse.ArgumentParser,
) -> None:
    """Register the `workflow` command."""
    workflow_parser = subparsers.add_parser(
        "workflow",
        help="Inspect and execute registered workflows",
        parents=[global_options],
    )
    w_sub = workflow_parser.add_subparsers(dest="workflow_cmd", required=True)

    w_list = w_sub.add_parser("list", help="List available workflows")
    w_list.add_argument(
        "--format",
        choices=["json", "table"],
        default="json",
        help="Output format",
    )

    w_desc = w_sub.add_parser("describe", help="Describe a workflow")
    w_desc.add_argument("name", help="Workflow name")
    w_desc.add_argument(
        "--schema",
        action="store_true",
        help="Include input/output JSON Schemas",
    )

    w_run = w_sub.add_parser("run", help="Execute a workflow")
    w_run.add_argument("name", help="Workflow name")
    w_run.add_argument(
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Inline parameter (repeatable)",
    )
    w_run.add_argument(
        "--input",
        dest="input_payload",
        help="JSON payload or @path/to/file.json",
    )
    w_run.add_argument(
        "--plan",
        action="store_true",
        help="Show execution plan without running",
    )
    w_run.add_argument(
        "--dry-run",
        action="store_true",
        help="Alias for --plan",
    )


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Args:
        argv: Command line arguments (defaults to sys.argv).

    Returns:
        Exit code (0 for success, 1 for error).
    """
    # Load environment configuration and configure logging once.
    load_dotenv()
    structured_logging.configure()

    # Parse command line arguments
    parser = build_parser()
    args = parser.parse_args(argv)

    # Resolve API key
    try:
        api_key = client.resolve_api_key(getattr(args, "api_key", None))
    except RuntimeError as error:
        parser.error(str(error))

    # Create service instance
    service = client.create_service(api_key)

    # Execute command and handle results
    try:
        result = _dispatch(service, args)
    except httpx.HTTPStatusError as error:
        response = getattr(error, "response", None)
        if response is not None:
            code = getattr(response, "status_code", "?")
            text = getattr(response, "text", "")
            sys.stderr.write(f"HTTP error: {code} {text}\n")
        else:
            sys.stderr.write("HTTP error\n")
        return 1
    except (ValueError, RuntimeError, OSError, httpx.RequestError) as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return 1

    # Output results if present
    pretty = bool(getattr(args, "pretty", False))
    save_path = getattr(args, "save", None)
    if result is not None:
        if save_path:
            save_json(save_path, result, pretty=pretty)
        print_json(result, pretty=pretty)

    return 0


def _dispatch(
    service: client.ExaService, args: argparse.Namespace
) -> dict[str, Any] | None:
    """Route to the correct service call based on the command.

    Args:
        service: Configured ExaService instance.
        args: Parsed command line arguments.

    Returns:
        Command result as dictionary, or None for streaming commands.
    """
    command = args.command

    handlers: dict[
        str, Callable[[client.ExaService, argparse.Namespace], dict[str, Any] | None]
    ] = {
        "search": _handle_search,
        "contents": _handle_contents,
        "find-similar": _handle_find_similar,
        "answer": _handle_answer,
        "research": _handle_research,
        "context": _handle_context,
        "agents": _handle_agents,
        "workflow": _handle_workflow,
    }

    try:
        handler = handlers[command]
    except KeyError as error:
        raise ValueError(f"Unsupported command: {command}") from error
    return handler(service, args)


def _handle_search(
    service: client.ExaService, args: argparse.Namespace
) -> dict[str, Any]:
    """Execute the search command."""
    base = _build_search_filters(args)
    contents = _build_contents_options(args)
    inputs = registry.get("search_cli").inputs_type(
        query=args.query,
        search_params=base,
        contents_params=contents,
    )
    result = registry.execute("search_cli", service, inputs)
    return result.results  # type: ignore[return-value]


def _handle_contents(
    service: client.ExaService, args: argparse.Namespace
) -> dict[str, Any]:
    """Execute the contents command."""
    inputs = registry.get("contents_cli").inputs_type(
        urls=args.urls,
        options=_build_contents_options(args),
    )
    result = registry.execute("contents_cli", service, inputs)
    return result.contents  # type: ignore[return-value]


def _handle_find_similar(
    service: client.ExaService, args: argparse.Namespace
) -> dict[str, Any]:
    """Execute the find-similar command."""
    base = _build_find_filters(args)
    contents = _build_contents_options(args)
    inputs = registry.get("find_similar_cli").inputs_type(
        url=args.url,
        find_params=base,
        contents_params=contents,
    )
    result = registry.execute("find_similar_cli", service, inputs)
    return result.results  # type: ignore[return-value]


def _handle_answer(
    service: client.ExaService, args: argparse.Namespace
) -> dict[str, Any] | None:
    """Execute the answer command."""
    # Check if streaming output is requested
    if getattr(args, "stream", False):
        opts = _build_answer_options(args)

        # Stream JSON lines if requested
        if getattr(args, "json_lines", False):
            for event in service.answer_stream_json(query=args.query, **opts):
                print(json.dumps(event, ensure_ascii=False))
            return None

        # Stream regular text output chunk-by-chunk
        for chunk in service.answer_stream(query=args.query, **opts):
            sys.stdout.write(str(chunk))
        sys.stdout.write("\n")
        return None

    # Standard synchronous answer
    inputs = registry.get("answer_cli").inputs_type(
        query=args.query, options=_build_answer_options(args)
    )
    result = registry.execute("answer_cli", service, inputs)
    return result.answer  # type: ignore[return-value]


def _handle_research(
    service: client.ExaService, args: argparse.Namespace
) -> dict[str, Any] | None:
    """Execute research subcommands."""
    subcommand = args.research_cmd
    actions: dict[
        str, Callable[[client.ExaService, argparse.Namespace], dict[str, Any] | None]
    ] = {
        "start": _research_start,
        "get": _research_get,
        "list": _research_list,
        "poll": _research_poll,
        "stream": _research_stream,
    }
    try:
        action = actions[subcommand]
    except KeyError as error:
        raise ValueError(f"Unknown research subcommand: {subcommand}") from error
    return action(service, args)


def _research_start(
    service: client.ExaService, args: argparse.Namespace
) -> dict[str, Any]:
    """Handle `research start`."""
    instructions = _read_arg_or_file(args.instructions)
    schema = _read_json_file(args.schema) if args.schema else None
    return service.research_start(
        instructions=instructions,
        model=args.model,
        output_schema=schema,
    )


def _research_get(
    service: client.ExaService, args: argparse.Namespace
) -> dict[str, Any]:
    """Handle `research get`."""
    return service.research_get(research_id=args.research_id, events=args.events)


def _research_list(
    service: client.ExaService, args: argparse.Namespace
) -> dict[str, Any]:
    """Handle `research list`."""
    return service.research_list(limit=args.limit, cursor=args.cursor)


def _research_poll(
    service: client.ExaService, args: argparse.Namespace
) -> dict[str, Any]:
    """Handle `research poll`."""
    # Polling uses SDK defaults; --preset is informational only.
    return service.research_poll(research_id=args.research_id)


def _research_stream(service: client.ExaService, args: argparse.Namespace) -> None:
    """Handle `research stream` (always JSON-lines)."""
    for event in service.research_stream(research_id=args.research_id):
        print(json.dumps(event, ensure_ascii=False))


def _handle_context(
    service: client.ExaService, args: argparse.Namespace
) -> dict[str, Any]:
    """Execute context subcommands."""
    if args.context_cmd != "query":
        raise ValueError(f"Unknown context subcommand: {args.context_cmd}")
    return service.context(query=args.query, tokens_num=args.tokens_num)


def _handle_workflow(
    service: client.ExaService, args: argparse.Namespace
) -> dict[str, Any] | None:
    """Execute workflow subcommands."""
    if args.workflow_cmd == "list":
        entries = [{"name": wf.name, "summary": wf.summary} for wf in registry.list()]
        if args.format == "table":
            for entry in entries:
                print(f"{entry['name']}: {entry['summary']}")
            return None
        return {"workflows": entries}

    if args.workflow_cmd == "describe":
        definition = registry.get(args.name)
        description: dict[str, Any] = {
            "name": definition.name,
            "summary": definition.summary,
        }
        if args.schema:
            description["input_schema"] = definition.inputs_type.model_json_schema()
            description["output_schema"] = definition.outputs_type.model_json_schema()
        plan_inputs = definition.inputs_type.model_construct()
        plan = definition.plan(plan_inputs)
        description["plan"] = [
            {"name": step.name, "description": step.description} for step in plan
        ]
        return description

    if args.workflow_cmd == "run":
        definition = registry.get(args.name)
        payload = _resolve_workflow_payload(args, definition)
        if args.plan or args.dry_run:
            plan = definition.plan(payload)
            return {
                "workflow": definition.name,
                "plan": [
                    {"name": step.name, "description": step.description}
                    for step in plan
                ],
            }
        outputs = registry.execute(args.name, service, payload)
        return {
            "workflow": definition.name,
            "outputs": outputs.model_dump(exclude_none=True),
        }
    raise ValueError(f"Unknown workflow subcommand: {args.workflow_cmd}")


def _handle_agents(
    _service: client.ExaService, args: argparse.Namespace
) -> dict[str, Any] | None:
    """Execute `agents` subcommands using the Agents SDK integration."""
    if os.getenv("EXA_DIRECT_ENABLE_OPENAI", "0").lower() not in {"1", "true", "yes"}:
        raise RuntimeError(
            "Agents disabled. Set EXA_DIRECT_ENABLE_OPENAI=1 and install openai-agents."
        )
    from exa_direct.integrations import agents as agents_module  # lazy import

    if args.agents_cmd != "run":
        raise ValueError(f"Unknown agents subcommand: {args.agents_cmd}")

    settings_kwargs: dict[str, Any] = {}
    if getattr(args, "model", None):
        settings_kwargs["model"] = args.model
    if getattr(args, "specialist_model", None):
        settings_kwargs["specialist_model"] = args.specialist_model
    if getattr(args, "max_turns", None) is not None:
        settings_kwargs["max_turns"] = args.max_turns
    settings = agents_module.CoordinatorSettings(
        model=settings_kwargs.get(
            "model", os.getenv("EXA_DIRECT_AGENTS_MODEL", "gpt-4.1-mini")
        ),
        max_turns=settings_kwargs.get("max_turns"),
        specialist_model=settings_kwargs.get("specialist_model"),
    )

    import asyncio as _asyncio

    async def _run():
        return await agents_module.run_coordinator(
            args.input,
            settings=settings,
            context=agents_module.WorkflowAgentContext(conversation_id=args.session_id),
            session_id=args.session_id,
            session_backend=args.session_backend,
            session_db_path=args.session_db,
        )

    result = _asyncio.run(_run())
    return {"final_output": getattr(result, "final_output", None)}


def _resolve_workflow_payload(args: argparse.Namespace, definition) -> Any:
    """Build workflow inputs from CLI parameters."""
    payload: dict[str, Any] = {}
    if args.input_payload:
        content = _read_arg_or_file(args.input_payload)
        payload.update(json.loads(content))
    for raw in args.param:
        if "=" not in raw:
            raise ValueError(f"Invalid --param format: {raw!r}")
        key, value = raw.split("=", 1)
        payload[key] = value
    try:
        return definition.inputs_type(**payload)
    except ValidationError as exc:
        raise ValueError(str(exc)) from exc


def _clean_params(raw: dict[str, Any]) -> dict[str, Any]:
    """Drop parameters whose values are falsy/None."""
    return {key: value for key, value in raw.items() if value not in (None, [], False)}


def _read_arg_or_file(value: str) -> str:
    """Read content from a file when prefixed with '@', else return the string.

    Args:
        value: Either plain text or a token like '@path/to/file'.

    Returns:
        Content string, either the original value or file contents.
    """
    if value.startswith("@"):
        path = value[1:]
        return Path(path).read_text(encoding="utf-8")
    return value


def _read_json_file(path: str) -> dict[str, Any]:
    """Read a JSON file into a dict."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _build_search_filters(args: argparse.Namespace) -> dict[str, Any]:
    """Build search filter parameters from CLI args."""
    return _clean_params({
        "num_results": args.num_results,
        "type": args.type_,
        "include_domains": args.include_domains,
        "exclude_domains": args.exclude_domains,
        "start_published_date": args.start_published_date,
        "end_published_date": args.end_published_date,
        "start_crawl_date": args.start_crawl_date,
        "end_crawl_date": args.end_crawl_date,
        "include_text": args.include_text,
        "exclude_text": args.exclude_text,
        "use_autoprompt": args.use_autoprompt,
        "category": args.category,
        "user_location": args.user_location,
        "moderation": args.moderation,
        "flags": args.flags,
    })


def _build_find_filters(args: argparse.Namespace) -> dict[str, Any]:
    """Build find-similar filter parameters from CLI args."""
    return _clean_params({
        "num_results": args.num_results,
        "exclude_source_domain": args.exclude_source_domain,
        "include_domains": args.include_domains,
        "exclude_domains": args.exclude_domains,
        "include_text": getattr(args, "include_text", None),
        "exclude_text": getattr(args, "exclude_text", None),
        "start_published_date": getattr(args, "start_published_date", None),
        "end_published_date": getattr(args, "end_published_date", None),
        "start_crawl_date": getattr(args, "start_crawl_date", None),
        "end_crawl_date": getattr(args, "end_crawl_date", None),
        "category": getattr(args, "category", None),
        "flags": getattr(args, "flags", None),
    })


def _build_answer_options(args: argparse.Namespace) -> dict[str, Any]:
    """Build answer options for service calls (includes include_text)."""
    schema = _read_json_file(args.output_schema) if args.output_schema else None
    # include_text must be passed even when False; do not drop it
    opts: dict[str, Any] = {"include_text": args.include_text}
    opts.update(
        _clean_params({
            "model": args.model,
            "system_prompt": args.system_prompt,
            "output_schema": schema,
            "user_location": args.user_location,
        })
    )
    return opts


def _add_contents_option_flags(p: argparse.ArgumentParser) -> None:
    """Add contents-related flags to a parser."""
    # Text
    p.add_argument("--text", action="store_true", help="Include full text")
    p.add_argument("--text-max-characters", type=int, dest="text_max_chars")
    p.add_argument(
        "--text-include-html-tags",
        action="store_true",
        dest="text_include_html",
        help="Include HTML tags in text",
    )
    # Highlights
    p.add_argument("--highlights", action="store_true", help="Include highlights")
    p.add_argument("--highlights-num-sentences", type=int, dest="hl_num_sentences")
    p.add_argument("--highlights-per-url", type=int, dest="hl_per_url")
    p.add_argument("--highlights-query", dest="hl_query")
    # Summary
    p.add_argument("--summary-query", dest="summary_query")
    p.add_argument("--summary-schema", dest="summary_schema")
    # Metadata
    p.add_argument("--metadata", action="store_true", dest="metadata")
    p.add_argument("--metadata-json", dest="metadata_json")
    # Subpages
    p.add_argument("--subpages", type=int, dest="subpages")
    p.add_argument("--subpage-target", dest="subpage_target")
    # Extras
    p.add_argument("--extras-links", type=int, dest="extras_links")
    p.add_argument("--extras-image-links", type=int, dest="extras_image_links")
    # Context
    p.add_argument("--context", action="store_true", dest="context")
    p.add_argument("--context-max-characters", type=int, dest="context_max_chars")
    # Livecrawl
    p.add_argument(
        "--livecrawl",
        choices=["always", "preferred", "fallback", "never", "auto"],
        help="Livecrawl freshness preference",
    )
    p.add_argument("--livecrawl-timeout", type=int, dest="livecrawl_timeout")
    # Filters and flags
    p.add_argument(
        "--filter-empty-results", action="store_true", dest="filter_empty_results"
    )
    p.add_argument("--contents-flags", nargs="*", dest="contents_flags")


def _build_contents_options(args: argparse.Namespace) -> dict[str, Any]:
    """Build SDK contents options from parsed args (snake_case keys)."""
    opts: dict[str, Any] = {}
    # text
    if getattr(args, "text", False) or (
        getattr(args, "text_max_chars", None) is not None
        or getattr(args, "text_include_html", False)
    ):
        if args.text_max_chars is not None or args.text_include_html:
            t: dict[str, Any] = {}
            if getattr(args, "text_max_chars", None) is not None:
                t["max_characters"] = args.text_max_chars
            if getattr(args, "text_include_html", False):
                t["include_html_tags"] = True
            opts["text"] = t
        else:
            opts["text"] = True
    # highlights
    if getattr(args, "highlights", False) or any(
        getattr(args, name, None) is not None
        for name in ("hl_num_sentences", "hl_per_url", "hl_query")
    ):
        h: dict[str, Any] = {}
        if args.hl_num_sentences is not None:
            h["num_sentences"] = args.hl_num_sentences
        if args.hl_per_url is not None:
            h["highlights_per_url"] = args.hl_per_url
        if args.hl_query:
            h["query"] = args.hl_query
        opts["highlights"] = h or True
    # summary
    if getattr(args, "summary_query", None) or getattr(args, "summary_schema", None):
        s: dict[str, Any] = {}
        if args.summary_query:
            s["query"] = args.summary_query
        if args.summary_schema:
            s["schema"] = _read_json_file(args.summary_schema)
        opts["summary"] = s
    # metadata
    if getattr(args, "metadata", False) or getattr(args, "metadata_json", None):
        if args.metadata_json:
            opts["metadata"] = _read_json_file(args.metadata_json)
        else:
            opts["metadata"] = True
    # subpages
    if getattr(args, "subpages", None) is not None:
        opts["subpages"] = args.subpages
    if getattr(args, "subpage_target", None):
        target = args.subpage_target
        if "," in target:
            opts["subpage_target"] = [p.strip() for p in target.split(",") if p.strip()]
        else:
            opts["subpage_target"] = target
    # extras
    if (
        getattr(args, "extras_links", None) is not None
        or getattr(args, "extras_image_links", None) is not None
    ):
        ex: dict[str, Any] = {}
        if args.extras_links is not None:
            ex["links"] = args.extras_links
        if args.extras_image_links is not None:
            ex["image_links"] = args.extras_image_links
        opts["extras"] = ex
    # context
    if (
        getattr(args, "context", False)
        or getattr(args, "context_max_chars", None) is not None
    ):
        if args.context_max_chars is not None:
            opts["context"] = {"max_characters": args.context_max_chars}
        else:
            opts["context"] = True
    # livecrawl
    if getattr(args, "livecrawl", None):
        opts["livecrawl"] = args.livecrawl
    if getattr(args, "livecrawl_timeout", None) is not None:
        opts["livecrawl_timeout"] = args.livecrawl_timeout
    # filter_empty_results
    if getattr(args, "filter_empty_results", False):
        opts["filter_empty_results"] = True
    # flags
    if getattr(args, "contents_flags", None):
        opts["flags"] = args.contents_flags
    return opts


if __name__ == "__main__":
    sys.exit(main())
