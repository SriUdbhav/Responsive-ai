import sys
from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

# Ensure UTF-8 output on Windows terminal
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _extract_content(message) -> str:
    content = getattr(message, "content", message)
    if isinstance(content, list):
        return "".join(b if isinstance(b, str) else b.get("text", "") for b in content)
    return str(content)


def research_pipeline(topic: str, status_callback=None) -> dict:
    def notify(stage, event, data=None):
        if status_callback:
            status_callback(stage, event, data)

    state = {}

    # Step 1: Search Agent
    print("\n" + "=" * 60)
    print("Step 1: Search Agent is working...")
    print("=" * 60)

    notify("search", "start")
    try:
        search_agent = build_search_agent()
        search_result = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
        })
        state["search_results"] = _extract_content(search_result["messages"][-1])
        notify("search", "done", state["search_results"])
    except Exception as error:
        notify("search", "error", str(error))
        raise

    print("\n--- Search Results ---")
    print(state["search_results"])

    # Step 2: Reader Agent
    print("\n" + "=" * 60)
    print("Step 2: Reader Agent is scraping top resources...")
    print("=" * 60)

    notify("reader", "start")
    try:
        reader_agent = build_reader_agent()
        # Pass full search results (capped at 3000 chars to avoid prompt overflow while preserving URLs)
        search_context = state["search_results"][:3000]
        reader_result = reader_agent.invoke({
            "messages": [(
                "user",
                f"Based on the following search results about '{topic}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search results:\n{search_context}"
            )]
        })
        state["scraped_content"] = _extract_content(reader_result["messages"][-1])
        notify("reader", "done", state["scraped_content"])
    except Exception as error:
        notify("reader", "error", str(error))
        raise

    print("\n--- Scraped Content ---")
    print(state["scraped_content"])

    # Step 3: Writer Chain
    print("\n" + "=" * 60)
    print("Step 3: Writer is drafting the report...")
    print("=" * 60)

    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )

    notify("writer", "start")
    try:
        state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": research_combined
        })
        notify("writer", "done", state["report"])
    except Exception as error:
        notify("writer", "error", str(error))
        raise

    print("\n--- Final Report ---")
    print(state["report"])

    # Step 4: Critic Chain
    print("\n" + "=" * 60)
    print("Step 4: Critic is reviewing the report...")
    print("=" * 60)

    notify("critic", "start")
    try:
        state["feedback"] = critic_chain.invoke({
            "report": state["report"]
        })
        notify("critic", "done", state["feedback"])
    except Exception as error:
        notify("critic", "error", str(error))
        raise

    print("\n--- Critic Review ---")
    print(state["feedback"])

    return state


if __name__ == "__main__":
    if len(sys.argv) > 1:
        topic_arg = " ".join(sys.argv[1:])
    else:
        topic_arg = input("\nEnter a research topic: ")
    research_pipeline(topic_arg)
