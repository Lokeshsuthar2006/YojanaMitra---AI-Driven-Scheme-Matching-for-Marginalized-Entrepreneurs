import { motion } from 'framer-motion';
import { Bot, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { api } from '../services/api';

function ruleFallback(result) {
  const passed = result.passed_rules || [];
  const failed = result.failed_rules || [];
  const missing = result.missing_fields || [];
  if (result.status === 'ELIGIBLE') {
    return `This explanation is generated from the deterministic rule results. The rule engine marked ${result.scheme_name} ELIGIBLE. ${passed.join(' ')} This is decision support, not a loan approval.`;
  }
  if (result.status === 'UNKNOWN') {
    return `This explanation is generated from the deterministic rule results. The rule engine marked ${result.scheme_name} UNKNOWN because information is missing: ${missing.join(', ') || 'additional profile details'}.`;
  }
  return `This explanation is generated from the deterministic rule results. The rule engine marked ${result.scheme_name} NOT ELIGIBLE. Failed checks: ${failed.join(' ') || 'The configured requirements were not satisfied.'}`;
}

export default function ExplanationPanel({ result, onClose }) {
  const [state, setState] = useState({ loading: true, data: null });

  useEffect(() => {
    let active = true;
    api.explain(result)
      .then(data => {
        if (!active) return;
        if (!data || typeof data.explanation !== 'string' || !data.explanation.trim()) {
          setState({ loading: false, data: { explanation: ruleFallback(result), source: 'Rule-result fallback', available: false } });
          return;
        }
        setState({ loading: false, data });
      })
      .catch(() => {
        if (active) setState({
          loading: false,
          data: {
            explanation: ruleFallback(result),
            source: 'Rule-result fallback',
            available: false,
          },
        });
      });
    return () => { active = false; };
  }, [result]);

  return (
    <motion.aside className="explain-panel" initial={{ x: 440 }} animate={{ x: 0 }} exit={{ x: 440 }}>
      <button className="icon-button" onClick={onClose} aria-label="Close explanation"><X /></button>
      <div className="eyebrow"><Bot size={16} /> Explanation layer</div>
      <h2>Yojana Mitra AI Explanation</h2>

      {state.loading
        ? <div className="skeleton lines" />
        : <>
            <p className="ai-copy">{state.data.explanation}</p>
            <p className="explanation-source">{state.data.source === 'Gemini explanation layer' ? 'Gemini explanation; eligibility remains determined by the rule engine.' : 'Rule-result fallback; Gemini is unavailable.'}</p>
            {state.data.notice && <p className="notice">{state.data.notice}</p>}
          </>
      }

      <div className="rule-list">
        <h3>What the rules checked</h3>
        {[...result.passed_rules, ...result.failed_rules].map((rule, i) => <p key={i}>{rule}</p>)}
        {result.missing_fields.map((rule, i) => <p key={i}>Missing: {rule}</p>)}
      </div>
      <small>AI interprets the completed rule result. It never determines eligibility.</small>
    </motion.aside>
  );
}
