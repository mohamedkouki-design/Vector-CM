import React from 'react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    // Log to console for debugging
    console.error('ErrorBoundary caught:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen p-8">
          <div className="max-w-3xl mx-auto">
            <div className="glass-card p-6">
              <h3 className="text-xl font-bold mb-2">Something went wrong</h3>
              <pre className="text-sm text-red-200 whitespace-pre-wrap">{String(this.state.error)}</pre>
              <div className="mt-4">
                <button onClick={() => window.location.reload()} className="btn-primary">Reload page</button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
