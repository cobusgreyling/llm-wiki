# Obsidian integration

Open your wiki project folder as an Obsidian vault. The agent maintains wikilinks; you browse the graph.

## Web Clipper

Clip articles directly to `raw/`, then tell your agent: "Ingest the new source in raw/."

## Dataview snippets

Add these to a dashboard note in your vault.

### All entities

```dataview
TABLE created, updated, sources
FROM "wiki/entities"
WHERE type = "entity"
SORT updated DESC
```

### All concepts

```dataview
TABLE created, updated, tags
FROM "wiki/concepts"
WHERE type = "concept"
SORT file.name ASC
```

### Sources by ingest date

```dataview
TABLE raw_file, created, updated
FROM "wiki/sources"
WHERE type = "source"
SORT created DESC
```

### Recent answers

```dataview
TABLE created, sources
FROM "wiki/answers"
WHERE type = "answer"
SORT created DESC
LIMIT 10
```

### Pages updated this week

```dataview
TABLE type, updated
FROM "wiki"
WHERE updated >= date(today) - dur(7 days)
SORT updated DESC
```

## Graph view

Use graph view to spot orphan pages (no inbound links) and hub concepts. Cross-check with `wiki lint --category orphan`.

## Marp

Generate slide decks from wiki content using the [Marp plugin](https://github.com/marp-team/marp-vscode).