# EUV Detection & Laser Communication - Frontend

TypeScript/React frontend for the EUV Detection & Laser Communication Device.

## Prerequisites

- Node.js 18+ and npm
- Backend API server running on `http://localhost:8000`

## Installation

```bash
npm install
```

## Development

Start the development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000` and will proxy API requests to the backend.

## Building for Production

Build the frontend:

```bash
npm run build
```

The built files will be in the `dist` directory. The backend server can serve these files directly.

## Project Structure

```
frontend/
├── src/
│   ├── components/      # React components
│   │   ├── Sidebar.tsx
│   │   ├── WavelengthMeasurement.tsx
│   │   └── LaserControl.tsx
│   ├── api.ts           # API client
│   ├── App.tsx          # Main app component
│   └── main.tsx         # Entry point
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Technologies

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Plotly.js** - Charts and graphs
- **FastAPI** (backend) - REST API

