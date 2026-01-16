# ⚛️ ProjectIQ Frontend Documentation

## 📖 Overview

ProjectIQ is a React 19 web application designed to evaluate software projects using Artificial Intelligence. This repository contains the client-side logic, handling user input, file uploads, and real-time result polling.

This documentation is structured to allow backend developers to integrate with the frontend without needing to inspect the React source code.

---

## 🛠 Technical Specifications

Based on `package.json` configuration:

| Category | Technology | Version | Description |
|----------|------------|---------|-------------|
| **Core** | React | ^19.2.0 | Latest React with concurrent features. |
| **Build Tool** | Vite | ^7.2.4 | Ultra-fast build and HMR. |
| **Routing** | React Router | ^7.12.0 | Client-side routing management. |
| **Styling** | Tailwind CSS | ^4.1.18 | Utility-first CSS framework. |
| **Linting** | ESLint | ^9.39.1 | Code quality and standard enforcement. |

---

## 🗺️ Routing Architecture

The application utilizes `react-router-dom` for navigation. The routing logic is centralized in `src/router.jsx`.

| Route | Component Target | Purpose | State/Status |
|-------|------------------|---------|--------------|
| `/` | `Landing.jsx` | Main entry point / Hero section. | **Active** |
| `/evaluate` | `Evaluate.jsx` | The core submission form interface. | **Active** |
| `/verify` | `Verify.jsx` | Result polling and display page. | **Active** (Requires `?job_id=` param) |
| `/features` | `Landing.jsx` | Features showcase. | ⚠️ **WIP / Empty** (Redirects to Home) |
| `/contact` | `Landing.jsx` | Contact information. | ⚠️ **WIP / Empty** (Redirects to Home) |

---

## 🔌 API Integration Contracts

**CRITICAL FOR BACKEND:** The frontend communicates with `http://localhost:8000`. Below are the strict data contracts for the two primary endpoints.

### 1. Project Submission Endpoint

**Trigger:** User clicks "Submit Project" in `Form.jsx`.

- **Method:** `POST`
- **URL:** `http://localhost:8000/submit`
- **Content-Type:** `multipart/form-data`

#### Request Payload (FormData)

The form supports two modes: **ZIP Upload** or **Git Repository**. The payload changes slightly based on the mode.

| Key | Type | Required? | Description / Logic |
|-----|------|-----------|---------------------|
| `project_type` | String | **Yes** | Selected category (e.g., `frontend`, `backend`, `fullstack`, `python`). |
| `description` | String | **Yes** | **Concat Logic:** The frontend combines fields into: `"{ProjectName} - {TechStack} - {UserDescription}"` |
| `single_zip` | File | **Conditional** | Sent only if user selects "Upload Archive". Contains the `.zip` file. |
| `git_url` | String | **Conditional** | Sent only if user selects "Git Repository". Contains the HTTP(S) URL. |

#### Expected Response (JSON)

The frontend listens for a `job_id` to transition the user to the verification phase.
```json
{
  "job_id": "unique-uuid-string"
}
```

- **On Success:** Frontend redirects browser to `/verify?job_id={job_id}`.
- **On Failure:** Frontend alerts "Submission failed."

---

### 2. Result Polling Endpoint

**Trigger:** Component mount in `Verify.jsx`.

- **Method:** `GET`
- **URL:** `http://localhost:8000/result/{jobId}`
- **Polling Interval:** Every **3,000ms** (3 seconds).

#### Polling Logic

The frontend logic relies on the `status` key in your JSON response.

| State | Backend Response | Frontend Action |
|-------|------------------|-----------------|
| **Processing** | `{ "status": "processing" }` | Ignores payload, waits 3 seconds, retries. |
| **Completed** | `{ "status": "completed", ...any_other_data }` | Stops the polling interval immediately and renders the full JSON response into a preformatted block. |

---

## 📂 File & Component Breakdown

### `src/components/Form/Form.jsx`

This is the most logic-heavy component.

- **State Management:** Handles `projectName`, `category`, `techStack` (array), and toggle between zip and repo modes.
- **Validation:**
  - Prevents submission if category is default.
  - Prevents submission if `techStack` is empty.
  - Validates `.zip` extension for file uploads.
  - Validates URL string format for repo submissions.
- **Visuals:** Includes a drag-and-drop zone with drag-state animations.

### `src/pages/Verify.jsx`

- **Dependency:** Strictly requires `job_id` in the URL query parameters.
- **Display:** Currently renders raw JSON via `JSON.stringify(result, null, 2)`.
- **UX:** Shows a simple "Processing..." text while the poller is active.

### `src/components/Navbar/Navbar.jsx`

- **Structure:** Responsive navigation bar.
- **Links:** Contains hardcoded links to `/features`, `/evaluate`, `/verify`, and `/contact`.
- **Mobile:** Wraps links in a hamburger menu for small screens.

### `src/components/Footer/Footer.jsx`

- **Content:** Static links for "Product", "Company", and "Legal" (currently dead links `#`).
- **Dynamic:** Copyright year is generated dynamically using `new Date().getFullYear()`.

### `src/pages/Landing.jsx`

- **Layout:** Wraps the `Navbar`, a hero image (GIF), and `Footer`.
- **Usage:** Currently serves as the fallback for empty routes (Features/Contact).

---

## 🚀 Setup & Development

To run this frontend locally while developing the backend:

### Install Dependencies:
```bash
npm install
```

### Start Development Server:
```bash
npm run dev
```

**Access the app at:** `http://localhost:5173`

**Ensure your backend is running on `http://localhost:8000`** to satisfy CORS/API requests.

### Build for Production:
```bash
npm run build
```

**Output directory:** `dist/`

---

## 📁 Project Structure
```
frontend/
├── dist/                    # Production build output
├── node_modules/            # Dependencies
├── public/                  # Static assets
│   └── panda.svg           # Logo/icon
├── src/
│   ├── assets/             # Images, fonts, etc.
│   ├── components/         # Reusable components
│   │   ├── Footer/
│   │   │   └── Footer.jsx
│   │   ├── Form/
│   │   │   └── Form.jsx
│   │   └── Navbar/
│   │       └── Navbar.jsx
│   ├── pages/              # Route-specific pages
│   │   ├── Contact.jsx
│   │   ├── Evaluate.jsx
│   │   ├── Features.jsx
│   │   ├── Landing.jsx
│   │   └── Verify.jsx
│   ├── App.css             # Global styles
│   ├── App.jsx             # Root component
│   ├── index.css           # Tailwind imports
│   ├── main.jsx            # App entry point
│   └── router.jsx          # Routing configuration
├── .gitignore
├── eslint.config.js
├── index.html              # HTML template
├── package-lock.json
├── package.json
└── README.md               # This file
```

---

## 🎯 Key Features

- **Dual Input Modes:** Support for both ZIP file uploads and Git repository URLs
- **Real-time Validation:** Client-side validation for all form inputs
- **Polling Mechanism:** Automatic result checking every 3 seconds
- **Responsive Design:** Mobile-first approach with Tailwind CSS
- **Modern React:** Utilizes React 19 features and patterns

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory (if needed for future configuration):
```env
VITE_API_BASE_URL=http://localhost:8000
```

### Backend Requirements

The backend must provide:

1. **POST `/submit`** - Accept multipart form data and return a job ID
2. **GET `/result/{jobId}`** - Return job status and results

---

## 📝 Notes for Backend Developers

- The frontend expects **immediate** job ID assignment upon submission
- Polling continues indefinitely until `status: "completed"` is received
- No authentication is currently implemented
- CORS must be configured to allow requests from `http://localhost:5173`
- All API responses should be valid JSON

---

## 🐛 Known Issues / TODO

- [ ] Features page content is not implemented
- [ ] Contact page content is not implemented
- [ ] Error handling needs improvement
- [ ] Loading states could be more sophisticated
- [ ] Result display is currently raw JSON (needs UI enhancement)

---

## 📄 License

[Add your license information here]

## 👥 Contributors

[Add contributor information here]