import React, { useEffect, useState } from 'react';
import { Loader2, Settings as SettingsIcon, Check } from 'lucide-react';

const BACKEND = process.env.REACT_APP_BACKEND_URL;

const OPTS = {
  tts_provider:     [{v:'auto',l:'Auto'},{v:'openai',l:'OpenAI'},{v:'elevenlabs',l:'ElevenLabs'}],
  default_language: [{v:'en',l:'EN'},{v:'zu',l:'ZU'},{v:'yo',l:'YO'},{v:'maa',l:'MAA'}],
  accent_theme:     [{v:'auto',l:'Auto · per persona'},{v:'crimson',l:'Crimson'},{v:'teal',l:'Teal'},{v:'silver',l:'Silver'},{v:'violet',l:'Violet'}],
};
const LABELS = {
  tts_provider:     'Voice provider',
  default_language: 'Default language',
  accent_theme:     'Accent theme',
};

export default function CustomizationPanel({ aiColor }) {
  const [settings, setSettings] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${BACKEND}/api/settings`);
        const data = await res.json();
        setSettings(data);
      } catch (_) { /* network */ }
    })();
  }, []);

  const save = async (key, value) => {
    setSaving(true);
    const next = { ...settings, [key]: value };
    setSettings(next);
    try {
      const res = await fetch(`${BACKEND}/api/settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ [key]: value }),
      });
      if (res.ok) {
        const data = await res.json();
        setSettings(data);
      }
    } catch (_) { /* network */ }
    setSaving(false);
  };

  if (!settings) {
    return <div className="bp-workbench"><Loader2 size={14} className="spin" /> Loading settings…</div>;
  }

  return (
    <div className="bp-workbench" data-testid="customization-panel">
      <h3 className="bp-title" style={{ color: aiColor }}><SettingsIcon size={14} /> Customization {saving && <Loader2 size={11} className="spin" style={{ marginLeft: 6 }} />}</h3>
      <p className="bp-help">Live system preferences. Saved instantly to MongoDB.</p>

      {Object.keys(OPTS).map((key) => (
        <div key={key} className="cust-row" data-testid={`cust-row-${key}`}>
          <div className="cust-label">{LABELS[key]}</div>
          <div className="cust-pills">
            {OPTS[key].map((o) => (
              <button
                key={o.v}
                className={`cust-pill ${settings[key] === o.v ? 'active' : ''}`}
                onClick={() => save(key, o.v)}
                data-testid={`cust-${key}-${o.v}`}
                style={settings[key] === o.v ? { borderColor: aiColor, color: aiColor } : undefined}
              >
                {settings[key] === o.v && <Check size={9} />} {o.l}
              </button>
            ))}
          </div>
        </div>
      ))}

      <div className="cust-row" data-testid="cust-row-voice_enabled">
        <div className="cust-label">AI voice playback</div>
        <button
          className={`cust-pill ${settings.voice_enabled ? 'active' : ''}`}
          onClick={() => save('voice_enabled', !settings.voice_enabled)}
          data-testid="cust-voice-toggle"
          style={settings.voice_enabled ? { borderColor: aiColor, color: aiColor } : undefined}
        >
          {settings.voice_enabled ? 'Enabled' : 'Disabled'}
        </button>
      </div>
    </div>
  );
}
