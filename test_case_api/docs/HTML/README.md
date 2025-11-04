# Test Case Generator API - HTML Documentation

Modern, interactive documentation for the Test Case Generator API workspace.

## 📁 Structure

```
HTML/
├── index.html           # Main documentation hub
├── pages/
│   ├── architecture.html    # System design and flow
│   ├── api-guide.html      # REST endpoint reference
│   ├── client-guide.html   # Python SDK guide
│   ├── operations.html     # Operational playbook
│   └── resources.html      # Supporting artifacts
└── assets/
    ├── css/
    │   └── styles.css  # Enhanced styling with syntax highlighting
    ├── js/
    │   └── script.js   # Interactive features and highlighting
    └── images/         # Future image assets
```

## 🎨 Features

### Design System
- **Modern Typography**: Inter font family with JetBrains Mono for code
- **Enhanced Color Palette**: Refined light/dark theme with semantic colors
- **Improved Spacing**: Consistent spacing scale and border radius system
- **Advanced Shadows**: Layered shadow system for depth

### Interactive Elements
- **Theme Toggle**: Light/dark mode with persistent preferences
- **Smart Navigation**: Active page highlighting with smooth transitions
- **Code Copying**: Click any code block to copy to clipboard
- **Smooth Scrolling**: Enhanced navigation experience
- **Responsive Design**: Mobile-first responsive layout

### Visual Enhancements
- **Mermaid Diagrams**: Interactive flowcharts and sequence diagrams
- **Hover Effects**: Subtle animations and state changes
- **Loading States**: Visual feedback for dynamic content
- **Sticky Navigation**: Always-accessible navigation bar

## 🚀 Usage

### Local Development
1. Open `index.html` in a modern browser
2. Navigate between pages using the top navigation
3. Toggle themes using the theme switcher
4. Copy code examples by clicking on them

### Deployment Options
- **GitHub Pages**: Push to `gh-pages` branch
- **Netlify**: Drag and drop the HTML folder
- **Vercel**: Deploy from repository
- **Static Hosting**: Upload to any web server

## 🎯 Content Overview

### Index (index.html)
- Project introduction and quick start
- Feature highlights with card grid
- Platform architecture diagram
- Guided reading path with timeline

### Architecture (architecture.html)
- Module breakdown and responsibilities
- Request/response flow diagrams
- Function reference table
- Configuration sources

### API Guide (api-guide.html)
- Complete endpoint matrix
- Request/response schemas
- Batch processing patterns
- File upload specifications

### Client SDK (client-guide.html)
- Python client installation
- Usage examples and patterns
- Generation pipeline flowchart
- Saving strategies

### Operations (operations.html)
- Streaming workflow guide
- Health monitoring patterns
- Troubleshooting playbook
- Operational checklists

### Resources (resources.html)
- Links to Markdown sources
- Sample file descriptions
- Supporting script references
- Workspace metadata

## 🛠 Customization

### Styling
Edit `assets/css/styles.css` to customize:
- Color schemes in CSS custom properties
- Typography and spacing scales
- Component-specific styles
- Responsive breakpoints

### Functionality
Modify `assets/js/script.js` to add:
- Custom interactions
- Enhanced navigation
- Additional utilities
- Analytics integration

## 📱 Browser Support

- **Chrome/Edge**: Full support including backdrop filters
- **Firefox**: Full support with graceful fallbacks
- **Safari**: Full support on macOS and iOS
- **Mobile**: Responsive design tested on all major devices

## 🔗 Integration

This documentation integrates seamlessly with:
- Existing Markdown documentation in `docs/`
- Sample files in `samples/`
- Source code in the workspace root
- CI/CD pipelines for automated updates

## 🎨 Design Tokens

The design system uses semantic design tokens:

```css
/* Colors */
--color-primary: #3b82f6;      /* Interactive elements */
--color-accent: #06b6d4;       /* Highlights and accents */
--color-success: #10b981;      /* Success states */
--color-warning: #f59e0b;      /* Warning states */
--color-error: #ef4444;        /* Error states */

/* Spacing */
--radius-sm: 8px;              /* Small components */
--radius-md: 12px;             /* Medium components */
--radius-lg: 16px;             /* Large components */
--radius-xl: 20px;             /* Extra large components */

/* Shadows */
--shadow-soft: ...;            /* Subtle elevation */
--shadow-medium: ...;          /* Standard elevation */
--shadow-large: ...;           /* Prominent elevation */
```

## 📈 Performance

- **Optimized Assets**: Minimal CSS/JS footprint
- **CDN Resources**: Mermaid and fonts loaded from CDN
- **Lazy Loading**: Diagrams render on demand
- **Caching**: Persistent theme preferences

## 🔄 Maintenance

To keep documentation current:
1. Update content when API changes
2. Sync examples with source code
3. Test responsive design on new devices
4. Monitor browser compatibility

---

Created with attention to modern web standards and user experience.