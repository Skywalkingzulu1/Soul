# CSS Quick Reference

## Selectors
```css
/* Element */
p { color: blue; }

/* Class */
.highlight { background: yellow; }

/* ID */
#header { height: 100px; }

/* Attribute */
[type="text"] { border: 1px solid gray; }

/* Pseudo-classes */
a:hover { color: red; }
p:first-child { font-weight: bold; }
li:nth-child(2n) { background: #eee; }

/* Pseudo-elements */
p::before { content: "→ "; }
p::first-letter { font-size: 2em; }
```

## Box Model
```css
.box {
    margin: 10px;      /* Outside space */
    padding: 20px;     /* Inside space */
    border: 1px solid black;
    width: 200px;
    box-sizing: border-box; /* Include padding/border in width */
}
```

## Flexbox
```css
.container {
    display: flex;
    flex-direction: row;         /* row, column */
    justify-content: center;    /* start, end, center, space-between */
    align-items: center;        /* stretch, center, start, end */
    gap: 20px;
}
```

## Grid
```css
.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: auto;
    gap: 10px;
}

.item {
    grid-column: span 2;  /* Span 2 columns */
}
```

## Animations
```css
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.animate {
    animation: fadeIn 1s ease-in-out;
    transition: transform 0.3s;
}

.hover:hover {
    transform: scale(1.1);
}
```

## Responsive
```css
/* Media Queries */
@media (max-width: 768px) {
    .column { width: 100%; }
}

@media (min-width: 1024px) {
    .container { max-width: 1200px; }
}

/* Mobile-first */
.mobile-first { width: 100%; }
@media (min-width: 768px) {
    .mobile-first { width: 50%; }
}
```