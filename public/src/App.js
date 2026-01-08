const { useState, useEffect, useRef } = React;

// --- Sub-Components (Unified for No-Build) ---

const ReadmeViewer = () => {
    const [content, setContent] = useState('');
    useEffect(() => {
        fetch('/api/readme').then(res => res.json()).then(data => setContent(data.content));
    }, []);
    return (
        <div style={{ padding: '20px', background: '#fff', border: '1px solid #ddd', whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
            {content || "Loading README..."}
        </div>
    );
};

const RecordForm = ({ onAdd }) => {
    const [dna, setDna] = useState('');
    return (
        <div className="card" style={{padding: '20px', background: '#fff', marginBottom: '20px', border: '1px solid #ddd'}}>
            <h3>🧬 Register DNA Sequence</h3>
            <div style={{ display: 'flex', gap: '10px' }}>
                <input 
                    type="text" 
                    value={dna} 
                    onChange={e => setDna(e.target.value.toUpperCase())} 
                    placeholder="ATCG..." 
                    style={{padding: '10px', flex: 1, border: '1px solid #ccc'}} 
                />
                <button 
                    onClick={() => { if(dna.trim()) { onAdd(dna); setDna(''); } }} 
                    style={{padding: '10px 20px', cursor: 'pointer', background: '#007bff', color: '#fff', border: 'none', borderRadius: '4px'}}
                >
                    Analyze
                </button>
            </div>
        </div>
    );
};

const RecordList = ({ records, onSelect }) => (
    <div className="card" style={{padding: '20px', background: '#fff', border: '1px solid #ddd'}}>
        <h3>📚 Genetic Database</h3>
        {records.length === 0 ? (
            <p style={{color: '#999'}}>No records found.</p>
        ) : (
            <ul style={{listStyle: 'none', padding: 0}}>
                {records.map(r => (
                    <li 
                        key={r.record_id} 
                        onClick={() => onSelect(r)} 
                        style={{
                            padding: '10px', 
                            borderBottom: '1px solid #eee', 
                            cursor: 'pointer',
                            transition: 'background 0.2s'
                        }}
                        onMouseEnter={e => e.currentTarget.style.background = '#f8f9fa'}
                        onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                    >
                        <strong>{r.record_id.slice(0,8)}</strong> - {r.predicted_type} ({r.record_type || 'DNA'})
                    </li>
                ))}
            </ul>
        )}
    </div>
);

const ApiTester = () => {
    const [res, setRes] = useState(null);
    const test = (path) => fetch(path).then(r => r.json()).then(setRes).catch(err => setRes({error: err.message}));
    return (
        <div style={{padding: '20px', background: '#fff', border: '1px solid #ddd'}}>
            <h3>🔬 API Quick Test</h3>
            <div style={{ display: 'flex', gap: '10px' }}>
                <button onClick={() => test('/api/records')}>Get Records</button>
                <button onClick={() => test('/api/records/stats')}>Stats</button>
                <button onClick={() => test('/api/ml/inspect')}>ML Inspect</button>
            </div>
            <pre style={{background: '#333', color: '#0f0', padding: '15px', marginTop: '15px', overflow: 'auto', maxHeight: '400px', borderRadius: '4px'}}>
                {JSON.stringify(res, null, 2)}
            </pre>
        </div>
    );
};

// --- Main App ---

export default function App() {
    const [records, setRecords] = useState([]);
    const [selected, setSelected] = useState(null);
    const [activeTab, setActiveTab] = useState('readme');
    const [loading, setLoading] = useState(false);

    const fetchRecords = () => {
        setLoading(true);
        fetch('/api/records')
            .then(res => res.json())
            .then(data => {
                setRecords(Array.isArray(data) ? data : []);
                setLoading(false);
            })
            .catch(err => {
                console.error("Fetch Error:", err);
                setLoading(false);
            });
    };
    
    useEffect(() => { fetchRecords(); }, []);

    const handleAdd = (dna) => {
        fetch('/api/records', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ dna_sequence: dna, record_type: 'DNA' })
        })
        .then(async res => {
            const data = await res.json();
            if (res.ok) {
                alert("Successfully analyzed and archived!");
                fetchRecords();
            } else {
                alert("Error: " + (data.error || "Failed to add record"));
            }
        })
        .catch(err => alert("Network Error: " + err.message));
    };

    return (
        <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
            <header style={{ marginBottom: '30px', borderBottom: '4px solid #007bff', paddingBottom: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                <div>
                    <h1 style={{margin: 0, color: '#007bff'}}>🧬 DNA Governance Admin UI</h1>
                    <p style={{color: '#666', margin: '5px 0 0 0'}}>Unified Management Console (No-Build Edition)</p>
                </div>
                <div style={{fontSize: '0.8rem', color: '#999'}}>
                    Sandbox: 20260104_234323_7cb6b2
                </div>
            </header>

            <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
                <button onClick={() => setActiveTab('readme')} style={{ padding: '10px 20px', background: activeTab === 'readme' ? '#007bff' : '#6c757d', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>📖 README</button>
                <button onClick={() => setActiveTab('records')} style={{ padding: '10px 20px', background: activeTab === 'records' ? '#007bff' : '#6c757d', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>🧬 Records</button>
                <button onClick={() => setActiveTab('api')} style={{ padding: '10px 20px', background: activeTab === 'api' ? '#007bff' : '#6c757d', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>🔬 API Tester</button>
            </div>

            <div className="content">
                {activeTab === 'readme' && <ReadmeViewer />}
                {activeTab === 'api' && <ApiTester />}
                {activeTab === 'records' && (
                    <div style={{ display: 'flex', gap: '20px' }}>
                        <div style={{ flex: 1.5 }}>
                            <RecordForm onAdd={handleAdd} />
                            <div style={{ position: 'relative' }}>
                                {loading && <div style={{ position: 'absolute', top: 50, left: 0, right: 0, textAlign: 'center', background: 'rgba(255,255,255,0.8)', padding: '20px', zIndex: 1 }}>Loading...</div>}
                                <RecordList records={records} onSelect={setSelected} />
                            </div>
                        </div>
                        <div style={{ flex: 1, padding: '20px', background: '#f0f4f8', borderRadius: '8px', border: '1px solid #d1d9e6', height: 'fit-content', position: 'sticky', top: '20px' }}>
                            <h3 style={{ marginTop: 0, borderBottom: '2px solid #d1d9e6', paddingBottom: '10px' }}>🔍 Record Detail</h3>
                            {selected ? (
                                <div style={{ fontSize: '0.9rem' }}>
                                    <p><strong>ID:</strong> <code style={{background: '#eee', padding: '2px 4px'}}>{selected.record_id}</code></p>
                                    <p><strong>Type:</strong> <span style={{background: '#007bff', color: '#fff', padding: '2px 6px', borderRadius: '3px'}}>{selected.record_type || 'DNA'}</span></p>
                                    <p><strong>Prediction:</strong> <span style={{fontWeight: 'bold', color: '#28a745'}}>{selected.predicted_type}</span></p>
                                    <p><strong>Created:</strong> {new Date(selected.birth_time).toLocaleString()}</p>
                                    <p><strong>Sequence:</strong></p>
                                    <pre style={{background: '#fff', padding: '10px', border: '1px solid #ddd', whiteSpace: 'pre-wrap', wordBreak: 'break-all', maxHeight: '200px', overflow: 'auto', fontFamily: 'monospace'}}>
                                        {selected.dna_sequence}
                                    </pre>
                                </div>
                            ) : <p style={{color: '#666', fontStyle: 'italic'}}>Select a record from the list to view its full molecular properties.</p>}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
