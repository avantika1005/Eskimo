const { useState, useEffect, useMemo } = React;

const API_BASE = "http://localhost:8000/api";

function App() {
  const [currentPage, setCurrentPage] = useState("login"); // login, dashboard, student
  const [selectedStudentId, setSelectedStudentId] = useState(null);

  // Initialize feather icons on mount and update
  useEffect(() => {
    if (window.feather) {
      window.feather.replace();
    }
  }, [currentPage, selectedStudentId]);

  if (currentPage === "login") {
    return <Login onLogin={() => setCurrentPage("dashboard")} />;
  }

  return (
    <div className="app-container">
      <header className="header-nav">
        <div className="brand">
          <i data-feather="shield"></i> Student Risk Dashboard
        </div>
        <div>
          <button className="btn btn-outline" style={{ marginRight: 8 }} onClick={() => setCurrentPage('dashboard')}>
            <i data-feather="grid"></i> Dashboard
          </button>
          <button className="btn btn-outline" onClick={() => setCurrentPage('login')}>
            <i data-feather="log-out"></i> Logout
          </button>
        </div>
      </header>

      <main className="view-container animate-fade-in">
        {currentPage === "dashboard" && (
          <Dashboard onSelectStudent={(id) => {
            setSelectedStudentId(id);
            setCurrentPage("student");
          }} />
        )}
        {currentPage === "student" && (
          <StudentDetail id={selectedStudentId} onBack={() => setCurrentPage("dashboard")} />
        )}
      </main>
    </div>
  );
}

// ================= LOGIN PAGE =================
function Login({ onLogin }) {
  return (
    <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center' }}>
      <div className="glass-panel animate-fade-in" style={{ padding: '48px', maxWidth: '420px', width: '100%', textAlign: 'center', position: 'relative' }}>
        <div style={{ position: 'absolute', top: '-30px', left: '50%', transform: 'translateX(-50%)', background: 'var(--surface-solid)', padding: '16px', borderRadius: '50%', border: '1px solid var(--border)', boxShadow: 'var(--shadow-md)', color: 'var(--primary)' }}>
          <i data-feather="shield" width="32" height="32"></i>
        </div>
        <h2 style={{ marginBottom: 8, marginTop: 24, fontSize: '1.75rem' }}>Student Risk Dashboard</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 32, fontSize: '0.9rem' }}>AI Early Warning System</p>
        <div className="input-group">
          <input type="text" className="input-field" placeholder="Email (admin@school.edu)" defaultValue="admin@school.edu" />
        </div>
        <div className="input-group">
          <input type="password" className="input-field" placeholder="Password" defaultValue="password" />
        </div>
        <button className="btn btn-primary" style={{ width: '100%', padding: '14px', fontSize: '1rem', marginTop: 24, borderRadius: '12px' }} onClick={onLogin}>
          Sign In
        </button>
      </div>
    </div>
  );
}

// ================= DASHBOARD PAGE =================
function Dashboard({ onSelectStudent }) {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);
  
  // Filters
  const [riskFilter, setRiskFilter] = useState("All");
  const [classFilter, setClassFilter] = useState("All");

  const fetchStudents = async () => {
    setLoading(true);
    let url = `${API_BASE}/students?risk_level=${riskFilter}&grade_class=${classFilter}`;
    try {
      const res = await fetch(url);
      const data = await res.json();
      setStudents(data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchStudents();
  }, [riskFilter, classFilter]);

  useEffect(() => {
    if (window.feather) window.feather.replace();
  });

  const uploadSuccess = () => {
    setShowUpload(false);
    fetchStudents();
  };

  // Stats
  const highRiskCount = students.filter(s => s.risk_level === 'High').length;
  const mediumRiskCount = students.filter(s => s.risk_level === 'Medium').length;
  const lowRiskCount = students.filter(s => s.risk_level === 'Low').length;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 48 }}>
        <div>
          <h1 style={{ fontSize: '2.25rem', marginBottom: 8 }}>Overview</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>Monitor student performance and early risk indicators.</p>
        </div>
        <button className="btn btn-primary" style={{ padding: '14px 28px', fontSize: '1rem', borderRadius: '16px' }} onClick={() => setShowUpload(true)}>
          <i data-feather="upload"></i> Upload CSV Data
        </button>
      </div>

      <div className="stat-grid" style={{ marginBottom: 48, gap: 32 }}>
        <div className="stat-card stat-high animate-slide-in" style={{ animationDelay: '0.1s', padding: '40px' }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: 16 }}><i data-feather="alert-triangle"></i> Critical Risk</h3>
          <div className="value" style={{ fontSize: '4.5rem' }}>{highRiskCount}</div>
        </div>
        <div className="stat-card stat-medium animate-slide-in" style={{ animationDelay: '0.2s', padding: '40px' }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: 16 }}><i data-feather="activity"></i> Medium Risk</h3>
          <div className="value" style={{ fontSize: '4.5rem' }}>{mediumRiskCount}</div>
        </div>
        <div className="stat-card stat-low animate-slide-in" style={{ animationDelay: '0.3s', padding: '40px' }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: 16 }}><i data-feather="check-circle"></i> Low Risk</h3>
          <div className="value" style={{ fontSize: '4.5rem' }}>{lowRiskCount}</div>
        </div>
      </div>

      <div style={{ padding: '0 8px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 32 }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 500 }}>Student Directory</h2>
          <div style={{ display: 'flex', gap: 24 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Risk:</span>
              <select className="input-field" value={riskFilter} onChange={e => setRiskFilter(e.target.value)} style={{ padding: '8px 40px 8px 16px', background: 'transparent' }}>
                <option value="All">All</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Class:</span>
              <select className="input-field" value={classFilter} onChange={e => setClassFilter(e.target.value)} style={{ padding: '8px 40px 8px 16px', background: 'transparent' }}>
                <option value="All">All</option>
                <option value="9th">9th</option>
                <option value="10th">10th</option>
              </select>
            </div>
          </div>
        </div>

        {loading ? (
          <div style={{ padding: 80, textAlign: 'center' }}><div className="spinner" style={{ margin: '0 auto', width: 48, height: 48 }}></div></div>
        ) : (
          <div className="table-container animate-fade-in" style={{ background: 'transparent', border: 'none', boxShadow: 'none' }}>
            <table style={{ borderCollapse: 'separate', borderSpacing: '0 8px' }}>
              <thead>
                <tr>
                  <th style={{ background: 'transparent', borderBottom: '1px solid var(--border)' }}>Student Name & ID</th>
                  <th style={{ background: 'transparent', borderBottom: '1px solid var(--border)' }}>Class Group</th>
                  <th style={{ background: 'transparent', borderBottom: '1px solid var(--border)' }}>AI Risk Score</th>
                  <th style={{ background: 'transparent', borderBottom: '1px solid var(--border)' }}>Status</th>
                  <th style={{ background: 'transparent', borderBottom: '1px solid var(--border)' }}>Primary Factor</th>
                  <th style={{ background: 'transparent', borderBottom: '1px solid var(--border)' }}></th>
                </tr>
              </thead>
              <tbody>
                {students.length === 0 && (
                  <tr>
                    <td colSpan="6" style={{ textAlign: 'center', padding: 64, color: 'var(--text-muted)', background: 'var(--surface-solid)', borderRadius: '16px' }}>
                      No students found matching your criteria.
                    </td>
                  </tr>
                )}
                {students.map(s => (
                  <tr key={s.id} onClick={() => onSelectStudent(s.id)} style={{ background: 'var(--surface)', borderRadius: '16px', overflow: 'hidden', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}>
                    <td style={{ padding: '24px 32px', borderTopLeftRadius: '16px', borderBottomLeftRadius: '16px', borderBottom: 'none' }}>
                      <div style={{ fontWeight: 600, color: 'white', fontSize: '1.1rem', marginBottom: 4 }}>{s.name}</div>
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{s.student_id}</div>
                    </td>
                    <td style={{ padding: '24px 32px', borderBottom: 'none' }}>
                      <span style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>{s.grade_class}</span>
                    </td>
                    <td style={{ padding: '24px 32px', borderBottom: 'none', fontWeight: 700, fontSize: '1.4rem', color: s.risk_level === 'High' ? 'var(--risk-high)' : 'var(--text-main)' }}>{s.risk_score}</td>
                    <td style={{ padding: '24px 32px', borderBottom: 'none' }}>
                      <span className={`badge badge-${s.risk_level.toLowerCase()}`} style={{ padding: '8px 16px', fontSize: '0.85rem' }}>
                        {s.risk_level === 'High' ? <i data-feather="alert-circle" width="14"></i> : null}
                        {s.risk_level} Risk
                      </span>
                    </td>
                    <td style={{ padding: '24px 32px', borderBottom: 'none', color: 'var(--text-muted)', fontSize: '0.95rem' }}>{s.top_factors ? s.top_factors.split(',')[0] : 'None calculated'}</td>
                    <td style={{ padding: '24px 32px', borderBottom: 'none', textAlign: 'right', color: 'var(--accent)', borderTopRightRadius: '16px', borderBottomRightRadius: '16px' }}><i data-feather="arrow-up-right" width="24" height="24"></i></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showUpload && <UploadModal onClose={() => setShowUpload(false)} onSuccess={uploadSuccess} />}
    </div>
  );
}

// ================= UPLOAD MODAL =================
function UploadModal({ onClose, onSuccess }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData
      });
      if (res.ok) {
        onSuccess();
      } else {
        alert("Error uploading file. Make sure it has correct columns.");
      }
    } catch (e) {
      console.error(e);
      alert("Failed to connect to backend");
    }
    setLoading(false);
  };

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(15, 23, 42, 0.8)', backdropFilter: 'blur(8px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
      <div className="glass-panel animate-fade-in" style={{ padding: 40, width: '450px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <h3 style={{ fontSize: '1.25rem' }}>Upload Student Data</h3>
          <span onClick={onClose} style={{ cursor: 'pointer', display: 'flex', color: 'var(--text-muted)' }}>
            <i data-feather="x"></i>
          </span>
        </div>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: 24, lineHeight: 1.5 }}>
          Upload a CSV file containing student records. Required columns include: Student ID, Student Name, Class / Grade, Attendance Percentage, Latest Exam Score...
        </p>
        <div className="input-group">
          <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0])} className="input-field" style={{ padding: '16px', border: '2px dashed rgba(255,255,255,0.2)', background: 'rgba(0,0,0,0.2)' }} />
        </div>
        <button className="btn btn-primary" style={{ width: '100%', marginTop: 24, padding: '14px' }} onClick={handleUpload} disabled={loading || !file}>
          {loading ? <span style={{ display: 'flex', gap: 8, alignItems: 'center' }}><div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }}></div> Processing ML Pipeline...</span> : <span style={{ display: 'flex', gap: 8, alignItems: 'center' }}><i data-feather="cpu" width="18"></i> Analyze Data Engine</span>}
        </button>
      </div>
    </div>
  );
}

// ================= STUDENT DETAIL PAGE =================
function StudentDetail({ id, onBack }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [action, setAction] = useState("");

  const fetchDetail = async () => {
    try {
      const res = await fetch(`${API_BASE}/students/${id}`);
      const json = await res.json();
      setData(json);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchDetail();
  }, [id]);

  useEffect(() => {
    if (window.feather) window.feather.replace();
  });

  const handleLogIntervention = async () => {
    if (!action.trim()) return;
    try {
      await fetch(`${API_BASE}/students/${id}/interventions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          action
        })
      });
      setAction("");
      fetchDetail(); // Refresh list
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) return <div style={{ padding: 60, textAlign: 'center' }}><div className="spinner" style={{ margin: '0 auto' }}></div></div>;
  if (!data || !data.student) return <div style={{ textAlign: 'center', padding: 40 }}>Error loading student.</div>;

  const { student, interventions } = data;
  
  const suggestedActions = [
    "Conduct a home visit",
    "Arrange a counselling session",
    "Assign a peer study buddy",
    "Assist with scholarship applications"
  ];

  return (
    <div className="animate-fade-in">
      <button className="btn btn-outline" style={{ marginBottom: 32 }} onClick={onBack}>
        <i data-feather="arrow-left" width="16"></i> Back to Dashboard
      </button>

      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: 32 }}>
        
        {/* Left Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
          
          <div className="glass-panel" style={{ padding: 40, display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95))' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
                <h1 style={{ fontSize: '2.5rem', margin: 0, lineHeight: 1 }}>{student.name}</h1>
              </div>
              <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>
                <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>{student.grade_class}</span> • ID: {student.student_id}
              </p>
            </div>
            <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 8 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Risk Score</span>
                  <div style={{ fontSize: '3.5rem', fontWeight: 700, color: student.risk_level === 'High' ? 'var(--risk-high)' : 'var(--text-main)', lineHeight: 1, textShadow: '0 2px 10px rgba(0,0,0,0.3)', fontFamily: 'Outfit' }}>
                    {student.risk_score}
                  </div>
                </div>
              </div>
              <span className={`badge badge-${student.risk_level.toLowerCase()}`} style={{ padding: '6px 16px', fontSize: '0.85rem' }}>
                {student.risk_level === 'High' ? <i data-feather="alert-octagon" width="14"></i> : null}
                {student.risk_level} Risk
              </span>
            </div>
          </div>

          <div className="glass-card animate-slide-in" style={{ padding: 32, animationDelay: '0.1s' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: '1.25rem' }}>
              <i data-feather="cpu" style={{ color: 'var(--accent)' }}></i> 
              Why is {student.name.split(' ')[0]} at risk?
            </h3>
            <div className="explanation-box">
              {student.llm_explanation}
            </div>

            <div style={{ marginTop: 32 }}>
              <h4 style={{ marginBottom: 16, color: 'var(--text-muted)', fontSize: '0.875rem', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Top Contributing Factors</h4>
              <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                {student.top_factors && student.top_factors.split(',').map((f, i) => (
                  <span key={i} style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', padding: '8px 16px', borderRadius: '999px', fontSize: '0.9rem' }}>
                    {f.trim()}
                  </span>
                ))}
              </div>
            </div>
            
            <div style={{ marginTop: 32, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
              <div className="metric-card">
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Attendance</span>
                <div className="metric-value">{student.attendance_pct}%</div>
              </div>
              <div className="metric-card">
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Latest Exam</span>
                <div className="metric-value">{student.latest_exam_score}%</div>
              </div>
              <div className="metric-card">
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Commute</span>
                <div className="metric-value">{student.distance_km}km</div>
              </div>
            </div>
          </div>
          
        </div>

        {/* Right Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
          
          {student.risk_level === 'High' && (
            <div className="glass-card animate-slide-in" style={{ padding: 32, background: 'linear-gradient(135deg, rgba(244, 63, 94, 0.15), rgba(190, 18, 60, 0.05))', borderColor: 'rgba(244, 63, 94, 0.3)', animationDelay: '0.2s' }}>
              <h3 style={{ color: 'var(--risk-high)', marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
                <i data-feather="zap"></i> Suggested Interventions
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {suggestedActions.map((actionText, i) => (
                  <button key={i} className="btn" style={{ background: 'rgba(15, 23, 42, 0.6)', color: 'var(--text-main)', border: '1px solid rgba(244, 63, 94, 0.2)', justifyContent: 'flex-start', textAlign: 'left', padding: '12px 16px' }} onClick={() => setAction(actionText)}>
                    <i data-feather="arrow-right" width="16" style={{ color: 'var(--risk-high)', opacity: 0.7 }}></i> {actionText}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="glass-card animate-slide-in" style={{ padding: 32, flex: 1, animationDelay: '0.3s' }}>
            <h3 style={{ marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
              <i data-feather="list" style={{ color: 'var(--accent)' }}></i> Intervention Log
            </h3>
            <div style={{ display: 'flex', gap: 12, marginBottom: 24 }}>
              <input type="text" className="input-field" style={{ flex: 1 }} placeholder="Record action taken..." value={action} onChange={e => setAction(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleLogIntervention()} />
              <button className="btn btn-primary" onClick={handleLogIntervention}>Log</button>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12, maxHeight: '400px', overflowY: 'auto', paddingRight: 8 }}>
              {interventions.length === 0 ? (
                <div style={{ color: 'var(--text-muted)', fontSize: '0.95rem', padding: 24, textAlign: 'center', background: 'rgba(0,0,0,0.1)', borderRadius: 8 }}>
                  No interventions logged yet.
                </div>
              ) : (
                interventions.slice().reverse().map(inv => (
                  <div key={inv.id} className="intervention-item">
                    <div style={{ fontSize: '0.95rem' }}>{inv.action}</div>
                    <div style={{ fontWeight: 500, fontSize: '0.8rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>{inv.date}</div>
                  </div>
                ))
              )}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}

// Mount App
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
