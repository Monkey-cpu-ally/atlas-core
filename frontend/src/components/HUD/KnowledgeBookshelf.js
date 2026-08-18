/* eslint-disable */
import React, { useEffect, useMemo, useState } from 'react';
import {
  BookOpen, Search, Loader2, RefreshCw, ExternalLink,
  GraduationCap, MessageCircle, Sparkles, Microscope,
} from 'lucide-react';
import './KnowledgeBookshelf.css';

const BACKEND = process.env.REACT_APP_BACKEND_URL || '';
const COLORS = ['#b23a48','#386641','#31587a','#7b2cbf','#bc6c25','#2a9d8f','#9b2226','#5f6f52','#3a5a40','#6d597a','#457b9d','#8d6e63'];
const PERSONAS = [
  { id: 'ajani', label: 'Ask Ajani', color: '#F03246' },
  { id: 'minerva', label: 'Ask Minerva', color: '#28C8BE' },
  { id: 'hermes', label: 'Ask Hermes', color: '#F4EFE4' },
];
const TYPES = ['all','book','paper','video','patent','lesson','project','blueprint','inventor','reference'];

const list = (data, keys = []) => {
  if (Array.isArray(data)) return data;
  for (const key of keys) if (Array.isArray(data?.[key])) return data[key];
  return [];
};
const sid = value => String(value?.id || value?.slug || value?.name || value || '').toLowerCase();
const sname = value => value?.name || value?.label || value?.title || value;
const resourceType = resource => {
  const raw = String(resource.type || resource.resource_type || resource.kind || resource.category || resource.source_type || 'reference').toLowerCase();
  if (raw.includes('youtube') || raw.includes('video')) return 'video';
  if (raw.includes('paper') || raw.includes('article') || raw.includes('arxiv') || raw.includes('journal')) return 'paper';
  if (raw.includes('patent')) return 'patent';
  if (raw.includes('blueprint') || raw.includes('cad') || raw.includes('schematic')) return 'blueprint';
  if (raw.includes('lesson') || raw.includes('course')) return 'lesson';
  if (raw.includes('project') || raw.includes('build')) return 'project';
  if (raw.includes('inventor') || raw.includes('person') || raw.includes('biograph')) return 'inventor';
  if (raw.includes('book') || raw.includes('textbook')) return 'book';
  return 'reference';
};
const sourceUrl = resource => resource?.url || resource?.source_url || resource?.canonical_url || null;
const resourceSubjects = resource => {
  if (Array.isArray(resource?.subjects) && resource.subjects.length) return resource.subjects.map(String);
  const single = resource?.subject || resource?.subject_id || resource?.domain;
  return single ? [String(single)] : ['General'];
};
const primarySubject = resource => resourceSubjects(resource)[0] || 'General';
const hasSubject = (resource, subjectId) => resourceSubjects(resource).some(subject => sid(subject) === subjectId);
const subjectLabel = resource => resourceSubjects(resource).join(' · ');
const colorFor = value => {
  const key = String(value || 'atlas').toLowerCase();
  let hash = 0;
  for (let i = 0; i < key.length; i += 1) hash = ((hash << 5) - hash) + key.charCodeAt(i);
  return COLORS[Math.abs(hash) % COLORS.length];
};

export default function KnowledgeBookshelf({ aiColor, initialSubject = null }) {
  const [subjects, setSubjects] = useState([]);
  const [resources, setResources] = useState([]);
  const [subject, setSubject] = useState(initialSubject ? sid(initialSubject) : 'all');
  const [type, setType] = useState('all');
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [reloadKey, setReloadKey] = useState(0);
  const [asking, setAsking] = useState('');
  const [answer, setAnswer] = useState(null);
  const [researching, setResearching] = useState(false);
  const [researchResult, setResearchResult] = useState(null);

  useEffect(() => { if (initialSubject) setSubject(sid(initialSubject)); }, [initialSubject]);
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError('');
    Promise.all([
      fetch(`${BACKEND}/api/kbase/subjects`).then(async response => {
        if (!response.ok) throw Error(`subjects ${response.status}`);
        return response.json();
      }),
      fetch(`${BACKEND}/api/kbase/resources`).then(async response => {
        if (!response.ok) throw Error(`resources ${response.status}`);
        return response.json();
      }),
    ]).then(([subjectData, resourceData]) => {
      if (!cancelled) {
        setSubjects(list(subjectData, ['subjects','items','data']));
        setResources(list(resourceData, ['resources','items','data']));
      }
    }).catch(err => {
      if (!cancelled) setError(err.message || 'Knowledge Bank unavailable');
    }).finally(() => {
      if (!cancelled) setLoading(false);
    });
    return () => { cancelled = true; };
  }, [reloadKey]);

  const subjectResources = useMemo(
    () => resources.filter(resource => subject === 'all' || hasSubject(resource, subject)),
    [resources, subject],
  );
  const counts = useMemo(() => subjectResources.reduce((acc, resource) => {
    const currentType = resourceType(resource);
    acc[currentType] = (acc[currentType] || 0) + 1;
    return acc;
  }, {}), [subjectResources]);
  const filtered = useMemo(() => subjectResources.filter(resource => {
    const haystack = [
      resource.title, resource.author, resource.summary, resource.description,
      resource.source, resource.provider, ...resourceSubjects(resource),
    ].filter(Boolean).join(' ').toLowerCase();
    return (type === 'all' || resourceType(resource) === type)
      && (!query.trim() || haystack.includes(query.trim().toLowerCase()));
  }), [subjectResources, type, query]);

  const teach = () => window.dispatchEvent(new CustomEvent('atlas-teach-resource', { detail: { resource: selected } }));

  const ask = async persona => {
    if (!selected || asking) return;
    setAsking(persona);
    setAnswer(null);
    const context = [
      `I am reading a Knowledge Bookshelf resource classified under: ${subjectLabel(selected)}.`,
      `Resource type: ${resourceType(selected)}.`,
      `Title: ${selected.title || 'Untitled resource'}.`,
      selected.author ? `Author: ${selected.author}.` : '',
      selected.summary || selected.description ? `Knowledge Bank summary: ${selected.summary || selected.description}` : '',
      'Explain this resource from your perspective. Focus on what I should understand, important connections, and what I should study or build next. Ground your answer in this selected resource and clearly say when you are making an inference.',
    ].filter(Boolean).join('\n');
    try {
      const response = await fetch(`${BACKEND}/api/chat/send`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ persona, message: context }),
      });
      const data = await response.json();
      if (!response.ok) throw Error(data.detail || `chat ${response.status}`);
      setAnswer({ persona, response: data.response });
    } catch (err) {
      setAnswer({ persona, error: err.message || 'Persona chat unavailable' });
    } finally {
      setAsking('');
    }
  };

  const researchMore = async () => {
    if (!selected || researching) return;
    setResearching(true);
    setResearchResult(null);
    const title = selected.title || 'Untitled resource';
    const summary = selected.summary || selected.description || '';
    const provider = selected.provider || selected.source || '';
    const researchQuery = [title, provider && `from ${provider}`, summary && `— ${summary.slice(0, 180)}`].filter(Boolean).join(' ');
    try {
      const response = await fetch(`${BACKEND}/api/research/orchestrate`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: primarySubject(selected), query: researchQuery, top_n: 5,
          use_live_web: true, ingest_catalog_resources: false,
        }),
      });
      const data = await response.json();
      if (!response.ok) throw Error(data.detail || `research ${response.status}`);
      setResearchResult(data);
    } catch (err) {
      setResearchResult({ status: 'error', error: err.message || 'Knowledge Bank research bridge unavailable' });
    } finally {
      setResearching(false);
    }
  };

  if (selected) {
    const accent = colorFor(primarySubject(selected));
    const verified = selected.verification_status || selected.evidence?.verification_status || selected.verified || selected.status;
    return <div className="knowledge-bookshelf kb-reading-room">
      <button className="bp-btn" onClick={() => { setSelected(null); setAnswer(null); setResearchResult(null); }}>← Return to bookshelf</button>
      <article className="kb-open-book" style={{ '--subject-accent': accent }}>
        <section className="kb-page kb-page-left">
          <div className="kb-bookmark"/><div className="kb-kicker">{subjectLabel(selected)}</div>
          <div className="kb-detail-type">{resourceType(selected).toUpperCase()}</div>
          <h2>{selected.title || 'Untitled resource'}</h2>
          {selected.author && <div className="kb-byline">by {selected.author}</div>}
          <div className="kb-source-seal">{verified ? `ATLAS SOURCE · ${String(verified).toUpperCase()}` : 'ATLAS KNOWLEDGE SOURCE'}</div>
        </section>
        <section className="kb-page kb-page-right">
          <h3>Research Notes</h3>
          <p>{selected.summary || selected.description || 'No summary is available yet.'}</p>
          <div className="kb-meta">Source: {selected.source || selected.provider || sourceUrl(selected) || 'ATLAS Knowledge Bank'}</div>
          <div className="kb-reader-actions">
            <button className="kb-action primary" onClick={teach} style={{ borderColor: aiColor }}><GraduationCap size={13}/> Teach Me</button>
            <button className="kb-action" disabled={researching} onClick={researchMore} style={{ borderColor: aiColor, color: aiColor }}>{researching ? <Loader2 size={12} className="spin"/> : <Microscope size={12}/>} Research More</button>
            {PERSONAS.map(persona => <button key={persona.id} className="kb-action" disabled={!!asking} onClick={() => ask(persona.id)} style={{ borderColor: persona.color, color: persona.color }}>{asking === persona.id ? <Loader2 size={12} className="spin"/> : <MessageCircle size={12}/>} {persona.label}</button>)}
            {sourceUrl(selected) && <a className="kb-action" href={sourceUrl(selected)} target="_blank" rel="noreferrer"><ExternalLink size={12}/> Open source</a>}
          </div>
          {researchResult && <div className={researchResult.status === 'error' ? 'bp-error' : 'bp-section'}><strong>RESEARCH · {String(researchResult.status || researchResult.result || 'COMPLETE').toUpperCase()}</strong><div className="bp-voice-body">{researchResult.error || researchResult.note || researchResult.summary || `Knowledge Bank research returned ${researchResult.existing_resources?.length ?? researchResult.resources?.length ?? 0} related resource(s).`}</div></div>}
          {answer && <div className={answer.error ? 'bp-error' : 'bp-section'}><strong>{answer.persona?.toUpperCase()}</strong><div className="bp-voice-body">{answer.error || answer.response}</div></div>}
          <div className="kb-action-note"><Sparkles size={11}/> Research results report the backend's actual status; unavailable evidence is never presented as verified.</div>
        </section>
      </article>
    </div>;
  }

  return <div className="knowledge-bookshelf">
    <div className="kb-header"><div><div className="kb-kicker">{initialSubject ? `${sname(initialSubject)} LIBRARY` : 'ATLAS RESEARCH ARCHIVE'}</div><h3 style={{ color: aiColor }}><BookOpen size={15}/> Knowledge Bookshelf</h3><p>{initialSubject ? `Resources classified under ${sname(initialSubject)}.` : 'Twenty-two disciplines organized as a living engineering library.'}</p></div><button className="bp-btn" onClick={() => setReloadKey(value => value + 1)}><RefreshCw size={12}/></button></div>
    <label className="kb-search"><Search size={13}/><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Search this library…"/></label>
    <div className="kb-subject-tabs"><button className={`kb-tab ${subject === 'all' ? 'active' : ''}`} onClick={() => setSubject('all')}>ALL SHELVES</button>{subjects.map(subjectValue => { const id = sid(subjectValue); const accent = colorFor(id); return <button key={id} className={`kb-tab ${subject === id ? 'active' : ''}`} onClick={() => setSubject(id)} style={{ '--tab-color': accent, ...(subject === id ? { borderColor: accent, color: accent } : {}) }}><span className="kb-tab-mark"/>{sname(subjectValue)}</button>; })}</div>
    <div className="kb-subject-tabs">{TYPES.map(typeValue => { const count = typeValue === 'all' ? subjectResources.length : (counts[typeValue] || 0); return <button key={typeValue} className={`kb-tab ${type === typeValue ? 'active' : ''}`} onClick={() => setType(typeValue)} style={type === typeValue ? { borderColor: aiColor, color: aiColor } : undefined}>{typeValue === 'all' ? 'ALL RESOURCES' : typeValue.toUpperCase()} · {count}</button>; })}</div>
    {loading && <div className="kb-state"><Loader2 size={15} className="spin"/> Loading Knowledge Bank…</div>}
    {!loading && error && <div className="kb-state kb-error">Knowledge Bank unavailable: {error}</div>}
    {!loading && !error && filtered.length === 0 && <div className="kb-state">No resources match this shelf yet.</div>}
    {!loading && !error && filtered.length > 0 && <div className="kb-library-wall">{filtered.map((resource, index) => <button key={resource.id || resource.resource_id || `${resource.title}-${index}`} className="kb-volume" onClick={() => setSelected(resource)} style={{ '--book-accent': colorFor(primarySubject(resource)) }}><span className="kb-volume-band"/><span className="kb-volume-type">{resourceType(resource).toUpperCase()}</span><strong>{resource.title || 'Untitled resource'}</strong><span className="kb-volume-author">{resource.author || resource.provider || primarySubject(resource)}</span><span className="kb-volume-subject">{subjectLabel(resource)}</span></button>)}</div>}
    <div className="kb-footer">{filtered.length} resource{filtered.length === 1 ? '' : 's'} · {type === 'all' ? 'all types' : type}</div>
  </div>;
}
