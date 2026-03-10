/** Haupt-Widget: Chat-Button + Chat-Fenster. */

import { useState } from 'react';
import { ChatWindow } from './ChatWindow';
import type { WidgetConfig } from './lib/config';

interface WidgetProps {
  config: WidgetConfig;
  visitorId: string;
}

export function Widget({ config, visitorId }: WidgetProps) {
  const [open, setOpen] = useState(false);

  return (
    <>
      {open && (
        <div className="widget-window">
          <ChatWindow config={config} visitorId={visitorId} />
        </div>
      )}
      <button
        className="widget-button"
        style={{ '--primary-color': config.primaryColor } as React.CSSProperties}
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? 'Chat schließen' : 'Chat öffnen'}
      >
        {open ? '✕' : '💬'}
      </button>
    </>
  );
}
