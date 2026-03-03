Generate a focused HTML visual aid for the lab.

## When to Use

- When a flow file marks `[VISUAL]` in a Show field
- When explaining spatial/relational concepts (architecture, data flow, pipelines)
- When a comparison table would be clearer than prose

## Visual Types

### Architecture Diagram
Boxes connected by labeled arrows. Each component has a name, brief description, and type badge (GPU, CPU, API, Storage). Connections show protocol and auth method.

### Pipeline Flow
Horizontal left-to-right stages with gate markers. Each stage shows: name, inputs, outputs. Gates show what checks happen at each transition. Use color to indicate security status (green=scanned, red=no scan, yellow=partial).

### Request Flow (Sequence Diagram)
Vertical sequence with labeled arrows between swimlanes. Each step shows what is sent and returned. Include auth and protocol details at boundaries.

### Comparison Table
Styled HTML table with header row and alternating row colors. Cells support checkmarks, X marks, short text, and status badges.

## Output

Write a single self-contained HTML file to `lab/.visuals/`. Name it: `[module]-[challenge]-[concept].html`

Example: `lab/.visuals/m3-c1-request-flow.html`

## Design Rules

- **Zero dependencies** — single HTML file, inline CSS and JS, no external assets
- **Dark theme** — background #0f172a, surfaces #1e293b, borders #334155
- **Text** — primary #f8fafc, muted #94a3b8, accent #38bdf8
- **Status colors** — success #4ade80, warning #fbbf24, danger #f87171
- **Fonts** — system-ui for labels, monospace for technical annotations
- **Size** — 100-300 lines max. Single viewport, no scrolling required
- **Animations** — subtle fade-in only. No scroll-snap, no navigation, no presentation controls
- **Labels** — minimal text. Annotations, not paragraphs. Use short phrases.

## HTML Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[Visual Title]</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #0f172a;
    color: #f8fafc;
    font-family: system-ui, -apple-system, sans-serif;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 2rem;
  }
  .container { max-width: 1200px; width: 100%; }
  h1 { font-size: 1.5rem; color: #38bdf8; margin-bottom: 1.5rem; font-weight: 600; }
  .component {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 1rem 1.25rem;
  }
  .badge {
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .badge-gpu { background: #7c3aed33; color: #a78bfa; }
  .badge-cpu { background: #0ea5e933; color: #38bdf8; }
  .badge-api { background: #f59e0b33; color: #fbbf24; }
  .badge-storage { background: #10b98133; color: #4ade80; }
  .badge-danger { background: #ef444433; color: #f87171; }
  .mono { font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 0.85rem; }
  .muted { color: #94a3b8; }
  .arrow { color: #475569; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
  .fade-in { animation: fadeIn 0.4s ease-out both; }
</style>
</head>
<body>
<div class="container">
  <!-- Visual content here -->
</div>
</body>
</html>
```

## After Generation

1. Write the HTML file to `lab/.visuals/`
2. Tell the student: "I've created a visual diagram. Open it in your browser: `lab/.visuals/[filename].html`"
3. Continue with the teaching flow — don't wait for them to confirm they opened it
