import React from 'react';

export default class HUDErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    // Keep the failure visible to developers without allowing one panel to
    // take down the entire ATLAS interface.
    // eslint-disable-next-line no-console
    console.error('[ATLAS HUD] component failure', error, info);
  }

  reset = () => {
    this.setState({ error: null });
  };

  render() {
    if (!this.state.error) return this.props.children;

    return (
      <div className="hud-error-boundary" role="alert" data-testid="hud-error-boundary">
        <strong>HUD module unavailable</strong>
        <span>The main interface is still running.</span>
        <button type="button" onClick={this.reset}>Retry module</button>
      </div>
    );
  }
}
