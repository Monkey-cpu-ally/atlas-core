/* eslint-disable */
import React, { useMemo, useState } from 'react';
import { ChevronLeft, ChevronRight, Library, Sparkles } from 'lucide-react';
import './KnowledgeCurriculum.css';

const FALLBACK_SUBJECTS = ['Aerospace','Architecture','AI','Biology','Business','Chemistry','Creative Writing','Economics','Electronics','Environmental Science','Film Studies','Game Design','History','Mathematics','Music Theory','Nanotechnology','Philosophy','Physics','Psychology','Robotics','Software Engineering','Visual Arts'];
const METRICS = ['Theory','Application','Problem Solving','Design','Research','Projects'];

const nameOf = s => s?.name || s?.label || s?.title || s;
const idOf = s => String(s?.id || s?.slug || nameOf(s) || '').toLowerCase();
const score = (name, metric) => { const key = `${name}:${metric}`; let h=0; for(let i=0;i<key.length;i+=1) h=((h<<5)-h)+key.charCodeAt(i); return 35 + (Math.abs(h)%61); };

export default function KnowledgeCurriculum({ subjects = [], aiColor, onEnterSubject }) {
  const list = subjects.length ? subjects : FALLBACK_SUBJECTS;
  const [index,setIndex] = useState(0);
  const active = list[index] || list[0];
  const activeName = nameOf(active);
  const activeId = idOf(active);
  const metrics = useMemo(() => METRICS.map(m => ({ label:m, value:score(activeName,m) })),[activeName]);
  const move = delta => setIndex(i => (i + delta + list.length) % list.length);
  const visible = [-3,-2,-1,0,1,2,3].map(offset => ({ offset, item:list[(index+offset+list.length)%list.length] }));

  return <div className="kc-shell" data-testid="knowledge-curriculum">
    <div className="kc-topline"><span>ATLAS KNOWLEDGE CURRICULUM</span><span>{index+1} / {list.length}</span></div>
    <div className="kc-stage">
      <button className="kc-arrow left" onClick={() => move(-1)} aria-label="Previous subject"><ChevronLeft/></button>
      <div className="kc-orbit" aria-label="Subject selector">
        {visible.map(({offset,item}) => <button key={`${idOf(item)}-${offset}`} className={`kc-orbit-item ${offset===0?'active':''}`} style={{'--offset':offset}} onClick={() => setIndex((index+offset+list.length)%list.length)}>{nameOf(item)}</button>)}
      </div>
      <main className="kc-graffiti-zone">
        <div className="kc-spray-cloud"/>
        <div className="kc-graffiti-shadow" aria-hidden="true">{activeName}</div>
        <div className="kc-graffiti" data-subject={activeId}>{activeName}</div>
        <div className="kc-stencil"><Sparkles size={12}/> SUBJECT IDENTITY // {activeId.toUpperCase()}</div>
        <button className="kc-enter" onClick={() => onEnterSubject(active)} style={{borderColor:aiColor,color:aiColor}}><Library size={14}/> ENTER {activeName.toUpperCase()} LIBRARY</button>
      </main>
      <aside className="kc-mastery">
        <div className="kc-mastery-title">MASTERY PROFILE</div>
        <div className="kc-score-ring"><span>{Math.round(metrics.reduce((a,m)=>a+m.value,0)/metrics.length)}</span><small>LEVEL</small></div>
        {metrics.map(m => <div className="kc-metric" key={m.label}><div><span>{m.label}</span><b>{m.value}</b></div><div className="kc-meter"><i style={{width:`${m.value}%`}}/></div></div>)}
        <div className="kc-note">Mastery display is a curriculum visualization. Live learner analytics can replace these placeholders when the learning-progress API is connected.</div>
      </aside>
      <button className="kc-arrow right" onClick={() => move(1)} aria-label="Next subject"><ChevronRight/></button>
    </div>
  </div>;
}
