# SPXIA Design System — Documentos PDF

Design system usado para geração de documentos PDF profissionais via HTML + Playwright.
Extraído dos documentos de curso e planejamento da SimplexIA.

---

## 1. Tipografia

| Papel | Fonte | Fallback | Uso |
|-------|-------|----------|-----|
| Display / Títulos | DM Serif Display | Georgia, serif | h1, h2, stats, números grandes |
| Corpo / UI | Outfit | system-ui, sans-serif | Parágrafos, tabelas, cards |
| Mono / Labels | JetBrains Mono | monospace | Headers de slide, badges, labels, código, footer |

**Google Fonts import:**
```html
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=JetBrains+Mono:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
```

**CSS variables:**
```css
--font-display: 'DM Serif Display', Georgia, serif;
--font-body: 'Outfit', system-ui, sans-serif;
--font-mono: 'JetBrains Mono', monospace;
```

### Escala tipográfica

| Elemento | Font | Size | Weight | Extras |
|----------|------|------|--------|--------|
| Cover h1 | display | 3.2-3.6rem | 400 | line-height: 1.05-1.08 |
| Slide h2 | display | 1.9-2rem | 400 | line-height: 1.15 |
| Slide intro | body | 0.85-0.9rem | 300 | color: gray-500, max-width: 460px |
| Phase header h3 | display | 1.05rem | 400 | — |
| Body text | body | 0.72-0.78rem | 400 | line-height: 1.5-1.6 |
| Table header | mono | 0.62rem | 600 | uppercase, letter-spacing: 0.05em |
| Table cell | body | 0.72rem | 400 | — |
| Slide header label | mono | 0.65rem | 600 | uppercase, letter-spacing: 0.08em |
| Slide header badge | mono | 0.6rem | 700 | — |
| Footer | mono | 0.55rem | 400 | letter-spacing: 0.08em |
| Cover label | mono | 0.65rem | 500 | uppercase, letter-spacing: 0.12em |
| Cover sub | body | 1-1.05rem | 300 | color: white 50% opacity |
| Stat value | display | 1.6-2rem | 400 | line-height: 1 |
| Stat label | mono | 0.55rem | 400 | uppercase, letter-spacing: 0.05em |

---

## 2. Cores

### Paleta principal

| Token | Hex | Uso |
|-------|-----|-----|
| `--gray-900` | `#1a1a1e` | Fundo capa, fundo closing, headers de tabela, phase headers |
| `--gray-700` | `#3a3a3f` | Texto secundário forte |
| `--gray-500` | `#6b6b72` | Texto secundário, labels, intros |
| `--gray-300` | `#b0b0b6` | Footer, page numbers |
| `--gray-100` | `#ececee` | Bordas, separadores, backgrounds sutis |
| `--bg` | `#fafaf9` | Background alternado de tabelas |
| `--white` | `#ffffff` | Background principal |
| `--black` | `#111111` | Texto máximo contraste (raramente usado) |
| `--red` | `#ED3237` | Acento principal — badges, milestones, itálicos, stats |
| `--red-light` | `#fef2f2` | Background de milestone boxes, risk-high |
| `--red-soft` | `rgba(237,50,55,0.08)` | Background sutil vermelho |
| `--blue` | `#2B435B` | Training boxes, elementos informativos |
| `--blue-light` | `#f0f4f8` | Background de training boxes |
| `--green` | `#38a169` | Note boxes, risk-low |
| `--green-light` | `#f0fff4` | Background de note boxes |

### Cores derivadas (opacidades)

| Contexto | Valor | Uso |
|----------|-------|-----|
| Cover text muted | `rgba(255,255,255,0.5)` | Subtítulo da capa |
| Cover labels | `rgba(255,255,255,0.35)` | Author, date, stat labels |
| Cover border | `rgba(255,255,255,0.1)` | Separador stats |
| Cover footer | `rgba(255,255,255,0.2)` | Footer na capa |
| Red border subtle | `rgba(237,50,55,0.15)` | Borda milestone box |

---

## 3. Layout de Página (Slide System)

### Configuração base

```css
@page { size: A4; margin: 0 }

.slide {
  width: 210mm;
  min-height: 297mm;
  padding: 50px 60px;
  page-break-after: always;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.slide:last-child { page-break-after: auto }
```

### Footer automático (pseudo-element)

Cada slide tem um footer via `::after`:
```css
.slide::after {
  content: 'SPXIA — Nome do Documento';
  position: absolute; bottom: 28px; left: 60px;
  font-family: var(--font-mono); font-size: 0.55rem;
  color: var(--gray-300); letter-spacing: 0.08em;
}
```

### Numeração de página

```css
.slide-num {
  position: absolute; bottom: 28px; right: 60px;
  font-family: var(--font-mono); font-size: 0.55rem;
  color: var(--gray-300);
}
```

### Spacer (empurra conteúdo para distribuir verticalmente)

```css
.spacer { flex: 1 }
```

---

## 4. Componentes

### 4.1 Cover (Capa)

- Background: `--gray-900`
- Layout: `justify-content: center; align-items: flex-start` (left-aligned)
- Padding: `60px 70px`
- Footer muda para branco com 20% opacidade

**Estrutura:**
```
┌─────────────────────────────────┐
│ [Logo SVG]                      │
│                                 │
│ ── Label (mono, red, uppercase) │
│ Título Grande                   │
│ com Itálico Vermelho            │
│ Subtítulo (white 50%)           │
│                                 │
│ ─────── separador ──────────    │
│ Stat1   Stat2   Stat3   Stat4   │
│                                 │
│ Author              Date       │
└─────────────────────────────────┘
```

### 4.2 Slide Header (Header de conteúdo)

Badge vermelho com número + label uppercase:

```css
.slide-header {
  display: flex; align-items: center; gap: 12px;
  margin-bottom: 28px; padding-bottom: 14px;
  border-bottom: 1.5px solid var(--gray-100);
}
.slide-header-num {
  /* Badge vermelho */
  color: white; background: var(--red);
  width: 28px; height: 28px; border-radius: 6px;
  font-family: var(--font-mono); font-size: 0.6rem; font-weight: 700;
}
.slide-header-text {
  font-family: var(--font-mono); font-size: 0.65rem;
  color: var(--gray-500); text-transform: uppercase;
}
```

### 4.3 Título de Slide (h2)

- Font: DM Serif Display
- Padrão: texto normal + `<em>` em itálico vermelho
- Exemplo: `Três frentes <em>estratégicas</em>`

### 4.4 Phase Header (Cabeçalho de fase)

```css
.phase-header {
  background: var(--gray-900); color: white;
  padding: 12px 18px;
  border-left: 4px solid var(--red);
  border-radius: 0 6px 6px 0;
}
/* h3 dentro: DM Serif Display, 1.05rem */
/* .dates: mono, 0.58rem, white 45% */
```

### 4.5 Phase Block (evita quebra de página)

```css
.phase-block {
  page-break-inside: avoid;
  margin-bottom: 16px;
}
```

Envolve: phase-header + table + milestone + training em um único bloco.

### 4.6 Tabelas

```css
th {
  background: var(--gray-900); color: white;
  font-family: var(--font-mono); font-size: 0.62rem;
  text-transform: uppercase; letter-spacing: 0.05em;
  padding: 7px 10px;
}
td {
  padding: 6px 10px;
  border-bottom: 1px solid var(--gray-100);
}
tr:nth-child(even) td { background: var(--bg) }
```

### 4.7 Milestone Box

```css
.milestone-box {
  background: var(--red-light);
  border: 1.5px solid rgba(237,50,55,0.15);
  border-radius: 6px; padding: 8px 14px;
  font-size: 0.72rem; font-weight: 600; color: var(--red);
  display: flex; align-items: center; gap: 8px;
}
.milestone-box::before {
  content: ''; width: 8px; height: 8px;
  border-radius: 50%; background: var(--red);
}
```

### 4.8 Training Box

```css
.training-box {
  background: var(--blue-light);
  border-left: 3px solid var(--blue);
  border-radius: 0 6px 6px 0;
  padding: 7px 14px;
  font-size: 0.68rem; color: var(--blue);
}
```

### 4.9 Note Box

```css
.note-box {
  background: var(--green-light);
  border-left: 3px solid var(--green);
  border-radius: 0 6px 6px 0;
  padding: 7px 14px;
  font-size: 0.72rem; color: #276749;
}
```

### 4.10 Stat Cards

```css
.stat-card {
  padding: 18px 16px; border-radius: 10px; text-align: center;
  border: 1px solid var(--gray-100);
}
.stat-card-dark {
  background: var(--gray-900); color: white;
}
.stat-val {
  font-family: var(--font-display); font-size: 1.6rem;
  color: var(--red);
}
.stat-lbl {
  font-family: var(--font-mono); font-size: 0.55rem;
  text-transform: uppercase; letter-spacing: 0.05em;
}
```

### 4.11 Risk Badges

```css
.risk-high { background: var(--red-light); color: var(--red); }
.risk-med  { background: #fffbeb; color: #b45309; }
.risk-low  { background: var(--green-light); color: var(--green); }
/* Todos: inline-block, padding: 1px 8px, border-radius: 4px, font-size: 0.62rem */
```

### 4.12 Timeline Box (ASCII art)

```css
.timeline-box {
  background: var(--gray-900);
  color: rgba(255,255,255,0.7);
  font-family: var(--font-mono); font-size: 0.52rem;
  padding: 16px 20px; border-radius: 8px;
  white-space: pre; line-height: 1.7;
}
```

### 4.13 Closing Slide (Encerramento)

```css
.closing {
  background: var(--gray-900); color: white;
  justify-content: center; align-items: center; text-align: center;
}
/* h2: DM Serif Display, 2.4rem, em vermelho */
/* p: 0.9rem, white 40% */
/* Logo SVG com opacity: 0.4, height: 28px */
/* Contato: mono, 0.65rem, white 25% */
```

---

## 5. Grids

```css
.grid-2 { display: grid; grid-template-columns: repeat(2,1fr); gap: 14px }
.grid-3 { display: grid; grid-template-columns: repeat(3,1fr); gap: 12px }
.grid-4 { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px }
```

---

## 6. Logo SVG Inline

O logo SPXIA é sempre inline SVG (não referência externa) para garantir renderização no PDF.

```html
<svg viewBox="0 0 1535.46 468.14" xmlns="http://www.w3.org/2000/svg"
     style="height:36px;shape-rendering:geometricPrecision">
  <!-- Classes: .cl0 = #FEFEFE (branco), .cl1 = #ED3237 (vermelho) -->
  <!-- Na capa e closing: fundo escuro, logo branco+vermelho -->
</svg>
```

**Tamanhos:**
- Capa: `height: 36px`
- Closing: `height: 28px`, `opacity: 0.4`

---

## 7. Geração do PDF

### Script (Playwright)

```javascript
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const htmlPath = path.resolve(__dirname, 'documento.html');
  await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle' });
  await page.pdf({
    path: 'Documento.pdf',
    format: 'A4',
    margin: { top: '0', bottom: '0', left: '0', right: '0' },
    printBackground: true,
    displayHeaderFooter: false,
  });
  await browser.close();
})();
```

**Importante:** Margem zero no Playwright porque o padding é controlado pelo CSS do `.slide`.

---

## 8. Padrões de Conteúdo

### Títulos de slide
Sempre usar DM Serif Display com uma palavra em `<em>` (itálico vermelho):
- "Três frentes **estratégicas**"
- "SDR Passivo e **Follow-up**"
- "Métricas e **metas**"

### Hierarquia por slide
```
[Slide Header: badge + label]
[h2: título com em]
[slide-intro: subtítulo cinza] (opcional)
[conteúdo: tabelas, cards, phase blocks]
[spacer]
[slide-num]
```

### Agrupamento de fases
- 2 fases por slide (máximo) para evitar corte
- Cada fase em `.phase-block` com `page-break-inside: avoid`
- Phase header + table + milestone + training = 1 bloco

---

## 9. Checklist para Novo Documento

- [ ] Google Fonts importado (DM Serif Display, Outfit, JetBrains Mono)
- [ ] CSS variables definidas (cores, fontes)
- [ ] Slide system com `@page { size: A4; margin: 0 }`
- [ ] Logo SVG inline (não img externa)
- [ ] Cover com fundo escuro, left-aligned
- [ ] Footer `::after` com nome do documento
- [ ] Numeração de página com `.slide-num`
- [ ] Títulos com `<em>` vermelho
- [ ] Slide headers com badge vermelho numerado
- [ ] Tabelas com th escuro e zebra striping
- [ ] Phase blocks com `page-break-inside: avoid`
- [ ] Closing slide com fundo escuro
- [ ] PDF gerado com margin: 0 no Playwright
