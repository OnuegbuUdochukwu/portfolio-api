import asyncio

from app.scrapers import hackernews, lobsters, devto, reddit


async def run_all() -> dict[str, int]:
    results: dict[str, int] = {}
    for scraper in [hackernews, lobsters, devto, reddit]:
        name = scraper.__name__.split(".")[-1]
        try:
            count = await scraper.scrape_and_persist()
            results[name] = count
        except Exception as e:
            print(f"[orchestrator] {name} failed: {e}")
            results[name] = -1
    return results


def main():
    results = asyncio.run(run_all())
    total = sum(v for v in results.values() if v > 0)
    print(f"\n[orchestrator] done — {total} total posts across {len(results)} sources")
    for name, count in results.items():
        status = "ok" if count >= 0 else "failed"
        print(f"  {name}: {count} ({status})")


if __name__ == "__main__":
    main()
