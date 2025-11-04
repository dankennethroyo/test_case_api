// Enhanced interactions for Test Case API documentation pages

(function () {
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const savedTheme = localStorage.getItem('testcase-docs-theme');
  const root = document.documentElement;

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    localStorage.setItem('testcase-docs-theme', theme);
    if (window.mermaid && typeof window.mermaid.initialize === 'function') {
      const mermaidTheme = theme === 'dark' ? 'dark' : 'neutral';
      window.mermaid.initialize({ startOnLoad: true, theme: mermaidTheme });
      window.mermaid.init(undefined, document.querySelectorAll('.mermaid'));
    }
  }

  // Initial theme selection
  const initialTheme = savedTheme || (prefersDark ? 'dark' : 'light');
  applyTheme(initialTheme);

  const toggleButton = document.querySelector('[data-action="toggle-theme"]');
  if (toggleButton) {
    function updateToggleButton(theme) {
      const isDark = theme === 'dark';
      toggleButton.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          ${isDark ? 
            '<path d="M12 3v18m-9-9h18"/>' : 
            '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>'}
        </svg>
        ${isDark ? 'Light Mode' : 'Dark Mode'}
      `;
    }
    
    toggleButton.addEventListener('click', function () {
      const currentTheme = root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
      const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
      applyTheme(nextTheme);
      updateToggleButton(nextTheme);
    });
    
    const currentTheme = root.getAttribute('data-theme');
    updateToggleButton(currentTheme);
  }

  // Navigation highlighting
  document.addEventListener('DOMContentLoaded', function () {
    const currentPath = window.location.pathname.split('/').pop();
    document.querySelectorAll('a[data-nav]').forEach(function (link) {
      const href = link.getAttribute('href');
      if ((currentPath && href.endsWith(currentPath)) || (!currentPath && href.endsWith('index.html'))) {
        link.classList.add('active');
      }
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function (link) {
      link.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });

    // Initialize syntax highlighting
    initializeSyntaxHighlighting();
    
    // Copy code blocks on click
    document.querySelectorAll('pre code').forEach(function (block) {
      block.style.cursor = 'pointer';
      block.title = 'Click to copy';
      block.addEventListener('click', function () {
        navigator.clipboard.writeText(this.textContent).then(function () {
          const originalTitle = block.title;
          block.title = 'Copied!';
          setTimeout(() => block.title = originalTitle, 2000);
        });
      });
    });

    // Add loading animation for Mermaid diagrams
    document.querySelectorAll('.mermaid').forEach(function (diagram) {
      diagram.style.minHeight = '200px';
      diagram.style.display = 'flex';
      diagram.style.alignItems = 'center';
      diagram.style.justifyContent = 'center';
    });
  });

  // Syntax highlighting function
  function initializeSyntaxHighlighting() {
    document.querySelectorAll('pre code').forEach(function (block) {
      // Detect language from class name
      const className = block.className;
      let language = 'text';
      
      if (className.includes('language-')) {
        language = className.match(/language-(\w+)/)[1];
      } else if (className.includes('hljs')) {
        language = className.replace('hljs', '').trim() || 'text';
      }
      
      // Add language indicator
      const pre = block.parentElement;
      if (pre.tagName === 'PRE') {
        pre.setAttribute('data-lang', language);
      }
      
      // Apply basic syntax highlighting
      highlightCode(block, language);
    });
  }

  function highlightCode(block, language) {
    const code = block.textContent;
    let highlighted = code;

    // Basic highlighting patterns
    const patterns = {
      // Comments
      comment: {
        regex: /(\/\/.*$|\/\*[\s\S]*?\*\/|#.*$)/gm,
        class: 'hljs-comment'
      },
      // Strings
      string: {
        regex: /("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|`(?:[^`\\]|\\.)*`)/g,
        class: 'hljs-string'
      },
      // Numbers
      number: {
        regex: /\b\d+\.?\d*\b/g,
        class: 'hljs-number'
      },
      // Keywords (common across languages)
      keyword: {
        regex: /\b(function|class|if|else|for|while|return|import|export|const|let|var|def|async|await|try|catch|finally)\b/g,
        class: 'hljs-keyword'
      },
      // Operators
      operator: {
        regex: /[+\-*\/=<>!&|]+/g,
        class: 'hljs-operator'
      }
    };

    // Language-specific patterns
    if (language === 'json') {
      patterns.attr = {
        regex: /"([^"]+)":/g,
        class: 'hljs-attr'
      };
    }

    if (language === 'powershell') {
      patterns.variable = {
        regex: /\$\w+/g,
        class: 'hljs-variable'
      };
      patterns.cmdlet = {
        regex: /\b[A-Z][a-z]+-[A-Z][a-z]+/g,
        class: 'hljs-built_in'
      };
    }

    if (language === 'python') {
      patterns.builtin = {
        regex: /\b(print|len|str|int|float|list|dict|range|enumerate)\b/g,
        class: 'hljs-built_in'
      };
    }

    // Apply highlighting
    let tokenMap = [];
    let offset = 0;

    // First pass: collect all matches
    Object.keys(patterns).forEach(type => {
      const pattern = patterns[type];
      let match;
      pattern.regex.lastIndex = 0;
      
      while ((match = pattern.regex.exec(code)) !== null) {
        tokenMap.push({
          start: match.index,
          end: match.index + match[0].length,
          class: pattern.class,
          text: match[0]
        });
      }
    });

    // Sort by start position
    tokenMap.sort((a, b) => a.start - b.start);

    // Remove overlapping tokens (keep first one)
    const filteredTokens = [];
    tokenMap.forEach(token => {
      const overlapping = filteredTokens.some(existing => 
        token.start < existing.end && token.end > existing.start
      );
      if (!overlapping) {
        filteredTokens.push(token);
      }
    });

    // Apply highlighting
    if (filteredTokens.length > 0) {
      let result = '';
      let lastIndex = 0;

      filteredTokens.forEach(token => {
        // Add text before token
        result += escapeHtml(code.substring(lastIndex, token.start));
        // Add highlighted token
        result += `<span class="${token.class}">${escapeHtml(token.text)}</span>`;
        lastIndex = token.end;
      });

      // Add remaining text
      result += escapeHtml(code.substring(lastIndex));
      
      block.innerHTML = result;
    }
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
})();
