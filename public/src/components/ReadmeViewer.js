import React, { useState, useEffect } from 'react';

const ReadmeViewer = () => {
    const [content, setContent] = useState('');
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch('http://127.0.0.1:5001/api/readme')
            .then(res => {
                if (!res.ok) throw new Error('Failed to load README');
                return res.json();
            })
            .then(data => setContent(data.content))
            .catch(err => setError(err.message));
    }, []);

    if (error) return <div className="error">Error loading README: {error}</div>;

    // 간단한 마크다운 파싱 (필요 시 라이브러리 사용 권장, 여기선 직접 구현)
    const renderMarkdown = (text) => {
        if (!text) return null;
        return text.split('\n').map((line, index) => {
            if (line.startsWith('# ')) return <h1 key={index}>{line.slice(2)}</h1>;
            if (line.startsWith('## ')) return <h2 key={index}>{line.slice(3)}</h2>;
            if (line.startsWith('### ')) return <h3 key={index}>{line.slice(4)}</h3>;
            if (line.startsWith('- ')) return <li key={index}>{line.slice(2)}</li>;
            if (line.startsWith('```')) return <pre key={index} style={{background: '#f4f4f4', padding: '10px'}}>{line}</pre>; // 코드 블록 시작/끝 단순 처리
            if (line === '') return <br key={index} />;
            return <p key={index}>{line}</p>;
        });
    };

    return (
        <div className="readme-viewer" style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '5px', background: '#fff' }}>
            {renderMarkdown(content)}
        </div>
    );
};

export default ReadmeViewer;
