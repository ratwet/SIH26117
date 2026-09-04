// src/markdown.js - Lightweight, fast, safe Markdown to HTML renderer for Aquanex

export function renderMarkdown(md) {
  if (!md) return '';

  let html = md;

  // Escape HTML entities to prevent XSS
  const escapeMap = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
  };
  
  // Extract and stash code blocks first
  const codeBlocks = [];
  html = html.replace(/```([a-zA-Z0-9_\-]+)?\n([\s\S]*?)```/g, (match, lang, code) => {
    const placeholder = `__CODE_BLOCK_${codeBlocks.length}__`;
    const escapedCode = code.replace(/[&<>]/g, tag => escapeMap[tag] || tag);
    codeBlocks.push(`
      <div class="code-block-wrapper">
        <div class="code-block-header">
          <span class="code-block-lang">${lang || 'code'}</span>
          <button class="btn-copy-code" onclick="navigator.clipboard.writeText(this.closest('.code-block-wrapper').querySelector('code').textContent)">Copy</button>
        </div>
        <pre><code class="language-${lang || 'plaintext'}">${escapedCode.trim()}</code></pre>
      </div>
    `);
    return placeholder;
  });

  // Extract inline code
  const inlineCodes = [];
  html = html.replace(/`([^`\n]+)`/g, (match, code) => {
    const placeholder = `__INLINE_CODE_${inlineCodes.length}__`;
    const escapedCode = code.replace(/[&<>]/g, tag => escapeMap[tag] || tag);
    inlineCodes.push(`<code class="inline-code">${escapedCode}</code>`);
    return placeholder;
  });

  // Headers
  html = html.replace(/^### (.*$)/gim, '<h3 class="md-h3">$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2 class="md-h2">$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1 class="md-h1">$1</h1>');

  // Blockquotes
  html = html.replace(/^\> (.*$)/gim, '<blockquote class="md-blockquote">$1</blockquote>');

  // Bold & Italic
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

  // Unordered lists
  html = html.replace(/^\s*[-*]\s+(.*$)/gim, '<li class="md-li">$1</li>');
  html = html.replace(/(<li class="md-li">.*<\/li>\n?)+/gim, '<ul class="md-ul">$&</ul>');

  // Tables
  html = html.replace(/^\|(.+)\|$/gim, (match) => {
    const cells = match.split('|').filter((c, i, arr) => i > 0 && i < arr.length - 1);
    if (cells.every(c => /^[\s\-:]+$/.test(c))) {
      return ''; // Divider row
    }
    const isHeader = !match.includes('__TABLE_STARTED__');
    const cellTag = isHeader ? 'th' : 'td';
    const inner = cells.map(c => `<${cellTag}>${c.trim()}</${cellTag}>`).join('');
    return `<tr>${inner}</tr>`;
  });

  // Wrap table rows in <table>
  html = html.replace(/(<tr>.*<\/tr>\n?)+/gim, '<div class="md-table-wrap"><table class="md-table">$&</table></div>');

  // Paragraphs (double newlines)
  const paragraphs = html.split(/\n\n+/);
  html = paragraphs.map(p => {
    const trimmed = p.trim();
    if (!trimmed) return '';
    if (trimmed.startsWith('<h1') || trimmed.startsWith('<h2') || trimmed.startsWith('<h3') ||
        trimmed.startsWith('<ul') || trimmed.startsWith('<blockquote') || trimmed.startsWith('<div class="code-block-wrapper') ||
        trimmed.startsWith('<div class="md-table-wrap') || trimmed.startsWith('__CODE_BLOCK_')) {
      return trimmed;
    }
    return `<p class="md-p">${trimmed.replace(/\n/g, '<br/>')}</p>`;
  }).join('\n');

  // Restore code blocks
  codeBlocks.forEach((block, idx) => {
    html = html.replace(`__CODE_BLOCK_${idx}__`, block);
  });

  // Restore inline codes
  inlineCodes.forEach((code, idx) => {
    html = html.replace(`__INLINE_CODE_${idx}__`, code);
  });

  return html;
}
