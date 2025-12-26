import { useState, useEffect } from 'react';
import axios from 'axios';
import './BidGenerator.css';

// Support both local and deployed environments
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function BidGenerator() {
  const [mode, setMode] = useState('smart'); // 'smart' or 'manual'
  const [smartContent, setSmartContent] = useState('');
  const [formData, setFormData] = useState({
    project_name: '',
    project_description: '',
    bid_rank: '',
    total_bids: '',
    your_bid_amount: '',
    winning_bid_amount: ''
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [parsing, setParsing] = useState(false);
  const [parsedData, setParsedData] = useState(null);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const [extractionSteps, setExtractionSteps] = useState([]);
  
  // New states for settings and refinement
  const [showSettings, setShowSettings] = useState(false);
  const [showRefineMenu, setShowRefineMenu] = useState(false);
  const [refining, setRefining] = useState(false);
  const [notification, setNotification] = useState(null);
  const [showCustomRefine, setShowCustomRefine] = useState(false);
  const [customInstruction, setCustomInstruction] = useState('');
  const [settings, setSettings] = useState({
    apiKey: localStorage.getItem('custom_api_key') || '',
    provider: localStorage.getItem('ai_provider') || 'gemini',
    model: localStorage.getItem('ai_model') || 'gemini-2.5-flash',
    useCustomKey: localStorage.getItem('use_custom_key') === 'true'
  });
  const [availableModels, setAvailableModels] = useState({});

  // Load available models from backend
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await axios.get(`${API_URL}/config`);
        setAvailableModels(response.data.available_models || {});
      } catch (err) {
        console.error('Failed to load config:', err);
      }
    };
    fetchConfig();
  }, []);

  const handleSmartPaste = async () => {
    if (!smartContent.trim()) {
      setError('Please paste project content');
      return;
    }

    setParsing(true);
    setError(null);
    setParsedData(null);

    try {
      const response = await axios.post(`${API_URL}/parse-project`, {
        raw_content: smartContent
      });
      setParsedData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to parse content');
    } finally {
      setParsing(false);
    }
  };

  const handleSmartGenerate = async () => {
    if (!smartContent.trim()) {
      setError('Please paste project content');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setExtractionSteps([]);

    // Show extraction steps
    const steps = [
      '📄 Parsing project content...',
      '💰 Extracting budget information...',
      '📊 Analyzing bid competition...',
      '🎯 Matching required skills...',
      '✨ Generating AI-powered bid...',
      '🚀 Optimizing proposal...'
    ];

    // Simulate step-by-step extraction
    for (let i = 0; i < steps.length - 1; i++) {
      setExtractionSteps(prev => [...prev, { text: steps[i], complete: false }]);
      await new Promise(resolve => setTimeout(resolve, 300));
      setExtractionSteps(prev => {
        const updated = [...prev];
        updated[updated.length - 1].complete = true;
        return updated;
      });
    }

    try {
      setExtractionSteps(prev => [...prev, { text: steps[steps.length - 1], complete: false }]);
      const response = await axios.post(`${API_URL}/smart-generate-bid`, {
        raw_content: smartContent
      });
      setExtractionSteps(prev => {
        const updated = [...prev];
        updated[updated.length - 1].complete = true;
        return updated;
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate bid. Please check your API configuration.');
      setExtractionSteps([]);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const payload = {
        project_name: formData.project_name,
        project_description: formData.project_description,
        bid_rank: formData.bid_rank ? parseInt(formData.bid_rank) : null,
        total_bids: formData.total_bids ? parseInt(formData.total_bids) : null,
        your_bid_amount: formData.your_bid_amount || null,
        winning_bid_amount: formData.winning_bid_amount || null
      };

      const response = await axios.post(`${API_URL}/generate-bid`, payload);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate bid. Please check your API configuration.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (result?.bid_text) {
      navigator.clipboard.writeText(result.bid_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleReset = () => {
    setSmartContent('');
    setParsedData(null);
    setFormData({
      project_name: '',
      project_description: '',
      bid_rank: '',
      total_bids: '',
      your_bid_amount: '',
      winning_bid_amount: ''
    });
    setResult(null);
    setError(null);
  };

  const showNotification = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 4000);
  };

  const handleSettingsSave = () => {
    localStorage.setItem('custom_api_key', settings.apiKey);
    localStorage.setItem('ai_provider', settings.provider);
    localStorage.setItem('ai_model', settings.model);
    localStorage.setItem('use_custom_key', settings.useCustomKey);
    setShowSettings(false);
    showNotification('⚙️ Settings saved! Changes will apply to next bid generation.', 'success');
  };

  const handleRefineBid = async (refinementType) => {
    if (!result?.bid_text) return;
    
    // If custom, show input dialog
    if (refinementType === 'custom') {
      setShowCustomRefine(true);
      setShowRefineMenu(false);
      return;
    }
    
    setRefining(true);
    setShowRefineMenu(false);
    setError(null);

    try {
      const payload = {
        original_bid: result.bid_text,
        refinement_type: refinementType,
        project_description: parsedData?.project_description || formData.project_description || ''
      };

      // Add custom settings if enabled
      if (settings.useCustomKey && settings.apiKey) {
        payload.api_key = settings.apiKey;
        payload.provider = settings.provider;
        payload.model = settings.model;
      }

      const response = await axios.post(`${API_URL}/refine-bid`, payload);
      
      // Update result with refined bid
      setResult(prev => ({
        ...prev,
        bid_text: response.data.refined_bid
      }));
      showNotification('✨ Bid refined successfully!', 'success');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to refine bid');
      showNotification('❌ Failed to refine bid', 'error');
    } finally {
      setRefining(false);
    }
  };

  const handleCustomRefinement = async () => {
    if (!customInstruction.trim()) {
      showNotification('⚠️ Please enter your custom instructions', 'warning');
      return;
    }

    setRefining(true);
    setShowCustomRefine(false);
    setError(null);

    try {
      const payload = {
        original_bid: result.bid_text,
        refinement_type: 'custom',
        custom_instruction: customInstruction,
        project_description: parsedData?.project_description || formData.project_description || ''
      };

      if (settings.useCustomKey && settings.apiKey) {
        payload.api_key = settings.apiKey;
        payload.provider = settings.provider;
        payload.model = settings.model;
      }

      const response = await axios.post(`${API_URL}/refine-bid`, payload);
      
      setResult(prev => ({
        ...prev,
        bid_text: response.data.refined_bid
      }));
      setCustomInstruction('');
      showNotification('✨ Custom refinement applied!', 'success');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to refine bid');
      showNotification('❌ Failed to apply custom refinement', 'error');
    } finally {
      setRefining(false);
    }
  };

  const refinementOptions = [
    { id: 'reduce_length', label: '✂️ Make Shorter', desc: 'Reduce to 150 words' },
    { id: 'make_casual', label: '😊 More Casual', desc: 'Friendly tone' },
    { id: 'make_formal', label: '💼 More Formal', desc: 'Business tone' },
    { id: 'add_urgency', label: '⚡ Add Urgency', desc: 'Emphasize availability' },
    { id: 'emphasize_skills', label: '🎯 Emphasize Skills', desc: 'Highlight expertise' },
    { id: 'add_examples', label: '📝 Add Examples', desc: 'Include work samples' },
    { id: 'custom', label: '✨ Custom', desc: 'Your own instructions' }
  ];

  return (
    <div className="bid-generator">
      {/* Toast Notification */}
      {notification && (
        <div className={`toast toast-${notification.type} animate-slide-down`}>
          {notification.message}
        </div>
      )}

      <div className="container">
        <header className="header">
          <div className="header-content">
            <div className="header-left">
              <div className="header-logo">
                <img src="/logo.png" alt="AI Bid Writer Logo" className="logo-img" />
                <div className="header-text">
                  <h1>AI Bid Writer</h1>
                  <p className="tagline">Win more projects with AI-powered proposals</p>
                </div>
              </div>
            </div>
            
            <div className="header-right">
              <button 
                className="settings-btn"
                onClick={() => setShowSettings(!showSettings)}
                title="Settings"
              >
                <span className="settings-icon">⚙️</span>
                <span className="settings-text">Settings</span>
              </button>
            </div>
          </div>
          
          <div className="mode-switch">
            <button 
              className={`mode-btn ${mode === 'smart' ? 'active' : ''}`}
              onClick={() => setMode('smart')}
            >
              🎯 Smart Mode
            </button>
            <button 
              className={`mode-btn ${mode === 'manual' ? 'active' : ''}`}
              onClick={() => setMode('manual')}
            >
              ✍️ Manual Mode
            </button>
          </div>
        </header>

        {/* Settings Panel */}
        {showSettings && (
          <div className="settings-panel animate-fade-in">
            <h3>⚙️ Settings</h3>
            <div className="settings-content">
              <div className="setting-group">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.useCustomKey}
                    onChange={(e) => setSettings({...settings, useCustomKey: e.target.checked})}
                  />
                  Use Custom API Key
                </label>
              </div>
              
              {settings.useCustomKey && (
                <>
                  <div className="setting-group">
                    <label>AI Provider</label>
                    <select 
                      value={settings.provider}
                      onChange={(e) => setSettings({
                        ...settings, 
                        provider: e.target.value,
                        model: availableModels[e.target.value]?.[0] || ''
                      })}
                    >
                      <option value="gemini">Google Gemini (Free)</option>
                      <option value="openai">OpenAI</option>
                      <option value="anthropic">Anthropic Claude</option>
                    </select>
                  </div>

                  <div className="setting-group">
                    <label>Model</label>
                    <select 
                      value={settings.model}
                      onChange={(e) => setSettings({...settings, model: e.target.value})}
                    >
                      {availableModels[settings.provider]?.map(model => (
                        <option key={model} value={model}>{model}</option>
                      ))}
                    </select>
                  </div>

                  <div className="setting-group">
                    <label>API Key</label>
                    <input
                      type="password"
                      placeholder="Enter your API key"
                      value={settings.apiKey}
                      onChange={(e) => setSettings({...settings, apiKey: e.target.value})}
                    />
                    <small>Your API key is stored locally and never sent to our servers</small>
                  </div>
                </>
              )}

              <div className="setting-actions">
                <button onClick={handleSettingsSave} className="btn-primary">
                  💾 Save Settings
                </button>
                <button onClick={() => setShowSettings(false)} className="btn-secondary">
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="content">
          {mode === 'smart' ? (
            // SMART MODE - Just paste everything
            <div className="smart-mode">
              <div className="form-group">
                <label htmlFor="smart_content">
                  Paste Entire Project Page <span className="required">*</span>
                  <span className="hint">Copy everything from the project page and paste it here</span>
                </label>
                <textarea
                  id="smart_content"
                  value={smartContent}
                  onChange={(e) => setSmartContent(e.target.value)}
                  placeholder="Paste the entire project page here - including title, description, bids, budget, everything!"
                  rows="15"
                  className="smart-textarea"
                />
              </div>

              {parsedData && (
                <div className="parsed-preview animate-slide-up">
                  <h3>📋 Extracted Information</h3>
                  <div className="parsed-grid">
                    {parsedData.project_name && (
                      <div className="parsed-item animate-fade-in" style={{ animationDelay: '0.1s' }}>
                        <strong>Project:</strong> {parsedData.project_name}
                      </div>
                    )}
                    {parsedData.total_bids && (
                      <div className="parsed-item animate-fade-in" style={{ animationDelay: '0.2s' }}>
                        <strong>Total Bids:</strong> {parsedData.total_bids}
                      </div>
                    )}
                    {parsedData.average_bid && (
                      <div className="parsed-item animate-fade-in" style={{ animationDelay: '0.3s' }}>
                        <strong>Average Bid:</strong> {parsedData.average_bid}
                      </div>
                    )}
                    {parsedData.budget_range && (
                      <div className="parsed-item animate-fade-in" style={{ animationDelay: '0.4s' }}>
                        <strong>Budget:</strong> {parsedData.budget_range}
                      </div>
                    )}
                    {parsedData.time_remaining && (
                      <div className="parsed-item animate-fade-in" style={{ animationDelay: '0.5s' }}>
                        <strong>Time Left:</strong> {parsedData.time_remaining}
                      </div>
                    )}
                    {parsedData.client_location && (
                      <div className="parsed-item animate-fade-in" style={{ animationDelay: '0.6s' }}>
                        <strong>Client:</strong> {parsedData.client_location}
                      </div>
                    )}
                  </div>
                  
                  {parsedData.project_description && (
                    <div className="project-description animate-fade-in" style={{ animationDelay: '0.7s' }}>
                      <h4>📝 Project Description</h4>
                      <div className="description-text">
                        {parsedData.project_description}
                      </div>
                    </div>
                  )}
                  
                  {parsedData.required_skills && parsedData.required_skills.length > 0 && (
                    <div className="required-skills animate-fade-in" style={{ animationDelay: '0.8s' }}>
                      <h4>🛠️ Required Skills</h4>
                      <div className="skills-tags">
                        {parsedData.required_skills.map((skill, index) => (
                          <span key={index} className="skill-tag">{skill}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {extractionSteps.length > 0 && (
                <div className="extraction-process">
                  <h3>⚙️ Processing...</h3>
                  <div className="extraction-steps">
                    {extractionSteps.map((step, index) => (
                      <div key={index} className={`extraction-step ${step.complete ? 'complete' : 'active'}`}>
                        <div className="step-icon">
                          {step.complete ? '✓' : '⟳'}
                        </div>
                        <div className="step-text">{step.text}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="button-group">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={handleSmartPaste}
                  disabled={parsing || !smartContent.trim()}
                >
                  {parsing ? (
                    <>
                      <span className="spinner"></span>
                      Parsing...
                    </>
                  ) : (
                    <>🔍 Preview Extraction</>
                  )}
                </button>
                <button 
                  type="button" 
                  className="btn btn-primary" 
                  onClick={handleSmartGenerate}
                  disabled={loading || !smartContent.trim()}
                >
                  {loading ? (
                    <>
                      <span className="spinner"></span>
                      Generating...
                    </>
                  ) : (
                    <>✨ Generate Bid</>
                  )}
                </button>
                <button type="button" className="btn btn-secondary" onClick={handleReset}>
                  🔄 Reset
                </button>
              </div>
            </div>
          ) : (
            // MANUAL MODE - Original form
            <div className="form-section">
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="project_name">
                  Project Name <span className="required">*</span>
                </label>
                <input
                  type="text"
                  id="project_name"
                  name="project_name"
                  value={formData.project_name}
                  onChange={handleInputChange}
                  placeholder="e.g., Website Text Scraping to Excel"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="project_description">
                  Project Description <span className="required">*</span>
                </label>
                <textarea
                  id="project_description"
                  name="project_description"
                  value={formData.project_description}
                  onChange={handleInputChange}
                  placeholder="Paste the full project description here..."
                  rows="10"
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="bid_rank">Your Bid Rank (Optional)</label>
                  <input
                    type="number"
                    id="bid_rank"
                    name="bid_rank"
                    value={formData.bid_rank}
                    onChange={handleInputChange}
                    placeholder="e.g., 16"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="total_bids">Total Bids (Optional)</label>
                  <input
                    type="number"
                    id="total_bids"
                    name="total_bids"
                    value={formData.total_bids}
                    onChange={handleInputChange}
                    placeholder="e.g., 23"
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="your_bid_amount">Your Bid Amount (Optional)</label>
                  <input
                    type="text"
                    id="your_bid_amount"
                    name="your_bid_amount"
                    value={formData.your_bid_amount}
                    onChange={handleInputChange}
                    placeholder="e.g., $100 USD"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="winning_bid_amount">Winning Bid (Optional)</label>
                  <input
                    type="text"
                    id="winning_bid_amount"
                    name="winning_bid_amount"
                    value={formData.winning_bid_amount}
                    onChange={handleInputChange}
                    placeholder="e.g., $75 USD"
                  />
                </div>
              </div>

              <div className="button-group">
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? (
                    <>
                      <span className="spinner"></span>
                      Generating...
                    </>
                  ) : (
                    <>✨ Generate Bid</>
                  )}
                </button>
                <button type="button" className="btn btn-secondary" onClick={handleReset}>
                  🔄 Reset
                </button>
              </div>
            </form>
          </div>
          )}

          {error && (
            <div className="alert alert-error">
              <strong>Error:</strong> {error}
            </div>
          )}

          {result && (
            <div className="result-section">
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-value">{result.project_analysis.project_type}</div>
                  <div className="stat-label">Project Type</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{result.confidence_score}%</div>
                  <div className="stat-label">Confidence</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{result.word_count}</div>
                  <div className="stat-label">Words</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{result.project_analysis.skill_match_score}%</div>
                  <div className="stat-label">Skill Match</div>
                </div>
              </div>

              <div className="bid-output">
                <div className="bid-header">
                  <h3>📝 Generated Bid</h3>
                  <div className="bid-actions">
                    <button className="btn btn-copy" onClick={handleCopy}>
                      {copied ? '✓ Copied!' : '📋 Copy'}
                    </button>
                    <div className="refine-dropdown">
                      <button 
                        className="btn btn-refine" 
                        onClick={() => setShowRefineMenu(!showRefineMenu)}
                        disabled={refining}
                      >
                        {refining ? '⏳ Refining...' : '✨ Refine Bid'}
                      </button>
                      {showRefineMenu && (
                        <div className="refine-menu animate-fade-in">
                          {refinementOptions.map(option => (
                            <button
                              key={option.id}
                              className="refine-option"
                              onClick={() => handleRefineBid(option.id)}
                            >
                              <span className="refine-label">{option.label}</span>
                              <span className="refine-desc">{option.desc}</span>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                <div className="bid-text">{result.bid_text}</div>
              </div>

              {result.project_analysis.matched_skills?.length > 0 && (
                <div className="info-card">
                  <h4>✅ Matched Skills</h4>
                  <div className="tags">
                    {result.project_analysis.matched_skills.map((skill, idx) => (
                      <span key={idx} className="tag tag-success">{skill}</span>
                    ))}
                  </div>
                </div>
              )}

              {result.project_analysis.required_skills?.length > 0 && (
                <div className="info-card">
                  <h4>🎯 Required Skills</h4>
                  <div className="tags">
                    {result.project_analysis.required_skills.map((skill, idx) => (
                      <span key={idx} className="tag tag-primary">{skill}</span>
                    ))}
                  </div>
                </div>
              )}

              {result.optimization && (
                <div className="optimization-card">
                  <h4>💡 Optimization Suggestions</h4>
                  
                  {result.optimization.estimated_win_probability && (
                    <div className="win-probability">
                      <div className="progress-bar">
                        <div 
                          className="progress-fill" 
                          style={{width: `${result.optimization.estimated_win_probability}%`}}
                        ></div>
                      </div>
                      <span className="probability-text">
                        {result.optimization.estimated_win_probability}% Win Probability
                      </span>
                    </div>
                  )}

                  {result.optimization.pricing_advice && (
                    <div className="advice-item">
                      <strong>💰 Pricing:</strong> {result.optimization.pricing_advice}
                    </div>
                  )}

                  {result.optimization.positioning_advice && (
                    <div className="advice-item">
                      <strong>🎯 Positioning:</strong> {result.optimization.positioning_advice}
                    </div>
                  )}

                  {result.optimization.improvements?.length > 0 && (
                    <div className="advice-list">
                      <strong>🔧 Improvements:</strong>
                      <ul>
                        {result.optimization.improvements.map((imp, idx) => (
                          <li key={idx}>{imp}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {result.optimization.warnings?.length > 0 && (
                    <div className="advice-list warnings">
                      <strong>⚠️ Warnings:</strong>
                      <ul>
                        {result.optimization.warnings.map((warn, idx) => (
                          <li key={idx}>{warn}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
        
        <footer className="footer">
          <div className="footer-content">
            <div className="footer-text">
              Built with curiosity by <strong>Vicky Kumar</strong>
            </div>
            <div className="footer-links">
              <a href="https://github.com/algsoch" target="_blank" rel="noopener noreferrer" className="footer-link">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                GitHub
              </a>
              <a href="https://www.linkedin.com/in/algsoch" target="_blank" rel="noopener noreferrer" className="footer-link">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                </svg>
                LinkedIn
              </a>
            </div>
          </div>
        </footer>
      </div>

      {/* Custom Refinement Modal */}
      {showCustomRefine && (
        <div className="modal-overlay" onClick={() => setShowCustomRefine(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>✨ Custom Refinement</h3>
              <button className="modal-close" onClick={() => setShowCustomRefine(false)}>✕</button>
            </div>
            <div className="modal-body">
              <label>Enter your custom instructions:</label>
              <textarea
                placeholder="E.g., 'Make it more technical', 'Add emphasis on deadlines', 'Include pricing justification'..."
                value={customInstruction}
                onChange={(e) => setCustomInstruction(e.target.value)}
                rows={4}
                autoFocus
              />
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowCustomRefine(false)}>
                Cancel
              </button>
              <button className="btn-primary" onClick={handleCustomRefinement} disabled={!customInstruction.trim()}>
                ✨ Apply
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default BidGenerator;
