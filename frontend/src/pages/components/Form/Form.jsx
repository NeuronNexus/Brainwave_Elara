import React, { useState, useRef } from 'react';
import { 
  Upload, 
  CheckCircle, 
  ChevronDown, 
  Shield, 
  GitBranch, 
  Code2, 
  X 
} from 'lucide-react';

const TECH_OPTIONS = [
  "React", "Vue.js", "Angular", "Next.js", "TypeScript",
  "Node.js", "Express", "Python", "Django", "Flask",
  "FastAPI", "Java", "Spring Boot", "Go", "Rust",
  "Docker", "Kubernetes", "AWS", "Firebase", "PostgreSQL"
];

const PROJECT_TYPES = [
  { value: 'frontend', label: 'Frontend Application' },
  { value: 'backend', label: 'Backend Service' },
  { value: 'fullstack', label: 'Full Stack Project' },
  { value: 'python', label: 'Python Automation / Script' }
];

export default function Form() {
  const [formData, setFormData] = useState({ 
    projectName: '', 
    category: 'default', 
    techStack: [],
    submissionType: 'zip', // 'zip' or 'repo'
    repoUrl: '',
    file: null 
  });
  
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = (e, status) => {
    e.preventDefault();
    setIsDragging(status);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) validateFile(file);
  };

  const validateFile = (file) => {
    if (file.name.endsWith('.zip') || file.type.includes('zip') || file.type.includes('compressed')) {
      setFormData(prev => ({ ...prev, file }));
    } else {
      alert("Please upload a .zip file");
    }
  };

  const toggleTech = (tech) => {
    setFormData(prev => {
      const exists = prev.techStack.includes(tech);
      return {
        ...prev,
        techStack: exists 
          ? prev.techStack.filter(t => t !== tech)
          : [...prev.techStack, tech]
      };
    });
  };

  // ONLY THIS FUNCTION IS CHANGED
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.category === 'default') {
      return alert("Please select a project type.");
    }
    if (formData.techStack.length === 0) {
      return alert("Please select at least one technology.");
    }

    if (formData.submissionType === 'zip') {
      if (!formData.file) return alert("Please upload a zip file.");
    } else {
      if (!formData.repoUrl || !formData.repoUrl.startsWith('http')) {
        return alert("Please enter a valid Git repository URL.");
      }
    }

    const data = new FormData();
    data.append("project_type", formData.category);
    data.append(
      "description",
      `${formData.projectName} | Tech: ${formData.techStack.join(", ")}`
    );

    if (formData.submissionType === 'zip') {
      data.append("single_zip", formData.file);
    } else {
      data.append("git_url", formData.repoUrl);
    }

    try {
      const res = await fetch("http://localhost:8000/submit", {
        method: "POST",
        body: data
      });

      const json = await res.json();
      if (!json.job_id) throw new Error("No job id returned");

      window.location.href = `/verify?job_id=${json.job_id}`;
    } catch (err) {
      console.error(err);
      alert("Submission failed.");
    }
  };

  const inputBaseClass = "block w-full bg-slate-900/50 border border-slate-600 rounded-lg py-3 px-4 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all";

  return (
    <div className="min-h-screen pt-24 pb-12 flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-950 relative">
      
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
        <div className="absolute top-20 left-10 w-72 h-72 bg-indigo-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>
      </div>

      <div className="w-full max-w-2xl z-10">
        <div className="text-center mb-10">
          <h1 className="text-4xl md:text-5xl font-extrabold text-white tracking-tight mb-4">
            Submit Your Work
          </h1>
          <p className="text-lg text-slate-400 max-w-xl mx-auto">
            Provide your project details and source code for review.
          </p>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700 rounded-2xl shadow-2xl p-8 md:p-10">
          <form onSubmit={handleSubmit} className="space-y-8">
            
            {/* Project Name */}
            <div className="space-y-2">
              <label htmlFor="projectName" className="block text-sm font-medium text-slate-300">Project Name</label>
              <input
                id="projectName"
                type="text"
                className={`${inputBaseClass} placeholder-slate-500`}
                placeholder="e.g. Mercury Dashboard v2"
                value={formData.projectName}
                onChange={(e) => setFormData({...formData, projectName: e.target.value})}
              />
            </div>

            {/* Category */}
            <div className="space-y-2">
              <label htmlFor="category" className="block text-sm font-medium text-slate-300">Project Category</label>
              <div className="relative">
                <select
                  id="category"
                  className={`${inputBaseClass} appearance-none`}
                  value={formData.category}
                  onChange={(e) => setFormData({...formData, category: e.target.value})}
                >
                  <option value="default" disabled>Select a project type...</option>
                  {PROJECT_TYPES.map(type => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
                <ChevronDown className="absolute right-4 top-3.5 h-5 w-5 text-slate-500 pointer-events-none" />
              </div>
            </div>

            {/* Tech Stack Multi-Select */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-slate-300">Technologies & Frameworks</label>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                {TECH_OPTIONS.map((tech) => {
                  const isSelected = formData.techStack.includes(tech);
                  return (
                    <button
                      key={tech}
                      type="button"
                      onClick={() => toggleTech(tech)}
                      className={`
                        text-xs font-medium py-2 px-2 rounded-md border transition-all duration-200
                        ${isSelected 
                          ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg shadow-indigo-500/25' 
                          : 'bg-slate-900/30 border-slate-700 text-slate-400 hover:border-slate-500 hover:text-slate-200'
                        }
                      `}
                    >
                      {tech}
                    </button>
                  );
                })}
              </div>
              <p className="text-xs text-slate-500 text-right pt-1">
                {formData.techStack.length} selected
              </p>
            </div>

            {/* Submission Type Toggle */}
            <div className="pt-2">
              <label className="block text-sm font-medium text-slate-300 mb-3">Submission Method</label>
              <div className="flex bg-slate-900/50 p-1 rounded-xl border border-slate-600 mb-6">
                <button
                  type="button"
                  onClick={() => setFormData(prev => ({ ...prev, submissionType: 'zip' }))}
                  className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2 ${
                    formData.submissionType === 'zip'
                      ? 'bg-slate-700 text-white shadow-sm'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <Upload className="h-4 w-4" />
                  Upload Archive
                </button>
                <button
                  type="button"
                  onClick={() => setFormData(prev => ({ ...prev, submissionType: 'repo' }))}
                  className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2 ${
                    formData.submissionType === 'repo'
                      ? 'bg-slate-700 text-white shadow-sm'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <GitBranch className="h-4 w-4" />
                  Git Repository
                </button>
              </div>

              {/* Conditional Content */}
              <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                {formData.submissionType === 'zip' ? (
                  <div
                    onClick={() => fileInputRef.current?.click()}
                    onDragOver={(e) => handleDrag(e, true)}
                    onDragLeave={(e) => handleDrag(e, false)}
                    onDrop={handleDrop}
                    className={`
                      relative border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-300 group
                      ${isDragging ? 'border-indigo-400 bg-indigo-500/10' : 'border-slate-600 hover:border-indigo-500/50 hover:bg-slate-700/30'}
                      ${formData.file ? 'bg-slate-900/80 border-solid border-green-500/50' : ''}
                    `}
                  >
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={(e) => e.target.files?.[0] && validateFile(e.target.files[0])}
                      accept=".zip,application/zip,application/x-zip-compressed"
                      className="hidden"
                    />

                    {formData.file ? (
                      <div className="animate-in fade-in zoom-in duration-300">
                        <div className="bg-green-500/20 p-4 rounded-full mb-3 mx-auto w-fit">
                          <CheckCircle className="h-8 w-8 text-green-400" />
                        </div>
                        <p className="text-white font-semibold text-lg">{formData.file.name}</p>
                        <p className="text-slate-400 text-sm mt-1">{(formData.file.size / (1024 * 1024)).toFixed(2)} MB • Ready to upload</p>
                        <div className="flex items-center justify-center gap-2 mt-4">
                           <span className="text-indigo-400 text-xs font-medium hover:underline">Click to replace</span>
                        </div>
                      </div>
                    ) : (
                      <>
                        <div className="bg-slate-700/50 p-4 rounded-full mb-4 group-hover:scale-110 transition-transform duration-300">
                          <Upload className={`h-8 w-8 ${isDragging ? 'text-indigo-400' : 'text-slate-400'}`} />
                        </div>
                        <p className="text-white font-medium text-lg mb-1">Click to upload or drag and drop</p>
                        <p className="text-slate-500 text-sm">ZIP files only (max. 500MB)</p>
                      </>
                    )}
                  </div>
                ) : (
                  <div className="space-y-2">
                    <label htmlFor="repoUrl" className="block text-sm font-medium text-slate-300">Repository URL</label>
                    <div className="relative group">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <GitBranch className="h-5 w-5 text-slate-500 group-focus-within:text-indigo-500 transition-colors" />
                      </div>
                      <input
                        id="repoUrl"
                        type="url"
                        className={`${inputBaseClass} pl-10`}
                        placeholder="https://github.com/username/project"
                        value={formData.repoUrl}
                        onChange={(e) => setFormData({...formData, repoUrl: e.target.value})}
                      />
                    </div>
                    <p className="text-xs text-slate-500 pl-1">
                      Supported: GitHub, GitLab, Bitbucket
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={formData.submissionType === 'zip' ? !formData.file : !formData.repoUrl}
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold py-4 px-8 rounded-lg shadow-lg shadow-indigo-500/20 transform transition-all hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Submit Project
            </button>

            {/* Footer */}
            <div className="flex items-center justify-center gap-2 text-slate-500 text-xs mt-4">
              <Shield className="h-3 w-3" />
              <span>Transfers are encrypted end-to-end via TLS 1.3</span>
            </div>

          </form>
        </div>
      </div>
    </div>
  );
}