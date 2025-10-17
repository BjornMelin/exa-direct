"""Command-line interface for the exa-direct tool.

This module provides a CLI for interacting with the Exa API,
supporting search, contents retrieval, research tasks, and code context queries.
It handles argument parsing, API key resolution, and output formatting.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import requests

from . import client
from .printing import print_json, save_json


def build_parser() -> argparse.ArgumentParser:
    """Construct the top-level argument parser.

    Returns:
        Configured ArgumentParser with all CLI commands and options.
    """
    parser = argparse.ArgumentParser(prog="exa", description="Direct Exa API CLI")

    # Global options
    parser.add_argument("--api-key", dest="api_key", help="Override EXA_API_KEY")
    parser.add_argument(
        "--pretty", action="store_true", help="Pretty-print JSON output"
    )
    parser.add_argument(
        "--save", dest="save", help="Optional file path for the JSON output"
    )

    # Command subparsers
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Register all command parsers
    _register_search(subparsers)
    _register_contents(subparsers)
    _register_find_similar(subparsers)
    _register_answer(subparsers)
    _register_research(subparsers)
    _register_context(subparsers)

    return parser


def _register_search(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """Register the `search` command.

    Args:
        subparsers: Parent subparsers action to add the search command to.
    """
    search_parser = subparsers.add_parser("search", help="Search the web with Exa")

    # Required arguments
    search_parser.add_argument(
        "--query", required=True, help="Natural language search query"
    )

    # Search configuration
    search_parser.add_argument(
        "--type",
        dest="type_",
        choices=["auto", "neural", "keyword", "fast"],
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


def _register_contents(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """Register the `contents` command.

    Args:
        subparsers: Parent subparsers action to add the contents command to.
    """
    contents_parser = subparsers.add_parser(
        "contents", help="Fetch page contents by URL"
    )

    # Required arguments
    contents_parser.add_argument("urls", nargs="+", help="One or more URLs to fetch")

    # Content options
    contents_parser.add_argument(
        "--text", action="store_true", help="Include full text"
    )
    contents_parser.add_argument(
        "--highlights", action="store_true", help="Include highlights"
    )
    contents_parser.add_argument(
        "--livecrawl",
        choices=["always", "preferred", "fallback", "never"],
        help="Livecrawl freshness preference",
    )


def _register_find_similar(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """Register the `find-similar` command.

    Args:
        subparsers: Parent subparsers action to add the find-similar command to.
    """
    similar_parser = subparsers.add_parser(
        "find-similar", help="Find pages similar to the provided URL"
    )

    # Required arguments
    similar_parser.add_argument(
        "--url",
        required=True,
        help="Source URL",
    )

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
    similar_parser.add_argument(
        "--include-domains",
        nargs="*",
        dest="include_domains",
        help="Domains to include",
    )
    similar_parser.add_argument(
        "--exclude-domains",
        nargs="*",
        dest="exclude_domains",
        help="Domains to exclude",
    )


def _register_answer(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """Register the `answer` command.

    Args:
        subparsers: Parent subparsers action to add the answer command to.
    """
    answer_parser = subparsers.add_parser("answer", help="Ask Exa to answer a question")

    # Required arguments
    answer_parser.add_argument("--query", required=True, help="Question to answer")

    # Output options
    answer_parser.add_argument(
        "--include-text",
        action="store_true",
        dest="include_text",
        help="Include citation text",
    )


def _register_research(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """Register the `research` command group.

    Args:
        subparsers: Parent subparsers action to add the research command to.
    """
    research = subparsers.add_parser("research", help="Research task operations")
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
    start.add_argument(
        "--infer-schema", action="store_true", help="Infer schema when not provided"
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
    poll = rsubs.add_parser("poll", help="Poll until completion")
    poll.add_argument("--id", required=True, dest="research_id", help="Research ID")
    poll.add_argument(
        "--model",
        choices=["exa-research-fast", "exa-research", "exa-research-pro"],
        help="Choose preset poll interval",
    )
    poll.add_argument(
        "--interval", type=int, help="Seconds between polls (overrides preset)"
    )
    poll.add_argument(
        "--timeout", type=int, default=600, help="Maximum seconds to wait"
    )

    # Stream research task
    stream = rsubs.add_parser("stream", help="Stream SSE events for a task")
    stream.add_argument("--id", required=True, dest="research_id", help="Research ID")
    stream.add_argument(
        "--json-events",
        action="store_true",
        dest="json_events",
        help="Parse SSE and emit one JSON object per event",
    )


def _register_context(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """Register the `context` command group.

    Args:
        subparsers: Parent subparsers action to add the context command to.
    """
    ctx = subparsers.add_parser("context", help="Exa Code context API")
    csubs = ctx.add_subparsers(dest="context_cmd", required=True)

    # Query command
    q = csubs.add_parser("query", help="Query for code examples/context")
    q.add_argument("--query", required=True, help="Query text")
    q.add_argument(
        "--tokensNum", dest="tokens_num", help="dynamic or integer token target"
    )


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Args:
        argv: Command line arguments (defaults to sys.argv).

    Returns:
        Exit code (0 for success, 1 for error).
    """
    # Parse command line arguments
    parser = build_parser()
    args = parser.parse_args(argv)

    # Resolve API key
    try:
        api_key = client.resolve_api_key(args.api_key)
    except RuntimeError as error:
        parser.error(str(error))

    # Create service instance
    service = client.create_service(api_key)

    # Execute command and handle results
    try:
        result = _dispatch(service, args)
    except requests.HTTPError as error:
        sys.stderr.write(
            f"HTTP error: {error.response.status_code} {error.response.text}\n"
        )
        return 1
    except Exception as exc:  # pylint: disable=broad-except  # noqa: BLE001
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
    # pylint: disable=too-many-branches,too-many-return-statements
    command = args.command

    # Search command
    if command == "search":
        # Build search parameters
        params: dict[str, Any] = {
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
        }
        cleaned_params = _clean_params(params)
        return service.search(query=args.query, params=cleaned_params)
    # Contents command
    if command == "contents":
        return service.contents(
            urls=args.urls,
            text=args.text,
            highlights=args.highlights,
            livecrawl=args.livecrawl,
        )

    # Find similar command
    if command == "find-similar":
        params = {
            "num_results": args.num_results,
            "exclude_source_domain": args.exclude_source_domain,
            "include_domains": args.include_domains,
            "exclude_domains": args.exclude_domains,
        }
        return service.find_similar(url=args.url, params=_clean_params(params))

    # Answer command
    if command == "answer":
        return service.answer(query=args.query, include_text=args.include_text)
    # Research commands
    if command == "research":
        sub = args.research_cmd

        # Start research task
        if sub == "start":
            instructions = _read_arg_or_file(args.instructions)
            schema = _read_json_file(args.schema) if args.schema else None
            return service.research_start(
                instructions=instructions,
                model=args.model,
                output_schema=schema,
                infer_schema=args.infer_schema,
            )

        # Get research task
        if sub == "get":
            return service.research_get(
                research_id=args.research_id, events=args.events
            )

        # List research tasks
        if sub == "list":
            return service.research_list(limit=args.limit, cursor=args.cursor)

        # Poll research task
        if sub == "poll":
            # Determine poll interval
            interval = args.interval
            if interval is None and args.model:
                interval = {
                    "exa-research-fast": 10,
                    "exa-research": 30,
                    "exa-research-pro": 40,
                }[args.model]
            if interval is None:
                interval = 30

            return service.research_poll(
                research_id=args.research_id,
                poll_interval=interval,
                max_wait_time=args.timeout,
            )

        # Stream research task
        if sub == "stream":
            if getattr(args, "json_events", False):
                # Stream parsed JSON events
                for event in service.research_stream_events(
                    research_id=args.research_id
                ):
                    print(json.dumps(event, ensure_ascii=False))
            else:
                # Stream raw SSE lines
                for line in service.research_stream(research_id=args.research_id):
                    print(line)
            return None
        raise ValueError(f"Unknown research subcommand: {sub}")

    # Context commands
    if command == "context":
        if args.context_cmd == "query":
            return service.context(query=args.query, tokens_num=args.tokens_num)
        raise ValueError(f"Unknown context subcommand: {args.context_cmd}")

    # Unknown command
    raise ValueError(f"Unsupported command: {command}")


def _clean_params(raw: dict[str, Any]) -> dict[str, Any]:
    """Drop parameters whose values are falsy/None.

    Args:
        raw: Dictionary of parameters to clean.

    Returns:
        Dictionary with falsy/None values removed.
    """
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


if __name__ == "__main__":
    sys.exit(main())
