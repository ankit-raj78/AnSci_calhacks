# Survey Analysis Platform

A web-based platform that enables users to upload survey designs and data files, ask natural language questions, and receive AI-powered analysis with a human-in-the-loop approval system.

## Features

- **User Workspaces**: Create and manage multiple workspaces for different survey projects
- **Document Upload**: Drag-and-drop interface for uploading survey designs and data files
- **AI-Powered Analysis**: Submit natural language queries and receive generated analysis plans and code
- **Human-in-the-Loop**: Review and approve AI-generated analysis before execution
- **Safe Code Execution**: Sandboxed execution environment for running approved analysis code
- **Plan Refinement**: Provide feedback to refine analysis plans if they don't meet requirements

## Architecture

```
survey-analysis-platform/
├── backend/                 # Flask backend
│   ├── app.py              # Main Flask application
│   ├── llm_integration.py  # LLM integration for plan/code generation
│   ├── code_executor.py    # Safe code execution module
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.js         # Main App component
│   │   └── index.js       # Entry point
│   └── package.json       # Node dependencies
└── README.md
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   - Create a `.env` file in the backend directory
   - Add your OpenAI API key: `OPENAI_API_KEY=your_key_here`

6. Run the Flask server:
   ```bash
   python app.py
   ```

The backend will start on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The frontend will start on `http://localhost:3000`

## Usage

1. **Create a Workspace**: Click "Create New Workspace" and give it a name

2. **Upload Documents**: 
   - Navigate to your workspace
   - Use the drag-and-drop area to upload survey files
   - Files with "design" in the name are marked as survey designs
   - Other files are marked as data files

3. **Submit a Query**:
   - Go to the "Analysis" tab
   - Enter your question (e.g., "Analyze satisfaction scores by age group")
   - Click "Submit Query"

4. **Review and Approve**:
   - Review the generated analysis plan and code
   - Click "Approve & Execute" to run the analysis
   - Or click "Reject & Refine" to provide feedback

5. **View Results**:
   - After execution, view the output and any generated visualizations
   - Files created during analysis are saved in the workspace directory

## API Endpoints

### Workspaces
- `GET /api/workspaces` - List all workspaces
- `POST /api/workspaces` - Create a new workspace

### Documents
- `POST /api/workspaces/<id>/upload` - Upload a document
- `GET /api/workspaces/<id>/documents` - List documents in workspace

### Queries
- `POST /api/workspaces/<id>/query` - Submit a new query
- `POST /api/queries/<id>/approve` - Approve or reject a query
- `POST /api/queries/<id>/refine` - Refine a query with feedback

## Security Considerations

- Code validation checks for dangerous operations before execution
- Code runs in a subprocess with timeout protection
- File uploads are restricted by size and type
- Generated code is sandboxed with limited file system access

## Technologies Used

- **Backend**: Flask, SQLAlchemy, OpenAI API
- **Frontend**: React, Axios, React Dropzone
- **Database**: SQLite (default)
- **Analysis Libraries**: Pandas, Matplotlib, Seaborn

## Future Enhancements

- User authentication and authorization
- Real-time collaboration features
- Export analysis results in various formats
- Integration with more data sources
- Advanced visualization options
- Query history and versioning
