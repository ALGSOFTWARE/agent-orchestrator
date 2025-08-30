# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---
project_area: "Logistics Intelligence Platform Frontend"
context_focus: "React-based chat interface for logistics operations"
status: "Active Development"
key_technologies:
  - "React 18"
  - "TypeScript"
  - "Vite"
  - "Tailwind CSS"
  - "shadcn/ui"
  - "React Router"
  - "TanStack React Query"
last_updated: "2025-08-30"
---

## Development Commands

### Core Development
```bash
# Install dependencies
npm install

# Start development server (runs on port 8080)
npm run dev

# Build for production
npm run build

# Build for development
npm run build:dev

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Project Architecture

### Technology Stack
- **Frontend Framework**: React 18 with TypeScript
- **Build Tool**: Vite with SWC plugin for fast compilation
- **Styling**: Tailwind CSS with custom design system
- **UI Components**: shadcn/ui component library built on Radix UI
- **Routing**: React Router v6 for SPA navigation
- **State Management**: TanStack React Query for server state
- **Development**: Lovable integration for AI-assisted development

### Directory Structure
```
src/
├── components/
│   ├── chat/          # Chat interface components
│   ├── layout/        # Layout components (AppLayout, Sidebar)
│   ├── system/        # System explanation components
│   └── ui/           # Reusable UI components (shadcn/ui)
├── pages/            # Route-based page components
├── hooks/            # Custom React hooks
└── lib/              # Utilities and configuration
```

### Key Components Architecture

**Chat System**:
- `ChatContainer`: Main chat interface orchestrator
- `ChatMessages`: Message display and history
- `ChatInput`: User input handling
- `MessageInterpreter`: Message parsing and interpretation
- `SmartMenu`: Context-aware action menu
- Document modals for logistics document viewing

**Layout System**:
- `AppLayout`: Main application shell with sidebar
- `Sidebar`: Navigation and branding
- All pages follow consistent layout patterns

**Document Types**:
The system handles logistics documents: CTE, AWL, BL, MANIFESTO, NF

### Routing Structure
- `/` - Landing page with system explanation and chat
- `/dashboard` - Main dashboard view
- `/jornadas` - Journey management
- `/entregas` - Delivery tracking
- `/documentos` - Document management
- `/relatorios` - Reporting interface
- `/configuracoes` - Settings
- `/clientes` - Client management
- `/login` & `/cadastro` - Authentication flows

### Design System

**Brand Colors**:
- Custom brand palette with dark, primary, and light variants
- Sidebar-specific color scheme
- Status colors for success, warning, and info states

**Styling Approach**:
- Utility-first with Tailwind CSS
- CSS custom properties for theming
- Responsive design patterns
- Dark mode support via CSS custom properties

### State Management Patterns

**Server State**: TanStack React Query for API interactions
**Component State**: React hooks (useState, useEffect)
**Toast Notifications**: Sonner for user feedback

### Development Guidelines

**Component Patterns**:
- Function components with TypeScript interfaces
- Custom hooks for reusable logic
- Prop drilling minimized through context when needed

**Styling Conventions**:
- Use Tailwind utility classes
- Leverage shadcn/ui components for consistency
- Custom CSS properties for theme values
- Responsive-first approach

**File Organization**:
- Components grouped by feature/domain
- Shared UI components in `/ui` directory
- Page components map to routes
- Custom hooks in `/hooks` directory

### Integration Points

This frontend is designed to work with:
- **Gatekeeper API**: Main backend service for logistics data
- **AI Agents**: Chat integration with logistics intelligence
- **Document Processing**: File upload and processing capabilities

### Testing

Currently no dedicated testing framework is configured. When adding tests, consider:
- Component testing with React Testing Library
- Unit tests for utilities and hooks
- Integration tests for key user flows

### Build Configuration

**Vite Configuration**:
- React SWC plugin for fast builds
- Path aliases: `@/` maps to `src/`
- Development server on port 8080
- Lovable development integration

**TypeScript**:
- Strict mode disabled for rapid development
- Path mapping configured for clean imports
- Separate configs for app and node environments

**Linting**:
- ESLint with TypeScript support
- React hooks and refresh plugins
- Relaxed unused variable rules for development