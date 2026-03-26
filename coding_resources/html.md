# HTML Quick Reference

## Basic Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Title</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>Hello World</h1>
    <script src="script.js"></script>
</body>
</html>
```

## Common Elements
```html
<!-- Text -->
<h1>Heading 1</h1> to <h6>Heading 6</h6>
<p>Paragraph text</p>
<span>Inline text</span>
<div>Block container</div>
<br> <!-- Line break -->
<hr> <!-- Horizontal rule -->

<!-- Links -->
<a href="https://example.com">Link text</a>
<a href="page.html" target="_blank">New tab</a>

<!-- Images -->
<img src="image.jpg" alt="Description" width="200">

<!-- Lists -->
<ul>
    <li>Item 1</li>
    <li>Item 2</li>
</ul>

<ol>
    <li>First</li>
    <li>Second</li>
</ol>

<!-- Tables -->
<table>
    <thead>
        <tr><th>Header</th></tr>
    </thead>
    <tbody>
        <tr><td>Data</td></tr>
    </tbody>
</table>
```

## Forms
```html
<form action="/submit" method="POST">
    <label for="name">Name:</label>
    <input type="text" id="name" name="name" required>
    
    <label for="email">Email:</label>
    <input type="email" id="email" name="email">
    
    <select name="option">
        <option value="1">Option 1</option>
        <option value="2">Option 2</option>
    </select>
    
    <textarea name="message" rows="4"></textarea>
    
    <button type="submit">Submit</button>
    <button type="reset">Reset</button>
</form>
```

## Semantic HTML5
```html
<header>Site header</header>
<nav>Navigation menu</nav>
<main>
    <article>
        <section>Content section</section>
    </article>
    <aside>Sidebar content</aside>
</main>
<footer>Site footer</footer>
```