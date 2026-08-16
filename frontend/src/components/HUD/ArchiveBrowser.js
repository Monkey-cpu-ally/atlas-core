/* eslint-disable */
import React, { useEffect, useState } from 'react';
import { Loader2, Archive, FileText, BookOpen } from 'lucide-react';
import KnowledgeBookshelf from './KnowledgeBookshelf';
import KnowledgeCurriculum from './KnowledgeCurriculum';

const BACKEND = process.env.REACT_APP_BACKEND_URL;

export default function ArchiveBrowser({ aiColor }) {
  const [tab, setTab] = useState('knowledge');
  const [knowledgeView, setKnowledgeView] = useState('curriculum');
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [subjects, setSubjects] = useState([]);
  const [files, setFiles] = useState([]);
  const [archive, setArchive] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`${BACKEND}/api/kbase/subjects`).then(r => r.ok ? r.json() : Promise.reject()).then(data => setSubjects(Array.isArray(data) ? data : (data.subjects || data.items || data.data || []))).catch(() => {});
  }, []);

  useEffect(() => {
    if (tab === 'knowledge') { setLoading(false); return undefined; }
    let cancelled = false; setLoading(true);
    (async () => { try {
      if (tab === 'files') { const r=await fetch(`${BACKEND}/api/files/list?limit=80`); const data=await r.json(); if(!cancelled)setFiles(Array.isArray(data)?data:(data.files||[])); }
      else { const r=await fetch(`${BACKEND}/api/atlas/archive/list`); const data=await r.json(); if(!cancelled)setArchive(data.entries||[]); }
    } catch(_){} if(!cancelled)setLoading(false); })();
    return () => { cancelled=true; };
  }, [tab]);

  const enterSubject = s => { setSelectedSubject(s); setKnowledgeView('bookshelf'); };

  return <div className="bp-workbench" data-testid="archive-browser">
    <h3 className="bp-title" style={{color:aiColor}}><Archive size={14}/> Research Archive</h3>
    <div className="bp-actions">
      <button className={`bp-btn ${tab==='knowledge'?'primary':''}`} onClick={() => setTab('knowledge')} style={tab==='knowledge'?{borderColor:aiColor,color:aiColor}:undefined}><BookOpen size={11}/> Knowledge</button>
      <button className={`bp-btn ${tab==='atlas'?'primary':''}`} onClick={() => setTab('atlas')} style={tab==='atlas'?{borderColor:aiColor,color:aiColor}:undefined}>Atlas memory</button>
      <button className={`bp-btn ${tab==='files'?'primary':''}`} onClick={() => setTab('files')} style={tab==='files'?{borderColor:aiColor,color:aiColor}:undefined}>Uploaded files</button>
    </div>

    {tab==='knowledge' && knowledgeView==='curriculum' && <KnowledgeCurriculum subjects={subjects} aiColor={aiColor} onEnterSubject={enterSubject}/>} 
    {tab==='knowledge' && knowledgeView==='bookshelf' && <div><button className="bp-btn" onClick={() => setKnowledgeView('curriculum')}>← Curriculum</button><KnowledgeBookshelf aiColor={aiColor} initialSubject={selectedSubject}/></div>}
    {loading && <div className="bp-section"><Loader2 size={14} className="spin"/> Loading…</div>}
    {!loading && tab==='atlas' && <div className="archive-list">{archive.length===0&&<div className="bp-section">No archive entries yet.</div>}{archive.map((e,i)=><div key={e.id||i} className="archive-row" style={{borderLeftColor:aiColor}}><div className="archive-row-head"><FileText size={11}/><span className="archive-row-title">{e.filename||e.topic||e.id||'untitled'}</span><span className="archive-row-tag">{e.classification?.routed_core||e.routed_to||e.kind||''}</span></div>{e.summary&&<div className="bp-voice-body">{e.summary}</div>}</div>)}</div>}
    {!loading && tab==='files' && <div className="archive-list">{files.length===0&&<div className="bp-section">No files uploaded.</div>}{files.map(f=><div key={f.id} className="archive-row" style={{borderLeftColor:aiColor}}><div className="archive-row-head"><FileText size={11}/><span className="archive-row-title">{f.filename}</span></div></div>)}</div>}
  </div>;
}
